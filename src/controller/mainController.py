# -*- coding: utf-8 -*-
import os
import logging
import webbrowser
import wx
import requests
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

        # Mastodon specific events.
        pub.subscribe(self.mastodon_new_item, "mastodon.new_item")
        pub.subscribe(self.mastodon_updated_item, "mastodon.updated_item")
        pub.subscribe(self.mastodon_new_conversation, "mastodon.conversation_received")
        pub.subscribe(self.mastodon_error_post, "mastodon.error_post")

        # connect application events to GUI
        widgetUtils.connect_event(self.view, widgetUtils.CLOSE_EVENT, self.exit_)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.show_hide, menuitem=self.view.show_hide)
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
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.open_conversation, menuitem=self.view.view_conversation)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.seekLeft, menuitem=self.view.seekLeft)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.seekRight, menuitem=self.view.seekRight)
        if widgetUtils.toolkit == "wx":
            widgetUtils.connect_event(self.view.nb, widgetUtils.NOTEBOOK_PAGE_CHANGED, self.buffer_changed)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.view_documentation, self.view.doc)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.view_changelog, self.view.changelog)
#        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.add_alias, self.view.addAlias)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.update_buffer, self.view.update_buffer)
#        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.manage_aliases, self.view.manageAliases)
        widgetUtils.connect_event(self.view, widgetUtils.MENU, self.report_error, self.view.reportError)

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
        if handler == None:
            if type == "mastodon":
                handler = MastodonHandler.Handler()
            self.handlers[type]=handler
        return handler

    def __init__(self):
        super(Controller, self).__init__()
        # Visibility state.
        self.showing = True
        # main window
        self.view = view.mainFrame()
        # buffers list.
        self.buffers = []
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
                self.create_ignored_session_buffer(sessions.sessions[i])
                continue
            # Valid types currently are mastodon (Work in progress)
            # More can be added later.
            valid_session_types = ["mastodon"]
            if sessions.sessions[i].type in valid_session_types:
                handler = self.get_handler(type=sessions.sessions[i].type)
                handler.create_buffers(sessions.sessions[i], controller=self)
        log.debug("Setting updates to buffers every %d seconds..." % (60*config.app["app-settings"]["update_period"],))
        self.update_buffers_function = RepeatingTimer(60*config.app["app-settings"]["update_period"], self.update_buffers)
        self.update_buffers_function.start()

    def start(self):
        """ Starts all buffer objects. Loads their items."""
        for i in sessions.sessions:
            if sessions.sessions[i].is_logged == False: continue
            self.start_buffers(sessions.sessions[i])
            self.set_buffer_positions(sessions.sessions[i])
            if hasattr(sessions.sessions[i], "start_streaming"):
                sessions.sessions[i].start_streaming()
        if config.app["app-settings"]["play_ready_sound"] == True:
            sessions.sessions[list(sessions.sessions.keys())[0]].sound.play("ready.ogg")
        if config.app["app-settings"]["speak_ready_msg"] == True:
            output.speak(_(u"Ready"))
        self.started = True
        if len(self.accounts) > 0:
            b = self.get_first_buffer(self.accounts[0])
            self.update_menus(handler=self.get_handler(b.session.type))

    def create_ignored_session_buffer(self, session):
        pub.sendMessage("core.create_account", name=session.get_name(), session_id=session.session_id)

    def login_account(self, session_id):
        for i in sessions.sessions:
            if sessions.sessions[i].session_id == session_id: session = sessions.sessions[i]
        session.login()
        handler = self.get_handler(type=session.type)
        if handler != None and hasattr(handler, "create_buffers"):
            handler.create_buffers(session=session, controller=self, createAccounts=False)
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
        log.debug("Creating buffer of type {0} with parent_tab of {2} arguments {1}".format(buffer_type, kwargs, parent_tab))
        if kwargs.get("parent") == None:
            kwargs["parent"] = self.view.nb
        if not hasattr(buffers, session_type):
            raise AttributeError("Session type %s does not exist yet." % (session_type))
        available_buffers = getattr(buffers, session_type)
        if not hasattr(available_buffers, buffer_type):
            raise AttributeError("Specified buffer type does not exist: %s" % (buffer_type,))
        buffer = getattr(available_buffers, buffer_type)(**kwargs)
        if start:
            if kwargs.get("function") == "user_timeline":
                try:
                    buffer.start_stream(play_sound=False)
                except ValueError:
                    commonMessageDialogs.unauthorized()
                    return
            else:
                call_threaded(buffer.start_stream)
        self.buffers.append(buffer)
        if parent_tab == None:
            log.debug("Appending buffer {}...".format(buffer,))
            self.view.add_buffer(buffer.buffer, buffer_title)
        else:
            self.view.insert_buffer(buffer.buffer, buffer_title, parent_tab)
            log.debug("Inserting buffer {0} into control {1}".format(buffer, parent_tab))

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

    def add_to_favourites(self, *args, **kwargs):
        buffer = self.get_current_buffer()
        if hasattr(buffer, "add_to_favorites"):
            return buffer.add_to_favorites()

    def remove_from_favourites(self, *args, **kwargs):
        buffer = self.get_current_buffer()
        if hasattr(buffer, "remove_from_favorites"):
            return buffer.remove_from_favorites()

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
                    if handler.menus[m] == None:
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
            output.speak(_(u"{0}: This account is not logged into Twitter.").format(account), True)
            return
        buff = self.view.search(buffer_object.name, account)
        if buff == None:
            output.speak(_(u"{0}: This account is not logged into Twitter.").format(account), True)
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
            output.speak(_(u"{0}: This account is not logged into Twitter.").format(account), True)
            return
        buff = self.view.search(buffer_object.name, account)
        if buff == None:
            output.speak(_(u"{0}: This account is not logged into twitter.").format(account), True)
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
            commonMessageDialogs.changed_keymap()
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
        # There is no twblue.es/en, so if English is the language used this should be False anyway.
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
        # There is no twblue.es/en, so if English is the language used this should be False anyway.
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

    def execute_action(self, action):
        if hasattr(self, action):
            getattr(self, action)()

    def update_buffers(self):
        for i in self.buffers[:]:
            if i.session != None and i.session.is_logged == True:
                try:
                    i.start_stream(mandatory=True)
                except Exception as err:
                    log.exception("Error %s starting buffer %s on account %s, with args %r and kwargs %r." % (str(err), i.name, i.account, i.args, i.kwargs))

    def update_buffer(self, *args, **kwargs):
        bf = self.get_current_buffer()
        if not hasattr(bf, "start_stream"):
            output.speak(_(u"Unable to update this buffer."))
            return
        output.speak(_(u"Updating buffer..."))
        n = bf.start_stream(mandatory=True, avoid_autoreading=True)
        if n != None:
            output.speak(_(u"{0} items retrieved").format(n,))

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

    def mastodon_error_post(self, name, reply_to, visibility, posts):
        home = self.search_buffer("home_timeline", name)
        if home != None:
            wx.CallAfter(home.post_from_error, visibility=visibility, reply_to=reply_to, data=posts)

    def report_error(self, *args, **kwargs):
        """Redirects the user to the issue page on github"""
        log.debug("Redirecting the user to report an error...")
        webbrowser.open_new_tab(application.report_bugs_url)
