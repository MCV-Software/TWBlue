# -*- coding: utf-8 -*-
""" Scanning code for autocompletion feature on TWBlue. This module can retrieve user objects from the selected Twitter account automatically. """
import time
import wx
import widgetUtils
import output
from tweepy.cursor import Cursor
from tweepy.errors import TweepyException
from pubsub import pub
from . import wx_scan
from . import manage
from . import storage

class autocompletionScan(object):
    def __init__(self, config, buffer, window):
        """ Class constructor. This class will take care of scanning the selected Twitter account to populate the database with users automatically upon request.

        :param config: Config for the session that will be scanned in search for users.
        :type config: dict
        :param buffer: home buffer for the focused session.
        :type buffer: controller.buffers.twitter.base.baseBuffer
        :param window: Main Window of TWBlue.
        :type window:wx.Frame
        """
        super(autocompletionScan, self).__init__()
        self.config = config
        self.buffer = buffer
        self.window = window

    def show_dialog(self):
        self.dialog = wx_scan.autocompletionScanDialog()
        self.dialog.set("friends", self.config["mysc"]["save_friends_in_autocompletion_db"])
        self.dialog.set("followers", self.config["mysc"]["save_followers_in_autocompletion_db"])
        if self.dialog.get_response() == widgetUtils.OK:
            confirmation = wx_scan.confirm()
            return confirmation

    def prepare_progress_dialog(self):
        self.progress_dialog = wx_scan.get_progress_dialog(parent=self.dialog)
        # connect method to update progress dialog
        pub.subscribe(self.on_update_progress, "on-update-progress")

    def on_update_progress(self, percent):
        if percent > 100:
            percent = 100
        wx.CallAfter(self.progress_dialog.Update, percent)

    def scan(self):
        """ Attempts to add all users selected by current user to the autocomplete database. """
        ids = []
        self.config["mysc"]["save_friends_in_autocompletion_db"] = self.dialog.get("friends")
        self.config["mysc"]["save_followers_in_autocompletion_db"] = self.dialog.get("followers")
        output.speak(_("Updating database... You can close this window now. A message will tell you when the process finishes."))
        database = storage.storage(self.buffer.session.session_id)
        percent = 0
        # Retrieve ids of all following users
        if self.dialog.get("friends") == True:
            for i in Cursor(self.buffer.session.twitter.get_friend_ids, count=5000).items():
                if str(i) not in ids:
                    ids.append(str(i))
        # same step, but for followers.
        if self.dialog.get("followers") == True:
            try:
                for i in Cursor(self.buffer.session.twitter.get_follower_ids, count=5000).items():
                    if str(i) not in ids:
                        ids.append(str(i))
            except TweepyException:
                wx.CallAfter(wx_scan.show_error)
                return self.done()
        # As next step requires batches of 100s users, let's split our user Ids so we won't break the param rules.
        split_users = [ids[i:i + 100] for i in range(0, len(ids), 100)]
        # store returned users in this list.
        users = []
        for z in split_users:
            if len(z) == 0:
                continue
            try:
                results = selff.buffer.session.twitter.lookup_users(user_id=z)
            except NameError:
                wx.CallAfter(wx_scan.show_error)
                return self.done()
            users.extend(results)
            time.sleep(1)
            percent = percent + (100/len(split_users))
            pub.sendMessage("on-update-progress", percent=percent)
        for user in users:
            database.set_user(user.screen_name, user.name, 1)
        self.done()

    def done(self):
        wx.CallAfter(self.progress_dialog.Destroy)
        wx.CallAfter(self.dialog.Destroy)
        pub.unsubscribe(self.on_update_progress, "on-update-progress")

def execute_at_startup(window, buffer, config):
    database = storage.storage(buffer.session.session_id)
    if config["mysc"]["save_followers_in_autocompletion_db"] == True and config["other_buffers"]["show_followers"] == True:
        buffer = window.search_buffer("followers", config["twitter"]["user_name"])
        for i in buffer.session.db[buffer.name]:
            database.set_user(i.screen_name, i.name, 1)
    else:
        database.remove_by_buffer(1)
    if config["mysc"]["save_friends_in_autocompletion_db"] == True and config["other_buffers"]["show_friends"] == True:
        buffer = window.search_buffer("friends", config["twitter"]["user_name"])
        for i in buffer.session.db[buffer.name]:
            database.set_user(i.screen_name, i.name, 2)
    else:
        database.remove_by_buffer(2)  