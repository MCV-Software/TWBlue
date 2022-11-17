# -*- coding: utf-8 -*-
import time
import logging
import wx
import widgetUtils
import output
from mysc.thread_utils import call_threaded
from controller.buffers.mastodon.base import BaseBuffer
from controller.mastodon import messages
from sessions.mastodon import templates, utils
from wxUI import buffers

log = logging.getLogger("controller.buffers.mastodon.conversations")

class UserBuffer(BaseBuffer):

    def create_buffer(self, parent, name):
        self.buffer = buffers.mastodon.userPanel(parent, name)

    def get_message(self):
        user = self.get_item()
        if user == None:
            return
        template = self.session.settings["templates"]["person"]
        t = templates.render_user(user=user, template=template, relative_times=self.session.settings["general"]["relative_times"], offset_hours=self.session.db["utc_offset"])
        return t

    def bind_events(self):
        widgetUtils.connect_event(self.buffer.list.list, widgetUtils.KEYPRESS, self.get_event)
        widgetUtils.connect_event(self.buffer, widgetUtils.BUTTON_PRESSED, self.post_status, self.buffer.post)
        widgetUtils.connect_event(self.buffer, widgetUtils.BUTTON_PRESSED, self.send_message, self.buffer.message)
        widgetUtils.connect_event(self.buffer, widgetUtils.BUTTON_PRESSED, self.user_actions, self.buffer.actions)
        widgetUtils.connect_event(self.buffer.list.list, wx.EVT_LIST_ITEM_RIGHT_CLICK, self.show_menu)
        widgetUtils.connect_event(self.buffer.list.list, wx.EVT_LIST_KEY_DOWN, self.show_menu_by_key)

    def fav(self):
        pass

    def unfav(self):
        pass

    def can_share(self):
        return False

    def reply(self, *args, **kwargs):
        return self.send_message()

    def send_message(self, *args, **kwargs):
        item = self.get_item()
        title = _("New conversation with {}").format(item.username)
        caption = _("Write your message here")
        users_str = "@{} ".format(item.acct)
        post = messages.post(session=self.session, title=title, caption=caption, text=users_str)
        post.message.visibility.SetSelection(3)
        response = post.message.ShowModal()
        if response == wx.ID_OK:
            post_data = post.get_data()
            call_threaded(self.session.send_post, posts=post_data, visibility="direct")
        if hasattr(post.message, "destroy"):
            post.message.destroy()

    def audio(self):
        pass

    def url(self):
        pass

    def destroy_status(self):
        pass

    def start_stream(self, mandatory=False, play_sound=True, avoid_autoreading=False):
        current_time = time.time()
        if self.execution_time == 0 or current_time-self.execution_time >= 180 or mandatory==True:
            self.execution_time = current_time
            log.debug("Starting stream for buffer %s, account %s and type %s" % (self.name, self.account, self.type))
            log.debug("args: %s, kwargs: %s" % (self.args, self.kwargs))
            count = self.session.settings["general"]["max_posts_per_call"]
            # toDo: Implement reverse timelines properly here.
            try:
                results = getattr(self.session.api, self.function)(limit=count, *self.args, **self.kwargs)
                if hasattr(results, "_pagination_next") and self.name not in self.session.db["pagination_info"]:
                    self.session.db["pagination_info"][self.name] = results._pagination_next
                results.reverse()
            except Exception as e:
                log.exception("Error %s" % (str(e)))
                return
            number_of_items = self.session.order_buffer(self.name, results)
            log.debug("Number of items retrieved: %d" % (number_of_items,))
            self.put_items_on_list(number_of_items)
            if number_of_items > 0 and  self.name != "sent_posts" and self.name != "sent_direct_messages" and self.sound != None and self.session.settings["sound"]["session_mute"] == False and self.name not in self.session.settings["other_buffers"]["muted_buffers"] and play_sound == True:
                self.session.sound.play(self.sound)
            # Autoread settings
            if avoid_autoreading == False and mandatory == True and number_of_items > 0 and self.name in self.session.settings["other_buffers"]["autoread_buffers"]:
                self.auto_read(number_of_items)
            return number_of_items

    def get_more_items(self):
        elements = []
        pagination_info = self.session.db["pagination_info"].get(self.name)
        if pagination_info == None:
            output.speak(_("There are no more items in this buffer."))
            return
        try:
            items = self.session.api.fetch_next(pagination_info)
            if hasattr(items, "_pagination_next"):
                self.session.db["pagination_info"][self.name] = items._pagination_next
        except Exception as e:
            log.exception("Error %s" % (str(e)))
            return
        items_db = self.session.db[self.name]
        for i in items:
            if utils.find_item(i, self.session.db[self.name]) == None:
                elements.append(i)
                if self.session.settings["general"]["reverse_timelines"] == False:
                    items_db.insert(0, i)
                else:
                    items_db.append(i)
        self.session.db[self.name] = items_db
        selection = self.buffer.list.get_selected()
        log.debug("Retrieved %d items from cursored search in function %s." % (len(elements), self.function))
        if self.session.settings["general"]["reverse_timelines"] == False:
            for i in elements:
                post = self.compose_function(i, self.session.db, self.session.settings["general"]["relative_times"], self.session.settings["general"]["show_screen_names"])
                self.buffer.list.insert_item(True, *post)
        else:
            for i in items:
                post = self.compose_function(i, self.session.db, self.session.settings["general"]["relative_times"], self.session.settings["general"]["show_screen_names"])
                self.buffer.list.insert_item(False, *post)
            self.buffer.list.select_item(selection)
        output.speak(_(u"%s items retrieved") % (str(len(elements))), True)

    def get_item_url(self):
        item = self.get_item()
        return item.url

    def user_details(self):
        item = self.get_item()
        pass

    def add_to_favorites(self):
        pass

    def remove_from_favorites(self):
        pass

    def toggle_favorite(self):
        pass

    def view_item(self):
        item = self.get_item()
        print(item)

    def ocr_image(self):
        pass

