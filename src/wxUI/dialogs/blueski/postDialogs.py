# -*- coding: utf-8 -*-
import wx


class Post(wx.Dialog):
    def __init__(self, caption=_("Post"), text="", *args, **kwds):
        super(Post, self).__init__(parent=None, id=wx.ID_ANY, *args, **kwds)
        self.SetTitle(caption)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Text
        post_label = wx.StaticText(self, wx.ID_ANY, caption)
        main_sizer.Add(post_label, 0, wx.ALL, 6)
        self.text = wx.TextCtrl(self, wx.ID_ANY, text, style=wx.TE_MULTILINE)
        self.Bind(wx.EVT_CHAR_HOOK, self.handle_keys, self.text)
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
        self.SetEscapeId(cancel.GetId())
        self.Layout()

        # Bindings
        self.btn_add.Bind(wx.EVT_BUTTON, self.on_add)
        self.btn_remove.Bind(wx.EVT_BUTTON, self.on_remove)
        self.attach_list.Bind(wx.EVT_LIST_ITEM_SELECTED, lambda evt: self.btn_remove.Enable(True))
        self.attach_list.Bind(wx.EVT_LIST_ITEM_DESELECTED, lambda evt: self.btn_remove.Enable(False))

    def handle_keys(self, event):
        shift = event.ShiftDown()
        if event.GetKeyCode() == wx.WXK_RETURN and not shift and hasattr(self, "send"):
            self.EndModal(wx.ID_OK)
        else:
            event.Skip()

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


class viewPost(wx.Dialog):
    def set_title(self, length):
        self.SetTitle(_("Post - %i characters ") % length)

    def __init__(self, text="", reposts_count=0, likes_count=0, source="", date="", privacy="", *args, **kwargs):
        super(viewPost, self).__init__(parent=None, id=wx.ID_ANY, size=(850, 850))
        self.init_ui(text, reposts_count, likes_count, source, date, privacy)

    def init_ui(self, text, reposts_count, likes_count, source, date, privacy):
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.create_text_section(panel, text), 1, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(self.create_image_description_section(panel), 1, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(self.create_info_section(panel, privacy, reposts_count, likes_count, source, date), 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(self.create_buttons_section(panel), 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        panel.SetSizer(main_sizer)
        self.SetClientSize(main_sizer.CalcMin())

    def create_text_section(self, panel, text):
        sizer = wx.StaticBoxSizer(wx.StaticBox(panel, wx.ID_ANY, _("Post")), wx.VERTICAL)
        self.text = wx.TextCtrl(panel, -1, text, style=wx.TE_READONLY | wx.TE_MULTILINE)
        sizer.Add(self.text, 1, wx.EXPAND | wx.ALL, 5)
        return sizer

    def create_image_description_section(self, panel):
        sizer = wx.StaticBoxSizer(wx.StaticBox(panel, wx.ID_ANY, _("Image description")), wx.VERTICAL)
        self.image_description = wx.TextCtrl(panel, -1, style=wx.TE_READONLY | wx.TE_MULTILINE)
        self.image_description.Enable(False)
        sizer.Add(self.image_description, 1, wx.EXPAND | wx.ALL, 5)
        return sizer

    def create_info_section(self, panel, privacy, reposts_count, likes_count, source, date):
        sizer = wx.StaticBoxSizer(wx.StaticBox(panel, wx.ID_ANY, _("Information")), wx.VERTICAL)
        flex_sizer = wx.FlexGridSizer(cols=3, hgap=10, vgap=10)
        flex_sizer.AddGrowableCol(1)
        flex_sizer.Add(wx.StaticText(panel, -1, _("Privacy")), 0, wx.ALIGN_CENTER_VERTICAL)
        flex_sizer.Add(wx.TextCtrl(panel, -1, privacy, style=wx.TE_READONLY | wx.TE_MULTILINE), 1, wx.EXPAND)
        flex_sizer.Add(self.create_reposts_section(panel, reposts_count), 1, wx.EXPAND | wx.ALL, 5)
        flex_sizer.Add(self.create_likes_section(panel, likes_count), 1, wx.EXPAND | wx.ALL, 5)
        flex_sizer.Add(wx.StaticText(panel, -1, _("Source")), 0, wx.ALIGN_CENTER_VERTICAL)
        flex_sizer.Add(wx.TextCtrl(panel, -1, source, style=wx.TE_READONLY | wx.TE_MULTILINE), 1, wx.EXPAND)
        flex_sizer.Add(wx.StaticText(panel, -1, _("Date")), 0, wx.ALIGN_CENTER_VERTICAL)
        flex_sizer.Add(wx.TextCtrl(panel, -1, date, style=wx.TE_READONLY | wx.TE_MULTILINE), 1, wx.EXPAND)
        sizer.Add(flex_sizer, 1, wx.EXPAND | wx.ALL, 5)
        return sizer

    def create_reposts_section(self, panel, reposts_count):
        sizer = wx.StaticBoxSizer(wx.StaticBox(panel, wx.ID_ANY, _("Reposts")), wx.VERTICAL)
        self.reposts_button = wx.Button(panel, -1, str(reposts_count))
        self.reposts_button.Enable(False)
        sizer.Add(self.reposts_button, 1, wx.EXPAND | wx.ALL, 5)
        return sizer

    def create_likes_section(self, panel, likes_count):
        sizer = wx.StaticBoxSizer(wx.StaticBox(panel, wx.ID_ANY, _("Likes")), wx.VERTICAL)
        self.likes_button = wx.Button(panel, -1, str(likes_count))
        self.likes_button.Enable(False)
        sizer.Add(self.likes_button, 1, wx.EXPAND | wx.ALL, 5)
        return sizer

    def create_buttons_section(self, panel):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.share = wx.Button(panel, wx.ID_ANY, _("&Copy link to clipboard"))
        self.share.Enable(False)
        self.spellcheck = wx.Button(panel, wx.ID_ANY, _("Check &spelling..."))
        self.translateButton = wx.Button(panel, wx.ID_ANY, _("&Translate..."))
        cancelButton = wx.Button(panel, wx.ID_CANCEL, _("C&lose"))
        cancelButton.SetDefault()
        sizer.Add(self.share, 0, wx.ALL, 5)
        sizer.Add(self.spellcheck, 0, wx.ALL, 5)
        sizer.Add(self.translateButton, 0, wx.ALL, 5)
        sizer.Add(cancelButton, 0, wx.ALL, 5)
        return sizer

    def set_text(self, text):
        self.text.ChangeValue(text)

    def get_text(self):
        return self.text.GetValue()

    def text_focus(self):
        self.text.SetFocus()

    def onSelect(self, ev):
        self.text.SelectAll()

    def enable_button(self, buttonName):
        if hasattr(self, buttonName):
            return getattr(self, buttonName).Enable()


class viewText(wx.Dialog):
    def __init__(self, title="", text="", *args, **kwargs):
        super(viewText, self).__init__(parent=None, id=wx.ID_ANY, size=(850, 850), title=title)
        panel = wx.Panel(self)
        label = wx.StaticText(panel, -1, _("Text"))
        self.text = wx.TextCtrl(panel, -1, text, style=wx.TE_READONLY | wx.TE_MULTILINE, size=(250, 180))
        self.text.SetFocus()
        textBox = wx.BoxSizer(wx.HORIZONTAL)
        textBox.Add(label, 0, wx.ALL, 5)
        textBox.Add(self.text, 1, wx.EXPAND, 5)
        mainBox = wx.BoxSizer(wx.VERTICAL)
        mainBox.Add(textBox, 0, wx.ALL, 5)
        self.spellcheck = wx.Button(panel, -1, _("Check &spelling..."), size=wx.DefaultSize)
        self.translateButton = wx.Button(panel, -1, _("&Translate..."), size=wx.DefaultSize)
        cancelButton = wx.Button(panel, wx.ID_CANCEL, _("C&lose"), size=wx.DefaultSize)
        cancelButton.SetDefault()
        buttonsBox = wx.BoxSizer(wx.HORIZONTAL)
        buttonsBox.Add(self.spellcheck, 0, wx.ALL, 5)
        buttonsBox.Add(self.translateButton, 0, wx.ALL, 5)
        buttonsBox.Add(cancelButton, 0, wx.ALL, 5)
        mainBox.Add(buttonsBox, 0, wx.ALL, 5)
        panel.SetSizer(mainBox)
        self.SetClientSize(mainBox.CalcMin())

