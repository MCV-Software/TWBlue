# -*- coding: utf-8 -*-
import logging
import widgetUtils
import output
from wxUI.dialogs.blueski import userActions as userActionsDialog
from extra.autocompletionUsers import completion
import languageHandler

log = logging.getLogger("controller.blueski.userActions")


class BasicUserSelector(object):
    def __init__(self, session, users=None):
        super(BasicUserSelector, self).__init__()
        self.session = session
        self.create_dialog(users=users or [])

    def create_dialog(self, users):
        pass

    def resolve_profile(self, actor):
        try:
            return self.session.get_profile(actor)
        except Exception:
            log.exception("Error resolving Bluesky profile for %s.", actor)
            return None

    def autocomplete_users(self, *args, **kwargs):
        c = completion.autocompletionUsers(self.dialog, self.session.session_id)
        c.show_menu("free")


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
        actor = self.dialog.get_user().strip()
        if not actor:
            output.speak(_("No user specified."), True)
            return

        profile = self.resolve_profile(actor)
        if not profile:
            output.speak(_("User not found."), True)
            return

        def g(obj, key, default=None):
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)

        did = g(profile, "did")
        viewer = g(profile, "viewer") or {}

        if not did:
            output.speak(_("User identifier not available."), True)
            return

        if action == "follow":
            if self.session.follow_user(did):
                output.speak(_("Followed."))
            else:
                output.speak(_("Failed to follow user."), True)
        elif action == "unfollow":
            follow_uri = g(viewer, "following")
            if not follow_uri:
                output.speak(_("Follow information not available."), True)
                return
            if self.session.unfollow_user(follow_uri):
                output.speak(_("Unfollowed."))
            else:
                output.speak(_("Failed to unfollow user."), True)
        elif action == "mute":
            if self.session.mute_user(did):
                output.speak(_("Muted."))
            else:
                output.speak(_("Failed to mute user."), True)
        elif action == "unmute":
            if self.session.unmute_user(did):
                output.speak(_("Unmuted."))
            else:
                output.speak(_("Failed to unmute user."), True)
        elif action == "block":
            if self.session.block_user(did):
                output.speak(_("Blocked."))
            else:
                output.speak(_("Failed to block user."), True)
        elif action == "unblock":
            block_uri = g(viewer, "blocking")
            if not block_uri:
                output.speak(_("Block information not available."), True)
                return
            if self.session.unblock_user(block_uri):
                output.speak(_("Unblocked."))
            else:
                output.speak(_("Failed to unblock user."), True)
