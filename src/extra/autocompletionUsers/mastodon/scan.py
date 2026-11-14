# -*- coding: utf-8 -*-
""" Scanning code for autocompletion feature on TWBlue. This module can retrieve user objects from the selected Mastodon account automatically. """
import time
import logging
import wx
import widgetUtils
import output
from enum import Enum
from pubsub import pub
from . import wx_scan
from extra.autocompletionUsers import manage, storage

log = logging.getLogger("extra.autocompletionUsers.mastodon.scan")


class ScanType(Enum):
    """Enum to distinguish between scanning followers or following users."""
    FOLLOWING = "following"
    FOLLOWERS = "followers"


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
        self.progress_dialog = None

    def show_dialog(self):
        """ displays a dialog to confirm which buffers should be scanned (followers or following users). """
        self.dialog = wx_scan.autocompletionScanDialog()
        self.dialog.set("friends", self.config["mysc"]["save_friends_in_autocompletion_db"])
        self.dialog.set("followers", self.config["mysc"]["save_followers_in_autocompletion_db"])
        if self.dialog.get_response() == widgetUtils.OK:
            confirmation = wx_scan.confirm()
            return confirmation

    def get_user_counts(self):
        """Get the followers and following counts from the user's account."""
        try:
            credentials = self.buffer.session.api.account_verify_credentials()
            followers_count = credentials.followers_count if self.dialog.get("followers") else 0
            following_count = credentials.following_count if self.dialog.get("friends") else 0
            return followers_count, following_count
        except Exception as e:
            log.exception(f"Error getting user counts: {e}")
            return 0, 0

    def prepare_progress_dialog(self):
        followers_count, following_count = self.get_user_counts()
        self.progress_dialog = wx_scan.autocompletionScanProgressDialog(
            followers_count=followers_count,
            following_count=following_count
        )
        self.progress_dialog.Show()

    def update_progress(self, current_users, current_page, scanning_type):
        """Update the progress dialog from the worker thread."""
        if self.progress_dialog:
            wx.CallAfter(self.progress_dialog.update_progress, current_users, current_page, scanning_type)

    def is_cancelled(self):
        """Check if the user has requested cancellation."""
        if self.progress_dialog:
            return self.progress_dialog.cancelled
        return False

    def _scan_users(self, scan_type, users_dict):
        """Scan users of the specified type and add them to the users dictionary.
        
        :param scan_type: ScanType.FOLLOWING or ScanType.FOLLOWERS
        :param users_dict: Dictionary to store users, keyed by user ID
        :returns: True if completed, False if cancelled
        """
        # Select the appropriate API method
        if scan_type == ScanType.FOLLOWING:
            api_method = self.buffer.session.api.account_following
        else:
            api_method = self.buffer.session.api.account_followers
        
        log.debug(f"Scanning {scan_type.value}...")
        current_page = 1
        first_page = api_method(id=self.buffer.session.db["user_id"], limit=80)
        self.update_progress(len(users_dict), current_page, scan_type.value)
        
        if first_page != None:
            for user in first_page:
                if user.id not in users_dict:
                    users_dict[user.id] = user
        
        next_page = first_page
        while next_page != None:
            if self.is_cancelled():
                log.info(f"Scan cancelled by user during {scan_type.value} scan.")
                return False
            time.sleep(0.25)  # Small delay to avoid rate limiting
            next_page = self.buffer.session.api.fetch_next(next_page)
            current_page += 1
            self.update_progress(len(users_dict), current_page, scan_type.value)
            if next_page == None:
                break
            for user in next_page:
                if user.id not in users_dict:
                    users_dict[user.id] = user
            log.debug(f"Scanned {len(users_dict)} users so far...")
        
        return True

    def scan(self):
        """ Attempts to add all users selected by current user to the autocomplete database. """
        self.config["mysc"]["save_friends_in_autocompletion_db"] = self.dialog.get("friends")
        self.config["mysc"]["save_followers_in_autocompletion_db"] = self.dialog.get("followers")
        output.speak(_("Scanning account. Please wait or press cancel to stop."))
        database = storage.storage(self.buffer.session.session_id)
        # Use a dictionary keyed by user ID for O(1) lookups instead of O(n) list comparisons
        users_dict = {}
        cancelled = False
        try:
            if self.dialog.get("friends") == True:
                if not self._scan_users(ScanType.FOLLOWING, users_dict):
                    cancelled = True
            if self.dialog.get("followers") == True and not cancelled:
                if not self._scan_users(ScanType.FOLLOWERS, users_dict):
                    cancelled = True
        except Exception as e:
            log.exception(f"Error scanning account: {e}")
            wx.CallAfter(wx_scan.show_error)
            return self.done()
        # Save users to database
        users = list(users_dict.values())
        new_users_count = 0
        if len(users) > 0:
            log.debug(f"Saving {len(users)} users to autocompletion database...")
            wx.CallAfter(self.progress_dialog.set_saving_status)
            for user in users:
                name = user.display_name if user.display_name != None and user.display_name != "" else user.username
                if database.set_user(user.acct, name, 1):
                    new_users_count += 1
        already_existed = len(users) - new_users_count
        if cancelled:
            log.info(f"Scan cancelled. Found {len(users)} users, {new_users_count} new, {already_existed} already in database.")
            wx.CallAfter(wx_scan.show_cancelled, len(users), new_users_count)
        else:
            log.info(f"Successfully imported {new_users_count} new users ({already_existed} already existed).")
            wx.CallAfter(wx_scan.show_success, len(users), new_users_count)
        self.done()

    def done(self):
        wx.CallAfter(self.progress_dialog.Destroy)
        wx.CallAfter(self.dialog.Destroy)

def add_user(session, database, user):
    """ Adds an user to the database. """
    user = session.api.account_lookup(user)
    if user != None:
            name = user.display_name if user.display_name != None and user.display_name != "" else user.username
            database.set_user(user.acct, name, 1)
