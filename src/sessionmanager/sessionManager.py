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
import asyncio # For async event handling
from pubsub import pub
from controller import settings
from sessions.mastodon import session as MastodonSession
from sessions.gotosocial import session as GotosocialSession
from sessions.atprotosocial import session as ATProtoSocialSession # Import ATProtoSocial session
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
        # Using CallAfter to handle async method from pubsub
        pub.subscribe(lambda type: wx.CallAfter(asyncio.create_task, self.manage_new_account(type)), "sessionmanager.new_account")
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
                    if config_test["mastodon"]["instance"] != "" and config_test["mastodon"]["access_token"] != "": # Basic validation
                        sessionsList.append(name)
                        self.sessions.append(dict(type=config_test["mastodon"].get("type", "mastodon"), id=i))
                elif config_test.get("atprotosocial") != None: # Check for ATProtoSocial config
                    handle = config_test["atprotosocial"].get("handle")
                    did = config_test["atprotosocial"].get("did") # DID confirms it was authorized
                    if handle and did:
                        name = _("{handle} (Bluesky)").format(handle=handle)
                        sessionsList.append(name)
                        self.sessions.append(dict(type="atprotosocial", id=i))
                    else: # Incomplete config, might be an old attempt or error
                        log.warning(f"Incomplete ATProtoSocial session config found for {i}, skipping.")
                        # Optionally delete malformed config here too
                        try:
                            log.debug("Deleting incomplete ATProtoSocial session %s" % (i,))
                            shutil.rmtree(os.path.join(paths.config_path(), i))
                        except Exception as e:
                            log.exception(f"Error deleting incomplete ATProtoSocial session {i}: {e}")
                        continue
                else: # Unknown or other session type not explicitly handled here for display
                    try:
                        log.debug("Deleting session %s with unknown type" % (i,))
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
            elif i.get("type") == "atprotosocial": # Handle ATProtoSocial session type
                s = ATProtoSocialSession.Session(i.get("id"))
            else:
                log.warning(f"Unknown session type '{i.get('type')}' for ID {i.get('id')}. Skipping.")
                continue

            s.get_configuration() # Assumes get_configuration() exists and is useful for all session types
                                  # For ATProtoSocial, this loads from its specific config file.

            # Login is now primarily handled by session.start() via mainController,
            # which calls _ensure_dependencies_ready().
            # Explicit s.login() here might be redundant or premature if full app context isn't ready.
            # We'll rely on the mainController to call session.start() which handles login.
            # if i.get("id") not in config.app["sessions"]["ignored_sessions"]:
            #     try:
            #         # For ATProtoSocial, login is async and handled by session.start()
            #         # if not s.is_ready(): # Only attempt login if not already ready
            #         #    log.info(f"Session {s.uid} ({s.kind}) not ready, login will be attempted by start().")
            #         pass
            #     except Exception as e:
            #         log.exception(f"Exception during pre-emptive login check for session {s.uid} ({s.kind}).")
            #         continue
            sessions.sessions[i.get("id")] = s # Add to global session store
            self.new_sessions[i.get("id")] = s # Track as a new session for this manager instance
#  self.view.destroy()

    def show_auth_error(self):
        error = view.auth_error() # This seems to be a generic auth error display

    async def manage_new_account(self, type): # Made async
        # Generic settings for all account types.
        location = (str(time.time())[-6:]) # Unique ID for the session config directory
        log.debug("Creating %s session in the %s path" % (type, location))

        s: sessions.base.baseSession | None = None # Type hint for session object

        if type == "mastodon":
            s = MastodonSession.Session(location)
        elif type == "atprotosocial":
            s = ATProtoSocialSession.Session(location)
        # Add other session types here if needed (e.g., gotosocial)
        # elif type == "gotosocial":
        # s = GotosocialSession.Session(location)

        if not s:
            log.error(f"Unsupported session type for creation: {type}")
            self.view.show_unauthorised_error() # Or a more generic "cannot create" error
            return

        try:
            result = await s.authorise() # Call the (now potentially async) authorise method
            if result == True:
                # Session config (handle, did for atproto) should be saved by authorise/login.
                # Here we just update the session manager's internal list and UI.
                session_type_for_dict = type # Store the actual type string
                if hasattr(s, 'settings') and s.settings and s.settings.get(type) and s.settings[type].get("type"):
                    # Mastodon might have a more specific type in its settings (e.g. gotosocial)
                     session_type_for_dict = s.settings[type].get("type")

                self.sessions.append(dict(id=location, type=session_type_for_dict))
                self.view.add_new_session_to_list() # This should update the UI list
                # The session object 's' itself isn't stored in self.new_sessions until do_ok if app is restarting
                # But for immediate use if not restarting, it might need to be added to sessions.sessions
                sessions.sessions[location] = s # Make it globally available immediately
                self.new_sessions[location] = s


            else: # Authorise returned False or None
                self.view.show_unauthorised_error()
                # Clean up the directory if authorization failed and nothing was saved
                if os.path.exists(os.path.join(paths.config_path(), location)):
                    try:
                        shutil.rmtree(os.path.join(paths.config_path(), location))
                        log.info(f"Cleaned up directory for failed auth: {location}")
                    except Exception as e_rm:
                        log.error(f"Error cleaning up directory {location} after failed auth: {e_rm}")
        except Exception as e:
            log.error(f"Error during new account authorization for type {type}: {e}", exc_info=True)
            self.view.show_unauthorised_error() # Show generic error
            # Clean up
            if os.path.exists(os.path.join(paths.config_path(), location)):
                try:
                    shutil.rmtree(os.path.join(paths.config_path(), location))
                except Exception as e_rm:
                    log.error(f"Error cleaning up directory {location} after exception: {e_rm}")


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
