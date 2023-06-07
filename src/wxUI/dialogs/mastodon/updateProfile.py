import wx


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

    def __init__(self, display_name: str="", note: str=""):
        """Initialize update profile dialog
        Parameters:
        - display_name: The user's display name to show in the display name field
        - note: The users bio to show in the bio field
        """
        super().__init__(parent=None)
        self.SetTitle(_("Update Profile"))
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # create widgets
        display_name_label = wx.StaticText(panel, label=_("Display Name"))
        self.display_name = wx.TextCtrl(panel, value=display_name, style=
                                        wx.TE_PROCESS_ENTER)
        bio_label = wx.StaticText(panel, label=_("Bio"))
        self.bio = wx.TextCtrl(panel, value=note, style=wx.TE_PROCESS_ENTER)
        ok = wx.Button(panel, wx.ID_OK, _(u"&OK"))
        ok.SetDefault()
        cancel = wx.Button(panel, wx.ID_CANCEL, _("&Close"))
        self.SetEscapeId(cancel.GetId())

        # manage sizers
        sizer.Add(display_name_label, wx.SizerFlags().Center())
        sizer.Add(self.display_name, wx.SizerFlags().Center())
        sizer.Add(cancel, wx.SizerFlags().Center())
        sizer.Add(ok, wx.SizerFlags().Center())
        sizer.Add(self.bio, wx.SizerFlags().Center())
        panel.SetSizer(sizer)
        panel.Fit()

        # manage events
        ok.Bind(wx.EVT_BUTTON, self.on_ok)

    def on_ok(self, *args):
        """Method called when user clicks ok in dialog"""
        self.data = {
                'display_name': self.display_name.GetValue(),
                'note': self.bio.GetValue()
                }
        self.EndModal(wx.ID_OK)
