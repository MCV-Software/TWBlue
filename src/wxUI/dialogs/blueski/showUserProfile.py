# -*- coding: utf-8 -*-
import wx
import logging
import languageHandler
import builtins
import requests
from io import BytesIO
from threading import Thread
from pubsub import pub

_ = getattr(builtins, "_", lambda s: s)

logger = logging.getLogger(__name__)


def returnTrue():
    return True

class ShowUserProfileDialog(wx.Dialog):
    def __init__(self, parent, session, user_identifier: str): # user_identifier can be DID or handle
        super(ShowUserProfileDialog, self).__init__(parent, title=_("User Profile"), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        self.session = session
        self.user_identifier = user_identifier
        self.profile_data = None # Will store the formatted profile dict
        self.target_user_did = None # Will store the resolved DID of the profile being viewed

        self._init_ui()
        self.SetMinSize((400, 300))
        self.CentreOnParent()

        Thread(target=self.load_profile_data, daemon=True).start()

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

    def load_profile_data(self):
        wx.CallAfter(self.SetStatusText, _("Loading profile..."))
        for ctrl in self.profile_field_ctrls.values():
            wx.CallAfter(ctrl.SetValue, _("Loading..."))

        # Initially hide all action buttons until state is known
        wx.CallAfter(self.follow_btn.Hide)
        wx.CallAfter(self.unfollow_btn.Hide)
        wx.CallAfter(self.mute_btn.Hide)
        wx.CallAfter(self.unmute_btn.Hide)
        wx.CallAfter(self.block_btn.Hide)
        wx.CallAfter(self.unblock_btn.Hide)

        try:
            api = self.session._ensure_client()
            try:
                raw_profile = api.app.bsky.actor.get_profile({"actor": self.user_identifier})
            except Exception:
                raw_profile = None
            wx.CallAfter(self._apply_profile_data, raw_profile)

        except Exception as e:
            logger.error(f"Error loading profile for {self.user_identifier}: {e}", exc_info=True)
            wx.CallAfter(self._apply_profile_error, e)

    def _apply_profile_data(self, raw_profile):
        if raw_profile:
            self.profile_data = self._format_profile_data(raw_profile)
            self.target_user_did = self.profile_data.get("did")
            self.user_identifier = self.target_user_did or self.user_identifier

            self.update_ui_fields()
            self.update_action_buttons_state()
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
        Thread(target=self._download_images, daemon=True).start()
        self.Layout()

    def _download_images(self):
        """Downloads avatar and banner images from Bluesky server."""
        avatar_url = self.profile_data.get("avatar") if self.profile_data else None
        banner_url = self.profile_data.get("banner") if self.profile_data else None

        avatar_bytes = None
        banner_bytes = None

        try:
            if banner_url:
                resp = requests.get(banner_url, timeout=10)
                if resp.status_code == 200:
                    banner_bytes = resp.content
        except Exception as e:
            logger.debug(f"Failed to download banner: {e}")

        try:
            if avatar_url:
                resp = requests.get(avatar_url, timeout=10)
                if resp.status_code == 200:
                    avatar_bytes = resp.content
        except Exception as e:
            logger.debug(f"Failed to download avatar: {e}")

        wx.CallAfter(self._draw_images, banner_bytes, avatar_bytes)

    def _draw_images(self, banner_bytes, avatar_bytes):
        """Draws downloaded images on the bitmap controls."""
        try:
            if banner_bytes:
                banner_image = wx.Image(BytesIO(banner_bytes), wx.BITMAP_TYPE_ANY)
                banner_image.Rescale(300, 100, wx.IMAGE_QUALITY_HIGH)
                self.bannerImage.SetBitmap(banner_image.ConvertToBitmap())

            if avatar_bytes:
                avatar_image = wx.Image(BytesIO(avatar_bytes), wx.BITMAP_TYPE_ANY)
                avatar_image.Rescale(150, 150, wx.IMAGE_QUALITY_HIGH)
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
        if not self.profile_data or not self.target_user_did or self.target_user_did == self._get_own_did():
            self.follow_btn.Hide()
            self.unfollow_btn.Hide()
            self.mute_btn.Hide()
            self.unmute_btn.Hide()
            self.block_btn.Hide()
            self.unblock_btn.Hide()
            self.Layout()
            return

        viewer_state = self.profile_data.get("viewer", {})
        is_following = bool(viewer_state.get("following"))
        is_muted = bool(viewer_state.get("muted"))
        # 'blocking' in viewer state is the URI of *our* block record, if we are blocking them.
        is_blocking_them = bool(viewer_state.get("blocking"))
        # 'blockedBy' means *they* are blocking us. If true, most actions might fail or be hidden.
        is_blocked_by_them = bool(viewer_state.get("blockedBy"))

        if is_blocked_by_them: # If they block us, we can't do much.
            self.follow_btn.Hide()
            self.unfollow_btn.Hide()
            self.mute_btn.Hide()
            self.unmute_btn.Hide()
            # We can still block them, or unblock them if we previously did.
            self.block_btn.Show(not is_blocking_them)
            self.unblock_btn.Show(is_blocking_them)
            self.Layout()
            return

        self.follow_btn.Show(not is_following and not is_blocking_them)
        self.unfollow_btn.Show(is_following and not is_blocking_them)

        self.mute_btn.Show(not is_muted and not is_blocking_them)
        self.unmute_btn.Show(is_muted and not is_blocking_them)

        self.block_btn.Show(not is_blocking_them) # Show block if we are not currently blocking them (even if they block us)
        self.unblock_btn.Show(is_blocking_them)   # Show unblock if we are currently blocking them

        self.Layout() # Refresh sizer to show/hide buttons correctly


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

        wx.BeginBusyCursor()
        self.SetStatusText(_("Performing action: {action}...").format(action=command))
        action_button = event.GetEventObject()
        if action_button:
            action_button.Disable()

        try:
            ok = False
            if command == "follow_user" and hasattr(self.session, "follow_user"):
                ok = self.session.follow_user(self.target_user_did)
            elif command == "unfollow_user" and hasattr(self.session, "unfollow_user"):
                viewer_state = self.profile_data.get("viewer", {}) if self.profile_data else {}
                follow_uri = viewer_state.get("following")
                if follow_uri:
                    ok = self.session.unfollow_user(follow_uri)
                else:
                    raise RuntimeError(_("Follow information not available."))
            elif command == "mute_user" and hasattr(self.session, "mute_user"):
                ok = self.session.mute_user(self.target_user_did)
            elif command == "unmute_user" and hasattr(self.session, "unmute_user"):
                ok = self.session.unmute_user(self.target_user_did)
            elif command == "block_user" and hasattr(self.session, "block_user"):
                ok = self.session.block_user(self.target_user_did)
            elif command == "unblock_user" and hasattr(self.session, "unblock_user"):
                viewer_state = self.profile_data.get("viewer", {}) if self.profile_data else {}
                block_uri = viewer_state.get("blocking")
                if not block_uri:
                    raise RuntimeError(_("Block information not available."))
                ok = self.session.unblock_user(block_uri)
            else:
                raise RuntimeError(_("This action is not supported yet."))

            if not ok:
                raise RuntimeError(_("Action failed."))

            wx.EndBusyCursor()
            wx.MessageBox(_("Action completed."), _("Success"), wx.OK | wx.ICON_INFORMATION, self)
            # Reload profile data in a new thread
            Thread(target=self.load_profile_data, daemon=True).start()
        except Exception as e:
            wx.EndBusyCursor()
            if action_button:
                action_button.Enable()
            self.SetStatusText(_("Action failed."))
            wx.MessageBox(str(e), _("Error"), wx.OK | wx.ICON_ERROR, self)

    def _get_own_did(self):
        if isinstance(self.session.db, dict):
            did = self.session.db.get("user_id")
            if did:
                return did
        try:
            api = self.session._ensure_client()
            if getattr(api, "me", None):
                return api.me.did
        except Exception:
            pass
        return None

    def _format_profile_data(self, profile_model):
        def g(obj, key, default=None):
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)

        def get_count(*keys):
            for k in keys:
                val = g(profile_model, k)
                if val is not None:
                    return val
            return None

        return {
            "did": g(profile_model, "did"),
            "handle": g(profile_model, "handle"),
            "displayName": g(profile_model, "displayName") or g(profile_model, "display_name") or g(profile_model, "handle"),
            "description": g(profile_model, "description"),
            "avatar": g(profile_model, "avatar"),
            "banner": g(profile_model, "banner"),
            "followersCount": get_count("followersCount", "followers_count"),
            "followsCount": get_count("followsCount", "follows_count", "followingCount", "following_count"),
            "postsCount": get_count("postsCount", "posts_count"),
            "viewer": g(profile_model, "viewer") or {},
        }

    def SetStatusText(self, text): # Simple status text for dialog title
        self.SetTitle(f"{_('User Profile')} - {text}")

