# -*- coding: utf-8 -*-
"""Wx dialogs for showing a user's profile."""

from pubsub import pub
from typing import Tuple
import wx
import output
from logging import getLogger
from threading import Thread

from controller.mastodon.profile_format import format_profile
from controller.mastodon.profile import ProfileController
from controller.mastodon import userActions
from mysc.image_utils import load_scaled_image


log = getLogger(__name__)


def selectUserDialog(users: list) -> tuple:
    """Choose a user from a possible list of users"""
    if len(users) == 1:
        return users[0]
    dlg = wx.Dialog(None, title=_("Select user"))
    label = wx.StaticText(dlg, label="Select a user: ")
    choiceList = []
    for user in users:
        if len(user) == 3:  # (display_name, username, id)
            choiceList.append(f"{user[0]}: @{user[1]}")
        else:  # (acct, id)
            choiceList.append(f"{user[0]}")
    choice = wx.Choice(dlg, choices=choiceList)
    ok = wx.Button(dlg, wx.ID_OK, _("OK"))
    ok.SetDefault()
    cancel = wx.Button(dlg, wx.ID_CANCEL, _("Cancel"))
    dlg.SetEscapeId(cancel.GetId())

    #sizers
    sizer = wx.GridSizer(2, 2, 5, 5)
    sizer.Add(label, wx.SizerFlags().Center())
    sizer.Add(choice, wx.SizerFlags().Center())
    sizer.Add(ok, wx.SizerFlags().Center())
    sizer.Add(cancel, wx.SizerFlags().Center())

    if dlg.ShowModal() == wx.ID_CANCEL:
        return ()
    # return the selected user
    return users[choice.GetSelection()]


def returnTrue():
    return True


class ShowUserProfile(wx.Dialog):
    """
    A dialog for Showing user profile
    layout is:
    ```
    header
    avatar
    name
    bio
    meta data
    ```
    """

    def __init__(self, user, session=None, profile_data=None, controller=None):
        """Initialize update profile dialog
        Parameters:
        - user: user dictionary
        """
        super().__init__(parent=None)
        self._refresh_focus = None
        self._action_pending = False
        self.user = user
        self.session = session
        user = profile_data or format_profile(user)
        self.profile_controller = controller or ProfileController(
            session, self, lambda query: Thread(target=query, daemon=True).start(), wx.CallAfter)
        self.profile_controller.view = self
        self.Bind(wx.EVT_WINDOW_DESTROY, self._on_destroy)
        self.SetTitle(_("{}'s Profile").format(user.display_name))
        self.panel = wx.Panel(self)
        wrapper = wx.BoxSizer(wx.VERTICAL)
        grid = wx.FlexGridSizer(cols=2, vgap=5, hgap=5)
        grid.AddGrowableCol(1, 1)
        for label, attribute, value, multiline in [
            (_("&Name:"), 'name_ctrl', user.display_name, False),
            (_("&Handle:"), 'handle_ctrl', getattr(self.user, 'acct', ''), False),
            (_("&Bio:"), 'bio_ctrl', user.note, True),
            (_("&URL:"), 'url_ctrl', user.url, False),
            (_("&Joined at:"), 'joinText_ctrl', user.joined, False),
        ]:
            grid.Add(wx.StaticText(self.panel, label=label), 0, wx.ALIGN_TOP | wx.ALL, 2)
            control = self.createTextCtrl(value, (400, 60) if multiline else (200, 30), multiline)
            setattr(self, attribute, control)
            grid.Add(control, 1, wx.EXPAND | wx.ALL, 2)
        for label, attribute in [(_("Banner:"), 'headerImage'), (_("Avatar:"), 'avatarImage')]:
            grid.Add(wx.StaticText(self.panel, label=label), 0, wx.ALL, 2)
            image = wx.StaticBitmap(self.panel)
            image.AcceptsFocusFromKeyboard = returnTrue
            setattr(self, attribute, image)
            grid.Add(image, 0, wx.ALL, 2)
        wrapper.Add(grid, 0, wx.EXPAND | wx.ALL, 10)
        timelines = wx.BoxSizer(wx.HORIZONTAL)
        for attribute, label, callback in [
            ('posts_ctrl', _("{} pos&ts. Click to open posts timeline").format(user.statuses_count), self.onPost),
            ('following_ctrl', _("{} &following. Click to open Following timeline").format(user.following_count), self.onFollowing),
            ('followers_ctrl', _("{} fo&llowers. Click to open followers timeline").format(user.followers_count), self.onFollowers),
        ]:
            button = wx.Button(self.panel, label=label)
            button.Bind(wx.EVT_BUTTON, callback)
            setattr(self, attribute, button)
            timelines.Add(button, 0, wx.ALL, 3)
        wrapper.Add(timelines, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        actions = wx.BoxSizer(wx.HORIZONTAL)
        self.action_buttons = {}
        for command, label in [('follow', _("&Follow")), ('unfollow', _("U&nfollow")),
                               ('mute', _("&Mute")), ('unmute', _("Unmu&te")),
                               ('block', _("&Block")), ('unblock', _("Unbl&ock"))]:
            button = wx.Button(self.panel, label=label)
            button.Bind(wx.EVT_BUTTON, lambda event, command=command: self.on_user_action(command))
            self.action_buttons[command] = button
            actions.Add(button, 0, wx.ALL, 3)
            button.Hide()
        wrapper.Add(actions, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        # Retained only for callers using the old entry point; not part of navigation.
        self.actions_ctrl = wx.Button(self.panel, label=_("&Actions"))
        self.actions_ctrl.Hide()
        details = wx.FlexGridSizer(cols=2, vgap=5, hgap=5)
        details.AddGrowableCol(1, 1)
        for label, attribute, value in [
            (_("&Private account:"), 'private_ctrl', user.locked),
            (_("B&ot account:"), 'botText_ctrl', user.bot),
            (_("&Discoverable account:"), 'discoverText_ctrl', user.discoverable),
        ]:
            details.Add(wx.StaticText(self.panel, label=label), 0, wx.ALL, 2)
            control = self.createTextCtrl(_("Yes") if value else _("No"), (200, 30))
            setattr(self, attribute, control)
            details.Add(control, 1, wx.EXPAND | wx.ALL, 2)
        wrapper.Add(details, 0, wx.EXPAND | wx.ALL, 10)
        self.fields_panel = wx.Panel(self.panel)
        self.fields_sizer = wx.BoxSizer(wx.VERTICAL)
        self.fields_panel.SetSizer(self.fields_sizer)
        self._render_fields(user.fields)
        wrapper.Add(self.fields_panel, 0, wx.EXPAND | wx.ALL, 5)
        self.close_btn = wx.Button(self.panel, wx.ID_CANCEL, _("&Close"))
        self.close_btn.SetDefault()
        self.SetEscapeId(self.close_btn.GetId())
        wrapper.Add(self.close_btn, 0, wx.ALIGN_RIGHT | wx.ALL, 10)
        self.panel.SetSizer(wrapper)
        outer = wx.BoxSizer(wx.VERTICAL)
        outer.Add(self.panel, 1, wx.EXPAND)
        self.SetSizerAndFit(outer)
        self.SetMinSize((500, 400))
        self.Center()
        self._getImages()
        if hasattr(user, 'actions'):
            self.show_follow_requested(getattr(user, 'follow_requested', False))
            self.show_profile_actions(user.actions)
        elif session is not None:
            self.profile_controller.load_relationship(self.user.id)


    def createTextCtrl(self, text: str, size: Tuple[int, int], multiline: bool = False) -> wx.TextCtrl:
        """Creates a wx.TextCtrl and returns it
        Parameters:
            text: The value of the wx.TextCtrl
            size: The size of the wx.TextCtrl
        Returns: the created wx.TextCtrl object
        """
        if not multiline:
            style= wx.TE_PROCESS_ENTER | wx.TE_PROCESS_TAB | wx.TE_READONLY
        else:
            style= wx.TE_PROCESS_ENTER | wx.TE_PROCESS_TAB | wx.TE_READONLY | wx.TE_MULTILINE
        textCtrl = wx.TextCtrl(self.panel, value=text, size=size, style=style)
        textCtrl.AcceptsFocusFromKeyboard = returnTrue
        return textCtrl

    def onAction(self, *args):
        """Opens the Open timeline dialog"""
        if self.session is not None:
            if self._action_pending:
                return
            self._action_pending = True
            selector = userActions.userActions(self.session, users=[self.user.acct],
                on_complete=self._on_action_finished)
            self._action_pending = selector.started
            self.actions_ctrl.SetFocus()
        else:
            pub.sendMessage('execute-action', action='follow')

    def _on_action_finished(self, error):
        self.finish_user_action(error)
        if error is None and not self.profile_controller.closed:
            self.profile_controller.load(self.user.id)

    def show_profile_actions(self, actions):
        for command, button in self.action_buttons.items():
            button.Show(command in actions)
        self.Layout()

    def show_follow_requested(self, requested):
        self.action_buttons['unfollow'].SetLabel(_("Cancel follow request") if requested else _("U&nfollow"))

    def show_relationship_error(self, error):
        message = _("Could not load available actions.")
        self.SetTitle(message)
        output.speak(message, True)

    def on_user_action(self, command):
        if self._action_pending:
            return
        if command in {'unfollow', 'block'}:
            message = (_("Are you sure you want to unfollow @{handle}?") if command == 'unfollow'
                       else _("Are you sure you want to block @{handle}? This will prevent them from interacting with you and hide their content."))
            confirmation = wx.MessageDialog(self, message.format(handle=self.user.acct), _("Confirm Action"), wx.YES_NO | wx.ICON_QUESTION)
            try:
                if confirmation.ShowModal() != wx.ID_YES:
                    self.action_buttons[command].SetFocus()
                    return
            finally:
                confirmation.Destroy()
        self.profile_controller.act(command, self.user.id)

    def show_action_loading(self, command):
        self._action_pending = True
        self._action_command = command
        self._action_focus = wx.Window.FindFocus()
        self.SetTitle(_("Performing action: {action}...").format(action=command))
        for button in self.action_buttons.values():
            button.Disable()

    def finish_user_action(self, error):
        self._action_pending = False
        if self.profile_controller.closed:
            return
        for button in self.action_buttons.values():
            button.Enable()
        self._refresh_focus = getattr(self, '_action_focus', None)
        if error is not None:
            self._refresh_focus = None
            self.show_error(error)
            return
        if self._refresh_focus is None:
            self._refresh_focus = self.action_buttons['follow']
        self.SetTitle(_("Action completed."))
        output.speak(_("Action completed."), True)

    def _restore_focus(self, focus):
        if not focus or not focus.IsShown() or not focus.IsEnabled():
            inverse = {'follow': 'unfollow', 'unfollow': 'follow', 'mute': 'unmute',
                       'unmute': 'mute', 'block': 'unblock', 'unblock': 'block'}
            focus = self.action_buttons.get(inverse.get(getattr(self, '_action_command', None)))
        if not focus or not focus.IsShown() or not focus.IsEnabled():
            focus = next((button for button in self.action_buttons.values() if button.IsShown()), self.close_btn)
        focus.SetFocus()

    def show_error(self, error):
        if self._refresh_focus is not None:
            message = _("Action completed, but the profile could not be refreshed.")
            self.SetTitle(message)
            output.speak(message, True)
            self._restore_focus(self._refresh_focus)
            self._refresh_focus = None
        else:
            wx.MessageBox(str(error), _("Error"), wx.OK | wx.ICON_ERROR, self)
            self._restore_focus(getattr(self, '_action_focus', None))

    def show_profile(self, user, data, controller):
        # Update existing widgets; the modal dialog and its focus are preserved.
        focus = self._refresh_focus or wx.Window.FindFocus()
        self.user = user
        self.show_follow_requested(getattr(data, 'follow_requested', False))
        self.show_profile_actions(getattr(data, 'actions', frozenset()))
        for control, value in [(self.name_ctrl, data.display_name), (self.url_ctrl, data.url),
                               (self.bio_ctrl, data.note), (self.joinText_ctrl, data.joined),
                               (self.handle_ctrl, getattr(user, 'acct', '')),
                               (self.private_ctrl, _("Yes") if data.locked else _("No")),
                               (self.botText_ctrl, _("Yes") if data.bot else _("No")),
                               (self.discoverText_ctrl, _("Yes") if data.discoverable else _("No"))]:
            control.ChangeValue(value)
        self.posts_ctrl.SetLabel(_("{} pos&ts. Click to open posts timeline").format(data.statuses_count))
        self.following_ctrl.SetLabel(_("{} &following. Click to open Following timeline").format(data.following_count))
        self.followers_ctrl.SetLabel(_("{} fo&llowers. Click to open followers timeline").format(data.followers_count))
        self._render_fields(data.fields)
        self.SetTitle(_("{}'s Profile").format(data.display_name))
        self.Layout()
        self._getImages()
        if focus:
            self._restore_focus(focus)
        self._refresh_focus = None

    def _render_fields(self, fields):
        self.fields_sizer.Clear(delete_windows=True)
        for number, field in enumerate(fields, 1):
            label = wx.StaticText(self.fields_panel, label=_("Field &{} - Label: ").format(number))
            name = wx.TextCtrl(self.fields_panel, value=field.name, style=wx.TE_READONLY)
            content_label = wx.StaticText(self.fields_panel, label=_("Content: "))
            content = wx.TextCtrl(self.fields_panel, value=field.value, style=wx.TE_READONLY | wx.TE_MULTILINE)
            for control in (label, name, content_label, content):
                self.fields_sizer.Add(control, 0, wx.EXPAND | wx.ALL, 5)
        self.fields_panel.Layout()

    def onPost(self, *args):
        """Open this user's timeline"""
        pub.sendMessage('execute-action', action='openPostTimeline', kwargs=dict(user=self.user))

    def onFollowing(self, *args):
        """Open following timeline for this user"""
        pub.sendMessage('execute-action', action='openFollowingTimeline', kwargs=dict(user=self.user))

    def onFollowers(self, *args):
        """Open followers timeline for this user"""
        pub.sendMessage('execute-action', action='openFollowersTimeline', kwargs=dict(user=self.user))

    def Destroy(self):
        self.profile_controller.close()
        return super().Destroy()

    def _on_destroy(self, event):
        if event.GetEventObject() is self:
            self.profile_controller.close()
        event.Skip()

    def _getImages(self):
        data = format_profile(self.user)
        self.profile_controller.load_images(data.header, data.avatar)

    def show_images(self, header, avatar):
        self._drawImages(header, avatar)

    def _drawImages(self, headerImageBytes, avatarImageBytes):
        """Draws images on the bitmap ui"""
    # log.debug("Drawing images...")
        # Header
        headerImage = load_scaled_image(headerImageBytes, 300, 100) if headerImageBytes else None
        if headerImage is not None:
            self.headerImage.SetBitmap(headerImage.ConvertToBitmap())

        # Avatar
        avatarImage = load_scaled_image(avatarImageBytes, 150, 150) if avatarImageBytes else None
        if avatarImage is not None:
            self.avatarImage.SetBitmap(avatarImage.ConvertToBitmap())


class ProfileView:
    """wx adapter for asynchronous profile lookup and modal lifetime."""
    def __init__(self, session):
        self.session = session

    def show_profile(self, user, data, controller):
        dialog = ShowUserProfile(user, self.session, data, controller)
        try:
            dialog.ShowModal()
        finally:
            dialog.Destroy()

    def show_error(self, error):
        wx.MessageBox(str(error), _("Error"), wx.OK | wx.ICON_ERROR)
