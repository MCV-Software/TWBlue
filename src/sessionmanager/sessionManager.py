# -*- coding: utf-8 -*-
""" Module to perform session actions such as adddition, removal or display of the global settings dialogue. """
import shutil
import time
import os
import logging
import widgetUtils
import sessions
import output
import paths
import config_utils
import config
from pubsub import pub
from tweepy.errors import TweepyException
from controller import settings
from sessions.twitter import session as TwitterSession
from sessions.mastodon import session as MastodonSession
from . import manager
from . import wxUI as view

log = logging.getLogger("sessionmanager.sessionManager")

class sessionManagerController(object):
    def __init__(self, started: bool = False):
        """ Class constructor.

        Creates the SessionManager class controller, responsible for the accounts within TWBlue. From this dialog, users can add/Remove accounts, or load the global settings dialog.

        :param started: Indicates whether this object is being created during application startup (when no other controller has been instantiated) or not. It is important for us to know this, as we won't show the button to open global settings dialog if the application has been started. Users must choose the corresponding option in the menu bar.
        :type started: bool
        """
        super(sessionManagerController, self).__init__()
        log.debug("Setting up the session manager.")
        self.started = started
        manager.setup()
        self.view = view.sessionManagerWindow()
        pub.subscribe(self.manage_new_account, "sessionmanager.new_account")
        pub.subscribe(self.remove_account, "sessionmanager.remove_account")
        if self.started == False:
            pub.subscribe(self.configuration, "sessionmanager.configuration")
        else:
            self.view.hide_configuration()
        # Store a temporary copy of new and removed sessions, so we will perform actions on them during call to on_ok.
        self.new_sessions = {}
        self.removed_sessions = []

    def fill_list(self):
        """ Fills the session list with all valid sessions that could be found in config path. """
        sessionsList = []
        reserved_dirs = ["dicts"]
        log.debug("Filling the sessions list.")
        self.sessions = []
        for i in os.listdir(paths.config_path()):
            if os.path.isdir(os.path.join(paths.config_path(), i)) and i not in reserved_dirs:
                log.debug("Adding session %s" % (i,))
                strconfig = "%s/session.conf" % (os.path.join(paths.config_path(), i))
                config_test = config_utils.load_config(strconfig)
                if len(config_test) == 0:
                    try:
                        log.debug("Deleting session %s" % (i,))
                        shutil.rmtree(os.path.join(paths.config_path(), i))
                        continue
                    except:
                        output.speak("An exception was raised while attempting to clean malformed session data. See the error log for details. If this message persists, contact the developers.",True)
                        os.exception("Exception thrown while removing malformed session")
                        continue
                if config_test.get("twitter") != None:
                    name = _("{account_name} (Twitter)").format(account_name=config_test["twitter"]["user_name"])
                    if config_test["twitter"]["user_key"] != "" and config_test["twitter"]["user_secret"] != "":
                        sessionsList.append(name)
                        self.sessions.append(i)
                elif config_test.get("mastodon") != None:
                    name = _("{account_name} (Mastodon)").format(account_name=config_test["mastodon"]["user_name"])
                    if config_test["mastodon"]["instance"] != "" and config_test["mastodon"]["access_token"] != "":
                        sessionsList.append(name)
                        self.sessions.append(i)
                else:
                    try:
                        log.debug("Deleting session %s" % (i,))
                        shutil.rmtree(os.path.join(paths.config_path(), i))
                    except:
                        output.speak("An exception was raised while attempting to clean malformed session data. See the error log for details. If this message persists, contact the developers.",True)
                        os.exception("Exception thrown while removing malformed session")
        self.view.fill_list(sessionsList)

    def show(self):
        if self.view.get_response() == widgetUtils.OK:
            self.do_ok()
#  else:
        self.view.destroy()

    def do_ok(self):
        log.debug("Starting sessions...")
        for i in self.sessions:
            if (i in sessions.sessions) == True: continue
            s = session.Session(i)
            s.get_configuration()
            if i not in config.app["sessions"]["ignored_sessions"]:
                try:
                    s.login()
                except TweepyException:
                    self.show_auth_error(s.settings["twitter"]["user_name"])
                    continue
            sessions.sessions[i] = s
            self.new_sessions[i] = s
#  self.view.destroy()

    def show_auth_error(self, user_name):
        error = view.auth_error(user_name)

    def manage_new_account(self, type):
        # Generic settings for all account types.
        location = (str(time.time())[-6:])
        log.debug("Creating %s session in the %s path" % (type, location))
        if type == "twitter":
            s = TwitterSession.Session(location)
        elif type == "mastodon":
            s = MastodonSession.Session(location)
        manager.manager.add_session(location)
        s.get_configuration()
        s.authorise()
        self.sessions.append(location)
        self.view.add_new_session_to_list()
        s.settings.write()

    def remove_account(self, index):
        selected_account = self.sessions[index]
        self.view.remove_session(index)
        self.removed_sessions.append(selected_account)
        self.sessions.remove(selected_account)
        shutil.rmtree(path=os.path.join(paths.config_path(), selected_account), ignore_errors=True)

    def configuration(self):
        """ Opens the global settings dialogue."""
        d = settings.globalSettingsController()
        if d.response == widgetUtils.OK:
            d.save_configuration()
