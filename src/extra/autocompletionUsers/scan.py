# -*- coding: utf-8 -*-
import time
import widgetUtils
import output
from tweepy.cursor import Cursor
from tweepy.errors import TweepyException
from pubsub import pub
from . import wx_scan
from . import manage
from . import storage
from mysc.thread_utils import call_threaded

class autocompletionScan(object):
    def __init__(self, config, buffer, window):
        super(autocompletionScan, self).__init__()
        self.config = config
        self.buffer = buffer
        self.window = window
        self.dialog = wx_scan.autocompletionScanDialog()
        self.dialog.set("friends", self.config["mysc"]["save_friends_in_autocompletion_db"])
        self.dialog.set("followers", self.config["mysc"]["save_followers_in_autocompletion_db"])
        if self.dialog.get_response() == widgetUtils.OK:
            confirmation = wx_scan.confirm()
            if confirmation == True:
                self.progress_dialog = wx_scan.get_progress_dialog()
                call_threaded(self.scan)
        # connect method to update progress dialog
        pub.subscribe(self.on_update_progress, "on-update-progress")

    def on_update_progress(self, percent):
        print(percent)
        if percent > 100:
            percent = 100
        self.progress_dialog.Update(percent)

    def scan(self):
        """ Attempts to add all users selected by current user to the autocomplete database. """
        ids = []
        self.config["mysc"]["save_friends_in_autocompletion_db"] = self.dialog.get("friends")
        self.config["mysc"]["save_followers_in_autocompletion_db"] = self.dialog.get("followers")
        output.speak(_("Updating database... You can close this window now. A message will tell you when the process finishes."))
        database = storage.storage(self.buffer.session.session_id)
        total_steps = 0
        if self.dialog.get("friends") == True:
            total_steps = total_steps + 2
        if self.dialog.get("followers") == True:
            total_steps = total_steps + 2
        max_per_stage = 100/total_steps
        percent = 0
        # Retrieve ids of all following users
        if self.dialog.get("friends") == True:
            for i in Cursor(self.buffer.session.twitter.get_friend_ids, count=5000).items():
                if str(i) not in ids:
                    ids.append(str(i))
            percent = percent + (100*max_per_stage/100)
            pub.sendMessage("on-update-progress", percent=percent)
        # same step, but for followers.
        if self.dialog.get("followers") == True:
            for i in Cursor(self.buffer.session.twitter.get_follower_ids, count=5000).items():
                if str(i) not in ids:
                    ids.append(str(i))
            percent = percent + (100*max_per_stage/100)
            pub.sendMessage("on-update-progress", percent=percent)
        # As next step requires batches of 100s users, let's split our user Ids so we won't break the param rules.
        split_users = [ids[i:i + 100] for i in range(0, len(ids), 100)]
        # store returned users in this list.
        users = []
        for z in split_users:
            if len(z) == 0:
                print("Invalid user count")
                continue
            print(len(z))
            results = self.buffer.session.twitter.lookup_users(user_id=z)
            users.extend(results)
            time.sleep(1)
            percent = percent + (max_per_stage/len(split_users))
            pub.sendMessage("on-update-progress", percent=percent)
        for user in users:
            database.set_user(user.screen_name, user.name, 1)
        self.progress_dialog.Destroy()
        wx_scan.show_success_dialog()
        self.dialog.Destroy()

    def add_users_to_database(self):
        self.config["mysc"]["save_friends_in_autocompletion_db"] = self.dialog.get("friends_buffer")
        self.config["mysc"]["save_followers_in_autocompletion_db"] = self.dialog.get("followers_buffer")
        output.speak(_(u"Updating database... You can close this window now. A message will tell you when the process finishes."))
        database = storage.storage(self.buffer.session.session_id)
        if self.dialog.get("followers_buffer") == True:
            buffer = self.window.search_buffer("followers", self.config["twitter"]["user_name"])
            for i in buffer.session.db[buffer.name]:
                database.set_user(i.screen_name, i.name, 1)
        else:
            database.remove_by_buffer(1)
        if self.dialog.get("friends_buffer") == True:
            buffer = self.window.search_buffer("friends", self.config["twitter"]["user_name"])
            for i in buffer.session.db[buffer.name]:
                database.set_user(i.screen_name, i.name, 2)
        else:
            database.remove_by_buffer(2)
        wx_settings.show_success_dialog()
        self.dialog.destroy()

    def view_list(self, ev):
        q = manage.autocompletionManager(self.buffer.session)
        q.show_settings()

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

    def __del__(self):
        pub.unsubscribe(self.on_update_progress, "on-update-progress")