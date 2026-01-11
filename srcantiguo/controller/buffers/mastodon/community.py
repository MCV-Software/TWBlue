# -*- coding: utf-8 -*-
import time
import logging
import mastodon
import widgetUtils
import output
from wxUI import commonMessageDialogs
from sessions.mastodon import utils
from . import base

log = logging.getLogger("controller.buffers.mastodon.community")

class CommunityBuffer(base.BaseBuffer):
    def __init__(self, community_url, *args, **kwargs):
        super(CommunityBuffer, self).__init__(*args, **kwargs)
        self.community_url = community_url
        self.community_api = mastodon.Mastodon(api_base_url=self.community_url)
        self.timeline = kwargs.get("timeline", "local")
        self.kwargs.pop("timeline")

    def get_buffer_name(self):
        type = _("Local") if self.timeline == "local" else _("Federated")
        instance = self.community_url.replace("https://", "")
        return _(f"{type} timeline for {instance}")

    def start_stream(self, mandatory=False, play_sound=True, avoid_autoreading=False):
        current_time = time.time()
        if self.execution_time == 0 or current_time-self.execution_time >= 180 or mandatory==True:
            self.execution_time = current_time
            log.debug("Starting stream for buffer %s, account %s and type %s" % (self.name, self.account, self.type))
            log.debug("args: %s, kwargs: %s" % (self.args, self.kwargs))
            count = self.session.settings["general"]["max_posts_per_call"]
            min_id = None
            # toDo: Implement reverse timelines properly here.
            if self.name in self.session.db and len(self.session.db[self.name]) > 0:
                if self.session.settings["general"]["reverse_timelines"]:
                    min_id = self.session.db[self.name][0].id
                else:
                    min_id = self.session.db[self.name][-1].id
            try:
                results = self.community_api.timeline(timeline=self.timeline, min_id=min_id, limit=count, *self.args, **self.kwargs)
                results.reverse()
            except Exception as e:
                log.exception("Error %s" % (str(e)))
                return
            number_of_items = self.session.order_buffer(self.name, results)
            log.debug("Number of items retrieved: %d" % (number_of_items,))
            self.put_items_on_list(number_of_items)
            if number_of_items > 0 and self.sound != None and self.session.settings["sound"]["session_mute"] == False and self.name not in self.session.settings["other_buffers"]["muted_buffers"] and play_sound == True:
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
            items = self.community_api.timeline(timeline=self.timeline, max_id=max_id, limit=self.session.settings["general"]["max_posts_per_call"], *self.args, **self.kwargs)
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
        safe = True
        if self.session.settings["general"]["read_preferences_from_instance"]:
            safe = self.session.expand_spoilers == False
        if self.session.settings["general"]["reverse_timelines"] == False:
            for i in elements:
                post = self.compose_function(i, self.session.db, self.session.settings, self.session.settings["general"]["relative_times"], self.session.settings["general"]["show_screen_names"], safe=safe)
                self.buffer.list.insert_item(True, *post)
        else:
            for i in elements:
                post = self.compose_function(i, self.session.db, self.session.settings, self.session.settings["general"]["relative_times"], self.session.settings["general"]["show_screen_names"], safe=safe)
                self.buffer.list.insert_item(False, *post)
            self.buffer.list.select_item(selection)
        output.speak(_(u"%s items retrieved") % (str(len(elements))), True)

    def remove_buffer(self, force=False):
        if force == False:
            dlg = commonMessageDialogs.remove_buffer()
        else:
            dlg = widgetUtils.YES
        if dlg == widgetUtils.YES:
            tl_info = f"{self.timeline}@{self.community_url}"
            self.session.settings["other_buffers"]["communities"].remove(tl_info)
            self.session.settings.write()
            if self.name in self.session.db:
                self.session.db.pop(self.name)
            return True
        elif dlg == widgetUtils.NO:
            return False

    def get_item_from_instance(self, *args, **kwargs):
        item = self.get_item()
        try:
            results = self.session.api.search(q=item.url, resolve=True, result_type="statuses")
        except Exception as e:
            log.exception("Error when searching for remote post.")
            return None
        item = results["statuses"][0]
        return item

    def reply(self, *args, **kwargs):
        item = self.get_item_from_instance()
        if item != None:
            super(CommunityBuffer, self).reply(item=item)

    def send_message(self, *args, **kwargs):
        item = self.get_item_from_instance()
        if item != None:
            super(CommunityBuffer, self).send_message(item=item)

    def share_item(self, *args, **kwargs):
        item = self.get_item_from_instance()
        if item != None:
            super(CommunityBuffer, self).share_item(item=item)

    def add_to_favorites(self, *args, **kwargs):
        item = self.get_item_from_instance()
        if item != None:
            super(CommunityBuffer, self).add_to_favorite(item=item)

    def remove_from_favorites(self, *args, **kwargs):
        item = self.get_item_from_instance()
        if item != None:
            super(CommunityBuffer, self).remove_from_favorites(item=item)

    def toggle_favorite(self, *args, **kwargs):
        item = self.get_item_from_instance()
        if item != None:
            super(CommunityBuffer, self).toggle_favorite(item=item)

    def toggle_bookmark(self, *args, **kwargs):
        item = self.get_item_from_instance()
        if item != None:
            super(CommunityBuffer, self).toggle_bookmark(item=item)

    def vote(self, *args, **kwargs):
        item = self.get_item_from_instance()
        if item != None:
            super(CommunityBuffer, self).vote(item=item)
    
    def view_item(self, *args, **kwargs):
        item = self.get_item_from_instance()
        if item != None:
            super(CommunityBuffer, self).view_item(item=item)
