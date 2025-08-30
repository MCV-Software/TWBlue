# -*- coding: utf-8 -*-
import wx


class Post(wx.Dialog):
    def __init__(self, caption=_("Post"), text="", *args, **kwds):
        super(Post, self).__init__(parent=None, id=wx.ID_ANY, *args, **kwds)
        self.SetTitle(caption)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Text
        self.text = wx.TextCtrl(self, wx.ID_ANY, text, style=wx.TE_MULTILINE)
        self.text.SetMinSize((400, 160))
        main_sizer.Add(self.text, 1, wx.EXPAND | wx.ALL, 6)

        # Sensitive + CW
        cw_box = wx.BoxSizer(wx.HORIZONTAL)
        self.sensitive = wx.CheckBox(self, wx.ID_ANY, _("Sensitive content (CW)"))
        self.spoiler = wx.TextCtrl(self, wx.ID_ANY)
        self.spoiler.Enable(False)
        self.sensitive.Bind(wx.EVT_CHECKBOX, lambda evt: self.spoiler.Enable(self.sensitive.GetValue()))
        cw_box.Add(self.sensitive, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 4)
        cw_box.Add(self.spoiler, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 4)
        main_sizer.Add(cw_box, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 2)

        # Attachments (images only)
        attach_box = wx.StaticBoxSizer(wx.VERTICAL, self, _("Attachments (images)"))
        self.attach_list = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.attach_list.InsertColumn(0, _("File"))
        self.attach_list.InsertColumn(1, _("Alt"))
        attach_box.Add(self.attach_list, 1, wx.EXPAND | wx.ALL, 5)
        btn_row = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_add = wx.Button(self, wx.ID_ADD, _("Add image..."))
        self.btn_remove = wx.Button(self, wx.ID_REMOVE, _("Remove"))
        self.btn_remove.Enable(False)
        btn_row.Add(self.btn_add, 0, wx.ALL, 2)
        btn_row.Add(self.btn_remove, 0, wx.ALL, 2)
        attach_box.Add(btn_row, 0, wx.ALIGN_LEFT)
        main_sizer.Add(attach_box, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 6)

        # Language (single optional)
        lang_row = wx.BoxSizer(wx.HORIZONTAL)
        lang_row.Add(wx.StaticText(self, label=_("Language")), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 4)
        self.lang_choice = wx.ComboBox(self, wx.ID_ANY, choices=["", "en", "es", "fr", "de", "ja", "pt", "ru", "zh"], style=wx.CB_DROPDOWN | wx.CB_READONLY)
        self.lang_choice.SetSelection(0)
        lang_row.Add(self.lang_choice, 0, wx.ALIGN_CENTER_VERTICAL)
        main_sizer.Add(lang_row, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 6)

        # Buttons
        btn_sizer = wx.StdDialogButtonSizer()
        self.send = wx.Button(self, wx.ID_OK, _("Send"))
        self.send.SetDefault()
        btn_sizer.AddButton(self.send)
        cancel = wx.Button(self, wx.ID_CANCEL, _("Cancel"))
        btn_sizer.AddButton(cancel)
        btn_sizer.Realize()
        main_sizer.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 4)

        self.SetSizer(main_sizer)
        main_sizer.Fit(self)
        self.Layout()

        # Bindings
        self.btn_add.Bind(wx.EVT_BUTTON, self.on_add)
        self.btn_remove.Bind(wx.EVT_BUTTON, self.on_remove)
        self.attach_list.Bind(wx.EVT_LIST_ITEM_SELECTED, lambda evt: self.btn_remove.Enable(True))
        self.attach_list.Bind(wx.EVT_LIST_ITEM_DESELECTED, lambda evt: self.btn_remove.Enable(False))

    def on_add(self, evt):
        if self.attach_list.GetItemCount() >= 4:
            wx.MessageBox(_("You can attach up to 4 images."), _("Attachment limit"), wx.ICON_INFORMATION)
            return
        fd = wx.FileDialog(self, _("Select image"), wildcard=_("Image files (*.png;*.jpg;*.jpeg;*.gif)|*.png;*.jpg;*.jpeg;*.gif"), style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if fd.ShowModal() != wx.ID_OK:
            fd.Destroy()
            return
        path = fd.GetPath()
        fd.Destroy()
        alt_dlg = wx.TextEntryDialog(self, _("Alternative text (optional)"), _("Description"))
        alt = ""
        if alt_dlg.ShowModal() == wx.ID_OK:
            alt = alt_dlg.GetValue()
        alt_dlg.Destroy()
        idx = self.attach_list.InsertItem(self.attach_list.GetItemCount(), path)
        self.attach_list.SetItem(idx, 1, alt)

    def on_remove(self, evt):
        sel = self.attach_list.GetFirstSelected()
        if sel != -1:
            self.attach_list.DeleteItem(sel)

    def get_payload(self):
        text = self.text.GetValue().strip()
        cw_text = self.spoiler.GetValue().strip() if self.sensitive.GetValue() else None
        lang = self.lang_choice.GetValue().strip() or None
        files = []
        for i in range(self.attach_list.GetItemCount()):
            files.append({
                "path": self.attach_list.GetItemText(i, 0),
                "alt": self.attach_list.GetItemText(i, 1),
            })
        return text, files, cw_text, (lang and [lang] or [])

