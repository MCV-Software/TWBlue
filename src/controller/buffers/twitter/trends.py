# -*- coding: utf-8 -*-
import time
import platform
if platform.system() == "Windows":
    import wx
    from wxUI import buffers, commonMessageDialogs, menus
    from controller import user, messages
elif platform.system() == "Linux":
    from gi.repository import Gtk
    from gtkUI import buffers, commonMessageDialogs
from controller import messages
import widgetUtils
import output
import logging
from mysc.thread_utils import call_threaded
from tweepy.errors import TweepyException
from pubsub import pub
from controller.buffers import base

log = logging.getLogger("controller.buffers.twitter.trends")

class TrendsBuffer(base.Buffer):
    def __init__(self, parent, name, sessionObject, account, trendsFor, *args, **kwargs):
        super(TrendsBuffer, self).__init__(parent=parent, sessionObject=sessionObject)
        self.trendsFor = trendsFor
        self.session = sessionObject
        self.account = account
        self.invisible = True
        self.buffer = buffers.trendsPanel(parent, name)
        self.buffer.account = account
        self.type = self.buffer.type
        self.bind_events()
        self.sound = "trends_updated.ogg"
        self.trends = []
        self.name = name
        self.buffer.name = name
        self.compose_function = self.compose_function_
        self.get_formatted_message = self.get_message
        self.reply = self.search_topic


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

    def start_stream(self, mandatory=False, play_sound=True, avoid_autoreading=False):
        # starts stream every 3 minutes.
        current_time = time.time()
        if self.execution_time == 0 or current_time-self.execution_time >= 180 or mandatory == True:
            self.execution_time = current_time
            try:
                data = self.session.twitter.get_place_trends(id=self.trendsFor)
            except TweepyException as err:
                log.exception("Error %s" % (str(err)))
            if not hasattr(self, "name_"):
                self.name_ = data[0]["locations"][0]["name"]
                pub.sendMessage("buffer-title-changed", buffer=self)
            self.trends = data[0]["trends"]
            self.put_items_on_the_list()
            if self.sound != None and self.session.settings["sound"]["session_mute"] == False and self.name not in self.session.settings["other_buffers"]["muted_buffers"] and play_sound == True:
                self.session.sound.play(self.sound)

    def put_items_on_the_list(self):
        selected_item = self.buffer.list.get_selected()
        self.buffer.list.clear()
        for i in self.trends:
            tweet = self.compose_function(i)
            self.buffer.list.insert_item(False, *tweet)
            self.buffer.set_position(self.session.settings["general"]["reverse_timelines"])

    def compose_function_(self, trend):
        return [trend["name"]]

    def bind_events(self):
        log.debug("Binding events...")
        self.buffer.list.list.Bind(wx.EVT_CHAR_HOOK, self.get_event)
        widgetUtils.connect_event(self.buffer, widgetUtils.BUTTON_PRESSED, self.tweet_about_this_trend, self.buffer.tweetTrendBtn)
        widgetUtils.connect_event(self.buffer, widgetUtils.BUTTON_PRESSED, self.post_status, self.buffer.tweet)
        widgetUtils.connect_event(self.buffer.list.list, wx.EVT_LIST_ITEM_RIGHT_CLICK, self.show_menu)
        widgetUtils.connect_event(self.buffer.list.list, wx.EVT_LIST_KEY_DOWN, self.show_menu_by_key)
        widgetUtils.connect_event(self.buffer, widgetUtils.BUTTON_PRESSED, self.search_topic, self.buffer.search_topic)

    def get_message(self):
        return self.compose_function(self.trends[self.buffer.list.get_selected()])[0]

    def remove_buffer(self, force=False):
        if force == False:
            dlg = commonMessageDialogs.remove_buffer()
        else:
            dlg = widgetUtils.YES
        if dlg == widgetUtils.YES:
            if self.name[:-3] in self.session.settings["other_buffers"]["trending_topic_buffers"]:
                self.session.settings["other_buffers"]["trending_topic_buffers"].remove(self.name[:-3])
                self.session.settings.write()
                if self.name in self.session.db:
                    self.session.db.pop(self.name)
                return True
        elif dlg == widgetUtils.NO:
            return False

    def url(self, *args, **kwargs):
        self.tweet_about_this_trend()

    def search_topic(self, *args, **kwargs):
        topic = self.trends[self.buffer.list.get_selected()]["name"]
        pub.sendMessage("search", term=topic)

    def show_menu(self, ev, pos=0, *args, **kwargs):
        menu = menus.trendsPanelMenu()
        widgetUtils.connect_event(menu, widgetUtils.MENU, self.search_topic, menuitem=menu.search_topic)
        widgetUtils.connect_event(menu, widgetUtils.MENU, self.tweet_about_this_trend, menuitem=menu.tweetThisTrend)
        widgetUtils.connect_event(menu, widgetUtils.MENU, self.view, menuitem=menu.view)
        widgetUtils.connect_event(menu, widgetUtils.MENU, self.copy, menuitem=menu.copy)
        if pos != 0:
            self.buffer.PopupMenu(menu, pos)
        else:
            self.buffer.PopupMenu(menu, ev.GetPosition())

    def view(self, *args, **kwargs):
        pub.sendMessage("execute-action", action="view_item")

    def copy(self, *args, **kwargs):
        pub.sendMessage("execute-action", action="copy_to_clipboard")

    def tweet_about_this_trend(self, *args, **kwargs):
        if self.buffer.list.get_count() == 0: return
        title = _("Tweet")
        caption = _("Write the tweet here")
        tweet = messages.tweet(session=self.session, title=title, caption=caption, text=self.get_message()+ " ")
        tweet.message.SetInsertionPoint(len(tweet.message.GetValue()))
        if tweet.message.ShowModal() == widgetUtils.OK:
            tweet_data = tweet.get_tweet_data()
            call_threaded(self.session.send_tweet, *tweet_data)
        if hasattr(tweet.message, "destroy"): tweet.message.destroy()

    def show_menu_by_key(self, ev):
        if self.buffer.list.get_count() == 0:
            return
        if ev.GetKeyCode() == wx.WXK_WINDOWS_MENU:
            self.show_menu(widgetUtils.MENU, pos=self.buffer.list.list.GetPosition())

    def open_in_browser(self, *args, **kwargs):
        output.speak(_(u"This action is not supported in the buffer, yet."))