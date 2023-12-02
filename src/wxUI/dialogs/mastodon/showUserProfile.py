# -*- coding: utf-8 -*-
"""Wx dialogs for showing a user's profile."""

from io import BytesIO
from pubsub import pub
from typing import Tuple
import requests
import wx

from sessions.mastodon.utils import html_filter


def _(s):
    return s


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

    def __init__(self, user):
        """Initialize update profile dialog
        Parameters:
        - user: user dictionary
        """
        super().__init__(parent=None)
        self.user = user
        self.SetTitle(_("{}'s Profile").format(user.display_name))
        self.panel = wx.Panel(self)
        wrapperSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer = wx.GridSizer(2, 5, 5)

        # create widgets
        nameLabel = wx.StaticText(self.panel, label=_("Name: "))
        name = self.createTextCtrl(user.display_name, size=(200, 30))
        mainSizer.Add(nameLabel, wx.SizerFlags().Center())
        mainSizer.Add(name, wx.SizerFlags().Center())

        urlLabel = wx.StaticText(self.panel, label=_("URL: "))
        url = self.createTextCtrl(user.url, size=(200, 30))
        mainSizer.Add(urlLabel, wx.SizerFlags().Center())
        mainSizer.Add(url, wx.SizerFlags().Center())

        bioLabel = wx.StaticText(self.panel, label=_("Bio: "))
        bio = self.createTextCtrl(html_filter(user.note), (400, 60))
        mainSizer.Add(bioLabel, wx.SizerFlags().Center())
        mainSizer.Add(bio, wx.SizerFlags().Center())

        joinLabel = wx.StaticText(self.panel, label=_("Joined at: "))
        joinText = self.createTextCtrl(user.created_at.strftime('%d %B, %Y'), (80, 30))
        mainSizer.Add(joinLabel, wx.SizerFlags().Center())
        mainSizer.Add(joinText, wx.SizerFlags().Center())

        actions = wx.Button(self.panel, label=_("Actions"))
        actions.Bind(wx.EVT_BUTTON, self.onAction)
        mainSizer.Add(actions, wx.SizerFlags().Center())

        # header
        headerLabel = wx.StaticText(self.panel, label=_("Header: "))
        try:
            response = requests.get(user.header)
        except requests.exceptions.RequestException:
            # Create empty image
            headerImage = wx.StaticBitmap()
        else:
            image_bytes = BytesIO(response.content)
            image = wx.Image(image_bytes, wx.BITMAP_TYPE_ANY)
            image.Rescale(300, 100, wx.IMAGE_QUALITY_HIGH)
            headerImage = wx.StaticBitmap(self.panel, bitmap=image.ConvertToBitmap())

        headerImage.AcceptsFocusFromKeyboard = returnTrue
        mainSizer.Add(headerLabel, wx.SizerFlags().Center())
        mainSizer.Add(headerImage, wx.SizerFlags().Center())

        # avatar
        avatarLabel = wx.StaticText(self.panel, label=_("Avatar: "))
        try:
            response = requests.get(user.avatar)
        except requests.exceptions.RequestException:
            # Create empty image
            avatarImage = wx.StaticBitmap()
        else:
            image_bytes = BytesIO(response.content)
            image = wx.Image(image_bytes, wx.BITMAP_TYPE_ANY)
            image.Rescale(150, 150, wx.IMAGE_QUALITY_HIGH)
            avatarImage = wx.StaticBitmap(self.panel, bitmap=image.ConvertToBitmap())

        avatarImage.AcceptsFocusFromKeyboard = returnTrue
        mainSizer.Add(avatarLabel, wx.SizerFlags().Center())
        mainSizer.Add(avatarImage, wx.SizerFlags().Center())

        self.fields = []
        for num, field in enumerate(user.fields):
            labelSizer = wx.BoxSizer(wx.HORIZONTAL)
            labelLabel = wx.StaticText(self.panel, label=_("Field {} - Label: ").format(num + 1))
            labelSizer.Add(labelLabel, wx.SizerFlags().Center().Border(wx.ALL, 5))
            labelText = self.createTextCtrl(html_filter(field.name), (230, 30), True)
            labelSizer.Add(labelText, wx.SizerFlags().Expand().Border(wx.ALL, 5))
            mainSizer.Add(labelSizer, 0, wx.CENTER)

            contentSizer = wx.BoxSizer(wx.HORIZONTAL)
            contentLabel = wx.StaticText(self.panel, label=_("Content: "))
            contentSizer.Add(contentLabel, wx.SizerFlags().Center())
            contentText = self.createTextCtrl(html_filter(field.value), (400, 60), True)
            contentSizer.Add(contentText, wx.SizerFlags().Center())
            mainSizer.Add(contentSizer, 0, wx.CENTER | wx.LEFT, 10)

        bullSwitch = {True: _('Yes'), False: _('No'), None: _('No')}
        privateSizer = wx.BoxSizer(wx.HORIZONTAL)
        privateLabel = wx.StaticText(self.panel, label=_("Private account: "))
        private = self.createTextCtrl(bullSwitch[user.locked], (30, 30))
        privateSizer.Add(privateLabel, wx.SizerFlags().Center())
        privateSizer.Add(private, wx.SizerFlags().Center())
        mainSizer.Add(privateSizer, 0, wx.ALL | wx.CENTER)

        botSizer = wx.BoxSizer(wx.HORIZONTAL)
        botLabel = wx.StaticText(self.panel, label=_("Bot account: "))
        botText = self.createTextCtrl(bullSwitch[user.bot], (30, 30))
        botSizer.Add(botLabel, wx.SizerFlags().Center())
        botSizer.Add(botText, wx.SizerFlags().Center())
        mainSizer.Add(botSizer, 0, wx.ALL | wx.CENTER)

        discoverSizer = wx.BoxSizer(wx.HORIZONTAL)
        discoverLabel = wx.StaticText(self.panel, label=_("Discoverable account: "))
        discoverText = self.createTextCtrl(bullSwitch[user.discoverable], (30, 30))
        discoverSizer.Add(discoverLabel, wx.SizerFlags().Center())
        discoverSizer.Add(discoverText, wx.SizerFlags().Center())
        mainSizer.Add(discoverSizer, 0, wx.ALL | wx.CENTER)

        posts = wx.Button(self.panel, label=_("{} posts. Click to open posts timeline").format(user.statuses_count))
        # posts.SetToolTip(_("Click to open {}'s posts").format(user.display_name))
        posts.Bind(wx.EVT_BUTTON, self.onPost)
        mainSizer.Add(posts, wx.SizerFlags().Center())

        following = wx.Button(self.panel, label=_("{} following. Click to open Following timeline").format(user.following_count))
        mainSizer.Add(following, wx.SizerFlags().Center())
        following.Bind(wx.EVT_BUTTON, self.onFollowing)

        followers = wx.Button(self.panel, label=_("{} followers. Click to open followers timeline").format(user.followers_count))
        mainSizer.Add(followers, wx.SizerFlags().Center())
        followers.Bind(wx.EVT_BUTTON, self.onFollowers)

        close = wx.Button(self.panel, wx.ID_CLOSE, _("Close"))
        self.SetEscapeId(close.GetId())
        close.SetDefault()
        wrapperSizer.Add(mainSizer, 0, wx.CENTER)
        wrapperSizer.Add(close, wx.SizerFlags().Center())
        self.panel.SetSizer(wrapperSizer)
        wrapperSizer.Fit(self.panel)
        self.panel.Center()
        mainSizer.Fit(self)
        self.Center()


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
        pub.sendMessage('execute-action', action='follow')

    def onPost(self, *args):
        """Open this user's timeline"""
        pub.sendMessage('execute-action', action='openPostTimeline', kwargs=dict(user=self.user))

    def onFollowing(self, *args):
        """Open following timeline for this user"""
        pub.sendMessage('execute-action', action='openFollowingTimeline', kwargs=dict(user=self.user))

    def onFollowers(self, *args):
        """Open followers timeline for this user"""
        pub.sendMessage('execute-action', action='openFollowersTimeline', kwargs=dict(user=self.user))
