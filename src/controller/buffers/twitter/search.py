# -*- coding: utf-8 -*-
import time
import platform
if platform.system() == "Windows":
    from wxUI import  commonMessageDialogs
elif platform.system() == "Linux":
    from gi.repository import Gtk
    from gtkUI import commonMessageDialogs
import logging
from . import base, people

log = logging.getLogger("controller.buffers.twitter.searchBuffer")

class SearchBuffer(base.BaseBuffer):

    def remove_buffer(self, force=False):
        if force == False:
            dlg = commonMessageDialogs.remove_buffer()
        else:
            dlg = widgetUtils.YES
        if dlg == widgetUtils.YES:
            if self.name[:-11] in self.session.settings["other_buffers"]["tweet_searches"]:
                self.session.settings["other_buffers"]["tweet_searches"].remove(self.name[:-11])
                self.session.settings.write()
                if self.name in self.session.db:
                    self.session.db.pop(self.name)
                return True
        elif dlg == widgetUtils.NO:
            return False

class SearchPeopleBuffer(people.PeopleBuffer):
    """ This is identical to a normal peopleBufferController, except that uses the page parameter instead of a cursor."""
    def __init__(self, parent, function, name, sessionObject, account, bufferType="peoplePanel", *args, **kwargs):
        super(SearchPeopleBuffer, self).__init__(parent, function, name, sessionObject, account, bufferType="peoplePanel", *args, **kwargs)
        if ("page" in self.kwargs) == False:
            self.page = 1
        else:
            self.page = self.kwargs.pop("page")

    def get_more_items(self, *args, **kwargs):
        # Add 1 to the page parameter, put it in kwargs and calls to get_more_items in the parent buffer.
        self.page = self.page +1
        self.kwargs["page"] = self.page
        super(SearchPeopleBuffer, self).get_more_items(*args, **kwargs)
        # remove the parameter again to make sure start_stream won't fetch items for this page indefinitely.
        self.kwargs.pop("page")

    def remove_buffer(self, force=False):
        if force == False:
            dlg = commonMessageDialogs.remove_buffer()
        else:
            dlg = widgetUtils.YES
        if dlg == widgetUtils.YES:
            if self.name[:-11] in self.session.settings["other_buffers"]["tweet_searches"]:
                self.session.settings["other_buffers"]["tweet_searches"].remove(self.name[:-11])
                self.session.settings.write()
                if self.name in self.session.db:
                    self.session.db.pop(self.name)
                return True
        elif dlg == widgetUtils.NO:
            return False

class ConversationBuffer(SearchBuffer):

    def start_stream(self, start=False, mandatory=False, play_sound=True, avoid_autoreading=False):
        # starts stream every 3 minutes.
        current_time = time.time()
        if self.execution_time == 0 or current_time-self.execution_time >= 180 or mandatory == True:
            self.execution_time = current_time
            if start == True:
                self.statuses = []
                self.ids = []
                self.statuses.append(self.tweet)
                self.ids.append(self.tweet.id)
                tweet = self.tweet
                if not hasattr(tweet, "in_reply_to_status_id"):
                    tweet.in_reply_to_status_id = None
                while tweet.in_reply_to_status_id != None:
                    try:
                        tweet = self.session.twitter.get_status(id=tweet.in_reply_to_status_id, tweet_mode="extended")
                    except TweepError as err:
                        break
                    self.statuses.insert(0, tweet)
                    self.ids.append(tweet.id)
                if tweet.in_reply_to_status_id == None:
                    self.kwargs["since_id"] = tweet.id
                    self.ids.append(tweet.id)
            val2 = self.session.search(self.name, tweet_mode="extended", *self.args, **self.kwargs)
            for i in val2:
                if i.in_reply_to_status_id in self.ids:
                    self.statuses.append(i)
                    self.ids.append(i.id)
                    tweet = i
            number_of_items = self.session.order_buffer(self.name, self.statuses)
            log.debug("Number of items retrieved: %d" % (number_of_items,))
            self.put_items_on_list(number_of_items)
            if number_of_items > 0 and self.sound != None and self.session.settings["sound"]["session_mute"] == False and self.name not in self.session.settings["other_buffers"]["muted_buffers"] and play_sound == True:
                self.session.sound.play(self.sound)
            # Autoread settings
            if avoid_autoreading == False and mandatory == True and number_of_items > 0 and self.name in self.session.settings["other_buffers"]["autoread_buffers"]:
                self.auto_read(number_of_items)
            return number_of_items

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
