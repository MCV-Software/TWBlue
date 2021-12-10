# -*- coding: utf-8 -*-
import platform
import widgetUtils
import arrow
import webbrowser
import output
import config
import languageHandler
import logging
from controller import messages
from sessions.twitter import compose, utils, templates
from mysc.thread_utils import call_threaded
from tweepy.errors import TweepyException
from pubsub import pub
from wxUI import commonMessageDialogs
from . import base

log = logging.getLogger("controller.buffers.twitter.dmBuffer")

class DirectMessagesBuffer(base.BaseBuffer):

    def get_more_items(self):
        # 50 results are allowed per API call, so let's assume max value can be 50.
        # reference: https://developer.twitter.com/en/docs/twitter-api/v1/direct-messages/sending-and-receiving/api-reference/list-events
        if self.session.settings["general"]["max_tweets_per_call"] > 50:
            count = 50
        else:
            count = self.session.settings["general"]["max_tweets_per_call"]
        total = 0
        # try to retrieve the cursor for the current buffer.
        cursor = self.session.db["cursors"].get(self.name)
        try:
            items = getattr(self.session.twitter, self.function)(return_cursors=True, cursor=cursor, count=count, *self.args, **self.kwargs)
            if type(items) == tuple:
                items, cursor = items
                if type(cursor) == tuple:
                    cursor = cursor[1]
                cursors = self.session.db["cursors"]
                cursors[self.name] = cursor
                self.session.db["cursors"] = cursors
            results = [i for i in items]
            items = results
            log.debug("Retrieved %d items for cursored search in function %s" % (len(items), self.function))
        except TweepyException as e:
            log.exception("Error %s" % (str(e)))
            return
        if items == None:
            return
        sent = []
        received = []
        sent_dms = self.session.db["sent_direct_messages"]
        received_dms = self.session.db["direct_messages"]
        for i in items:
            if int(i.message_create["sender_id"]) == self.session.db["user_id"]:
                if self.session.settings["general"]["reverse_timelines"] == False:
                    sent_dms.insert(0, i)
                    sent.append(i)
                else:
                    sent_dms.append(i)
                    sent.insert(0, i)
            else:
                if self.session.settings["general"]["reverse_timelines"] == False:
                    received_dms.insert(0, i)
                    received.append(i)
                else:
                    received_dms.append(i)
                    received.insert(0, i)
            total = total+1
        self.session.db["direct_messages"] = received_dms
        self.session.db["sent_direct_messages"] = sent_dms
        user_ids = [item.message_create["sender_id"] for item in items]
        self.session.save_users(user_ids)
        pub.sendMessage("more-sent-dms", data=sent, account=self.session.db["user_name"])
        selected = self.buffer.list.get_selected()
        if self.session.settings["general"]["reverse_timelines"] == True:
            for i in received:
                if int(i.message_create["sender_id"]) == self.session.db["user_id"]:
                    continue
                tweet = self.compose_function(i, self.session.db, self.session.settings["general"]["relative_times"], self.session.settings["general"]["show_screen_names"], self.session)
                self.buffer.list.insert_item(True, *tweet)
            self.buffer.list.select_item(selected)
        else:
            for i in received:
                if int(i.message_create["sender_id"]) == self.session.db["user_id"]:
                    continue
                tweet = self.compose_function(i, self.session.db, self.session.settings["general"]["relative_times"], self.session.settings["general"]["show_screen_names"], self.session)
                self.buffer.list.insert_item(True, *tweet)
        output.speak(_(u"%s items retrieved") % (total), True)

    def reply(self, *args, **kwargs):
        tweet = self.get_right_tweet()
        screen_name = self.session.get_user(tweet.message_create["sender_id"]).screen_name
        message = messages.reply(session=self.session, title=_("Mention"), caption=_("Mention to %s") % (screen_name,), text="@%s " % (screen_name,), thread_mode=False, users=[screen_name,])
        if message.message.ShowModal() == widgetUtils.OK:
            tweet_data = message.get_tweet_data()
            call_threaded(self.session.send_tweet, tweet_data)
        if hasattr(message.message, "destroy"):
            message.message.destroy()

    def onFocus(self, *args, **kwargs):
        tweet = self.get_tweet()
        if platform.system() == "Windows" and self.session.settings["general"]["relative_times"] == True:
            # fix this:
            original_date = arrow.get(int(tweet.created_timestamp))
            ts = original_date.humanize(locale=languageHandler.getLanguage())
            self.buffer.list.list.SetItem(self.buffer.list.get_selected(), 2, ts)
        if self.session.settings['sound']['indicate_audio'] and utils.is_audio(tweet):
            self.session.sound.play("audio.ogg")
        if self.session.settings['sound']['indicate_img'] and utils.is_media(tweet):
            self.session.sound.play("image.ogg")

    def clear_list(self):
        dlg = commonMessageDialogs.clear_list()
        if dlg == widgetUtils.YES:
            self.session.db[self.name] = []
            self.buffer.list.clear()

    def auto_read(self, number_of_items):
        if number_of_items == 1 and self.name in self.session.settings["other_buffers"]["autoread_buffers"] and self.name not in self.session.settings["other_buffers"]["muted_buffers"] and self.session.settings["sound"]["session_mute"] == False:
            if self.session.settings["general"]["reverse_timelines"] == False:
                tweet = self.session.db[self.name][-1]
            else:
                tweet = self.session.db[self.name][0]
            output.speak(_(u"New direct message"))
            output.speak(" ".join(self.compose_function(tweet, self.session.db, self.session.settings["general"]["relative_times"], self.session.settings["general"]["show_screen_names"], self.session)))
        elif number_of_items > 1 and self.name in self.session.settings["other_buffers"]["autoread_buffers"] and self.name not in self.session.settings["other_buffers"]["muted_buffers"] and self.session.settings["sound"]["session_mute"] == False:
            output.speak(_(u"{0} new direct messages.").format(number_of_items,))

    def open_in_browser(self, *args, **kwargs):
        output.speak(_(u"This action is not supported in the buffer yet."))

    def get_message(self):
        template = self.session.settings["templates"]["dm"]
        dm = self.get_right_tweet()
        t = templates.render_dm(dm, template, self.session, relative_times=self.session.settings["general"]["relative_times"], offset_seconds=self.session.db["utc_offset"])
        return t

class SentDirectMessagesBuffer(DirectMessagesBuffer):

    def __init__(self, *args, **kwargs):
        super(SentDirectMessagesBuffer, self).__init__(*args, **kwargs)
        if ("sent_direct_messages" in self.session.db) == False:
            self.session.db["sent_direct_messages"] = []

    def get_more_items(self):
        output.speak(_(u"Getting more items cannot be done in this buffer. Use the direct messages buffer instead."))

    def start_stream(self, *args, **kwargs):
        pass

    def put_more_items(self, items):
        if self.session.settings["general"]["reverse_timelines"] == True:
            for i in items:
                tweet = self.compose_function(i, self.session.db, self.session.settings["general"]["relative_times"], self.session.settings["general"]["show_screen_names"], self.session)
                self.buffer.list.insert_item(False, *tweet)
        else:
            for i in items:
                tweet = self.compose_function(i, self.session.db, self.session.settings["general"]["relative_times"], self.session.settings["general"]["show_screen_names"], self.session)
                self.buffer.list.insert_item(False, *tweet)

    def get_message(self):
        template = self.session.settings["templates"]["dm_sent"]
        dm = self.get_right_tweet()
        t = templates.render_dm(dm, template, self.session, relative_times=self.session.settings["general"]["relative_times"], offset_seconds=self.session.db["utc_offset"])
        return t
