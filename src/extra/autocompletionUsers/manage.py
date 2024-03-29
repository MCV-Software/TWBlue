# -*- coding: utf-8 -*-
""" Management of users in the local database for autocompletion. """
import time
import widgetUtils
from wxUI import commonMessageDialogs
from . import storage, wx_manage
from .mastodon import scan as mastodon

class autocompletionManage(object):
    def __init__(self, session):
        """ class constructor. Manages everything related to user autocompletion.

        :param session: Sessiom where the autocompletion management has been requested.
        :type session: sessions.base.Session.
        """
        super(autocompletionManage, self).__init__()
        self.session = session
        # Instantiate database so we can perform modifications on it.
        self.database = storage.storage(self.session.session_id)

    def show_settings(self):
        """ display user management  dialog and connect events associated to it. """
        self.dialog = wx_manage.autocompletionManageDialog()
        self.users = self.database.get_all_users()
        self.dialog.put_users(self.users)
        widgetUtils.connect_event(self.dialog.add, widgetUtils.BUTTON_PRESSED, self.add_user)
        widgetUtils.connect_event(self.dialog.remove, widgetUtils.BUTTON_PRESSED, self.remove_user)
        self.dialog.get_response()

    def update_list(self):
        """ update users list in management dialog. This function is normallhy used after we modify the database in any way, so we can reload all users in the autocompletion user management list. """
        item = self.dialog.users.get_selected()
        self.dialog.users.clear()
        self.users = self.database.get_all_users()
        self.dialog.put_users(self.users)
        self.dialog.users.select_item(item)

    def add_user(self, *args, **kwargs):
        """ Add a new username to the autocompletion database. """
        usr = self.dialog.get_user()
        if usr == False:
            return
        user_added = False
        if self.session.type == "mastodon":
            user_added = mastodon.add_user(session=self.session, database=self.database, user=usr)
        if user_added == False:
            self.dialog.show_invalid_user_error()
            return
        self.update_list()

    def remove_user(self, *args, **kwargs):
        """ Remove focused user from the autocompletion database. """
        if commonMessageDialogs.delete_user_from_db() == widgetUtils.YES:
            item = self.dialog.users.get_selected()
            user = self.users[item]
            self.database.remove_user(user[0])
            self.update_list()
