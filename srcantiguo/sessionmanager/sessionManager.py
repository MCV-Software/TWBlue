# -*- coding: utf-8 -*-
""" Module to perform session actions such as addition, removal or display of the global settings dialogue. """
import time
import os
import logging
import shutil
import widgetUtils
import sessions
import output
import paths
import config_utils
import config
import application
from pubsub import pub
from controller import settings
from sessions.mastodon import session as MastodonSession
from sessions.gotosocial import session as GotosocialSession
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
        # Initialize the manager, responsible for storing session objects.
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
                if config_test.get("mastodon") != None:
                    name = _("{account_name}@{instance} (Mastodon)").format(account_name=config_test["mastodon"]["user_name"], instance=config_test["mastodon"]["instance"].replace("https://", ""))
                    if config_test["mastodon"]["instance"] != "" and config_test["mastodon"]["access_token"] != "":
                        sessionsList.append(name)
                        self.sessions.append(dict(type=config_test["mastodon"].get("type", "mastodon"), id=i))
                else:
                    try:
                        log.debug("Deleting session %s" % (i,))
                        shutil.rmtree(os.path.join(paths.config_path(), i))
                    except:
                        output.speak("An exception was raised while attempting to clean malformed session data. See the error log for details. If this message persists, contact the developers.",True)
                        os.exception("Exception thrown while removing malformed session")
        self.view.fill_list(sessionsList)

    def show(self):
        """ Displays the session manager dialog. """
        if self.view.get_response() == widgetUtils.OK:
            self.do_ok()
#  else:
        self.view.destroy()

    def do_ok(self):
        log.debug("Starting sessions...")
        for i in self.sessions:
            # Skip already created sessions. Useful when session manager controller is not created during startup.
            if sessions.sessions.get(i.get("id")) != None:
                continue
            # Create the session object based in session type.
            if i.get("type") == "mastodon":
                s = MastodonSession.Session(i.get("id"))
            elif i.get("type") == "gotosocial":
                s = GotosocialSession.Session(i.get("id"))
            s.get_configuration()
            if i.get("id") not in config.app["sessions"]["ignored_sessions"]:
                try:
                    s.login()
                except Exception as e:
                    log.exception("Exception during login on a TWBlue session.")
                    continue
            sessions.sessions[i.get("id")] = s
            self.new_sessions[i.get("id")] = s
#  self.view.destroy()

    def show_auth_error(self):
        error = view.auth_error()

    def manage_new_account(self, type):
        # Generic settings for all account types.
        location = (str(time.time())[-6:])
        log.debug("Creating %s session in the %s path" % (type, location))
        if type == "mastodon":
            s = MastodonSession.Session(location)
        result = s.authorise()
        if result == True:
            self.sessions.append(dict(id=location, type=s.settings["mastodon"].get("type")))
            self.view.add_new_session_to_list()

    def remove_account(self, index):
        selected_account = self.sessions[index]
        self.view.remove_session(index)
        self.removed_sessions.append(selected_account.get("id"))
        self.sessions.remove(selected_account)
        shutil.rmtree(path=os.path.join(paths.config_path(), selected_account.get("id")), ignore_errors=True)

    def configuration(self):
        """ Opens the global settings dialogue."""
        d = settings.globalSettingsController()
        if d.response == widgetUtils.OK:
            d.save_configuration()
