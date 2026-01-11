# -*- coding: utf-8 -*-
""" Scanning code for autocompletion feature on TWBlue. This module can retrieve user objects from the selected Mastodon account automatically. """
import time
import wx
import widgetUtils
import output
from pubsub import pub
from . import wx_scan
from extra.autocompletionUsers import manage, storage

class autocompletionScan(object):
    def __init__(self, config, buffer, window):
        """ Class constructor. This class will take care of scanning the selected Mastodon account to populate the database with users automatically upon request.

        :param config: Config for the session that will be scanned in search for users.
        :type config: dict
        :param buffer: home buffer for the focused session.
        :type buffer: controller.buffers.mastodon.base.baseBuffer
        :param window: Main Window of TWBlue.
        :type window:wx.Frame
        """
        super(autocompletionScan, self).__init__()
        self.config = config
        self.buffer = buffer
        self.window = window

    def show_dialog(self):
        """ displays a dialog to confirm which buffers should be scanned (followers or following users). """
        self.dialog = wx_scan.autocompletionScanDialog()
        self.dialog.set("friends", self.config["mysc"]["save_friends_in_autocompletion_db"])
        self.dialog.set("followers", self.config["mysc"]["save_followers_in_autocompletion_db"])
        if self.dialog.get_response() == widgetUtils.OK:
            confirmation = wx_scan.confirm()
            return confirmation

    def prepare_progress_dialog(self):
        self.progress_dialog = wx_scan.autocompletionScanProgressDialog()
        # connect method to update progress dialog
        pub.subscribe(self.on_update_progress, "on-update-progress")
        self.progress_dialog.Show()

    def on_update_progress(self):
        wx.CallAfter(self.progress_dialog.progress_bar.Pulse)

    def scan(self):
        """ Attempts to add all users selected by current user to the autocomplete database. """
        self.config["mysc"]["save_friends_in_autocompletion_db"] = self.dialog.get("friends")
        self.config["mysc"]["save_followers_in_autocompletion_db"] = self.dialog.get("followers")
        output.speak(_("Updating database... You can close this window now. A message will tell you when the process finishes."))
        database = storage.storage(self.buffer.session.session_id)
        percent = 0
        users = []
        if self.dialog.get("friends") == True:
            first_page = self.buffer.session.api.account_following(id=self.buffer.session.db["user_id"], limit=80)
            pub.sendMessage("on-update-progress")
            if first_page != None:
                for user in first_page:
                    users.append(user)
            next_page = first_page
            while next_page != None:
                next_page = self.buffer.session.api.fetch_next(next_page)
                pub.sendMessage("on-update-progress")
                if next_page == None:
                    break
                for user in next_page:
                    users.append(user)
        # same step, but for followers.
        if self.dialog.get("followers") == True:
            first_page = self.buffer.session.api.account_followers(id=self.buffer.session.db["user_id"], limit=80)
            pub.sendMessage("on-update-progress")
            if first_page != None:
                for user in first_page:
                    if user not in users:
                        users.append(user)
            next_page = first_page
            while next_page != None:
                next_page = self.buffer.session.api.fetch_next(next_page)
                pub.sendMessage("on-update-progress")
                if next_page == None:
                    break
                for user in next_page:
                    if user not in users:
                        users.append(user)
#            except TweepyException:
#                wx.CallAfter(wx_scan.show_error)
#                return self.done()
        for user in users:
            name = user.display_name if user.display_name != None and user.display_name != "" else user.username
            database.set_user(user.acct, name, 1)
        wx.CallAfter(wx_scan .show_success, len(users))
        self.done()

    def done(self):
        wx.CallAfter(self.progress_dialog.Destroy)
        wx.CallAfter(self.dialog.Destroy)
        pub.unsubscribe(self.on_update_progress, "on-update-progress")

def add_user(session, database, user):
    """ Adds an user to the database. """
    user = session.api.account_lookup(user)
    if user != None:
            name = user.display_name if user.display_name != None and user.display_name != "" else user.username
            database.set_user(user.acct, name, 1)
