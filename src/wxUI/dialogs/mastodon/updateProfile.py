import os
import requests
from io import BytesIO

import wx


def return_true():
    return True


class UpdateProfileDialog(wx.Dialog):
    """
    A dialog for user to update his / her profile details.
    layout is:
    ```
    header
    avatar
    name
    bio
    meta data
    ```
    """

    def __init__(self, display_name: str, note: str, header: str, avatar: str, fields: list, locked: bool, bot: bool, discoverable: bool):
        """Initialize update profile dialog
        Parameters:
        - display_name: The user's display name to show in the display name field
        - note: The users bio to show in the bio field
        - header: the users header pic link
        - avatar: The users avatar pic link
        """
        super().__init__(parent=None)
        self.SetTitle(_("Update Profile"))
        self.header = header
        self.avatar = avatar

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # create widgets
        display_name_label = wx.StaticText(panel, label=_("Display Name"))
        self.display_name = wx.TextCtrl(panel, value=display_name, style= wx.TE_PROCESS_ENTER, size=(200, 30))
        name_sizer = wx.BoxSizer(wx.HORIZONTAL)
        name_sizer.Add(display_name_label, wx.SizerFlags().Center())
        name_sizer.Add(self.display_name, wx.SizerFlags().Center())
        sizer.Add(name_sizer, wx.CENTER)

        bio_label = wx.StaticText(panel, label=_("Bio"))
        self.bio = wx.TextCtrl(panel, value=note, style=wx.TE_PROCESS_ENTER | wx.TE_MULTILINE, size=(400, 60))
        bio_sizer = wx.BoxSizer(wx.HORIZONTAL)
        bio_sizer.Add(bio_label, wx.SizerFlags().Center())
        bio_sizer.Add(self.bio, wx.SizerFlags().Center())
        sizer.Add(bio_sizer, wx.CENTER)

        # header
        header_label = wx.StaticText(panel, label=_("Header"))
        try:
            response = requests.get(self.header)
        except requests.exceptions.RequestException:
            # Create empty image
            self.header_image = wx.StaticBitmap()
        else:
            image_bytes = BytesIO(response.content)
            image = wx.Image(image_bytes, wx.BITMAP_TYPE_ANY)
            image.Rescale(300, 100, wx.IMAGE_QUALITY_HIGH)
            self.header_image = wx.StaticBitmap(panel, bitmap=image.ConvertToBitmap())

        self.header_image.AcceptsFocusFromKeyboard = return_true
        self.change_header = wx.Button(panel, label=_("Change header"))
        header_sizer = wx.BoxSizer(wx.HORIZONTAL)
        header_sizer.Add(header_label, wx.SizerFlags().Center())
        header_sizer.Add(self.header_image, wx.SizerFlags().Center())
        header_sizer.Add(self.change_header, wx.SizerFlags().Center())
        sizer.Add(header_sizer, wx.CENTER)

        # avatar
        avatar_label = wx.StaticText(panel, label=_("Avatar"))
        try:
            response = requests.get(self.avatar)
        except requests.exceptions.RequestException:
            # Create empty image
            self.avatar_image = wx.StaticBitmap()
        else:
            image_bytes = BytesIO(response.content)
            image = wx.Image(image_bytes, wx.BITMAP_TYPE_ANY)
            image.Rescale(150, 150, wx.IMAGE_QUALITY_HIGH)
            self.avatar_image = wx.StaticBitmap(panel, bitmap=image.ConvertToBitmap())

        self.avatar_image.AcceptsFocusFromKeyboard = return_true
        self.change_avatar = wx.Button(panel, label=_("Change avatar"))
        avatar_sizer = wx.BoxSizer(wx.HORIZONTAL)
        avatar_sizer.Add(avatar_label, wx.SizerFlags().Center())
        avatar_sizer.Add(self.avatar_image, wx.SizerFlags().Center())
        avatar_sizer.Add(self.change_avatar, wx.SizerFlags().Center())
        sizer.Add(avatar_sizer, wx.CENTER)

        self.fields = []
        for i in range(1, 5):
            field_sizer = wx.BoxSizer(wx.HORIZONTAL)
            field_label = wx.StaticText(panel, label=_("Field {}: Label").format(i))
            field_sizer.Add(field_label, wx.SizerFlags().Center().Border(wx.ALL, 5))

            label_textctrl = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER | wx.TE_MULTILINE, size=(200, 30))
            if i <= len(fields):
                label_textctrl.SetValue(fields[i-1][0])
            field_sizer.Add(label_textctrl, wx.SizerFlags().Expand().Border(wx.ALL, 5))

            content_label = wx.StaticText(panel, label=_("Content"))
            field_sizer.Add(content_label, wx.SizerFlags().Center().Border(wx.ALL, 5))

            content_textctrl = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER | wx.TE_MULTILINE, size=(400, 60))
            if i <= len(fields):
                content_textctrl.SetValue(fields[i-1][1])
            field_sizer.Add(content_textctrl, wx.SizerFlags().Expand().Border(wx.ALL, 5))
            sizer.Add(field_sizer, 0, wx.CENTER)
            self.fields.append((label_textctrl, content_textctrl))

        self.locked = wx.CheckBox(panel, label=_("Private account"))
        self.locked.SetValue(locked)
        self.bot = wx.CheckBox(panel, label=_("Bot account"))
        self.bot.SetValue(bot)
        self.discoverable = wx.CheckBox(panel, label=_("Discoverable account"))
        self.discoverable.SetValue(discoverable)
        sizer.Add(self.locked, wx.SizerFlags().Expand().Border(wx.ALL, 5))
        sizer.Add(self.bot, wx.SizerFlags().Expand().Border(wx.ALL, 5))
        sizer.Add(self.discoverable, wx.SizerFlags().Expand().Border(wx.ALL, 5))

        ok = wx.Button(panel, wx.ID_OK, _(u"&OK"))
        ok.SetDefault()
        cancel = wx.Button(panel, wx.ID_CANCEL, _("&Close"))
        self.SetEscapeId(cancel.GetId())
        action_sizer = wx.BoxSizer(wx.HORIZONTAL)
        action_sizer.Add(ok, wx.SizerFlags().Center())
        action_sizer.Add(cancel, wx.SizerFlags().Center())
        sizer.Add(action_sizer, wx.CENTER)
        panel.SetSizer(sizer)
        sizer.Fit(self)
        self.Center()

        # manage events
        ok.Bind(wx.EVT_BUTTON, self.on_ok)
        self.change_header.Bind(wx.EVT_BUTTON, self.on_change_header)
        self.change_avatar.Bind(wx.EVT_BUTTON, self.on_change_avatar)

        self.AutoLayout = True

    def on_ok(self, *args):
        """Method called when user clicks ok in dialog"""
        self.data = {
                'display_name': self.display_name.GetValue(),
                'note': self.bio.GetValue(),
                'header': self.header,
                'avatar': self.avatar,
                'fields': [(label.GetValue(), content.GetValue()) for label, content in self.fields if label.GetValue() and content.GetValue()],
                'locked': self.locked.GetValue(),
                'bot': self.bot.GetValue(),
                'discoverable': self.discoverable.GetValue(),
                }
        self.EndModal(wx.ID_OK)

    def on_change_header(self, *args):
        """Display a dialog for the user to choose a picture and update the
        appropriate attribute"""
        wildcard = "Images (*.png;*.jpg;*.gif)|*.png;*.jpg;*.gif"
        dlg = wx.FileDialog(self, _("Select header image - max 2MB"), wildcard=wildcard)
        if dlg.ShowModal() == wx.CLOSE:
            return
        if os.path.getsize(dlg.GetPath()) > 2097152:
            # File size exceeds the limit
            message = _("The selected file is larger than 2MB. Do you want to select another file?")
            caption = _("File more than 2MB")
            style = wx.YES_NO | wx.ICON_WARNING

            # Display the message box
            result = wx.MessageBox(message, caption, style)
            return self.on_change_header() if result == wx.YES else None

        self.header = dlg.GetPath()
        image = wx.Image(self.header, wx.BITMAP_TYPE_ANY)
        image.Rescale(150, 150, wx.IMAGE_QUALITY_HIGH)
        self.header_image.SetBitmap(image.ConvertToBitmap())

    def on_change_avatar(self, *args):
        """Display a dialog for the user to choose a picture and update the
        appropriate attribute"""
        wildcard = "Images (*.png;*.jpg;*.gif)|*.png;*.jpg;*.gif"
        dlg = wx.FileDialog(self, _("Select avatar image - max 2MB"), wildcard=wildcard)
        if dlg.ShowModal() == wx.CLOSE:
            return
        if os.path.getsize(dlg.GetPath()) > 2097152:
            # File size exceeds the limit
            message = _("The selected file is larger than 2MB. Do you want to select another file?")
            caption = _("File more than 2MB")
            style = wx.YES_NO | wx.ICON_WARNING

            # Display the message box
            result = wx.MessageBox(message, caption, style)
            return self.on_change_avatar() if result == wx.YES else None

        self.avatar = dlg.GetPath()
        image = wx.Image(self.avatar, wx.BITMAP_TYPE_ANY)
        image.Rescale(150, 150, wx.IMAGE_QUALITY_HIGH)
        self.avatar_image.SetBitmap(image.ConvertToBitmap())
