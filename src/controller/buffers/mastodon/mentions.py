# -*- coding: utf-8 -*-
import time
import logging
import output
from controller.buffers.mastodon.base import BaseBuffer
from sessions.mastodon import utils

log = logging.getLogger("controller.buffers.mastodon.mentions")

class MentionsBuffer(BaseBuffer):

    def get_item(self):
        index = self.buffer.list.get_selected()
        if index > -1 and self.session.db.get(self.name) != None and len(self.session.db[self.name]) > index:
            return self.session.db[self.name][index]["status"]

    def start_stream(self, mandatory=False, play_sound=True, avoid_autoreading=False):
        current_time = time.time()
        if self.execution_time == 0 or current_time-self.execution_time >= 180 or mandatory==True:
            self.execution_time = current_time
            log.debug("Starting stream for buffer %s, account %s and type %s" % (self.name, self.account, self.type))
            log.debug("args: %s, kwargs: %s" % (self.args, self.kwargs))
            count = self.session.settings["general"]["max_posts_per_call"]
            min_id = None
            try:
                items = getattr(self.session.api, self.function)(min_id=min_id, limit=count, types=["mention"], *self.args, **self.kwargs)
                items.reverse()
            except Exception as e:
                log.exception("Error %s" % (str(e)))
                return
            # Attempt to remove items with no statuses attached to them as it might happen when blocked accounts have notifications.
            items = [item for item in items if item.status != None]
            number_of_items = self.session.order_buffer(self.name, items)
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
        if self.session.settings["general"]["reverse_timelines"] == False:
            max_id = self.session.db[self.name][0].id
        else:
            max_id = self.session.db[self.name][-1].id
        try:
            items = getattr(self.session.api, self.function)(max_id=max_id, limit=self.session.settings["general"]["max_posts_per_call"], types=["mention"], *self.args, **self.kwargs)
        except Exception as e:
            log.exception("Error %s" % (str(e)))
            return
        # Attempt to remove items with no statuses attached to them as it might happen when blocked accounts have notifications.
        items = [item for item in items if item.status != None]
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
        safe = True
        if self.session.settings["general"]["read_preferences_from_instance"]:
            safe = self.session.expand_spoilers == False
        if self.session.settings["general"]["reverse_timelines"] == False:
            for i in elements:
                post = self.compose_function(i.status, self.session.db, self.session.settings, self.session.settings["general"]["relative_times"], self.session.settings["general"]["show_screen_names"], safe=safe)
                self.buffer.list.insert_item(True, *post)
        else:
            for i in elements:
                post = self.compose_function(i.status, self.session.db, self.session.settings, self.session.settings["general"]["relative_times"], self.session.settings["general"]["show_screen_names"], safe=safe)
                self.buffer.list.insert_item(False, *post)
            self.buffer.list.select_item(selection)
        output.speak(_(u"%s items retrieved") % (str(len(elements))), True)

    def put_items_on_list(self, number_of_items):
        list_to_use = self.session.db[self.name]
        if number_of_items == 0 and self.session.settings["general"]["persist_size"] == 0: return
        log.debug("The list contains %d items " % (self.buffer.list.get_count(),))
        log.debug("Putting %d items on the list" % (number_of_items,))
        safe = True
        if self.session.settings["general"]["read_preferences_from_instance"]:
            safe = self.session.expand_spoilers == False
        if self.buffer.list.get_count() == 0:
            for i in list_to_use:
                post = self.compose_function(i.status, self.session.db, self.session.settings, self.session.settings["general"]["relative_times"], self.session.settings["general"]["show_screen_names"], safe=safe)
                self.buffer.list.insert_item(False, *post)
            self.buffer.set_position(self.session.settings["general"]["reverse_timelines"])
        elif self.buffer.list.get_count() > 0 and number_of_items > 0:
            if self.session.settings["general"]["reverse_timelines"] == False:
                items = list_to_use[len(list_to_use)-number_of_items:]
                for i in items:
                    post = self.compose_function(i.status, self.session.db, self.session.settings, self.session.settings["general"]["relative_times"], self.session.settings["general"]["show_screen_names"], safe=safe)
                    self.buffer.list.insert_item(False, *post)
            else:
                items = list_to_use[0:number_of_items]
                items.reverse()
                for i in items:
                    post = self.compose_function(i.status, self.session.db, self.session.settings, self.session.settings["general"]["relative_times"], self.session.settings["general"]["show_screen_names"], safe=safe)
                    self.buffer.list.insert_item(True, *post)
        log.debug("Now the list contains %d items " % (self.buffer.list.get_count(),))

    def add_new_item(self, item):
        safe = True
        if self.session.settings["general"]["read_preferences_from_instance"]:
            safe = self.session.expand_spoilers == False
        post = self.compose_function(item.status, self.session.db, self.session.settings, self.session.settings["general"]["relative_times"], self.session.settings["general"]["show_screen_names"], safe=safe)
        if self.session.settings["general"]["reverse_timelines"] == False:
            self.buffer.list.insert_item(False, *post)
        else:
            self.buffer.list.insert_item(True, *post)
        if self.name in self.session.settings["other_buffers"]["autoread_buffers"] and self.name not in self.session.settings["other_buffers"]["muted_buffers"] and self.session.settings["sound"]["session_mute"] == False:
            output.speak(" ".join(post[:2]), speech=self.session.settings["reporting"]["speech_reporting"], braille=self.session.settings["reporting"]["braille_reporting"])
