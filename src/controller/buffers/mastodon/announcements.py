# -*- coding: utf-8 -*-
import time
import logging
import arrow
import widgetUtils
import wx
import output
import languageHandler
import config
from pubsub import pub
from controller.buffers.mastodon.base import BaseBuffer
from sessions.mastodon import compose, templates
from wxUI import buffers
from wxUI.dialogs.mastodon import menus
from mysc.thread_utils import call_threaded

log = logging.getLogger("controller.buffers.mastodon.announcements")

class AnnouncementsBuffer(BaseBuffer):

    def __init__(self, *args, **kwargs):
        # We enforce compose_func="compose_announcement"
        kwargs["compose_func"] = "compose_announcement"
        super(AnnouncementsBuffer, self).__init__(*args, **kwargs)
        self.type = "announcementsBuffer"

    def create_buffer(self, parent, name):
        self.buffer = buffers.mastodon.announcementsPanel(parent, name)

    def get_buffer_name(self):
        return _("Announcements")

    def bind_events(self):
        self.buffer.set_focus_function(self.onFocus)
        widgetUtils.connect_event(self.buffer.list.list, widgetUtils.KEYPRESS, self.get_event)
        widgetUtils.connect_event(self.buffer, widgetUtils.BUTTON_PRESSED, self.dismiss_announcement, self.buffer.dismiss)
        widgetUtils.connect_event(self.buffer.list.list, wx.EVT_LIST_ITEM_RIGHT_CLICK, self.show_menu)
        widgetUtils.connect_event(self.buffer.list.list, wx.EVT_LIST_KEY_DOWN, self.show_menu_by_key)

    def dismiss_announcement(self, event=None, item=None, *args, **kwargs):
        index = self.buffer.list.get_selected()
        if index == -1: return
        item = self.session.db[self.name][index]
        
        # Optimistic UI update or wait for API? Let's wait for API to be safe, but run threaded.
        # We need a custom call because 'announcements_dismiss' returns None on success usually.
        def _do_dismiss():
            try:
                self.session.api_call(call_name="announcements_dismiss", id=str(item.id))
                # If success, update UI in main thread
                wx.CallAfter(self._on_dismiss_success, index)
            except Exception as e:
                log.exception("Error dismissing announcement")
                self.session.sound.play("error.ogg")

        call_threaded(_do_dismiss)

    def _on_dismiss_success(self, index):
        if index < len(self.session.db[self.name]):
            self.session.db[self.name].pop(index)
            self.buffer.list.remove_item(index)
            output.speak(_("Announcement dismissed."))

        def show_menu(self, ev, pos=0, *args, **kwargs):
            if self.buffer.list.get_count() == 0:
                return
            # Create a simple menu
            menu = wx.Menu()
            dismiss_item = menu.Append(wx.ID_ANY, _("Dismiss"))
            copy_item = menu.Append(wx.ID_ANY, _("Copy text"))
            
            self.buffer.Bind(wx.EVT_MENU, self.dismiss_announcement, dismiss_item)
            self.buffer.Bind(wx.EVT_MENU, self.copy, copy_item)
            
            if pos != 0:
                self.buffer.PopupMenu(menu, pos)
            else:
                self.buffer.PopupMenu(menu, self.buffer.list.list.GetPosition())
    
        def url(self, *args, **kwargs):
            self.dismiss_announcement()
    
        def get_more_items(self):        output.speak(_("This buffer does not support loading more items."), True)

    # Disable social interactions not applicable to announcements
    def reply(self, *args, **kwargs):
        pass

    def share_item(self, *args, **kwargs):
        pass

    def toggle_favorite(self, *args, **kwargs):
        pass

    def add_to_favorites(self, *args, **kwargs):
        pass

    def remove_from_favorites(self, *args, **kwargs):
        pass

    def toggle_bookmark(self, *args, **kwargs):
        pass

    def mute_conversation(self, *args, **kwargs):
        pass

    def vote(self, *args, **kwargs):
        pass

    def send_message(self, *args, **kwargs):
        pass

    def user_details(self, *args, **kwargs):
        pass

    def view_item(self, *args, **kwargs):
        # We could implement a specific viewer for announcements if needed, 
        # but the default one expects a status object structure.
        pass

    def copy(self, event=None):
        item = self.get_item()
        if item:
             pub.sendMessage("execute-action", action="copy_to_clipboard")

    def onFocus(self, *args, **kwargs):
        # Similar logic to BaseBuffer but adapted if needed. 
        # BaseBuffer.onFocus handles reading long posts.
        if config.app["app-settings"]["read_long_posts_in_gui"] == True and self.buffer.list.list.HasFocus():
            wx.CallLater(40, output.speak, self.get_message(), interrupt=True)

    def get_message(self):
        # Override to use announcement template
        announcement = self.get_item()
        if announcement == None:
            return
        template = self.session.settings.get("templates", {}).get("announcement", templates.announcement_default_template)
        t = templates.render_announcement(announcement, template, self.session.settings, relative_times=self.session.settings["general"]["relative_times"], offset_hours=self.session.db["utc_offset"])
        return t

    def start_stream(self, mandatory=False, play_sound=True, avoid_autoreading=False):
        current_time = time.time()
        if self.execution_time == 0 or current_time-self.execution_time >= 300 or mandatory==True:
            self.execution_time = current_time
            log.debug("Starting stream for announcements buffer")
            try:
                # The announcements API does not accept min_id or limit parameters
                results = self.session.api.announcements()
                # Reverse the list so order_buffer processes them according to user preference
                results.reverse()
            except Exception as e:
                log.exception("Error retrieving announcements: %s" % (str(e)))
                return 0
            
            # order_buffer handles duplication filtering by ID internally
            number_of_items = self.session.order_buffer(self.name, results)
            log.debug("Number of new announcements retrieved: %d" % (number_of_items,))
            
            self.put_items_on_list(number_of_items)
            
            if number_of_items > 0 and play_sound == True and self.sound != None and self.session.settings["sound"]["session_mute"] == False:
                self.session.sound.play(self.sound)
            
            return number_of_items
        return 0
