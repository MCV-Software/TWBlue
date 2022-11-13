# -*- coding: utf-8 -*-
import time
import logging
import wx
import widgetUtils
import output
from controller.buffers.mastodon.base import BaseBuffer
from sessions.mastodon import utils, templates
from wxUI import buffers, commonMessageDialogs
log = logging.getLogger("controller.buffers.mastodon.conversations")

class ConversationListBuffer(BaseBuffer):

    def create_buffer(self, parent, name):
        self.buffer = buffers.mastodon.conversationListPanel(parent, name)

    def get_item(self):
        index = self.buffer.list.get_selected()
        if index > -1 and self.session.db.get(self.name) != None and len(self.session.db[self.name]) > index:
            return self.session.db[self.name][index]["last_status"]

    def get_formatted_message(self):
        return self.compose_function(self.get_conversation(), self.session.db, self.session.settings["general"]["relative_times"], self.session.settings["general"]["show_screen_names"])[1]

    def get_conversation(self):
        index = self.buffer.list.get_selected()
        if index > -1 and self.session.db.get(self.name) != None:
            return self.session.db[self.name][index]

    def get_message(self):
        conversation = self.get_conversation()
        if conversation == None:
            return
        template = self.session.settings["templates"]["conversation"]
        toot_template = self.session.settings["templates"]["toot"]
        t = templates.render_conversation(conversation=conversation, template=template, toot_template=toot_template, relative_times=self.session.settings["general"]["relative_times"], offset_hours=self.session.db["utc_offset"])
        return t

    def start_stream(self, mandatory=False, play_sound=True, avoid_autoreading=False):
        current_time = time.time()
        if self.execution_time == 0 or current_time-self.execution_time >= 180 or mandatory==True:
            self.execution_time = current_time
            log.debug("Starting stream for buffer %s, account %s and type %s" % (self.name, self.account, self.type))
            log.debug("args: %s, kwargs: %s" % (self.args, self.kwargs))
            count = self.session.settings["general"]["max_toots_per_call"]
            min_id = None
            # toDo: Implement reverse timelines properly here.
#            if (self.name != "favorites" and self.name != "bookmarks") and self.name in self.session.db and len(self.session.db[self.name]) > 0:
#                min_id = self.session.db[self.name][-1].id
            try:
                results = getattr(self.session.api, self.function)(min_id=min_id, limit=count, *self.args, **self.kwargs)
                results.reverse()
            except Exception as e:
                log.exception("Error %s" % (str(e)))
                return
            new_position, number_of_items = self.order_buffer(results)
            log.debug("Number of items retrieved: %d" % (number_of_items,))
            self.put_items_on_list(number_of_items)
            if new_position > -1:
                self.buffer.list.select_item(new_position)
            if number_of_items > 0 and  self.name != "sent_toots" and self.name != "sent_direct_messages" and self.sound != None and self.session.settings["sound"]["session_mute"] == False and self.name not in self.session.settings["other_buffers"]["muted_buffers"] and play_sound == True:
                self.session.sound.play(self.sound)
            # Autoread settings
            if avoid_autoreading == False and mandatory == True and number_of_items > 0 and self.name in self.session.settings["other_buffers"]["autoread_buffers"]:
                self.auto_read(number_of_items)
            return number_of_items

    def get_more_items(self):
        elements = []
        if self.session.settings["general"]["reverse_timelines"] == False:
            max_id = self.session.db[self.name][0].last_status.id
        else:
            max_id = self.session.db[self.name][-1].last_status.id
        try:
            items = getattr(self.session.api, self.function)(max_id=max_id, limit=self.session.settings["general"]["max_toots_per_call"], *self.args, **self.kwargs)
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
                conversation = self.compose_function(i, self.session.db, self.session.settings["general"]["relative_times"], self.session.settings["general"]["show_screen_names"])
                self.buffer.list.insert_item(True, *conversation)
        else:
            for i in items:
                conversation = self.compose_function(i, self.session.db, self.session.settings["general"]["relative_times"], self.session.settings["general"]["show_screen_names"])
                self.buffer.list.insert_item(False, *conversation)
            self.buffer.list.select_item(selection)
        output.speak(_(u"%s items retrieved") % (str(len(elements))), True)

    def get_item_position(self, conversation):
        for i in range(len(self.session.db[self.name])):
            if self.session.db[self.name][i].id == conversation.id:
                return i

    def order_buffer(self, data):
        num = 0
        focus_object = None
        if self.session.db.get(self.name) == None:
            self.session.db[self.name] = []
        objects = self.session.db[self.name]
        for i in data:
            position = self.get_item_position(i)
            if position != None:
                conversation = self.session.db[self.name][position]
                if conversation.last_status.id != i.last_status.id:
                    focus_object = i
                    objects.pop(position)
                    self.buffer.list.remove_item(position)
                    if self.session.settings["general"]["reverse_timelines"] == False:
                        objects.append(i)
                    else:
                        objects.insert(0, i)
                    num = num+1
            else:
                if self.session.settings["general"]["reverse_timelines"] == False:
                    objects.append(i)
                else:
                    objects.insert(0, i)
                num = num+1
        self.session.db[self.name] = objects
        if focus_object == None:
            return (-1, num)
        new_position = self.get_item_position(focus_object)
        if new_position != None:
            return (new_position, num)
        return (-1, num)

    def bind_events(self):
        log.debug("Binding events...")
        self.buffer.set_focus_function(self.onFocus)
        widgetUtils.connect_event(self.buffer.list.list, widgetUtils.KEYPRESS, self.get_event)
        widgetUtils.connect_event(self.buffer, widgetUtils.BUTTON_PRESSED, self.post_status, self.buffer.toot)
        widgetUtils.connect_event(self.buffer, widgetUtils.BUTTON_PRESSED, self.reply, self.buffer.reply)
        widgetUtils.connect_event(self.buffer.list.list, wx.EVT_LIST_ITEM_RIGHT_CLICK, self.show_menu)
        widgetUtils.connect_event(self.buffer.list.list, wx.EVT_LIST_KEY_DOWN, self.show_menu_by_key)

    def fav(self):
        pass

    def unfav(self):
        pass

    def can_share(self):
        return False

    def send_message(self):
        return self.reply()

    def onFocus(self, *args, **kwargs):
        toot = self.get_item()
        if self.session.settings['sound']['indicate_audio'] and utils.is_audio_or_video(toot):
            self.session.sound.play("audio.ogg")
        if self.session.settings['sound']['indicate_img'] and utils.is_image(toot):
            self.session.sound.play("image.ogg")

    def destroy_status(self):
        pass

class ConversationBuffer(BaseBuffer):

    def __init__(self, toot, *args, **kwargs):
        self.toot = toot
        super(ConversationBuffer, self).__init__(*args, **kwargs)

    def start_stream(self, mandatory=False, play_sound=True, avoid_autoreading=False):
        current_time = time.time()
        if self.execution_time == 0 or current_time-self.execution_time >= 180 or mandatory==True:
            self.execution_time = current_time
            log.debug("Starting stream for buffer %s, account %s and type %s" % (self.name, self.account, self.type))
            log.debug("args: %s, kwargs: %s" % (self.args, self.kwargs))
            self.toot = self.session.api.status(id=self.toot.id)
            # toDo: Implement reverse timelines properly here.
            try:
                results = []
                items = getattr(self.session.api, self.function)(*self.args, **self.kwargs)
                [results.append(item) for item in items.ancestors]
                results.append(self.toot)
                [results.append(item) for item in items.descendants]
            except Exception as e:
                log.exception("Error %s" % (str(e)))
                return
            number_of_items = self.session.order_buffer(self.name, results)
            log.debug("Number of items retrieved: %d" % (number_of_items,))
            self.put_items_on_list(number_of_items)
            if number_of_items > 0 and  self.name != "sent_toots" and self.name != "sent_direct_messages" and self.sound != None and self.session.settings["sound"]["session_mute"] == False and self.name not in self.session.settings["other_buffers"]["muted_buffers"] and play_sound == True:
                self.session.sound.play(self.sound)
            # Autoread settings
            if avoid_autoreading == False and mandatory == True and number_of_items > 0 and self.name in self.session.settings["other_buffers"]["autoread_buffers"]:
                self.auto_read(number_of_items)
            return number_of_items


    def get_more_items(self):
        output.speak(_(u"This action is not supported for this buffer"), True)

    def remove_buffer(self, force=False):
        if force == False:
            dlg = commonMessageDialogs.remove_buffer()
        else:
            dlg = widgetUtils.YES
        if dlg == widgetUtils.YES:
            if self.name in self.session.db:
                self.session.db.pop(self.name)
            return True
        elif dlg == widgetUtils.NO:
            return False