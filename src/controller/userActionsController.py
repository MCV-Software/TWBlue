# -*- coding: utf-8 -*-
import widgetUtils
import output
from wxUI.dialogs import userActions
from pubsub import pub
from tweepy.errors  import TweepyException
from extra import autocompletionUsers

class userActionsController(object):
    def __init__(self, buffer, users=[], default="follow"):
        super(userActionsController, self).__init__()
        self.buffer = buffer
        self.session = buffer.session
        self.dialog = userActions.UserActionsDialog(users, default)
        widgetUtils.connect_event(self.dialog.autocompletion, widgetUtils.BUTTON_PRESSED, self.autocomplete_users)
        if self.dialog.get_response() == widgetUtils.OK:
            self.process_action()

    def autocomplete_users(self, *args, **kwargs):
        c = autocompletionUsers.completion.autocompletionUsers(self.dialog, self.session.session_id)
        c.show_menu("dm")

    def process_action(self):
        action = self.dialog.get_action()
        user = self.dialog.get_user()
        if user == "": return
        getattr(self, action)(user)

    def follow(self, user):
        try:
            self.session.twitter.create_friendship(screen_name=user )
        except TweepyException  as err:
            output.speak("Error %s" % (str(err)), True)

    def unfollow(self, user):
        try:
            id = self.session.twitter.destroy_friendship(screen_name=user )
        except TweepyException as err:
            output.speak("Error %s" % (str(err)), True)

    def mute(self, user):
        try:
            id = self.session.twitter.create_mute(screen_name=user )
        except TweepyException as err:
            output.speak("Error %s" % (str(err)), True)

    def unmute(self, user):
        try:
            id = self.session.twitter.destroy_mute(screen_name=user )
        except TweepyException as err:
            output.speak("Error %s" % (str(err)), True)

    def report(self, user):
        try:
            id = self.session.twitter.report_spam(screen_name=user )
        except TweepyException as err:
            output.speak("Error %s" % (str(err)), True)

    def block(self, user):
        try:
            id = self.session.twitter.create_block(screen_name=user )
        except TweepyException as err:
            output.speak("Error %s" % (str(err)), True)

    def unblock(self, user):
        try:
            id = self.session.twitter.destroy_block(screen_name=user )
        except TweepyException as err:
            output.speak("Error %s" % (str(err)), True)

    def ignore_client(self, user):
        tweet = self.buffer.get_right_tweet()
        if hasattr(tweet, "sender"):
            output.speak(_(u"You can't ignore direct messages"))
            return
        client = tweet.source
        if client not in self.session.settings["twitter"]["ignored_clients"]:
            self.session.settings["twitter"]["ignored_clients"].append(client)
            self.session.settings.write()
