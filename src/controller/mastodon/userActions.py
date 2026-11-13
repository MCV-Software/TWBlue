# -*- coding: utf-8 -*-
import logging
import widgetUtils
import output
import wx
from mysc.thread_utils import call_threaded
from wxUI.dialogs.mastodon import userActions as userActionsDialog
from wxUI.dialogs.mastodon import userTimeline as userTimelineDialog
from pubsub import pub
from mastodon import MastodonError, MastodonNotFoundError
#from extra.autocompletionUsers import completion

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
            user = self.session.lookup_account(user)
            return user
        except MastodonError:
            log.exception("Error searching for user %s.".format(user))

class userActions(BasicUserSelector):

    def __init__(self, *args, execute=None, dispatch=None, on_complete=None, **kwargs):
        self.execute = execute or call_threaded
        self.dispatch = dispatch or wx.CallAfter
        self.on_complete = on_complete
        self.started = False
        super(userActions, self).__init__(*args, **kwargs)
        try:
            if self.dialog.get_response() == widgetUtils.OK:
                self.process_action()
        finally:
            self.dialog.Destroy()

    def create_dialog(self, users):
        self.dialog = userActionsDialog.UserActionsDialog(users)
        widgetUtils.connect_event(self.dialog.autocompletion, widgetUtils.BUTTON_PRESSED, self.autocomplete_users)

    def process_action(self):
        action = self.dialog.get_action()
        user = self.dialog.get_user()
        if action in {'unfollow', 'block'}:
            message = (_("Are you sure you want to unfollow @{handle}?") if action == 'unfollow'
                       else _("Are you sure you want to block @{handle}? This will prevent them from interacting with you and hide their content."))
            confirmation = wx.MessageDialog(self.dialog, message.format(handle=user), _("Confirm Action"), wx.YES_NO | wx.ICON_QUESTION)
            try:
                if confirmation.ShowModal() != wx.ID_YES:
                    return
            finally:
                confirmation.Destroy()
        def perform():
            try:
                account = self.session.lookup_account(user)
                if account is None:
                    raise RuntimeError('User not found.')
                self.session.perform_user_action(action, account.id)
            except Exception as error:
                log.exception('Error performing user action')
                if self.on_complete:
                    self.dispatch(self.on_complete, error)
                else:
                    self.dispatch(output.speak, "Error %s" % error, True)
            else:
                if self.on_complete:
                    self.dispatch(self.on_complete, None)
                else:
                    self.dispatch(output.speak, _("Action completed."), True)
        self.started = True
        self.execute(perform)

    def follow(self, user):
        try:
            self.session.perform_user_action("follow", user.id)
        except MastodonError  as err:
            output.speak("Error %s" % (str(err)), True)

    def unfollow(self, user):
        try:
            result = self.session.perform_user_action("unfollow", user.id)
        except MastodonError as err:
            output.speak("Error %s" % (str(err)), True)

    def mute(self, user):
        try:
            id = self.session.perform_user_action("mute", user.id)
        except MastodonError as err:
            output.speak("Error %s" % (str(err)), True)

    def unmute(self, user):
        try:
            id = self.session.perform_user_action("unmute", user.id)
        except MastodonError as err:
            output.speak("Error %s" % (str(err)), True)

    def block(self, user):
        try:
            id = self.session.perform_user_action("block", user.id)
        except MastodonError as err:
            output.speak("Error %s" % (str(err)), True)

    def unblock(self, user):
        try:
            id = self.session.perform_user_action("unblock", user.id)
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
