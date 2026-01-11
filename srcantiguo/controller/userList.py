# -*- coding: utf-8 -*-
import widgetUtils
from pubsub import pub
from wxUI.dialogs import userList

class UserListController(object):
    def __init__(self, users, session, title):
        super(UserListController, self).__init__()
        self.session = session
        self.users = self.process_users(users)
        self.dialog = userList.UserListDialog(title=title, users=[user.get("display_name", user.get("acct")) for user in self.users])
        widgetUtils.connect_event(self.dialog.actions_button, widgetUtils.BUTTON_PRESSED, self.on_actions)
        widgetUtils.connect_event(self.dialog.details_button, widgetUtils.BUTTON_PRESSED, self.on_details)
        self.dialog.ShowModal()

    def process_users(self, users):
        return {}

    def on_actions(self):
        pass

    def on_details(self, *args, **kwargs):
        pass