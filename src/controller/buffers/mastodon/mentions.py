# -*- coding: utf-8 -*-
import time
import logging
from controller.buffers.mastodon.base import BaseBuffer
from sessions.mastodon import utils

log = logging.getLogger("controller.buffers.mastodon.mentions")

class MentionsBuffer(BaseBuffer):

    def start_stream(self, mandatory=False, play_sound=True, avoid_autoreading=False):
        current_time = time.time()
        if self.execution_time == 0 or current_time-self.execution_time >= 180 or mandatory==True:
            self.execution_time = current_time
            log.debug("Starting stream for buffer %s, account %s and type %s" % (self.name, self.account, self.type))
            log.debug("args: %s, kwargs: %s" % (self.args, self.kwargs))
            count = self.session.settings["general"]["max_toots_per_call"]
            min_id = None
            # toDo: Implement reverse timelines properly here.
#            if self.name != "favorites" and self.name in self.session.db and len(self.session.db[self.name]) > 0:
#                min_id = self.session.db[self.name][-1].id
            try:
                items = getattr(self.session.api, self.function)(min_id=min_id, limit=count, exclude_types=["follow", "favourite", "reblog", "poll", "follow_request"], *self.args, **self.kwargs)
                items.reverse()
                results = [item.status for item in items if item.get("status") and item.type == "mention"]
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
        elements = []
        if self.session.settings["general"]["reverse_timelines"] == False:
            max_id = self.session.db[self.name][0].id
        else:
            max_id = self.session.db[self.name][-1].id
        try:
            items = getattr(self.session.api, self.function)(max_id=max_id, limit=self.session.settings["general"]["max_toots_per_call"], exclude_types=["follow", "favourite", "reblog", "poll", "follow_request"], *self.args, **self.kwargs)
            items = [item.status for item in items if item.get("status") and item.type == "mention"]
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
                toot = self.compose_function(i, self.session.db, self.session.settings["general"]["relative_times"], self.session.settings["general"]["show_screen_names"])
                self.buffer.list.insert_item(True, *toot)
        else:
            for i in items:
                toot = self.compose_function(i, self.session.db, self.session.settings["general"]["relative_times"], self.session.settings["general"]["show_screen_names"])
                self.buffer.list.insert_item(False, *toot)
            self.buffer.list.select_item(selection)
        output.speak(_(u"%s items retrieved") % (str(len(elements))), True)