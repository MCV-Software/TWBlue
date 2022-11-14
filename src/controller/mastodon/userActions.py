# -*- coding: utf-8 -*-
import logging
import widgetUtils
import output
from wxUI.dialogs.mastodon import userActions
from pubsub import pub
from mastodon import MastodonError, MastodonNotFoundError
from extra.autocompletionUsers import completion

log = logging.getLogger("controller.mastodon.userActions")

class userActionsController(object):
    def __init__(self, session, users=[], default="follow"):
        super(userActionsController, self).__init__()
        self.session = session
        self.dialog = userActions.UserActionsDialog(users, default)
        widgetUtils.connect_event(self.dialog.autocompletion, widgetUtils.BUTTON_PRESSED, self.autocomplete_users)
        if self.dialog.get_response() == widgetUtils.OK:
            self.process_action()

    def autocomplete_users(self, *args, **kwargs):
        c = completion.autocompletionUsers(self.dialog, self.session.session_id)
        c.show_menu("dm")

    def process_action(self):
        action = self.dialog.get_action()
        user = self.dialog.get_user()
        user = self.search_user(user)
        if user == None:
            return
        getattr(self, action)(user)

    def search_user(self, user):
        try:
            users = self.session.api.account_search(user)
            if len(users) > 0:
                return users[0]
        except MastodonError:
            log.exception("Error searching for user %s.".format(user))

    def follow(self, user):
        try:
            self.session.api.account_follow(user.id)
            pub.sendMessage("restartStreaming", session=self.session.session_id)
        except MastodonError  as err:
            output.speak("Error %s" % (str(err)), True)

    def unfollow(self, user):
        try:
            result = self.session.api.account_unfollow(user.id)
            pub.sendMessage("restartStreaming", session=self.session.session_id)
        except MastodonError as err:
            output.speak("Error %s" % (str(err)), True)

    def mute(self, user):
        try:
            id = self.session.api.account_mute(user.id)
            pub.sendMessage("restartStreaming", session=self.session.session_id)
        except MastodonError as err:
            output.speak("Error %s" % (str(err)), True)

    def unmute(self, user):
        try:
            id = self.session.api.account_unmute(user.id)
            pub.sendMessage("restartStreaming", session=self.session.session_id)
        except MastodonError as err:
            output.speak("Error %s" % (str(err)), True)

    def block(self, user):
        try:
            id = self.session.api.account_block(user.id)
            pub.sendMessage("restartStreaming", session=self.session.session_id)
        except MastodonError as err:
            output.speak("Error %s" % (str(err)), True)

    def unblock(self, user):
        try:
            id = self.session.api.account_unblock(user.id)
        except MastodonError as err:
            output.speak("Error %s" % (str(err)), True)
