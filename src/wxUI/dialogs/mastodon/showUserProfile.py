# -*- coding: utf-8 -*-
"""Wx dialogs for showing a user's profile."""

from io import BytesIO
import os
from typing import Tuple
import requests
import wx

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

    def __init__(self, display_name: str, url: str, note: str, header: str, avatar: str, fields: list, locked: bool, bot: bool, discoverable: bool):
        """Initialize update profile dialog
        Parameters:
        - display_name: The user's display name to show in the display name field
        - url: The user's url
        - note: The users bio to show in the bio field
        - header: the users header pic link
        - avatar: The users avatar pic link
        """
        super().__init__(parent=None)
        self.SetTitle(_("{}'s Profile").format(display_name))
        self.panel = wx.Panel(self)
        wrapper = wx.BoxSizer(wx.VERTICAL)
        sizer = wx.GridSizer(2, 11, 5, 5)

        # create widgets
        nameLabel = wx.StaticText(self.panel, label=_("Name: "))
        name = self.createTextCtrl(display_name, size=(200, 30))
        sizer.Add(nameLabel, wx.SizerFlags().Center())
        sizer.Add(name, wx.SizerFlags().Center())

        urlLabel = wx.StaticText(self.panel, label=_("URL: "))
        url = self.createTextCtrl(url, size=(200, 30))
        sizer.Add(urlLabel, wx.SizerFlags().Center())
        sizer.Add(url, wx.SizerFlags().Center())

        bioLabel = wx.StaticText(self.panel, label=_("Bio: "))
        bio = self.createTextCtrl(note, (400, 60))
        sizer.Add(bioLabel, wx.SizerFlags().Center())
        sizer.Add(bio, wx.SizerFlags().Center())

        # header
        headerLabel = wx.StaticText(self.panel, label=_("Header: "))
        try:
            response = requests.get(header)
        except requests.exceptions.RequestException:
            # Create empty image
            headerImage = wx.StaticBitmap()
        else:
            image_bytes = BytesIO(response.content)
            image = wx.Image(image_bytes, wx.BITMAP_TYPE_ANY)
            image.Rescale(300, 100, wx.IMAGE_QUALITY_HIGH)
            headerImage = wx.StaticBitmap(self.panel, bitmap=image.ConvertToBitmap())

        headerImage.AcceptsFocusFromKeyboard = returnTrue
        sizer.Add(headerLabel, wx.SizerFlags().Center())
        sizer.Add(headerImage, wx.SizerFlags().Center())

        # avatar
        avatarLabel = wx.StaticText(self.panel, label=_("Avatar"))
        try:
            response = requests.get(avatar)
        except requests.exceptions.RequestException:
            # Create empty image
            avatarImage = wx.StaticBitmap()
        else:
            image_bytes = BytesIO(response.content)
            image = wx.Image(image_bytes, wx.BITMAP_TYPE_ANY)
            image.Rescale(150, 150, wx.IMAGE_QUALITY_HIGH)
            avatarImage = wx.StaticBitmap(self.panel, bitmap=image.ConvertToBitmap())

        avatarImage.AcceptsFocusFromKeyboard = returnTrue
        sizer.Add(avatarLabel, wx.SizerFlags().Center())
        sizer.Add(avatarImage, wx.SizerFlags().Center())

        self.fields = []
        for num, (label, content) in enumerate(fields):
            labelSizer = wx.BoxSizer(wx.HORIZONTAL)
            labelLabel = wx.StaticText(self.panel, label=_("Field {} - Label: ").format(num))
            labelSizer.Add(labelLabel, wx.SizerFlags().Center().Border(wx.ALL, 5))
            labelText = self.createTextCtrl(label, (230, 30), True)
            labelSizer.Add(labelText, wx.SizerFlags().Expand().Border(wx.ALL, 5))
            sizer.Add(labelSizer, 0, wx.CENTER)

            contentSizer = wx.BoxSizer(wx.HORIZONTAL)
            contentLabel = wx.StaticText(self.panel, label=_("Content: "))
            contentSizer.Add(contentLabel, wx.SizerFlags().Center())
            contentText = self.createTextCtrl(content, (400, 60), True)
            contentSizer.Add(contentText, wx.SizerFlags().Center())
            sizer.Add(contentSizer, 0, wx.CENTER | wx.LEFT, 10)

        close = wx.Button(self.panel, wx.ID_CLOSE, _("Close"))
        self.SetEscapeId(close.GetId())
        close.SetDefault()
        sizer.Add(close, wx.SizerFlags().Center())
        wrapper.Add(sizer, 0, wx.CENTER)  # For padding
        self.panel.SetSizerAndFit(wrapper)
        sizer.Fit(self)
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
