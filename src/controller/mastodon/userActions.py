# -*- coding: utf-8 -*-
import logging
import widgetUtils
import output
from wxUI.dialogs.mastodon import userActions as userActionsDialog
from wxUI.dialogs.mastodon import userTimeline as userTimelineDialog
from pubsub import pub
from mastodon import MastodonError, MastodonNotFoundError
from extra.autocompletionUsers import completion

log = logging.getLogger("controller.mastodon.userActions")

class BasicUserSelector(object):
    def __init__(self, session, users=[]):
        super(BasicUserSelector, self).__init__()
        self.session = session
        self.create_dialog(users=users)

    def create_dialog(self, users):
        pass

    def autocomplete_users(self, *args, **kwargs):
        c = completion.autocompletionUsers(self.dialog, self.session.session_id)
        c.show_menu("dm")

    def search_user(self, user):
        try:
            users = self.session.api.account_search(user)
            if len(users) > 0:
                return users[0]
        except MastodonError:
            log.exception("Error searching for user %s.".format(user))

class userActions(BasicUserSelector):

    def __init__(self, *args, **kwargs):
        super(userActions, self).__init__(*args, **kwargs)
        if self.dialog.get_response() == widgetUtils.OK:
            self.process_action()

    def create_dialog(self, users):
        self.dialog = userActionsDialog.UserActionsDialog(users)
        widgetUtils.connect_event(self.dialog.autocompletion, widgetUtils.BUTTON_PRESSED, self.autocomplete_users)

    def process_action(self):
        action = self.dialog.get_action()
        user = self.dialog.get_user()
        user = self.search_user(user)
        if user == None:
            return
        getattr(self, action)(user)

    def follow(self, user):
        try:
            self.session.api.account_follow(user.id)
        except MastodonError  as err:
            output.speak("Error %s" % (str(err)), True)

    def unfollow(self, user):
        try:
            result = self.session.api.account_unfollow(user.id)
        except MastodonError as err:
            output.speak("Error %s" % (str(err)), True)

    def mute(self, user):
        try:
            id = self.session.api.account_mute(user.id)
        except MastodonError as err:
            output.speak("Error %s" % (str(err)), True)

    def unmute(self, user):
        try:
            id = self.session.api.account_unmute(user.id)
        except MastodonError as err:
            output.speak("Error %s" % (str(err)), True)

    def block(self, user):
        try:
            id = self.session.api.account_block(user.id)
        except MastodonError as err:
            output.speak("Error %s" % (str(err)), True)

    def unblock(self, user):
        try:
            id = self.session.api.account_unblock(user.id)
        except MastodonError as err:
            output.speak("Error %s" % (str(err)), True)

class UserTimeline(BasicUserSelector):

    def create_dialog(self, users):
        self.dialog = userTimelineDialog.UserTimeline(users)
        widgetUtils.connect_event(self.dialog.autocompletion, widgetUtils.BUTTON_PRESSED, self.autocomplete_users)

    def process_action(self):
        action = self.dialog.get_action()
        user = self.dialog.get_user()
        user = self.search_user(user)
        if user == None:
            return
        self.user = user
        return action