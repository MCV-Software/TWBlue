# -*- coding: utf-8 -*-
import time
import wx
from wxUI import buffers, dialogs, commonMessageDialogs, menus
from controller import user
from controller import messages
import widgetUtils
import arrow
import webbrowser
import output
import config
import sound
import languageHandler
import logging
from audio_services import youtube_utils
from controller.buffers.base import base
from sessions.twitter import compose, utils, reduce, templates
from mysc.thread_utils import call_threaded
from tweepy.errors import TweepyException
from tweepy.cursor import Cursor
from pubsub import pub
from sessions.twitter.long_tweets import twishort, tweets

log = logging.getLogger("controller.buffers")

def _tweets_exist(function):
    """ A decorator to execute a function only if the selected buffer contains at least one item."""
    def function_(self, *args, **kwargs):
        if self.buffer.list.get_count() > 0:
            function(self, *args, **kwargs)
    return function_

class BaseBuffer(base.Buffer):
    def __init__(self, parent, function, name, sessionObject, account, sound=None, bufferType=None, compose_func="compose_tweet", *args, **kwargs):
        super(BaseBuffer, self).__init__(parent, function, *args, **kwargs)
        log.debug("Initializing buffer %s, account %s" % (name, account,))
        if bufferType != None:
            self.buffer = getattr(buffers, bufferType)(parent, name)
        else:
            self.buffer = buffers.basePanel(parent, name)
        self.invisible = True
        self.name = name
        self.type = self.buffer.type
        self.session = sessionObject
        self.compose_function = getattr(compose, compose_func)
        log.debug("Compose_function: %s" % (self.compose_function,))
        self.account = account
        self.buffer.account = account
        self.bind_events()
        self.sound = sound
        if "-timeline" in self.name or "-favorite" in self.name:
            self.finished_timeline = False
            # Add a compatibility layer for username based timelines from config.
            # ToDo: Remove this in some new versions of the client, when user ID timelines become mandatory.
            try:
                int(self.kwargs["user_id"])
            except ValueError:
                self.is_screen_name = True
                self.kwargs["screen_name"] = self.kwargs["user_id"]
                self.kwargs.pop("user_id")

    def get_buffer_name(self):
        """ Get buffer name from a set of different techniques."""
        # firstly let's take the easier buffers.
        basic_buffers = dict(home_timeline=_(u"Home"), mentions=_(u"Mentions"), direct_messages=_(u"Direct messages"), sent_direct_messages=_(u"Sent direct messages"), sent_tweets=_(u"Sent tweets"), favourites=_(u"Likes"), followers=_(u"Followers"), friends=_(u"Friends"), blocked=_(u"Blocked users"), muted=_(u"Muted users"))
        if self.name in list(basic_buffers.keys()):
            return basic_buffers[self.name]
        # Check user timelines
        elif hasattr(self, "username"):
            if "-timeline" in self.name:
                return _(u"{username}'s timeline").format(username=self.username,)
            elif "-favorite" in self.name:
                return _(u"{username}'s likes").format(username=self.username,)
            elif "-followers" in self.name:
                return _(u"{username}'s followers").format(username=self.username,)
            elif "-friends" in self.name:
                return _(u"{username}'s friends").format(username=self.username,)
        log.error("Error getting name for buffer %s" % (self.name,))
        return _(u"Unknown buffer")

    def post_status(self, *args, **kwargs):
        title = _("Tweet")
        caption = _("Write the tweet here")
        tweet = messages.tweet(self.session, title, caption, "")
        response = tweet.message.ShowModal()
        if response == wx.ID_OK:
            tweet_data = tweet.get_tweet_data()
            call_threaded(self.session.send_tweet, *tweet_data)
        if hasattr(tweet.message, "destroy"):
            tweet.message.destroy()

    def get_formatted_message(self):
        if self.type == "dm" or self.name == "direct_messages":
            return self.compose_function(self.get_right_tweet(), self.session.db, self.session.settings["general"]["relative_times"], self.session.settings["general"]["show_screen_names"], self.session)[1]
        return self.get_message()

    def get_message(self):
        template = self.session.settings["templates"]["tweet"]
        tweet = self.get_right_tweet()
        t = templates.render_tweet(tweet, template, self.session, relative_times=self.session.settings["general"]["relative_times"], offset_seconds=self.session.db["utc_offset"])
        return t

    def get_full_tweet(self):
        tweet = self.get_right_tweet()
        tweetsList = []
        tweet_id = tweet.id
        message = None
        if hasattr(tweet, "message"):
            message = tweet.message
        try:
            tweet = self.session.twitter.get_status(id=tweet_id, include_ext_alt_text=True, tweet_mode="extended")
            tweet.full_text = utils.expand_urls(tweet.full_text, tweet.entities)
        except TweepyException as e:
            utils.twitter_error(e)
            return
        if message != None:
            tweet.message = message
        l = tweets.is_long(tweet)
        while l != False:
            tweetsList.append(tweet)
            try:
                tweet = self.session.twitter.get_status(id=l, include_ext_alt_text=True, tweet_mode="extended")
                tweet.full_text = utils.expand_urls(tweet.full_text, tweet.entities)
            except TweepyException as e:
                utils.twitter_error(e)
                return
            l = tweets.is_long(tweet)
            if l == False:
                tweetsList.append(tweet)
        return (tweet, tweetsList)

    def start_stream(self, mandatory=False, play_sound=True, avoid_autoreading=False):
        # starts stream every 3 minutes.
        current_time = time.time()
        if self.execution_time == 0 or current_time-self.execution_time >= 180 or mandatory==True:
            self.execution_time = current_time
            log.debug("Starting stream for buffer %s, account %s and type %s" % (self.name, self.account, self.type))
            log.debug("args: %s, kwargs: %s" % (self.args, self.kwargs))
            if self.name != "direct_messages":
                val = self.session.call_paged(self.function, self.name, *self.args, **self.kwargs)
            else:
                # 50 results are allowed per API call, so let's assume max value can be 50.
                # reference: https://developer.twitter.com/en/docs/twitter-api/v1/direct-messages/sending-and-receiving/api-reference/list-events
                if self.session.settings["general"]["max_tweets_per_call"] > 50:
                    count = 50
                else:
                    count = self.session.settings["general"]["max_tweets_per_call"]
                # try to retrieve the cursor for the current buffer.
                try:
                    val = getattr(self.session.twitter, self.function)(return_cursors=True, count=count, *self.args, **self.kwargs)
                    if type(val) == tuple:
                        val, cursor = val
                        if type(cursor) == tuple:
                            cursor = cursor[1]
                        cursors = self.session.db["cursors"]
                        cursors[self.name] = cursor
                        self.session.db["cursors"] = cursors
                    results = [i for i in val]
                    val = results
                    val.reverse()
                    log.debug("Retrieved %d items from the cursored search on function %s." %(len(val), self.function))
                    user_ids = [item.message_create["sender_id"] for item in val]
                    self.session.save_users(user_ids)
                except TweepyException as e:
                    log.exception("Error %s" % (str(e)))
                    return
            number_of_items = self.session.order_buffer(self.name, val)
            log.debug("Number of items retrieved: %d" % (number_of_items,))
            self.put_items_on_list(number_of_items)
            if hasattr(self, "finished_timeline") and self.finished_timeline == False:
                if "-timeline" in self.name:
                    self.username = self.session.get_user(self.kwargs.get("user_id")).screen_name
                elif "-favorite" in self.name:
                    self.username = self.session.get_user(self.kwargs.get("user_id")).screen_name
                self.finished_timeline = True
            if number_of_items > 0 and self.name != "sent_tweets" and self.name != "sent_direct_messages" and self.sound != None and self.session.settings["sound"]["session_mute"] == False and self.name not in self.session.settings["other_buffers"]["muted_buffers"] and play_sound == True:
                self.session.sound.play(self.sound)
            # Autoread settings
            if avoid_autoreading == False and mandatory == True and number_of_items > 0 and self.name in self.session.settings["other_buffers"]["autoread_buffers"]:
                self.auto_read(number_of_items)
            return number_of_items

    def auto_read(self, number_of_items):
        if number_of_items == 1 and self.name in self.session.settings["other_buffers"]["autoread_buffers"] and self.name not in self.session.settings["other_buffers"]["muted_buffers"] and self.session.settings["sound"]["session_mute"] == False:
            if self.session.settings["general"]["reverse_timelines"] == False:
                tweet = self.session.db[self.name][-1]
            else:
                tweet = self.session.db[self.name][0]
            output.speak(_(u"New tweet in {0}").format(self.get_buffer_name()))
            output.speak(" ".join(self.compose_function(tweet, self.session.db, self.session.settings["general"]["relative_times"], self.session.settings["general"]["show_screen_names"], self.session)))
        elif number_of_items > 1 and self.name in self.session.settings["other_buffers"]["autoread_buffers"] and self.name not in self.session.settings["other_buffers"]["muted_buffers"] and self.session.settings["sound"]["session_mute"] == False:
            output.speak(_(u"{0} new tweets in {1}.").format(number_of_items, self.get_buffer_name()))

    def get_more_items(self):
        elements = []
        if self.session.settings["general"]["reverse_timelines"] == False:
            last_id = self.session.db[self.name][0].id
        else:
            last_id = self.session.db[self.name][-1].id
        try:
            items = getattr(self.session.twitter, self.function)(max_id=last_id, count=self.session.settings["general"]["max_tweets_per_call"], *self.args, **self.kwargs)
        except TweepyException as e:
            log.exception("Error %s" % (str(e)))
            return
        if items == None:
            return
        items_db = self.session.db[self.name]
        self.session.add_users_from_results(items)
        for i in items:
            if utils.is_allowed(i, self.session.settings, self.name) == True and utils.find_item(i, self.session.db[self.name]) == None:
                i = reduce.reduce_tweet(i)
                i = self.session.check_quoted_status(i)
                i = self.session.check_long_tweet(i)
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
                tweet = self.compose_function(i, self.session.db, self.session.settings["general"]["relative_times"], self.session.settings["general"]["show_screen_names"], self.session)
                self.buffer.list.insert_item(True, *tweet)
        else:
            for i in items:
                tweet = self.compose_function(i, self.session.db, self.session.settings["general"]["relative_times"], self.session.settings["general"]["show_screen_names"], self.session)
                self.buffer.list.insert_item(False, *tweet)
            self.buffer.list.select_item(selection)
        output.speak(_(u"%s items retrieved") % (str(len(elements))), True)

    def remove_buffer(self, force=False):
        if "-timeline" in self.name:
            if force == False:
                dlg = commonMessageDialogs.remove_buffer()
            else:
                dlg = widgetUtils.YES
            if dlg == widgetUtils.YES:
                if self.name[:-9] in self.session.settings["other_buffers"]["timelines"]:
                    self.session.settings["other_buffers"]["timelines"].remove(self.name[:-9])
                    self.session.settings.write()
                    if self.name in self.session.db:
                        self.session.db.pop(self.name)
                    return True
            elif dlg == widgetUtils.NO:
                return False
        elif "favorite" in self.name:
            if force == False:
                dlg = commonMessageDialogs.remove_buffer()
            else:
                dlg = widgetUtils.YES
            if dlg == widgetUtils.YES:
                if self.name[:-9] in self.session.settings["other_buffers"]["favourites_timelines"]:
                    self.session.settings["other_buffers"]["favourites_timelines"].remove(self.name[:-9])
                    if self.name in self.session.db:
                        self.session.db.pop(self.name)
                    self.session.settings.write()
                    return True
            elif dlg == widgetUtils.NO:
                return False
        else:
            output.speak(_(u"This buffer is not a timeline; it can't be deleted."), True)
            return False

    def remove_tweet(self, id):
        if type(self.session.db[self.name]) == dict: return
        items = self.session.db[self.name]
        for i in range(0, len(items)):
            if items[i].id == id:
                items.pop(i)
                self.remove_item(i)
        self.session.db[self.name] = items

    def put_items_on_list(self, number_of_items):
        list_to_use = self.session.db[self.name]
        if number_of_items == 0 and self.session.settings["general"]["persist_size"] == 0: return
        log.debug("The list contains %d items " % (self.buffer.list.get_count(),))
        log.debug("Putting %d items on the list" % (number_of_items,))
        if self.buffer.list.get_count() == 0:
            for i in list_to_use:
                tweet = self.compose_function(i, self.session.db, self.session.settings["general"]["relative_times"], self.session.settings["general"]["show_screen_names"], self.session)
                self.buffer.list.insert_item(False, *tweet)
            self.buffer.set_position(self.session.settings["general"]["reverse_timelines"])
        elif self.buffer.list.get_count() > 0 and number_of_items > 0:
            if self.session.settings["general"]["reverse_timelines"] == False:
                items = list_to_use[len(list_to_use)-number_of_items:]
                for i in items:
                    tweet = self.compose_function(i, self.session.db, self.session.settings["general"]["relative_times"], self.session.settings["general"]["show_screen_names"], self.session)
                    self.buffer.list.insert_item(False, *tweet)
            else:
                items = list_to_use[0:number_of_items]
                items.reverse()
                for i in items:
                    tweet = self.compose_function(i, self.session.db, self.session.settings["general"]["relative_times"], self.session.settings["general"]["show_screen_names"], self.session)
                    self.buffer.list.insert_item(True, *tweet)
        log.debug("Now the list contains %d items " % (self.buffer.list.get_count(),))

    def add_new_item(self, item):
        tweet = self.compose_function(item, self.session.db, self.session.settings["general"]["relative_times"], self.session.settings["general"]["show_screen_names"], self.session)
        if self.session.settings["general"]["reverse_timelines"] == False:
            self.buffer.list.insert_item(False, *tweet)
        else:
            self.buffer.list.insert_item(True, *tweet)
        if self.name in self.session.settings["other_buffers"]["autoread_buffers"] and self.name not in self.session.settings["other_buffers"]["muted_buffers"] and self.session.settings["sound"]["session_mute"] == False:
            output.speak(" ".join(tweet[:2]), speech=self.session.settings["reporting"]["speech_reporting"], braille=self.session.settings["reporting"]["braille_reporting"])

    def bind_events(self):
        log.debug("Binding events...")
        self.buffer.set_focus_function(self.onFocus)
        widgetUtils.connect_event(self.buffer.list.list, widgetUtils.KEYPRESS, self.get_event)
        widgetUtils.connect_event(self.buffer, widgetUtils.BUTTON_PRESSED, self.post_status, self.buffer.tweet)
#  if self.type == "baseBuffer":
        widgetUtils.connect_event(self.buffer, widgetUtils.BUTTON_PRESSED, self.share_item, self.buffer.retweet)
        widgetUtils.connect_event(self.buffer, widgetUtils.BUTTON_PRESSED, self.send_message, self.buffer.dm)
        widgetUtils.connect_event(self.buffer, widgetUtils.BUTTON_PRESSED, self.reply, self.buffer.reply)
        widgetUtils.connect_event(self.buffer.list.list, wx.EVT_LIST_ITEM_RIGHT_CLICK, self.show_menu)
        widgetUtils.connect_event(self.buffer.list.list, wx.EVT_LIST_KEY_DOWN, self.show_menu_by_key)

    def show_menu(self, ev, pos=0, *args, **kwargs):
        if self.buffer.list.get_count() == 0: return
        if self.name == "sent_tweets" or self.name == "direct_messages":
            menu = menus.sentPanelMenu()
        elif self.name == "direct_messages":
            menu = menus.dmPanelMenu()
            widgetUtils.connect_event(menu, widgetUtils.MENU, self.send_message, menuitem=menu.reply)
            widgetUtils.connect_event(menu, widgetUtils.MENU, self.user_actions, menuitem=menu.userActions)
        else:
            menu = menus.basePanelMenu()
            widgetUtils.connect_event(menu, widgetUtils.MENU, self.reply, menuitem=menu.reply)
            widgetUtils.connect_event(menu, widgetUtils.MENU, self.user_actions, menuitem=menu.userActions)
            widgetUtils.connect_event(menu, widgetUtils.MENU, self.share_item, menuitem=menu.retweet)
            widgetUtils.connect_event(menu, widgetUtils.MENU, self.fav, menuitem=menu.fav)
            widgetUtils.connect_event(menu, widgetUtils.MENU, self.unfav, menuitem=menu.unfav)
        widgetUtils.connect_event(menu, widgetUtils.MENU, self.url_, menuitem=menu.openUrl)
        widgetUtils.connect_event(menu, widgetUtils.MENU, self.audio, menuitem=menu.play)
        widgetUtils.connect_event(menu, widgetUtils.MENU, self.view, menuitem=menu.view)
        widgetUtils.connect_event(menu, widgetUtils.MENU, self.copy, menuitem=menu.copy)
        widgetUtils.connect_event(menu, widgetUtils.MENU, self.destroy_status, menuitem=menu.remove)
        if hasattr(menu, "openInBrowser"):
            widgetUtils.connect_event(menu, widgetUtils.MENU, self.open_in_browser, menuitem=menu.openInBrowser)
        if pos != 0:
            self.buffer.PopupMenu(menu, pos)
        else:
            self.buffer.PopupMenu(menu, ev.GetPosition())

    def view(self, *args, **kwargs):
        pub.sendMessage("execute-action", action="view_item")

    def copy(self, *args, **kwargs):
        pub.sendMessage("execute-action", action="copy_to_clipboard")

    def user_actions(self, *args, **kwargs):
        pub.sendMessage("execute-action", action="follow")

    def fav(self, *args, **kwargs):
        pub.sendMessage("execute-action", action="add_to_favourites")

    def unfav(self, *args, **kwargs):
        pub.sendMessage("execute-action", action="remove_from_favourites")

    def delete_item_(self, *args, **kwargs):
        pub.sendMessage("execute-action", action="delete_item")

    def url_(self, *args, **kwargs):
        self.url()

    def show_menu_by_key(self, ev):
        if self.buffer.list.get_count() == 0:
            return
        if ev.GetKeyCode() == wx.WXK_WINDOWS_MENU:
            self.show_menu(widgetUtils.MENU, pos=self.buffer.list.list.GetPosition())

    def get_tweet(self):
        if hasattr(self.session.db[self.name][self.buffer.list.get_selected()], "retweeted_status"):
            tweet = self.session.db[self.name][self.buffer.list.get_selected()].retweeted_status
        else:
            tweet = self.session.db[self.name][self.buffer.list.get_selected()]
        return tweet

    def get_right_tweet(self):
        tweet = self.session.db[self.name][self.buffer.list.get_selected()]
        return tweet

    def can_share(self):
        tweet = self.get_right_tweet()
        user = self.session.get_user(tweet.user)
        is_protected = user.protected
        return is_protected==False

    @_tweets_exist
    def reply(self, *args, **kwargs):
        tweet = self.get_right_tweet()
        user = self.session.get_user(tweet.user)
        screen_name = user.screen_name
        id = tweet.id
        users = utils.get_all_mentioned(tweet, self.session.db, field="screen_name")
        ids = utils.get_all_mentioned(tweet, self.session.db, field="id")
        # Build the window title
        if len(users) < 1:
            title=_("Reply to {arg0}").format(arg0=screen_name)
        else:
            title=_("Reply")
        message = messages.reply(self.session, title, _("Reply to %s") % (screen_name,), "", users=users, ids=ids)
        if message.message.ShowModal() == widgetUtils.OK:
            if config.app["app-settings"]["remember_mention_and_longtweet"]:
                if len(users) > 0:
                    config.app["app-settings"]["mention_all"] = message.message.mention_all.GetValue()
                config.app.write()
            tweet_data = dict(text=message.message.text.GetValue(), attachments=message.attachments, poll_options=message.poll_options, poll_period=message.poll_period)
            call_threaded(self.session.reply, in_reply_to_status_id=id, text=message.message.text.GetValue(), attachments=message.attachments, exclude_reply_user_ids=message.get_ids())
        if hasattr(message.message, "destroy"): message.message.destroy()
        self.session.settings.write()

    @_tweets_exist
    def send_message(self, *args, **kwargs):
        tweet = self.get_right_tweet()
        if self.type == "dm":
            screen_name = self.session.get_user(tweet.message_create["sender_id"]).screen_name
            users = [screen_name]
        elif self.type == "people":
            screen_name = tweet.screen_name
            users = [screen_name]
        else:
            screen_name = self.session.get_user(tweet.user).screen_name
            users = utils.get_all_users(tweet, self.session)
        dm = messages.dm(self.session, _("Direct message to %s") % (screen_name,), _("New direct message"), users)
        if dm.message.ShowModal() == widgetUtils.OK:
            screen_name = dm.message.cb.GetValue()
            user = self.session.get_user_by_screen_name(screen_name)
            recipient_id =  user
            text = dm.message.text.GetValue()
            if len(dm.attachments) > 0:
                attachment = dm.attachments[0]
            else:
                attachment = None
            call_threaded(self.session.direct_message, text=text, recipient=recipient_id, attachment=attachment)
        if hasattr(dm.message, "destroy"): dm.message.destroy()

    @_tweets_exist
    def share_item(self, *args, **kwargs):
        if self.can_share() == False:
            return output.speak(_("This action is not supported on protected accounts."))
        tweet = self.get_right_tweet()
        id = tweet.id
        if self.session.settings["general"]["retweet_mode"] == "ask":
            answer = commonMessageDialogs.retweet_question(self.buffer)
            if answer == widgetUtils.YES:
                self._retweet_with_comment(tweet, id)
            elif answer == widgetUtils.NO:
                self._direct_retweet(id)
        elif self.session.settings["general"]["retweet_mode"] == "direct":
            self._direct_retweet(id)
        else:
            self._retweet_with_comment(tweet, id)

    def _retweet_with_comment(self, tweet, id):
        if hasattr(tweet, "retweeted_status"):
            tweet = tweet.retweeted_status
        retweet = messages.tweet(session=self.session, title=_("Quote"), caption=_("Add your comment to the tweet"), max=256, thread_mode=False)
        if retweet.message.ShowModal() == widgetUtils.OK:
            text = retweet.message.text.GetValue()
            tweet_data = dict(text=text, attachments=retweet.attachments, poll_period=retweet.poll_period, poll_options=retweet.poll_options)
            tweet_data.update(quote_tweet_id=id)
            call_threaded(self.session.send_tweet, *[tweet_data])
        if hasattr(retweet.message, "destroy"):
            retweet.message.Destroy()

    def _direct_retweet(self, id):
        item = self.session.api_call(call_name="retweet", _sound="retweet_send.ogg", id=id)

    def onFocus(self, *args, **kwargs):
        tweet = self.get_tweet()
        # fix this:
        original_date = arrow.get(self.session.db[self.name][self.buffer.list.get_selected()].created_at, locale="en")
        ts = original_date.humanize(locale=languageHandler.getLanguage())
        self.buffer.list.list.SetItem(self.buffer.list.get_selected(), 2, ts)
        if self.session.settings['sound']['indicate_audio'] and utils.is_audio(tweet):
            self.session.sound.play("audio.ogg")
        if self.session.settings['sound']['indicate_geo'] and utils.is_geocoded(tweet):
            self.session.sound.play("geo.ogg")
        if self.session.settings['sound']['indicate_img'] and utils.is_media(tweet):
            self.session.sound.play("image.ogg")
        can_share = self.can_share()
        pub.sendMessage("toggleShare", shareable=can_share)
        self.buffer.retweet.Enable(can_share)

    def audio(self, url='', *args, **kwargs):
        if sound.URLPlayer.player.is_playing():
            return sound.URLPlayer.stop_audio()
        tweet = self.get_tweet()
        if tweet == None: return
        urls = utils.find_urls(tweet, twitter_media=True)
        if len(urls) == 1:
            url=urls[0]
        elif len(urls) > 1:
            urls_list = dialogs.urlList.urlList()
            urls_list.populate_list(urls)
            if urls_list.get_response() == widgetUtils.OK:
                url=urls_list.get_string()
            if hasattr(urls_list, "destroy"): urls_list.destroy()
        if url != '':
            #   try:
            sound.URLPlayer.play(url, self.session.settings["sound"]["volume"])
#   except:
#    log.error("Exception while executing audio method.")

# @_tweets_exist
    def url(self, url='', announce=True, *args, **kwargs):
        if url == '':
            tweet = self.get_tweet()
            urls = utils.find_urls(tweet)
            if len(urls) == 1:
                url=urls[0]
            elif len(urls) > 1:
                urls_list = dialogs.urlList.urlList()
                urls_list.populate_list(urls)
                if urls_list.get_response() == widgetUtils.OK:
                    url=urls_list.get_string()
                if hasattr(urls_list, "destroy"): urls_list.destroy()
            if url != '':
                if announce:
                    output.speak(_(u"Opening URL..."), True)
                webbrowser.open_new_tab(url)

    def clear_list(self):
        dlg = commonMessageDialogs.clear_list()
        if dlg == widgetUtils.YES:
            self.session.db[self.name] = []
            self.buffer.list.clear()

    @_tweets_exist
    def destroy_status(self, *args, **kwargs):
        index = self.buffer.list.get_selected()
        if self.type == "events" or self.type == "people" or self.type == "empty" or self.type == "account": return
        answer = commonMessageDialogs.delete_tweet_dialog(None)
        if answer == widgetUtils.YES:
            items = self.session.db[self.name]
            try:
                if self.name == "direct_messages" or self.name == "sent_direct_messages":
                    self.session.twitter.delete_direct_message(id=self.get_right_tweet().id)
                    items.pop(index)
                else:
                    self.session.twitter.destroy_status(id=self.get_right_tweet().id)
                    items.pop(index)
                self.buffer.list.remove_item(index)
            except TweepyException:
                self.session.sound.play("error.ogg")
            self.session.db[self.name] = items

    @_tweets_exist
    def user_details(self):
        tweet = self.get_right_tweet()
        if self.type == "dm":
            users = [self.session.get_user(tweet.message_create["sender_id"]).screen_name]
        elif self.type == "people":
            users = [tweet.screen_name]
        else:
            users = utils.get_all_users(tweet, self.session)
        dlg = dialogs.utils.selectUserDialog(title=_(u"User details"), users=users)
        if dlg.get_response() == widgetUtils.OK:
            user.profileController(session=self.session, user=dlg.get_user())
        if hasattr(dlg, "destroy"): dlg.destroy()

    def get_quoted_tweet(self, tweet):
        quoted_tweet = self.session.twitter.get_status(id=tweet.id)
        quoted_tweet.text = utils.find_urls_in_text(quoted_tweet.text, quoted_tweet.entities)
        l = tweets.is_long(quoted_tweet)
        id = tweets.get_id(l)
        original_tweet = self.session.twitter.get_status(id=id)
        original_tweet.text = utils.find_urls_in_text(original_tweet.text, original_tweet.entities)
        return compose.compose_quoted_tweet(quoted_tweet, original_tweet, self.session.db, self.session.settings["general"]["relative_times"])

    def get_item_url(self):
        tweet = self.get_tweet()
        url = "https://twitter.com/{screen_name}/status/{tweet_id}".format(screen_name=self.session.get_user(tweet.user).screen_name, tweet_id=tweet.id)
        return url

    def open_in_browser(self, *args, **kwargs):
        url = self.get_item_url()
        output.speak(_(u"Opening item in web browser..."))
        webbrowser.open(url)