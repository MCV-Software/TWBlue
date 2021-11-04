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
            results = self.get_replies_v1(self.tweet)
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
        # firstly we would try to retrieve the whole thread, then we will get replies.
        # this makes us to waste two search API calls, but there's no better option to retrieve the whole thread including replies, unfortunately.
        thread_results = []
        reply_results = []
        # try to fetch conversation_id of the tweet initiating the buffer.
        try:
            tweet = self.session.twitter_v2.get_tweet(id=self.tweet.id, user_auth=True, tweet_fields=["conversation_id", "author_id"])
            thread_results.append(tweet.data)
        except TweepyException as e:
            log.exception("Error attempting to retrieve tweet conversation ID")
            thread_results.append(self.tweet)
            # Return earlier cause we can't do anything if we cannot fetch the object from twitter.
            return thread_results
        # If tweet contains a conversation_id param, let's retrieve the original tweet which started the conversation so we will have the whole reference for later.
        if hasattr(tweet.data, "conversation_id") and tweet.data.conversation_id != None:
            conversation_id = tweet.data.conversation_id
            original_tweet = self.session.twitter_v2.get_tweet(id=tweet.data.conversation_id, user_auth=True, tweet_fields=["conversation_id", "author_id"])
            thread_results.insert(0, original_tweet.data)
        else:
            conversation_id = tweet.data.id
        # find all tweets replying to the original thread only. Those tweets are sent by the same author who originally posted the first tweet.
        try:
            term = "conversation_id:{} from:{} to:{}".format(conversation_id, original_tweet.data.author_id, original_tweet.data.author_id)
            thread_tweets = self.session.twitter_v2.search_recent_tweets(term, user_auth=True, max_results=98, tweet_fields=["in_reply_to_user_id", "author_id", "conversation_id"])
            if thread_tweets.data != None:
                thread_results.extend(thread_tweets.data)
            # Search only replies to conversation_id.
            term = "conversation_id:{}".format(conversation_id, original_tweet.data.author_id)
            reply_tweets = self.session.twitter_v2.search_recent_tweets(term, user_auth=True, max_results=50, tweet_fields=["in_reply_to_user_id", "author_id", "conversation_id"])
            if reply_tweets.data != None:
                reply_results.extend(reply_tweets.data)
        except TweepyException as e:
            log.exception("There was an error when attempting to retrieve the whole conversation for buffer {}".format(self.buffer.name))
        # convert v2 tweets in normal, V1.1 tweets so we don't have to deal with those kind of objects in our infrastructure.
        # ToDo: Remove this last step once we support natively all objects fetched via Twitter API V2.
        results = []
        ids = [tweet.id for tweet in thread_results]
        if len(ids) > 0:
            try:
                thread_results = self.session.twitter.lookup_statuses(ids, include_ext_alt_text=True, tweet_mode="extended")
                thread_results.sort(key=lambda x: x.id)
                results.extend(thread_results)
            except TweepyException as e:
                log.exception("There was an error attempting to retrieve tweets for Twitter API V1.1, in conversation buffer {}".format(self.name))
                return []
        ids = [tweet.id for tweet in reply_results]
        if len(ids) > 0:
            try:
                reply_results = self.session.twitter.lookup_statuses(ids, include_ext_alt_text=True, tweet_mode="extended")
                reply_results.sort(key=lambda x: x.id)
                results.extend(reply_results)
            except TweepyException as e:
                log.exception("There was an error attempting to retrieve tweets for Twitter API V1.1, in conversation buffer {}".format(self.name))
        return results

    def get_replies_v1(self, tweet):
        try:
            tweet = self.session.twitter.get_status(id=tweet.id, tweet_mode="extended")
        except:
            log.exception("Error getting tweet for making a conversation buffer.")
            return []
        results = []
        results.append(tweet)
        if hasattr(tweet, "in_reply_to_status_id") and tweet.in_reply_to_status_id != None:
            while tweet.in_reply_to_status_id != None:
                original_tweet = self.session.twitter.get_status(id=tweet.in_reply_to_status_id, tweet_mode="extended")
                results.insert(0, original_tweet)
                tweet = original_tweet
        try:
            term = "from:{} to:{}".format(tweet.user.screen_name, tweet.user.screen_name)
            thread_tweets = self.session.twitter.search_tweets(term, count=100, since_id=tweet.id, tweet_mode="extended")
            results.extend(thread_tweets)
        except TweepyException as e:
            log.exception("There was an error when attempting to retrieve the whole conversation for buffer {}".format(self.buffer.name))

        try:
            term = "to:{}".format(tweet.user.screen_name)
            reply_tweets = self.session.twitter.search_tweets(term, count=100, since_id=tweet.id, tweet_mode="extended")
            ids = [t.id for t in results]
            reply_tweets = [t for t in reply_tweets if hasattr(t, "in_reply_to_status_id") and t.in_reply_to_status_id in ids]
            results.extend(reply_tweets)
        except TweepyException as e:
            log.exception("There was an error when attempting to retrieve the whole conversation for buffer {}".format(self.buffer.name))
        results.sort(key=lambda x: x.id)
        return results