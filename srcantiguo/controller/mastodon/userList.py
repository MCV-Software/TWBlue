# -*- coding: utf-8 -*-
from mastodon import MastodonError
from wxUI.dialogs.mastodon import showUserProfile
from controller.userList import UserListController
from . import userActions

class MastodonUserList(UserListController):

    def process_users(self, users):
        return [dict(id=user.id, display_name=f"{user.display_name} (@{user.acct})", acct=user.acct) for user in users]

    def on_actions(self, *args, **kwargs):
        user = self.dialog.user_list.GetSelection()
        user_account = self.users[user]
        u = userActions.userActions(self.session, [user_account.get("acct")])

    def on_details(self, *args, **kwargs):
        user = self.dialog.user_list.GetSelection()
        user_id = self.users[user].get("id")
        try:
            user_object = self.session.api.account(user_id)
        except MastodonError:
            return
        dlg = showUserProfile.ShowUserProfile(user_object)
        dlg.ShowModal()
