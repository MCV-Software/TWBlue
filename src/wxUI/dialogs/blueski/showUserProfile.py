# -*- coding: utf-8 -*-
import wx
import logging
import languageHandler
import builtins
from threading import Thread
from pubsub import pub

from mysc.image_utils import load_scaled_image
from controller.blueski.profile import ProfileController
from controller.blueski.profile_format import format_profile

_ = getattr(builtins, "_", lambda s: s)

logger = logging.getLogger(__name__)


def returnTrue():
    return True

class ShowUserProfileDialog(wx.Dialog):
    def __init__(self, parent, session, user_identifier: str): # user_identifier can be DID or handle
        super(ShowUserProfileDialog, self).__init__(parent, title=_("User Profile"), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        self.session = session
        self.user_identifier = user_identifier
        self._action_busy = False
        self.profile_data = None # Will store the formatted profile dict
        self.target_user_did = None # Will store the resolved DID of the profile being viewed

        self._init_ui()
        self.SetMinSize((400, 300))
        self.CentreOnParent()

        self.profile_controller = ProfileController(
            session, self,
            execute=lambda query: Thread(target=query, daemon=True).start(),
            dispatch=wx.CallAfter,
        )
        self.Bind(wx.EVT_WINDOW_DESTROY, self._on_profile_destroy)
        self.load_profile_data()

    def _init_ui(self):
        self.panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Profile Info Section (StaticTexts for labels and values)
        self.info_grid_sizer = wx.FlexGridSizer(cols=2, vgap=5, hgap=5)
        self.info_grid_sizer.AddGrowableCol(1, 1)

        # Basic text fields (name, handle, bio)
        fields = [
            (_("&Name:"), "displayName"), (_("&Handle:"), "handle"),
            (_("&Bio:"), "description")
        ]
        self.profile_field_ctrls = {}

        for label_text, data_key in fields:
            lbl = wx.StaticText(self.panel, label=label_text)
            style = wx.TE_READONLY | wx.TE_PROCESS_TAB
            if data_key == "description":
                style |= wx.TE_MULTILINE
            else:
                style |= wx.BORDER_NONE
            val_ctrl = wx.TextCtrl(self.panel, style=style)
            if data_key != "description":
                val_ctrl.SetBackgroundColour(self.panel.GetBackgroundColour())
            val_ctrl.AcceptsFocusFromKeyboard = returnTrue

            self.info_grid_sizer.Add(lbl, 0, wx.ALIGN_RIGHT | wx.ALIGN_TOP | wx.ALL, 2)
            self.info_grid_sizer.Add(val_ctrl, 1, wx.EXPAND | wx.ALL, 2)
            self.profile_field_ctrls[data_key] = val_ctrl

        # Banner image
        bannerLabel = wx.StaticText(self.panel, label=_("Banner:"))
        self.bannerImage = wx.StaticBitmap(self.panel)
        self.bannerImage.AcceptsFocusFromKeyboard = returnTrue
        self.info_grid_sizer.Add(bannerLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_TOP | wx.ALL, 2)
        self.info_grid_sizer.Add(self.bannerImage, 0, wx.ALL, 2)

        # Avatar image
        avatarLabel = wx.StaticText(self.panel, label=_("Avatar:"))
        self.avatarImage = wx.StaticBitmap(self.panel)
        self.avatarImage.AcceptsFocusFromKeyboard = returnTrue
        self.info_grid_sizer.Add(avatarLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_TOP | wx.ALL, 2)
        self.info_grid_sizer.Add(self.avatarImage, 0, wx.ALL, 2)

        main_sizer.Add(self.info_grid_sizer, 1, wx.EXPAND | wx.ALL, 10)

        # Timeline buttons (like Mastodon - with counters)
        timeline_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.posts_btn = wx.Button(self.panel, label=_("0 pos&ts"))
        self.posts_btn.Bind(wx.EVT_BUTTON, self.onPosts)
        timeline_sizer.Add(self.posts_btn, 0, wx.ALL, 3)

        self.following_btn = wx.Button(self.panel, label=_("0 &following"))
        self.following_btn.Bind(wx.EVT_BUTTON, self.onFollowing)
        timeline_sizer.Add(self.following_btn, 0, wx.ALL, 3)

        self.followers_btn = wx.Button(self.panel, label=_("0 fo&llowers"))
        self.followers_btn.Bind(wx.EVT_BUTTON, self.onFollowers)
        timeline_sizer.Add(self.followers_btn, 0, wx.ALL, 3)

        main_sizer.Add(timeline_sizer, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 5)

        # Action Buttons
        actions_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.follow_btn = wx.Button(self.panel, label=_("&Follow"))
        self.unfollow_btn = wx.Button(self.panel, label=_("U&nfollow"))
        self.mute_btn = wx.Button(self.panel, label=_("&Mute"))
        self.unmute_btn = wx.Button(self.panel, label=_("Unmu&te"))
        self.block_btn = wx.Button(self.panel, label=_("&Block"))
        self.unblock_btn = wx.Button(self.panel, label=_("Unbl&ock"))

        self.follow_btn.Bind(wx.EVT_BUTTON, lambda evt, cmd="follow_user": self.on_user_action(evt, cmd))
        self.unfollow_btn.Bind(wx.EVT_BUTTON, lambda evt, cmd="unfollow_user": self.on_user_action(evt, cmd))
        self.mute_btn.Bind(wx.EVT_BUTTON, lambda evt, cmd="mute_user": self.on_user_action(evt, cmd))
        self.unmute_btn.Bind(wx.EVT_BUTTON, lambda evt, cmd="unmute_user": self.on_user_action(evt, cmd))
        self.block_btn.Bind(wx.EVT_BUTTON, lambda evt, cmd="block_user": self.on_user_action(evt, cmd))
        self.unblock_btn.Bind(wx.EVT_BUTTON, lambda evt, cmd="unblock_user": self.on_user_action(evt, cmd))

        actions_sizer.Add(self.follow_btn, 0, wx.ALL, 3)
        actions_sizer.Add(self.unfollow_btn, 0, wx.ALL, 3)
        actions_sizer.Add(self.mute_btn, 0, wx.ALL, 3)
        actions_sizer.Add(self.unmute_btn, 0, wx.ALL, 3)
        actions_sizer.Add(self.block_btn, 0, wx.ALL, 3)
        actions_sizer.Add(self.unblock_btn, 0, wx.ALL, 3)
        main_sizer.Add(actions_sizer, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 10)

        # Close Button
        close_btn = wx.Button(self.panel, wx.ID_CANCEL, _("&Close"))
        close_btn.SetDefault()
        main_sizer.Add(close_btn, 0, wx.ALIGN_RIGHT | wx.ALL, 10)
        self.SetEscapeId(close_btn.GetId())

        self.panel.SetSizer(main_sizer)
        self.Fit()

    def Destroy(self):
        # wx may defer destruction until idle; invalidate callbacks immediately.
        self.profile_controller.close()
        if self._action_busy:
            wx.EndBusyCursor()
            self._action_busy = False
        return super().Destroy()

    def _on_profile_destroy(self, event):
        if event.GetEventObject() is self:
            self.profile_controller.close()
            if self._action_busy:
                wx.EndBusyCursor()
                self._action_busy = False
        event.Skip()

    def load_profile_data(self):
        # Preserve the existing entry point; the controller schedules the query.
        self.profile_controller.load(self.user_identifier)

    def show_profile_loading(self):
        self.SetStatusText(_("Loading profile..."))
        for ctrl in self.profile_field_ctrls.values():
            ctrl.SetValue(_("Loading..."))
        for button in (self.follow_btn, self.unfollow_btn, self.mute_btn,
                       self.unmute_btn, self.block_btn, self.unblock_btn):
            button.Hide()

    def _apply_profile_data(self, raw_profile):
        if raw_profile:
            self.profile_data = raw_profile
            self.target_user_did = self.profile_data.get("did")
            self.user_identifier = self.target_user_did or self.user_identifier

            self.update_ui_fields()
            self.SetTitle(_("Profile: {handle}").format(handle=self.profile_data.get("handle", "")))
            self.SetStatusText(_("Profile loaded."))
        else:
            for ctrl in self.profile_field_ctrls.values():
                ctrl.SetValue(_("Not found."))
            self.SetStatusText(_("Profile not found for '{ident}'.").format(ident=self.user_identifier))
            wx.MessageBox(_("User profile for '{ident}' not found.").format(ident=self.user_identifier), _("Error"), wx.OK | wx.ICON_ERROR, self)
        self.Layout()

    def _apply_profile_error(self, err):
        for ctrl in self.profile_field_ctrls.values():
            ctrl.SetValue(_("Error loading."))
        self.SetStatusText(_("Error loading profile."))
        wx.MessageBox(_("Error loading profile: {error}").format(error=str(err)), _("Error"), wx.OK | wx.ICON_ERROR, self)
        self.Layout()

    def update_ui_fields(self):
        if not self.profile_data:
            return

        for key, ctrl in self.profile_field_ctrls.items():
            value = self.profile_data.get(key)
            if key == "description" and value:
                ctrl.SetMinSize((-1, 60))

            if isinstance(value, (int, float)):
                ctrl.SetValue(str(value))
            else:
                ctrl.SetValue(value or _("N/A"))

        # Update timeline buttons with counts
        posts_count = self.profile_data.get("postsCount") or 0
        followers_count = self.profile_data.get("followersCount") or 0
        following_count = self.profile_data.get("followsCount") or 0

        self.posts_btn.SetLabel(_("{count} pos&ts. Click to open posts timeline").format(count=posts_count))
        self.followers_btn.SetLabel(_("{count} fo&llowers. Click to open followers timeline").format(count=followers_count))
        self.following_btn.SetLabel(_("{count} &following. Click to open following timeline").format(count=following_count))

        # Start image download in background thread
        self._download_images()
        self.Layout()

    def _download_images(self):
        data = self.profile_data or {}
        self.profile_controller.load_images(data.get("banner"), data.get("avatar"))

    def _draw_images(self, banner_bytes, avatar_bytes):
        """Draws downloaded images on the bitmap controls."""
        try:
            if banner_bytes:
                banner_image = load_scaled_image(banner_bytes, 300, 100)
                if banner_image is not None:
                    self.bannerImage.SetBitmap(banner_image.ConvertToBitmap())

            if avatar_bytes:
                avatar_image = load_scaled_image(avatar_bytes, 150, 150)
                if avatar_image is not None:
                    self.avatarImage.SetBitmap(avatar_image.ConvertToBitmap())

            self.Layout()
            self.Fit()
        except Exception as e:
            logger.debug(f"Failed to draw images: {e}")

    def onPosts(self, *args):
        """Open this user's posts timeline."""
        if self.profile_data:
            pub.sendMessage('execute-action', action='openPostTimeline', kwargs=dict(user=self.profile_data))

    def onFollowing(self, *args):
        """Open following timeline for this user."""
        if self.profile_data:
            pub.sendMessage('execute-action', action='openFollowingTimeline', kwargs=dict(user=self.profile_data))

    def onFollowers(self, *args):
        """Open followers timeline for this user."""
        if self.profile_data:
            pub.sendMessage('execute-action', action='openFollowersTimeline', kwargs=dict(user=self.profile_data))

    def update_action_buttons_state(self):
        actions = self.profile_controller.available_actions(self.profile_data)
        self.show_profile_actions(actions)

    def show_profile_actions(self, actions):
        for command, button in {
            "follow_user": self.follow_btn, "unfollow_user": self.unfollow_btn,
            "mute_user": self.mute_btn, "unmute_user": self.unmute_btn,
            "block_user": self.block_btn, "unblock_user": self.unblock_btn,
        }.items():
            button.Show(command in actions)
        self.Layout()

    def on_user_action(self, event, command: str):
        if not self.target_user_did: # Should be set by load_profile_data
            wx.MessageBox(_("User identifier (DID) not available for this action."), _("Error"), wx.OK | wx.ICON_ERROR)
            return

        # Confirmation for sensitive actions
        confirmation_map = {
            "unfollow_user": _("Are you sure you want to unfollow @{handle}?").format(handle=self.profile_data.get("handle","this user")),
            "block_user": _("Are you sure you want to block @{handle}? This will prevent them from interacting with you and hide their content.").format(handle=self.profile_data.get("handle","this user")),
            # Unblock usually doesn't need confirmation, but can be added if desired.
        }
        if command in confirmation_map:
            dlg = wx.MessageDialog(self, confirmation_map[command], _("Confirm Action"), wx.YES_NO | wx.ICON_QUESTION)
            if dlg.ShowModal() != wx.ID_YES:
                dlg.Destroy()
                return
            dlg.Destroy()

        self.profile_controller.act(
            command, self.target_user_did, dict(self.profile_data.get("viewer", {})),
            self.user_identifier,
        )

    def show_action_loading(self, command):
        self._action_busy = True
        wx.BeginBusyCursor()
        self.SetStatusText(_("Performing action: {action}...").format(action=command))
        for button in (self.follow_btn, self.unfollow_btn, self.mute_btn,
                       self.unmute_btn, self.block_btn, self.unblock_btn):
            button.Disable()

    def finish_user_action(self, error):
        if self._action_busy:
            wx.EndBusyCursor()
            self._action_busy = False
        for button in (self.follow_btn, self.unfollow_btn, self.mute_btn,
                       self.unmute_btn, self.block_btn, self.unblock_btn):
            button.Enable()
        if error is None:
            wx.MessageBox(_("Action completed."), _("Success"), wx.OK | wx.ICON_INFORMATION, self)
        else:
            self.SetStatusText(_("Action failed."))
            wx.MessageBox(_(str(error)), _("Error"), wx.OK | wx.ICON_ERROR, self)

    def _get_own_did(self):
        return self.profile_controller.own_did()

    def _format_profile_data(self, profile_model):
        # Compatibility entry point; formatting is independent of wx.
        return format_profile(profile_model)

    def SetStatusText(self, text): # Simple status text for dialog title
        self.SetTitle(f"{_('User Profile')} - {text}")

