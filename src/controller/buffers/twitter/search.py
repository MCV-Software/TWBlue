# -*- coding: utf-8 -*-
import time
import platform
import locale
if platform.system() == "Windows":
    from wxUI import  commonMessageDialogs
elif platform.system() == "Linux":
    from gi.repository import Gtk
    from gtkUI import commonMessageDialogs
import widgetUtils
import logging
from tweepy.errors import TweepyException
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
        current_time = time.time()
        if self.execution_time == 0 or current_time-self.execution_time >= 180 or mandatory == True:
            self.execution_time = current_time
            results = self.get_replies(self.tweet)
            number_of_items = self.session.order_buffer(self.name, results)
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

    def get_replies(self, tweet):
        """ Try to retrieve the whole conversation for the passed object by using a mix between calls to API V1.1 and V2 """
        results = []
        try:
            tweet = self.session.twitter_v2.get_tweet(id=self.tweet.id, user_auth=True, tweet_fields=["conversation_id"])
            results.append(tweet.data)
            original_tweet = self.session.twitter_v2.get_tweet(id=tweet.data.conversation_id, user_auth=True, tweet_fields=["conversation_id"])
            results.insert(0, original_tweet.data)
            term = "conversation_id:{}".format(tweet.data.conversation_id)
            tweets = self.session.twitter_v2.search_recent_tweets(term, user_auth=True, max_results=98, tweet_fields=["in_reply_to_user_id", "author_id", "conversation_id"])
            if tweets.data != None:
                results.extend(tweets.data)
        except TweepyException as e:
            log.exception("There was an error when attempting to retrieve the whole conversation for buffer {}".format(self.buffer.name))
        new_results = []
        ids = [tweet.id for tweet in results]
        try:
            results = self.session.twitter.lookup_statuses(ids, include_ext_alt_text=True, tweet_mode="extended")
            results.sort(key=lambda x: x.id)
        except TweepyException as e:
            log.exception("There was an error attempting to retrieve tweets for Twitter API V1.1, in conversation buffer {}".format(self.name))
            return []
        return results