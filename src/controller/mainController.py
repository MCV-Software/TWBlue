# -*- coding: utf-8 -*-
import os
import sys
import logging
import webbrowser
import wx
import requests
import asyncio
import keystrokeEditor
import sessions
import widgetUtils
import config
import languageHandler
import application
import sound
import output
from pubsub import pub
from extra import SoundsTutorial
from update import updater
from wxUI import view, dialogs, commonMessageDialogs, sysTrayIcon
from keyboard_handler.wx_handler import WXKeyboardHandler
from sessionmanager import manager, sessionManager
from controller import buffers
from mysc import restart
from mysc import localization
from mysc.thread_utils import call_threaded
from mysc.repeating_timer import RepeatingTimer
from controller.mastodon import handler as MastodonHandler
from controller.blueski import handler as BlueskiHandler # Added import
from . import settings, userAlias

log = logging.getLogger("mainController")

class Controller(object):

    """ Main Controller for TWBlue. It manages the main window and sessions."""

    def search_buffer(self, name_, user):

        """ Searches a buffer.
       name_ str: The name for the buffer
       user str: The account for the buffer.
       for example you may want to search the home_timeline buffer for the tw_blue2 user.
        Return type: buffers.buffer object."""
        for i in self.buffers:
            if i.name == name_ and i.account == user: return i

    def get_current_buffer(self):
        """ Get the current focused bufferObject.
        Return type: buffers.buffer object."""
        buffer = self.view.get_current_buffer()
        if hasattr(buffer, "account"):
            buffer = self.search_buffer(buffer.name, buffer.account)
            return buffer

    def get_best_buffer(self):
        """ Get the best buffer for doing  something using the session object.
        This function is useful when you need to open a timeline or post a tweet, and the user is in a buffer without a session, for example the events buffer.
        Return type: twitterBuffers.buffer object."""
        # Gets the parent buffer to know what account is doing an action
        view_buffer = self.view.get_current_buffer()
        # If the account has no session attached, we will need to search the first available non-empty buffer for that account to use its session.
        if view_buffer.type == "account" or view_buffer.type == "empty":
            buffer = self.get_first_buffer(view_buffer.account)
        else:
            buffer = self.search_buffer(view_buffer.name, view_buffer.account)
        if buffer != None: return buffer

    def get_first_buffer(self, account):
        """ Gets the first valid buffer for an account.
        account str: A twitter username.
        The first valid buffer is the home timeline."""
        for i in self.buffers:
            if i.account == account and i.invisible == True and i.session != None:
                return i

    def get_last_buffer(self, account):
        """ Gets the last valid buffer for an account.
        account str: A twitter username.
        The last valid buffer is the last buffer that contains a session object assigned."""
        results = self.get_buffers_for_account(account)
        return results[-1]

    def get_first_buffer_index(self, account):
        buff = self.get_first_buffer(account)
        return self.view.search(buff.name, buff.account)

    def get_last_buffer_index(self, account):
        buff = self.get_last_buffer(account)
        return self.view.search(buff.name, buff.account)

    def get_buffers_for_account(self, account):
        results = []
        buffers = self.view.get_buffers()
        [results.append(self.search_buffer(i.name, i.account)) for i in buffers if i.account == account and (i.type != "account")]
        return results

    def get_handler(self, type):
        """Return the controller handler for a given session type."""
        try:
            if type == "mastodon":
                return MastodonHandler.Handler()
            if type == "blueski":
                return BlueskiHandler.Handler()
        except Exception:
            log.exception("Error creating handler for type %s", type)
        return None

    def bind_other_events(self):
        """ Binds the local application events with their functions."""
        log.debug("Binding other application events...")

        # Core application pubsub events.
        pub.subscribe(self.logout_account, "logout")
        pub.subscribe(self.login_account, "login")
        pub.subscribe(self.execute_action, "execute-action")
        pub.subscribe(self.search_topic, "search")
        pub.subscribe(self.create_buffer, "createBuffer")
        pub.subscribe(self.toggle_share_settings, "toggleShare")
        pub.subscribe(self.invisible_shorcuts_changed, "invisible-shorcuts-changed")
        pub.subscribe(self.create_account_buffer, "core.create_account")
        pub.subscribe(self.change_buffer_title, "core.change_buffer_title")
        pub.subscribe(self.handle_compose_dialog_send, "compose_dialog.send_post") # For new compose dialog

        # Mastodon specific events.
        pub.subscribe(self.mastodon_new_item, "mastodon.new_item")
        pub.subscribe(self.mastodon_updated_item, "mastodon.updated_item")
        pub.subscribe(self.mastodon_new_conversation, "mastodon.conversation_received")
        pub.subscribe(self.mastodon_error_post, "mastodon.error_post")

        # Bluesky specific events.
        pub.subscribe(self.blueski_new_item, "blueski.new_item")

        # connect application events to GUI
        widgetUtils.connect_event(self.view, widgetUtils.CLOSE_EVENT, self.exit_)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.show_hide, menuitem=self.view.show_hide)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.update_profile, menuitem=self.view.updateProfile)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.search, menuitem=self.view.menuitem_search)
#        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.list_manager, menuitem=self.view.lists)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.find, menuitem=self.view.find)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.accountConfiguration, menuitem=self.view.account_settings)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.configuration, menuitem=self.view.prefs)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.ocr_image, menuitem=self.view.ocr)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.learn_sounds, menuitem=self.view.sounds_tutorial)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.exit, menuitem=self.view.close)
        widgetUtils.connect_event(self.view, widgetUtils.CLOSE_EVENT, self.exit)
        if widgetUtils.toolkit == "wx":
            log.debug("Binding the exit function...")
            widgetUtils.connectExitFunction(self.exit_)
            widgetUtils.connect_event(self.view, widgetUtils.MENU, self.edit_keystrokes, menuitem=self.view.keystroke_editor)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.post_tweet, self.view.compose)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.post_reply, self.view.reply)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.post_retweet, self.view.share)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.add_to_favourites, self.view.fav)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.remove_from_favourites, self.view.unfav)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.view_item, self.view.view)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.delete, self.view.delete)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.follow, menuitem=self.view.follow)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.send_dm, self.view.dm)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.user_details, self.view.details)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.get_more_items, menuitem=self.view.load_previous_items)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.clear_buffer, menuitem=self.view.clear)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.remove_buffer, self.view.deleteTl)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.check_for_updates, self.view.check_for_updates)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.about, menuitem=self.view.about)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.visit_website, menuitem=self.view.visit_website)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.get_soundpacks, menuitem=self.view.get_soundpacks)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.manage_accounts, self.view.manage_accounts)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.toggle_autoread, menuitem=self.view.autoread)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.toggle_buffer_mute, self.view.mute_buffer)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.open_timeline, self.view.timeline)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.open_favs_timeline, self.view.favs)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.community_timeline, self.view.community_timeline)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.open_conversation, menuitem=self.view.view_conversation)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.seekLeft, menuitem=self.view.seekLeft)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.seekRight, menuitem=self.view.seekRight)
        if widgetUtils.toolkit == "wx":
            widgetUtils.connect_event(self.view.nb, widgetUtils.NOTEBOOK_PAGE_CHANGED, self.buffer_changed)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.view_documentation, self.view.doc)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.view_changelog, self.view.changelog)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.add_alias, self.view.addAlias)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.update_buffer, self.view.update_buffer)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.manage_aliases, self.view.manageAliases)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.report_error, self.view.reportError)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.create_filter, self.view.filter)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.manage_filters, self.view.manage_filters)

    def set_systray_icon(self):
        self.systrayIcon = sysTrayIcon.SysTrayIcon()
        widgetUtils.connect_event(self.systrayIcon, widgetUtils.MENU, self.post_tweet, menuitem=self.systrayIcon.post)
        widgetUtils.connect_event(self.systrayIcon, widgetUtils.MENU, self.configuration, menuitem=self.systrayIcon.global_settings)
        widgetUtils.connect_event(self.systrayIcon, widgetUtils.MENU, self.accountConfiguration, menuitem=self.systrayIcon.account_settings)
        widgetUtils.connect_event(self.systrayIcon, widgetUtils.MENU, self.show_hide, menuitem=self.systrayIcon.show_hide)
        widgetUtils.connect_event(self.systrayIcon, widgetUtils.MENU, self.check_for_updates, menuitem=self.systrayIcon.check_for_updates)
        widgetUtils.connect_event(self.systrayIcon, widgetUtils.MENU, self.view_documentation, menuitem=self.systrayIcon.doc)
        widgetUtils.connect_event(self.systrayIcon, widgetUtils.MENU, self.exit, menuitem=self.systrayIcon.exit)
        widgetUtils.connect_event(self.systrayIcon, widgetUtils.TASKBAR_LEFT_CLICK, self.taskbar_left_click)
        widgetUtils.connect_event(self.systrayIcon, widgetUtils.TASKBAR_RIGHT_CLICK, self.taskbar_right_click)

    def taskbar_left_click(self, *args, **kwargs):
        if self.showing == True:
            self.view.set_focus()
        else:
            self.show_hide()

    def taskbar_right_click(self, *args, **kwargs):
        self.systrayIcon.show_menu()

    def get_handler(self, type):
        handler = self.handlers.get(type)
        if handler is None:
            if type == "mastodon":
                handler = MastodonHandler.Handler()
            elif type == "blueski":
                handler = BlueskiHandler.Handler()
            self.handlers[type] = handler
        return handler

    def __init__(self):
        super(Controller, self).__init__()
        # Visibility state.
        self.showing = True
        # main window
        self.view = view.mainFrame()
        # buffers list.
        self.buffers: list[buffers.base.Buffer] = [] # Added type hint
        self.started = False
        # accounts list.
        self.accounts = []
        # This saves the current account (important in invisible mode)
        self.current_account = ""
        # this saves current menu bar layout.
        self.menubar_current_handler = ""
        # Handlers are special objects as they manage the mapping of available features and events in different social networks.
        self.handlers = dict()
        self.view.prepare()
        self.bind_other_events()
        self.set_systray_icon()

    def check_invisible_at_startup(self):
        # Visibility check.
        if config.app["app-settings"]["hide_gui"] == True:
            self.show_hide()
            self.view.Show()
            self.view.Hide()
        # Invisible keyboard Shorcuts check.
        if config.app["app-settings"]["use_invisible_keyboard_shorcuts"] == True:
            km = self.create_invisible_keyboard_shorcuts()
            self.register_invisible_keyboard_shorcuts(km)

    def do_work(self):
        """ Creates the buffer objects for all accounts. This does not starts the buffer streams, only creates the objects."""
        log.debug("Creating buffers for all sessions...")
        for i in sessions.sessions:
            log.debug("Working on session %s" % (i,))
            if sessions.sessions[i].is_logged == False:
                if sessions.sessions[i].session_id in config.app["sessions"]["ignored_sessions"]:
                    self.create_ignored_session_buffer(sessions.sessions[i])
                    continue
                # Try auto-login for sessions if credentials exist
                try:
                    sessions.sessions[i].login()
                except Exception:
                    log.exception("Auto-login attempt failed for session %s", i)
                if sessions.sessions[i].is_logged == False:
                    self.create_ignored_session_buffer(sessions.sessions[i])
                    continue
            # Supported session types
            valid_session_types = ["mastodon", "blueski"]
            if sessions.sessions[i].type in valid_session_types:
                try:
                    handler = self.get_handler(type=sessions.sessions[i].type)
                    if handler is not None:
                        handler.create_buffers(sessions.sessions[i], controller=self)
                except Exception:
                    log.exception("Error creating buffers for session %s (%s)", i, sessions.sessions[i].type)
        log.debug("Setting updates to buffers every %d seconds..." % (60*config.app["app-settings"]["update_period"],))
        self.update_buffers_function = RepeatingTimer(60*config.app["app-settings"]["update_period"], self.update_buffers)
        self.update_buffers_function.start()

    def start(self):
        """ Starts all buffer objects. Loads their items."""
        for i in sessions.sessions:
            if sessions.sessions[i].is_logged == False: continue
            call_threaded(self._start_session_buffers, sessions.sessions[i])
        if len(sessions.sessions) > 0 and config.app["app-settings"]["play_ready_sound"] == True:
            sessions.sessions[list(sessions.sessions.keys())[0]].sound.play("ready.ogg")
        if config.app["app-settings"]["speak_ready_msg"] == True:
            output.speak(_(u"Ready"))
        self.started = True
        if len(self.accounts) > 0:
            b = self.get_first_buffer(self.accounts[0])
            self.update_menus(handler=self.get_handler(b.session.type))

    def _start_session_buffers(self, session):
        """Helper to start buffers for a session in a background thread."""
        try:
            self.start_buffers(session)
            self.set_buffer_positions(session)
            if hasattr(session, "start_streaming"):
                session.start_streaming()
        except Exception:
            log.exception("Error starting buffers for session %s", session.session_id)

    def create_ignored_session_buffer(self, session):
        pub.sendMessage("core.create_account", name=session.get_name(), session_id=session.session_id)

    def login_account(self, session_id):
        session = None
        for i in sessions.sessions:
            if sessions.sessions[i].session_id == session_id:
                session = sessions.sessions[i]
                break
        if not session:
            return
        
        old_name = session.get_name()
        try:
            session.login()
        except Exception as e:
            log.exception("Login failed for session %s", session_id)
            output.speak(_("Login failed for {0}: {1}").format(old_name, str(e)), True)
            return

        if not session.logged:
            output.speak(_("Login failed for {0}. Please check your credentials.").format(old_name), True)
            return

        new_name = session.get_name()
        if old_name != new_name:
            log.info(f"Account name changed from {old_name} to {new_name} after login")
            if self.current_account == old_name:
                self.current_account = new_name
            if old_name in self.accounts:
                idx = self.accounts.index(old_name)
                self.accounts[idx] = new_name
            else:
                self.accounts.append(new_name)
            
            # Update root buffer name and account
            for b in self.buffers:
                if b.account == old_name:
                    b.account = new_name
                    if hasattr(b, "buffer"):
                        b.buffer.account = new_name
                    # If this is the root node, its name matches old_name (e.g. "Bluesky")
                    if b.name == old_name:
                        b.name = new_name
                        if hasattr(b, "buffer"):
                            b.buffer.name = new_name
            
            # Update tree node label
            self.change_buffer_title(old_name, old_name, new_name)

        handler = self.get_handler(type=session.type)
        if handler != None and hasattr(handler, "create_buffers"):
            try:
                handler.create_buffers(session=session, controller=self, createAccounts=False)
            except Exception:
                log.exception("Error creating buffers after login for session %s (%s)", session.session_id, session.type)
        self.start_buffers(session)
        if hasattr(session, "start_streaming"):
            session.start_streaming()

    def create_account_buffer(self, name, session_id, logged=False):
        account = buffers.base.AccountBuffer(self.view.nb, name, name, session_id)
        if logged == False:
            account.logged = logged
        account.setup_account()
        self.buffers.append(account)
        self.view.add_buffer(account.buffer , name=name)

    def create_buffer(self, buffer_type="baseBuffer", session_type="twitter", buffer_title="", parent_tab=None, start=False, kwargs={}):
        # Copy kwargs to avoid mutating a shared dict across calls
        if not isinstance(kwargs, dict):
            kwargs = {}
        else:
            kwargs = dict(kwargs)
        log.debug("Creating buffer of type {0} with parent_tab of {2} arguments {1}".format(buffer_type, kwargs, parent_tab))
        if kwargs.get("parent") == None:
            kwargs["parent"] = self.view.nb
        if not hasattr(buffers, session_type) and session_type != "blueski": # Allow blueski to be handled separately
            raise AttributeError("Session type %s does not exist yet." % (session_type))

        try:
            buffer_panel_class = None
            if session_type == "blueski":
                from controller.buffers.blueski import timeline as BlueskiTimelines
                from controller.buffers.blueski import user as BlueskiUsers
                from controller.buffers.blueski import chat as BlueskiChats
                
                if "user_id" in kwargs and "session" not in kwargs:
                     kwargs["session"] = sessions.sessions.get(kwargs["user_id"])
                
                if "name" not in kwargs: kwargs["name"] = buffer_title

                buffer_map = {
                    "home_timeline": BlueskiTimelines.HomeTimeline,
                    "following_timeline": BlueskiTimelines.FollowingTimeline,
                    "notifications": BlueskiTimelines.NotificationBuffer,
                    "conversation": BlueskiTimelines.Conversation,
                    "likes": BlueskiTimelines.LikesBuffer,
                    "MentionsBuffer": BlueskiTimelines.MentionsBuffer,
                    "mentions": BlueskiTimelines.MentionsBuffer,
                    "SentBuffer": BlueskiTimelines.SentBuffer,
                    "sent": BlueskiTimelines.SentBuffer,
                    "SearchBuffer": BlueskiTimelines.SearchBuffer,
                    "search": BlueskiTimelines.SearchBuffer,
                    "UserBuffer": BlueskiUsers.UserBuffer,
                    "FollowersBuffer": BlueskiUsers.FollowersBuffer,
                    "FollowingBuffer": BlueskiUsers.FollowingBuffer,
                    "BlocksBuffer": BlueskiUsers.BlocksBuffer,
                    "PostUserListBuffer": BlueskiUsers.PostUserListBuffer,
                    "ConversationListBuffer": BlueskiChats.ConversationListBuffer,
                    "ChatMessageBuffer": BlueskiChats.ChatBuffer,
                    "chat_messages": BlueskiChats.ChatBuffer,
                    "UserTimeline": BlueskiTimelines.UserTimeline,
                    "user_timeline": BlueskiTimelines.UserTimeline,
                }

                buffer_panel_class = buffer_map.get(buffer_type)
                if buffer_panel_class is None:
                    # Fallback for others including user_timeline to HomeTimeline for now
                    log.warning(f"Unsupported Blueski buffer type: {buffer_type}. Falling back to HomeTimeline.")
                    buffer_panel_class = BlueskiTimelines.HomeTimeline
            else: # Existing logic for other session types
                available_buffers = getattr(buffers, session_type)
                if not hasattr(available_buffers, buffer_type):
                    raise AttributeError("Specified buffer type does not exist: %s" % (buffer_type,))
                buffer_panel_class = getattr(available_buffers, buffer_type)

            # Instantiate the panel
            # Ensure 'parent' kwarg is correctly set if not already
            if "parent" not in kwargs:
                kwargs["parent"] = self.view.nb # self.view.nb is the wx.Treebook

            buffer = buffer_panel_class(**kwargs) # This is the wx.Panel instance

            if start:
                try:
                    if hasattr(buffer, "start_stream"):
                        buffer.start_stream(mandatory=True, play_sound=False)
                except ValueError:
                    commonMessageDialogs.unauthorized()
                    return
            self.buffers.append(buffer)
            if parent_tab == None:
                log.debug("Appending buffer {}...".format(buffer,))
                self.view.add_buffer(buffer.buffer, buffer_title)
            else:
                self.view.insert_buffer(buffer.buffer, buffer_title, parent_tab)
                log.debug("Inserting buffer {0} into control {1}".format(buffer, parent_tab))
        except Exception:
            log.exception("Error creating buffer '%s' for session_type '%s'", buffer_type, session_type)

    def set_buffer_positions(self, session):
        "Sets positions for buffers if values exist in the database."
        for i in self.buffers:
            if i.account == session.get_name() and i.name+"_pos" in session.db and hasattr(i.buffer,'list'):
                i.buffer.list.select_item(session.db[str(i.name+"_pos")])

    def logout_account(self, session_id):
        for i in sessions.sessions:
            if sessions.sessions[i].session_id == session_id: session = sessions.sessions[i]
        name =session.get_name()
        delete_buffers = []
        for i in self.buffers:
            if i.account == name and i.name != name:
                delete_buffers.append(i.name)
        for i in delete_buffers:
            self.destroy_buffer(i, name)
        session.db = None
        session.logged = False

    def destroy_buffer(self, buffer_name, session_name):
        buffer = self.search_buffer(buffer_name, session_name)
        if buffer == None:
            return
        buff = self.view.search(buffer.name, session_name)
        if buff == None:
            return
        self.view.delete_buffer(buff)
        self.buffers.remove(buffer)
        del buffer

    def search_topic(self, term):
        self.search(value=term)

    def search(self, event=None, value="", *args, **kwargs):
        buffer = self.get_best_buffer()
        handler = self.get_handler(type=buffer.session.type)
        if handler != None and hasattr(handler, "search"):
            return handler.search(controller=self, session=buffer.session, value=value)

    def find(self, *args, **kwargs):
        if 'string' in kwargs:
            string=kwargs['string']
        else:
            string=''
        dlg = dialogs.find.findDialog(string)
        if dlg.get_response() == widgetUtils.OK and dlg.get("string") != "":
            string = dlg.get("string")
        #If we still have an empty string for some reason (I.E. user clicked cancel, etc), return here.
        if string == '':
            log.debug("Find canceled.")
            return
        page = self.get_current_buffer()
        if not hasattr(page.buffer, "list"):
            output.speak(_(u"No session is currently in focus. Focus a session with the next or previous session shortcut."), True)
            return
        count = page.buffer.list.get_count()
        if count < 1:
            output.speak(_(u"Empty buffer."), True)
            return
        start = page.buffer.list.get_selected()
        for i in range(start, count):
            if string.lower() in page.buffer.list.get_text_column(i, 1).lower():
                page.buffer.list.select_item(i)
                return output.speak(page.get_message(), True)
        output.speak(_(u"{0} not found.").format(string,), True)

    def seekLeft(self, *args, **kwargs):
        try:
            sound.URLPlayer.seek(-5000)
        except:
            output.speak("Unable to seek.",True)

    def seekRight(self, *args, **kwargs):
        try:
            sound.URLPlayer.seek(5000)
        except:
            output.speak("Unable to seek.",True)

    def edit_keystrokes(self, *args, **kwargs):
        buffer = self.get_best_buffer()
        editor = keystrokeEditor.KeystrokeEditor(buffer.session.type)
        if editor.changed == True:
            config.keymap.write()
            register = False
            # determines if we need to reassign the keymap.
            if self.showing == False:
                register = True
            elif config.app["app-settings"]["use_invisible_keyboard_shorcuts"] == True:
                register = True
            # If there is a keyboard handler instance we need unregister all old keystrokes before register the new ones.
            if hasattr(self, "keyboard_handler"):
                keymap = {}
                for i in editor.hold_map:
                    if hasattr(self, i): keymap[editor.hold_map[i]] = getattr(self, i)
                self.unregister_invisible_keyboard_shorcuts(keymap)
            self.invisible_shorcuts_changed(registered=register)

    def learn_sounds(self, *args, **kwargs):
        """ Opens the sounds tutorial for the current account."""
        buffer = self.get_best_buffer()
        SoundsTutorial.soundsTutorial(buffer.session)

    def configuration(self, *args, **kwargs):
        """ Opens the global settings dialogue."""
        d = settings.globalSettingsController()
        if d.response == widgetUtils.OK:
            d.save_configuration()
            if d.needs_restart == True:
                commonMessageDialogs.needs_restart()
                restart.restart_program()

    def accountConfiguration(self, *args, **kwargs):
        """ Opens the account settings dialogue for the current account."""
        buffer = self.get_best_buffer()
        handler = self.get_handler(type=buffer.session.type)
        if handler != None and hasattr(handler, "account_settings"):
            manager.manager.set_current_session(buffer.session.session_id)
            return handler.account_settings(buffer=buffer, controller=self)

    def check_for_updates(self, *args, **kwargs):
        if not getattr(sys, 'frozen', False):
            log.debug("Running from source, can't update")
            commonMessageDialogs.cant_update_source()
            return
        update = updater.do_update()
        if update == False:
            view.no_update_available()

    def delete(self, *args, **kwargs):
        """ Deletes an item in the current buffer.
        Users can only remove their tweets and direct messages, other users' tweets and people (followers, friends, blocked, etc) can not be removed using this method."""
        buffer = self.view.get_current_buffer()
        if hasattr(buffer, "account"):
            buffer = self.search_buffer(buffer.name, buffer.account)
            buffer.destroy_status()

    def edit_post(self, *args, **kwargs):
        """ Edits a post in the current buffer.
        Users can only edit their own posts."""
        buffer = self.view.get_current_buffer()
        if hasattr(buffer, "account"):
            buffer = self.search_buffer(buffer.name, buffer.account)
            if hasattr(buffer, "edit_status"):
                buffer.edit_status()

    def exit(self, *args, **kwargs):
        if config.app["app-settings"]["ask_at_exit"] == True:
            answer = commonMessageDialogs.exit_dialog(self.view)
            if answer == widgetUtils.YES:
                self.exit_()
        else:
            self.exit_()

    def exit_(self, *args, **kwargs):
        for i in self.buffers: i.save_positions()
        log.debug("Exiting...")
        log.debug("Saving global configuration...")
        for item in sessions.sessions:
            if sessions.sessions[item].logged == False:
                continue
            sessions.sessions[item].sound.cleaner.cancel()
            log.debug("Saving database for " +    sessions.sessions[item].session_id)
            sessions.sessions[item].save_persistent_data()
        self.systrayIcon.RemoveIcon()
        pidpath = os.path.join(os.getenv("temp"), "{}.pid".format(application.name))
        if os.path.exists(pidpath):
            os.remove(pidpath)
        widgetUtils.exit_application()

    def follow(self, *args, **kwargs):
        buffer = self.get_current_buffer()
        handler = self.get_handler(type=buffer.session.type)
        if handler != None and hasattr(handler, "follow"):
            return handler.follow(buffer=buffer)

    def add_alias(self, *args, **kwargs):
        buffer = self.get_best_buffer()
        handler = self.get_handler(type=buffer.session.type)
        if handler != None and hasattr(handler, "add_alias"):
            return handler.add_alias(buffer=buffer)

    def manage_aliases(self, *args, **kwargs):
        buffer = self.get_best_buffer()
        alias_controller = userAlias.userAliasController(buffer.session.settings)

    def post_tweet(self, event=None):
        buffer = self.get_best_buffer()
        if hasattr(buffer, "post_status"):
            buffer.post_status()

    def handle_compose_dialog_send(self, session, text, files, reply_to, cw_text, is_sensitive, kwargs, dialog_instance):
        """Handles the actual sending of a post after ComposeDialog publishes data."""
        async def do_send_post():
            try:
                wx.CallAfter(dialog_instance.send_btn.Disable)
                wx.CallAfter(wx.BeginBusyCursor)

                post_uri = await session.send_message(
                    message=text,
                    files=files,
                    reply_to=reply_to,
                    cw_text=cw_text,
                    is_sensitive=is_sensitive,
                    **kwargs
                )
                if post_uri:
                    output.speak(_("Post sent successfully!"), True)
                    wx.CallAfter(dialog_instance.EndModal, wx.ID_OK)
                    # Optionally, add to relevant buffer or update UI
                    # This might involve fetching the new post and adding to message_cache and posts_buffer
                    # new_post_data = await session.util.get_post_by_uri(post_uri) # Assuming such a util method
                    # if new_post_data:
                    #    await self.check_buffers(new_post_data) # check_buffers needs to handle PostView or dict
                else:
                    # This case should ideally be handled by send_message raising an error
                    output.speak(_("Failed to send post. The server did not confirm the post creation."), True)
                    wx.CallAfter(dialog_instance.send_btn.Enable, True)

            except NotificationError as e:
                logger.error(f"NotificationError sending post via dialog: {e}", exc_info=True)
                output.speak(_("Error sending post: {error}").format(error=str(e)), True)
                wx.CallAfter(wx.MessageBox, str(e), _("Post Error"), wx.OK | wx.ICON_ERROR, dialog_instance)
                if not dialog_instance.IsBeingDeleted(): wx.CallAfter(dialog_instance.send_btn.Enable, True)
            except Exception as e:
                logger.error(f"Unexpected error sending post via dialog: {e}", exc_info=True)
                output.speak(_("An unexpected error occurred: {error}").format(error=str(e)), True)
                wx.CallAfter(wx.MessageBox, str(e), _("Error"), wx.OK | wx.ICON_ERROR, dialog_instance)
                if not dialog_instance.IsBeingDeleted(): wx.CallAfter(dialog_instance.send_btn.Enable, True)
            finally:
                if not dialog_instance.IsBeingDeleted(): wx.CallAfter(wx.EndBusyCursor)

        asyncio.create_task(do_send_post())


    def post_reply(self, *args, **kwargs):
        buffer = self.get_current_buffer()
        if hasattr(buffer, "reply"):
            return buffer.reply()


    def send_dm(self, *args, **kwargs):
        buffer = self.get_current_buffer()
        if hasattr(buffer, "send_message"):
            buffer.send_message()

    def post_retweet(self, *args, **kwargs):
        buffer = self.get_current_buffer()
        if hasattr(buffer, "share_item"):
            return buffer.share_item()
        session = getattr(buffer, "session", None)
        if not session:
            return
        if getattr(session, "type", "") == "blueski":
            item_uri = None
            if hasattr(buffer, "get_selected_item_id"):
                item_uri = buffer.get_selected_item_id()
            if not item_uri:
                output.speak(_("No item selected."), True)
                return

            if self.showing == False:
                dlg = wx.TextEntryDialog(None, _("Write your quote (optional):"), _("Quote"))
                if dlg.ShowModal() == wx.ID_OK:
                    text = dlg.GetValue().strip()
                    dlg.Destroy()
                    try:
                        if text:
                            uri = session.send_message(text, quote_uri=item_uri)
                            if uri:
                                output.speak(_("Quote posted."), True)
                            else:
                                output.speak(_("Failed to send quote."), True)
                        else:
                            # Confirm repost (share) depending on preference (boost_mode)
                            ask = True
                            try:
                                ask = session.settings["general"].get("boost_mode", "ask") == "ask"
                            except Exception:
                                ask = True
                            if ask:
                                confirm = wx.MessageDialog(None, _("Would you like to share this post?"), _("Boost"), wx.YES_NO|wx.ICON_QUESTION)
                                if confirm.ShowModal() != wx.ID_YES:
                                    confirm.Destroy()
                                    return
                                confirm.Destroy()
                            r_uri = session.repost(item_uri)
                            if r_uri:
                                output.speak(_("Post shared."), True)
                            else:
                                output.speak(_("Failed to share post."), True)
                    except Exception:
                        log.exception("Error sharing/quoting Bluesky post (invisible)")
                        output.speak(_("An error occurred while sharing the post."), True)
                else:
                    dlg.Destroy()
                return

            from wxUI.dialogs.blueski.postDialogs import Post as ATPostDialog
            dlg = ATPostDialog(caption=_("Quote post"))
            if dlg.ShowModal() == wx.ID_OK:
                text, files, cw_text, langs = dlg.get_payload()
                dlg.Destroy()
                try:
                    if text or files or cw_text:
                        uri = session.send_message(text, files=files, cw_text=cw_text, is_sensitive=bool(cw_text), languages=langs, quote_uri=item_uri)
                        if uri:
                            output.speak(_("Quote posted."), True)
                            try:
                                if hasattr(buffer, "start_stream"):
                                    buffer.start_stream(mandatory=False, play_sound=False)
                            except Exception:
                                pass
                        else:
                            output.speak(_("Failed to send quote."), True)
                    else:
                        # Confirm repost without comment depending on preference
                        ask = True
                        try:
                            ask = session.settings["general"].get("boost_mode", "ask") == "ask"
                        except Exception:
                            ask = True
                        if ask:
                            confirm = wx.MessageDialog(self.view, _("Would you like to share this post?"), _("Boost"), wx.YES_NO|wx.ICON_QUESTION)
                            if confirm.ShowModal() != wx.ID_YES:
                                confirm.Destroy()
                                return
                            confirm.Destroy()
                        r_uri = session.repost(item_uri)
                        if r_uri:
                            output.speak(_("Post shared."), True)
                        else:
                            output.speak(_("Failed to share post."), True)
                except Exception:
                    log.exception("Error sharing/quoting Bluesky post (dialog)")
                    output.speak(_("An error occurred while sharing the post."), True)
            else:
                dlg.Destroy()
            return

    def add_to_favourites(self, *args, **kwargs):
        buffer = self.get_current_buffer()
        if hasattr(buffer, "add_to_favorites"): # Generic buffer method
            return buffer.add_to_favorites()
        elif hasattr(buffer, "toggle_favorite"):
            return buffer.toggle_favorite()
        elif buffer.session and buffer.session.KIND == "blueski":
             # Fallback if buffer doesn't have the method but session is blueski (e.g. ChatBuffer)
             # Chat messages can't be liked yet in this implementation, or handled by specific buffer
             output.speak(_("This item cannot be liked."), True)
             return


    def remove_from_favourites(self, *args, **kwargs):
        buffer = self.get_current_buffer()
        if hasattr(buffer, "remove_from_favorites"): # Generic buffer method
            return buffer.remove_from_favorites()
        elif buffer.session and buffer.session.KIND == "blueski":
            item_uri = buffer.get_selected_item_id()
            if not item_uri:
                output.speak(_("No item selected to unlike."), True)
                return

            like_uri = None
            # Check viewer state from message_cache first, then panel's internal viewer_states
            if buffer.session and hasattr(buffer.session, "message_cache") and item_uri in buffer.session.message_cache:
                cached_post = buffer.session.message_cache[item_uri]
                if isinstance(cached_post, dict) and isinstance(cached_post.get("viewer"), dict):
                    like_uri = cached_post["viewer"].get("like")
                elif hasattr(cached_post, "viewer") and cached_post.viewer: # SDK model
                    like_uri = cached_post.viewer.like

            if not like_uri and hasattr(buffer, "get_item_viewer_state"): # Fallback to panel's state if any
                like_uri = buffer.get_item_viewer_state(item_uri, "like_uri")

            if not like_uri:
                output.speak(_("Could not find the original like record for this post, or it's already unliked."), True)
                logger.warning(f"Attempted to unlike post {item_uri} but its like_uri was not found.")
                return

            social_handler = self.get_handler(buffer.session.KIND)
            async def _unlike():
                result = await social_handler.unlike_item(buffer.session, like_uri)
                wx.CallAfter(output.speak, result["message"], True)
                if result.get("status") == "success":
                    if hasattr(buffer, "store_item_viewer_state"):
                        wx.CallAfter(buffer.store_item_viewer_state, item_uri, "like_uri", None)
                    # Also update the item in message_cache
                    if buffer.session and hasattr(buffer.session, "message_cache") and item_uri in buffer.session.message_cache:
                        cached_post = buffer.session.message_cache[item_uri]
                        if isinstance(cached_post, dict) and isinstance(cached_post.get("viewer"), dict):
                             cached_post["viewer"]["like"] = None
                        elif hasattr(cached_post, "viewer") and cached_post.viewer:
                             cached_post.viewer.like = None
            asyncio.create_task(_unlike())


    def toggle_like(self, *args, **kwargs):
        buffer = self.get_current_buffer()
        if hasattr(buffer, "toggle_favorite"):
            return buffer.toggle_favorite()

    def vote(self, *args, **kwargs):
        buffer = self.get_current_buffer()
        if hasattr(buffer, "vote"):
            return buffer.vote()

    def view_item(self, *args, **kwargs):
        buffer = self.get_current_buffer()
        if hasattr(buffer, "view_item"):
            return buffer.view_item()

    def open_in_browser(self, *args, **kwargs):
        buffer = self.get_current_buffer()
        if hasattr(buffer, "open_in_browser"):
            buffer.open_in_browser()

    def open_favs_timeline(self, *args, **kwargs):
        buffer = self.get_best_buffer()
        handler = self.get_handler(type=buffer.session.type)
        if handler != None and hasattr(handler, "open_timeline"):
            return handler.open_timeline(controller=self, buffer=buffer, default="favorites")


    def open_timeline(self, *args, **kwargs):
        buffer = self.get_best_buffer()
        handler = self.get_handler(type=buffer.session.type)
        if handler != None and hasattr(handler, "open_timeline"):
            return handler.open_timeline(controller=self, buffer=buffer)

    def open_conversation(self, *args, **kwargs):
        buffer = self.get_best_buffer()
        handler = self.get_handler(type=buffer.session.type)
        if handler != None and hasattr(handler, "open_conversation"):
            return handler.open_conversation(controller=self, buffer=buffer)

    def show_hide(self, *args, **kwargs):
        km = self.create_invisible_keyboard_shorcuts()
        if self.showing == True:
            if config.app["app-settings"]["use_invisible_keyboard_shorcuts"] == False:
                self.register_invisible_keyboard_shorcuts(km)
            self.view.Hide()
            self.fix_wrong_buffer()
            self.showing = False
        else:
            if config.app["app-settings"]["use_invisible_keyboard_shorcuts"] == False:
                self.unregister_invisible_keyboard_shorcuts(km)
            self.view.Show()
            self.showing = True

    def get_more_items(self, *args, **kwargs):
        buffer = self.get_current_buffer()
        if hasattr(buffer, "get_more_items"):
            return buffer.get_more_items()

    def clear_buffer(self, *args, **kwargs):
        buffer = self.get_current_buffer()
        if hasattr(buffer, "clear_list"):
            return buffer.clear_list()

    def remove_buffer(self, *args, **kwargs):
        buffer = self.get_current_buffer()
        if not hasattr(buffer, "account"):
            return
        buff = self.view.search(buffer.name, buffer.account)
        answer = buffer.remove_buffer()
        if answer == False:
            return
        log.debug("destroying buffer...")
        self.right()
        self.view.delete_buffer(buff)
        buffer.session.sound.play("delete_timeline.ogg")
        self.buffers.remove(buffer)
        del buffer

    def skip_buffer(self, forward=True):
        buff = self.get_current_buffer()
        if buff.invisible == False:
            self.view.advance_selection(forward)

    def buffer_changed(self, *args, **kwargs):
        buffer = self.get_current_buffer()
        if buffer is None:
            return
        old_account = self.current_account
        new_account = buffer.account
        if new_account != old_account:
            self.current_account = buffer.account
            new_first_buffer = self.get_first_buffer(new_account)
            if new_first_buffer != None and new_first_buffer.session.type != self.menubar_current_handler:
                handler = self.get_handler(new_first_buffer.session.type)
                self.menubar_current_handler = new_first_buffer.session.type
                self.update_menus(handler)
        if not hasattr(buffer, "session") or buffer.session == None:
            return
        muted = autoread = False
        if buffer.name in buffer.session.settings["other_buffers"]["muted_buffers"]:
            muted = True
        elif buffer.name in buffer.session.settings["other_buffers"]["autoread_buffers"]:
            autoread = True
        self.view.check_menuitem("mute_buffer", muted)
        self.view.check_menuitem("autoread", autoread)

    def update_menus(self, handler):
        if hasattr(handler, "menus"):
            for m in list(handler.menus.keys()):
                if hasattr(self.view, m):
                    menu_item = getattr(self.view, m)
                    if handler.menus[m] == "HIDE":
                        menu_item.Enable(False)
                        menu_item.SetItemLabel("")
                    elif handler.menus[m] == None:
                        menu_item.Enable(False)
                    else:
                        menu_item.Enable(True)
                        menu_item.SetItemLabel(handler.menus[m])
        if hasattr(handler, "item_menu"):
            self.view.menubar.SetMenuLabel(1, handler.item_menu)

    def fix_wrong_buffer(self):
        buf = self.get_best_buffer()
        if buf == None:
            for i in self.accounts:
                buffer = self.view.search("home_timeline", i)
                if buffer != None:
                    break
        else:
            buffer = self.view.search("home_timeline", buf.session.get_name())
        if buffer!=None:
            self.view.change_buffer(buffer)

    def up(self, *args, **kwargs):
        page = self.get_current_buffer()
        if not hasattr(page.buffer, "list"):
            output.speak(_(u"No session is currently in focus. Focus a session with the next or previous session shortcut."), True)
            return
        position = page.buffer.list.get_selected()
        index = position-1
        try:
            page.buffer.list.select_item(index)
        except:
            pass
        if position == page.buffer.list.get_selected():
            page.session.sound.play("limit.ogg")

#        try:
        output.speak(page.get_message(), True)
#        except:
#            pass

    def down(self, *args, **kwargs):
        page = self.get_current_buffer()
        if not hasattr(page.buffer, "list"):
            output.speak(_(u"No session is currently in focus. Focus a session with the next or previous session shortcut."), True)
            return
        position = page.buffer.list.get_selected()
        index = position+1
#        try:
        page.buffer.list.select_item(index)
#        except:
#            pass
        if position == page.buffer.list.get_selected():
            page.session.sound.play("limit.ogg")
#        try:
        output.speak(page.get_message(), True)
#        except:
#            pass

    def left(self, *args, **kwargs):
        buff = self.view.get_current_buffer_pos()
        buffer = self.get_current_buffer()
        if not hasattr(buffer.buffer, "list"):
            output.speak(_(u"No session is currently in focus. Focus a session with the next or previous session shortcut."), True)
            return
        if buff == self.get_first_buffer_index(buffer.account) or buff == 0:
            self.view.change_buffer(self.get_last_buffer_index(buffer.account))
        else:
            self.view.change_buffer(buff-1)
        while self.get_current_buffer().invisible == False: self.skip_buffer(False)
        buffer = self.get_current_buffer()
        if self.showing == True: buffer.buffer.set_focus_in_list()
        try:
            msg = _(u"%s, %s of %s") % (self.view.get_buffer_text(), buffer.buffer.list.get_selected()+1, buffer.buffer.list.get_count())
        except:
            msg = _(u"%s. Empty") % (self.view.get_buffer_text(),)
        output.speak(msg, True)

    def right(self, *args, **kwargs):
        buff = self.view.get_current_buffer_pos()
        buffer = self.get_current_buffer()
        if not hasattr(buffer.buffer, "list"):
            output.speak(_(u"No session is currently in focus. Focus a session with the next or previous session shortcut."), True)
            return
        if buff == self.get_last_buffer_index(buffer.account) or buff+1 == self.view.get_buffer_count():
            self.view.change_buffer(self.get_first_buffer_index(buffer.account))
        else:
            self.view.change_buffer(buff+1)
        while self.get_current_buffer().invisible == False: self.skip_buffer(True)
        buffer = self.get_current_buffer()
        if self.showing == True: buffer.buffer.set_focus_in_list()
        try:
            msg = _(u"%s, %s of %s") % (self.view.get_buffer_text(), buffer.buffer.list.get_selected()+1, buffer.buffer.list.get_count())
        except:
            msg = _(u"%s. Empty") % (self.view.get_buffer_text(),)
        output.speak(msg, True)

    def next_account(self, *args, **kwargs):
        if not self.accounts:
            output.speak(_("No accounts available."), True)
            return
        try:
            index = self.accounts.index(self.current_account)
        except ValueError:
            index = -1
        if index+1 == len(self.accounts):
            index = 0
        else:
            index = index+1
        account = self.accounts[index]
        self.current_account = account
        buffer_object = self.get_first_buffer(account)
        if buffer_object == None:
            output.speak(_(u"{0}: This account is not logged in.").format(account), True)
            return
        buff = self.view.search(buffer_object.name, account)
        if buff == None:
            output.speak(_(u"{0}: This account is not logged in.").format(account), True)
            return
        self.view.change_buffer(buff)
        buffer = self.get_current_buffer()
        if self.showing == True: buffer.buffer.set_focus_in_list()
        try:
            msg = _(u"%s. %s, %s of %s") % (buffer.account, self.view.get_buffer_text(), buffer.buffer.list.get_selected()+1, buffer.buffer.list.get_count())
        except:
            msg = _(u"%s. Empty") % (self.view.get_buffer_text(),)
        output.speak(msg, True)

    def previous_account(self, *args, **kwargs):
        if not self.accounts:
            output.speak(_("No accounts available."), True)
            return
        try:
            index = self.accounts.index(self.current_account)
        except ValueError:
            index = 0
        if index-1 < 0:
            index = len(self.accounts)-1
        else:
            index = index-1
        account = self.accounts[index]
        self.current_account = account
        buffer_object = self.get_first_buffer(account)
        if buffer_object == None:
            output.speak(_(u"{0}: This account is not logged in.").format(account), True)
            return
        buff = self.view.search(buffer_object.name, account)
        if buff == None:
            output.speak(_(u"{0}: This account is not logged in.").format(account), True)
            return
        self.view.change_buffer(buff)
        buffer = self.get_current_buffer()
        if self.showing == True: buffer.buffer.set_focus_in_list()
        try:
            msg = _(u"%s. %s, %s of %s") % (buffer.account, self.view.get_buffer_text(), buffer.buffer.list.get_selected()+1, buffer.buffer.list.get_count())
        except:
            msg = _(u"%s. Empty") % (self.view.get_buffer_text(),)
        output.speak(msg, True)

    def go_home(self):
        buffer = self.get_current_buffer()
        buffer.buffer.list.select_item(0)
#        try:
        output.speak(buffer.get_message(), True)
#        except:
#            pass

    def go_end(self):
        buffer = self.get_current_buffer()
        buffer.buffer.list.select_item(buffer.buffer.list.get_count()-1)
#        try:
        output.speak(buffer.get_message(), True)
#        except:
#            pass

    def go_page_up(self):
        buffer = self.get_current_buffer()
        if buffer.buffer.list.get_selected() <= 20:
            index = 0
        else:
            index = buffer.buffer.list.get_selected() - 20
        buffer.buffer.list.select_item(index)
#        try:
        output.speak(buffer.get_message(), True)
#        except:
#            pass

    def go_page_down(self):
        buffer = self.get_current_buffer()
        if buffer.buffer.list.get_selected() >= buffer.buffer.list.get_count() - 20:
            index = buffer.buffer.list.get_count()-1
        else:
            index = buffer.buffer.list.get_selected() + 20
        buffer.buffer.list.select_item(index)
#        try:
        output.speak(buffer.get_message(), True)
#        except:
#            pass

    def url(self, *args, **kwargs):
        buffer = self.get_current_buffer()
        if hasattr(buffer, "url"):
            buffer.url()

    def audio(self, *args, **kwargs):
        buffer = self.get_current_buffer()
        if hasattr(buffer, "audio"):
            return buffer.audio()

    def volume_down(self, *args, **kwargs):
        buffer = self.get_current_buffer()
        if hasattr(buffer, "volume_down"):
            return buffer.volume_down()

    def volume_up(self, *args, **kwargs):
        buffer = self.get_current_buffer()
        if hasattr(buffer, "volume_up"):
            return buffer.volume_up()

    def create_invisible_keyboard_shorcuts(self):
        keymap = {}
        for i in config.keymap["keymap"]:
            if hasattr(self, i):
                if config.keymap["keymap"][i] != "":
                    keymap[config.keymap["keymap"][i]] = getattr(self, i)
        return keymap

    def register_invisible_keyboard_shorcuts(self, keymap):
        if config.changed_keymap:
            build_number = sys.getwindowsversion().build
            if build_number > 22000:
                system = "Windows 11"
                keystroke_editor_shortcut = "Control+Win+Alt+K"
            else:
                system = "Windows 10"
                keystroke_editor_shortcut = "Win+Alt+K"
            commonMessageDialogs.changed_keymap(system, keystroke_editor_shortcut)
        # Make sure we pass a keymap without undefined keystrokes.
        new_keymap = {key: keymap[key] for key in keymap.keys() if keymap[key] != ""}
        self.keyboard_handler = WXKeyboardHandler(self.view)
        self.keyboard_handler.register_keys(new_keymap)

    def unregister_invisible_keyboard_shorcuts(self, keymap):
        try:
            self.keyboard_handler.unregister_keys(keymap)
            del self.keyboard_handler
        except AttributeError:
            pass

    def notify(self, session, play_sound=None, message=None, notification=False):
        if session.settings["sound"]["session_mute"] == True:
            return
        if play_sound != None:
            session.sound.play(play_sound)
        if message != None:
            output.speak(message, speech=session.settings["reporting"]["speech_reporting"], braille=session.settings["reporting"]["braille_reporting"])

    def start_buffers(self, session):
        log.debug("starting buffers... Session %s" % (session.session_id,))
        handler = self.get_handler(type=session.type)
        for i in self.buffers:
            if i.session == session and i.needs_init == True:
                handler.start_buffer(controller=self, buffer=i)

    def set_positions(self):
        for i in sessions.sessions:
            self.set_buffer_positions(i)

    def invisible_shorcuts_changed(self, registered):
        if registered == True:
            km = self.create_invisible_keyboard_shorcuts()
            self.register_invisible_keyboard_shorcuts(km)
        elif registered == False:
            km = self.create_invisible_keyboard_shorcuts()
            self.unregister_invisible_keyboard_shorcuts(km)

    def about(self, *args, **kwargs):
        self.view.about_dialog()

    def get_soundpacks(self, *args, **kwargs):
        # This should redirect users of other languages to the right version of the TWBlue website.
        lang = languageHandler.curLang[:2]
        url = application.url
        final_url = "{0}/{1}/soundpacks".format(url, lang)
        try:
            response = requests.get(final_url)
        except:
            output.speak(_(u"An error happened while trying to connect to the server. Please try later."))
            return
        # There is no twblue.mcvsoftware.com/en, so if English is the language used this should be False anyway.
        if response.status_code == 200 and lang != "en":
            webbrowser.open_new_tab(final_url)
        else:
            webbrowser.open_new_tab(application.url+"/soundpacks")

    def visit_website(self, *args, **kwargs):
        # This should redirect users of other languages to the right version of the TWBlue website.
        lang = languageHandler.curLang[:2]
        url = application.url
        final_url = "{0}/{1}".format(url, lang)
        try:
            response = requests.get(final_url)
        except:
            output.speak(_(u"An error happened while trying to connect to the server. Please try later."))
            return
        # There is no twblue.mcvsoftware.com/en, so if English is the language used this should be False anyway.
        if response.status_code == 200 and lang != "en":
            webbrowser.open_new_tab(final_url)
        else:
            webbrowser.open_new_tab(application.url)

    def manage_accounts(self, *args, **kwargs):
        sm = sessionManager.sessionManagerController(started=True)
        sm.fill_list()
        sm.show()
        for i in sm.new_sessions:
            handler = self.get_handler(type=sessions.sessions[i].type)
            if handler != None and hasattr(handler, "create_buffers"):
                handler.create_buffers(controller=self, session=sessions.sessions[i])
            call_threaded(self.start_buffers, sessions.sessions[i])
        for i in sm.removed_sessions:
            if sessions.sessions[i].logged == True:
                self.logout_account(sessions.sessions[i].session_id)
            self.destroy_buffer(sessions.sessions[i].get_name(), sessions.sessions[i].get_name())
            if sessions.sessions[i].get_name() in self.accounts:
                self.accounts.remove(sessions.sessions[i].get_name())
            sessions.sessions.pop(i)

    def toggle_autoread(self, *args, **kwargs):
        buffer = self.get_current_buffer()
        if hasattr(buffer, "session") and buffer.session == None:
            return
        if buffer.name not in buffer.session.settings["other_buffers"]["autoread_buffers"]:
            buffer.session.settings["other_buffers"]["autoread_buffers"].append(buffer.name)
            output.speak(_(u"The auto-reading of new tweets is enabled for this buffer"), True)
        elif buffer.name in buffer.session.settings["other_buffers"]["autoread_buffers"]:
            buffer.session.settings["other_buffers"]["autoread_buffers"].remove(buffer.name)
            output.speak(_(u"The auto-reading of new tweets is disabled for this buffer"), True)
        buffer.session.settings.write()

    def toggle_session_mute(self, *args, **kwargs):
        buffer = self.get_best_buffer()
        if buffer.session.settings["sound"]["session_mute"] == False:
            buffer.session.settings["sound"]["session_mute"] = True
            output.speak(_(u"Session mute on"), True)
        elif buffer.session.settings["sound"]["session_mute"] == True:
            buffer.session.settings["sound"]["session_mute"] = False
            output.speak(_(u"Session mute off"), True)
        buffer.session.settings.write()

    def toggle_buffer_mute(self, *args, **kwargs):
        buffer = self.get_current_buffer()
        if hasattr(buffer, "session") and buffer.session == None:
            return
        if buffer.name not in buffer.session.settings["other_buffers"]["muted_buffers"]:
            buffer.session.settings["other_buffers"]["muted_buffers"].append(buffer.name)
            output.speak(_(u"Buffer mute on"), True)
        elif buffer.name in buffer.session.settings["other_buffers"]["muted_buffers"]:
            buffer.session.settings["other_buffers"]["muted_buffers"].remove(buffer.name)
            output.speak(_(u"Buffer mute off"), True)
        buffer.session.settings.write()

    def view_documentation(self, *args, **kwargs):
        lang = localization.get("documentation")
        os.chdir("documentation/%s" % (lang,))
        webbrowser.open("manual.html")
        os.chdir("../../")

    def view_changelog(self, *args, **kwargs):
        lang = localization.get("documentation")
        os.chdir("documentation/%s" % (lang,))
        webbrowser.open("changelog.html")
        os.chdir("../../")

    def copy_to_clipboard(self, *args, **kwargs):
        output.copy(self.get_current_buffer().get_message())
        output.speak(_(u"Copied"))

    def repeat_item(self, *args, **kwargs):
        output.speak(self.get_current_buffer().get_message())

    def execute_action(self, action, kwargs={}):
        if hasattr(self, action):
            getattr(self, action)(**kwargs)

    def update_buffers(self):
        for i in self.buffers[:]:
            if i.session != None and i.session.is_logged == True:
                try:
                    i.start_stream(mandatory=True)
                except Exception as err:
                    log.exception("Error %s starting buffer %s on account %s, with args %r and kwargs %r." % (str(err), i.name, i.account, i.args, i.kwargs))

    def update_buffer(self, *args, **kwargs):
        """Handles the 'Update buffer' menu command to fetch newest items."""
        bf = self.get_current_buffer() # bf is the buffer panel instance
        if not bf or not hasattr(bf, "session") or not bf.session:
            output.speak(_(u"No active session for this buffer."), True)
            return

        output.speak(_(u"Updating buffer..."), True)
        session = bf.session

        output.speak(_(u"Updating buffer..."), True)
        session = bf.session

        import threading
        is_blueski = (getattr(session, "KIND", None) == "blueski" or getattr(session, "type", None) == "blueski")

        def do_update_sync():
            new_ids = []
            try:
                if is_blueski:
                    if hasattr(bf, "start_stream"):
                        count = bf.start_stream(mandatory=True)
                        if count: new_ids = [str(x) for x in range(count)]
                    else:
                        wx.CallAfter(output.speak, _(u"This buffer type cannot be updated."), True)
                        return
                else: # Generic fallback for other sessions
                     # If they are async, this might be tricky in a thread without a loop
                     # But most old sessions in TWBlue are sync (using threads)
                    if hasattr(bf, "start_stream"):
                        count = bf.start_stream(mandatory=True, avoid_autoreading=True)
                        if count: new_ids = [str(x) for x in range(count)]
                    else:
                        wx.CallAfter(output.speak, _(u"Unable to update this buffer."), True)
                        return

                # Generic feedback
                if bf.type in ["home_timeline", "user_timeline", "notifications", "mentions"]:
                    wx.CallAfter(output.speak, _("{0} new items.").format(len(new_ids)), True)
                
            except Exception as e:
                log.exception("Error updating buffer %s", bf.name)
                wx.CallAfter(output.speak, _("An error occurred while updating the buffer."), True)
        
        if is_blueski:
             threading.Thread(target=do_update_sync).start()
        else:
             # Original async logic for others if needed, but likely they are sync too. 
             # Assuming TWBlue architecture is mostly thread-based for legacy sessions.
             # If we have an async loop running, we could use it for async-capable sessions.
             # For safety, let's use the thread approach generally if we are not sure about the loop state.
             threading.Thread(target=do_update_sync).start()


    def get_more_items(self, *args, **kwargs):
        """Handles 'Load previous items' menu command."""
        bf = self.get_current_buffer() # bf is the buffer panel instance
        if not bf or not hasattr(bf, "session") or not bf.session:
            output.speak(_(u"No active session for this buffer."), True)
            return

        session = bf.session
        # The buffer panel (bf) needs to store its own cursor for pagination of older items
        # e.g., bf.pagination_cursor or bf.older_items_cursor
        # This cursor should be set by the result of previous fetch_..._timeline(new_only=False) calls.

        # For Blueski, session methods like fetch_home_timeline store their own cursor (e.g., session.home_timeline_cursor)
        # The panel (bf) itself should manage its own cursor for "load more"

        current_cursor = None
        can_load_more_natively = False

        if getattr(session, "KIND", None) == "blueski":
            if hasattr(bf, "load_more_posts"): # For BlueskiUserTimelinePanel & BlueskiHomeTimelinePanel
                can_load_more_natively = True
            if hasattr(bf, "load_more_posts"):
                can_load_more_natively = True
            elif hasattr(bf, "load_more_users"):
                can_load_more_natively = True
            elif bf.type == "notifications" and hasattr(bf, "load_more_notifications"): # Check for specific load_more
                 can_load_more_natively = True
            elif bf.type == "notifications" and hasattr(bf, "refresh_notifications"): # Fallback for notifications to refresh
                 # If load_more_notifications doesn't exist, 'Load More' will just refresh.
                 can_load_more_natively = True # It will call refresh_notifications via the final 'else'
            else:
                if hasattr(bf, "get_more_items"):
                    return bf.get_more_items()
                else:
                    output.speak(_(u"This buffer does not support loading more items in this way."), True)
                    return
        else: # For other non-Blueski session types
            if hasattr(bf, "get_more_items"):
                return bf.get_more_items()
            else:
                output.speak(_(u"This buffer does not support loading more items."), True)
                return

        output.speak(_(u"Loading more items..."), True)

        async def do_load_more():
            try:
                if session.KIND == "blueski":
                    if hasattr(bf, "load_more_posts"):
                        await bf.load_more_posts(limit=config.app["app-settings"].get("items_per_request", 20))
                    elif hasattr(bf, "load_more_users"):
                        await bf.load_more_users(limit=config.app["app-settings"].get("items_per_request", 30))
                    elif bf.type == "notifications" and hasattr(bf, "refresh_notifications"):
                        # This will re-fetch recent, not older. A true "load_more_notifications(cursor=...)" is needed for that.
                        wx.CallAfter(output.speak, _("Refreshing notifications..."), True)
                        await bf.refresh_notifications(limit=config.app["app-settings"].get("items_per_request", 20))
                    # Feedback is handled by panel methods for consistency

            except NotificationError as e:
                wx.CallAfter(output.speak, str(e), True)
            except Exception as e_general:
                logger.error(f"Error loading more items for buffer {bf.name}: {e_general}", exc_info=True)
                output.speak(_("An error occurred while loading more items."), True)

        wx.CallAfter(asyncio.create_task, do_load_more())


    def buffer_title_changed(self, buffer):
        if buffer.name.endswith("-timeline"):
            title = _(u"Timeline for {}").format(buffer.username,)
        elif buffer.name.endswith("-followers"):
            title = _(u"Followers for {}").format(buffer.username,)
        elif buffer.name.endswith("-friends"):
            title = _(u"Friends for {}").format(buffer.username,)
        elif buffer.name.endswith("-following"):
            title = _(u"Following for {}").format(buffer.username,)
        buffer_index = self.view.search(buffer.name, buffer.account)
        self.view.set_page_title(buffer_index, title)

    def ocr_image(self, *args, **kwargs):
        buffer = self.get_current_buffer()
        if hasattr(buffer, "ocr_image"):
            return buffer.ocr_image()

    def save_data_in_db(self):
        for i in sessions.sessions:
            sessions.sessions[i].save_persistent_data()

    def toggle_share_settings(self, shareable=True):
        self.view.share.Enable(shareable)

    def mastodon_new_item(self, item, session_name, _buffers):
        sound_to_play = None
        for buff in _buffers:
            buffer = self.search_buffer(buff, session_name)
            if buffer == None or buffer.session.get_name() != session_name:
                return
            buffer.add_new_item(item)
            if buff == "home_timeline": sound_to_play = "tweet_received.ogg"
            elif buff == "mentions": sound_to_play = "mention_received.ogg"
            elif buff == "direct_messages": sound_to_play = "dm_received.ogg"
            elif buff == "sent": sound_to_play = "tweet_send.ogg"
            elif buff == "followers" or buff == "following": sound_to_play = "update_followers.ogg"
            elif buff == "notifications": sound_to_play = "new_event.ogg"
            elif "timeline" in buff: sound_to_play = "tweet_timeline.ogg"
            else: sound_to_play = None
            if sound_to_play != None and buff not in buffer.session.settings["other_buffers"]["muted_buffers"]:
                self.notify(buffer.session, sound_to_play)

    def mastodon_updated_item(self, item, session_name, _buffers):
        sound_to_play = None
        for buff in _buffers.keys():
            buffer = self.search_buffer(buff, session_name)
            if buffer == None or buffer.session.get_name() != session_name:
                return
            buffer.update_item(item, _buffers[buff])

    # Normally, we'd define this function on mastodon's session, but we need to access conversationListBuffer and here is the best place to do so.
    def mastodon_new_conversation(self, conversation, session_name):
        buffer = self.search_buffer("direct_messages", session_name)
        if buffer == None:
            log.error("Buffer not found: direct_messages on {}".format(session_name))
            return # Direct messages buffer is hidden
        new_position, number_of_items = buffer.order_buffer([conversation])
        buffer.put_items_on_list(number_of_items)
        if new_position > -1:
            buffer.buffer.list.select_item(new_position)
#        if number_of_items > 0:
#            sound_to_play = "dm_received.ogg"
#            if "direct_messages" not in buffer.session.settings["other_buffers"]["muted_buffers"]:
#                self.notify(buffer.session, sound_to_play)

    def blueski_new_item(self, item, session_name, _buffers):
        """Handle new items from Bluesky polling."""
        sound_to_play = None
        for buff in _buffers:
            buffer = self.search_buffer(buff, session_name)
            if buffer is None or buffer.session.get_name() != session_name:
                continue
            if hasattr(buffer, "add_new_item"):
                buffer.add_new_item(item)
            # Determine sound to play
            if buff == "notifications":
                sound_to_play = "notification_received.ogg"
            elif buff == "home_timeline":
                sound_to_play = "tweet_received.ogg"
            elif "timeline" in buff:
                sound_to_play = "tweet_timeline.ogg"
            else:
                sound_to_play = None
            # Play sound if buffer is not muted
            if sound_to_play is not None:
                try:
                    muted = buffer.session.settings["other_buffers"].get("muted_buffers", [])
                    if buff not in muted:
                        self.notify(buffer.session, sound_to_play)
                except Exception:
                    pass

    def mastodon_error_post(self, name, reply_to, visibility, posts, language):
        home = self.search_buffer("home_timeline", name)
        if home != None:
            wx.CallAfter(home.post_from_error, visibility=visibility, reply_to=reply_to, data=posts, lang=language)

    def change_buffer_title(self, name, buffer, title):
        buffer_index = self.view.search(buffer, name)
        if buffer_index != None and buffer_index > -1:
            self.view.set_page_title(buffer_index, title)

    def report_error(self, *args, **kwargs):
        """Redirects the user to the issue page on github"""
        log.debug("Redirecting the user to report an error...")
        webbrowser.open_new_tab(application.report_bugs_url)

    def update_profile(self, *args):
        """Updates the users profile"""
        log.debug("Update profile")
        buffer = self.get_best_buffer()
        handler = self.get_handler(buffer.session.type)
        if handler:
            handler.update_profile(buffer.session)

    def user_details(self, *args):
        """Displays a user's profile."""
        log.debug("Showing user profile...")
        buffer = self.get_current_buffer() # Use current buffer to get context if item is selected
        if not buffer or not buffer.session:
            buffer = self.get_best_buffer() # Fallback if current buffer has no session

        if not buffer or not buffer.session:
            output.speak(_("No active session to view user details."), True)
            return

        handler = self.get_handler(type=buffer.session.type)
        if handler and hasattr(handler, 'user_details'):
            # The handler's user_details method is responsible for extracting context
            # (e.g., selected user) from the buffer and displaying the profile.
            # For Blueski, handler.user_details calls the ShowUserProfileDialog.
            result = handler.user_details(buffer)
            if asyncio.iscoroutine(result):
                call_threaded(asyncio.run, result)
        else:
            output.speak(_("This session type does not support viewing user details in this way."), True)


    def openPostTimeline(self, *args, user=None): # "user" here is often the user object from selected item
        """Opens selected user's posts timeline. Renamed to open_user_timeline in handlers for clarity."""
        current_buffer = self.get_current_buffer()
        if not current_buffer or not current_buffer.session:
            current_buffer = self.get_best_buffer()

        if not current_buffer or not current_buffer.session:
            output.speak(_("No active session available."), True)
            return

        session_to_use = current_buffer.session
        handler = self.get_handler(type=session_to_use.type)

        # Prefer the new standardized 'open_user_timeline'
        if hasattr(handler, 'open_user_timeline'):
            user_payload = user # Use passed 'user' if available
            if user_payload is None and hasattr(current_buffer, 'get_selected_item_author_details'):
                 author_details = current_buffer.get_selected_item_author_details()
                 if author_details:
                     user_payload = author_details

            result = handler.open_user_timeline(main_controller=self, session=session_to_use, user_payload=user_payload)
            if asyncio.iscoroutine(result):
                call_threaded(asyncio.run, result)

        elif hasattr(handler, 'openPostTimeline'): # Fallback for older handler structure
            # This path might not correctly pass main_controller if the old handler expects it differently
            handler.openPostTimeline(self, current_buffer, user)
        else:
            output.speak(_("This session type does not support opening user timelines directly."), True)


    def openFollowersTimeline(self, *args, user=None):
        """Opens selected user's followers timeline
        Parameters:
        args: Other argument. Useful when binding to widgets.
        user: if specified, open this user timeline. It is currently mandatory, but could be optional when user selection is implemented in handler
        """
        current_buffer = self.get_current_buffer()
        if not current_buffer or not current_buffer.session:
            current_buffer = self.get_best_buffer()

        if not current_buffer or not current_buffer.session:
            output.speak(_("No active session available."), True)
            return

        session_to_use = current_buffer.session
        handler = self.get_handler(type=session_to_use.type)

        if user is None and hasattr(current_buffer, 'get_selected_item_author_details'):
            author_details = current_buffer.get_selected_item_author_details()
            if author_details: user = author_details

        if handler and hasattr(handler, 'open_followers_timeline'):
            result = handler.open_followers_timeline(main_controller=self, session=session_to_use, user_payload=user)
            if asyncio.iscoroutine(result):
                call_threaded(asyncio.run, result)
        elif handler and hasattr(handler, 'openFollowersTimeline'): # Fallback
            handler.openFollowersTimeline(self, current_buffer, user)
        else:
            output.speak(_("This session type does not support opening followers list."), True)


    def openFollowingTimeline(self, *args, user=None):
        """Opens selected user's  following timeline
        Parameters:
        args: Other argument. Useful when binding to widgets.
        user: if specified, open this user timeline. It is currently mandatory, but could be optional when user selection is implemented in handler
        """
        current_buffer = self.get_current_buffer()
        if not current_buffer or not current_buffer.session:
            current_buffer = self.get_best_buffer()

        if not current_buffer or not current_buffer.session:
            output.speak(_("No active session available."), True)
            return

        session_to_use = current_buffer.session
        handler = self.get_handler(type=session_to_use.type)

        if user is None and hasattr(current_buffer, 'get_selected_item_author_details'):
            author_details = current_buffer.get_selected_item_author_details()
            if author_details: user = author_details

        if handler and hasattr(handler, 'open_following_timeline'):
            result = handler.open_following_timeline(main_controller=self, session=session_to_use, user_payload=user)
            if asyncio.iscoroutine(result):
                call_threaded(asyncio.run, result)
        elif handler and hasattr(handler, 'openFollowingTimeline'): # Fallback
            handler.openFollowingTimeline(self, current_buffer, user)
        else:
            output.speak(_("This session type does not support opening following list."), True)


    def community_timeline(self, *args, user=None): # user param seems unused here based on mastodon impl
        buffer = self.get_best_buffer()
        handler = self.get_handler(type=buffer.session.type)
        if handler and hasattr(handler, 'community_timeline'):
            handler.community_timeline(self, buffer)

    def create_filter(self, *args, **kwargs):
        buffer = self.get_best_buffer()
        handler = self.get_handler(type=buffer.session.type)
        if handler and hasattr(handler, 'create_filter'):
            handler.create_filter(self, buffer)

    def manage_filters(self, *args, **kwargs):
        buffer = self.get_best_buffer()
        handler = self.get_handler(type=buffer.session.type)
        if handler and hasattr(handler, 'manage_filters'):
            handler.manage_filters(self, buffer)
