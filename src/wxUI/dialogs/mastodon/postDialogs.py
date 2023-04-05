import wx

class Post(wx.Dialog):
    def __init__(self, caption=_("Post"), text="", *args, **kwds):
        super(Post, self).__init__(parent=None, id=wx.ID_ANY, *args, **kwds)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        post_sizer = wx.WrapSizer(wx.VERTICAL)
        main_sizer.Add(post_sizer, 1, wx.EXPAND, 0)
        post_label = wx.StaticText(self, wx.ID_ANY, caption)
        post_sizer.Add(post_label, 0, 0, 0)
        self.text = wx.TextCtrl(self, wx.ID_ANY, text, style=wx.TE_MULTILINE)
        self.Bind(wx.EVT_CHAR_HOOK, self.handle_keys, self.text)
        self.text.SetMinSize((350, -1))
        post_sizer.Add(self.text, 0, 0, 0)
        lists_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(lists_sizer, 1, wx.EXPAND, 0)
        attachments_sizer = wx.WrapSizer(wx.VERTICAL)
        lists_sizer.Add(attachments_sizer, 1, wx.EXPAND, 0)
        attachments_label = wx.StaticText(self, wx.ID_ANY, _("Attachments"))
        attachments_sizer.Add(attachments_label, 0, 0, 0)
        self.attachments = wx.ListCtrl(self, wx.ID_ANY, style=wx.LC_HRULES | wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_VRULES)
        self.attachments.Enable(False)
        self.attachments.AppendColumn(_("File"), format=wx.LIST_FORMAT_LEFT, width=-1)
        self.attachments.AppendColumn(_("Type"), format=wx.LIST_FORMAT_LEFT, width=-1)
        self.attachments.AppendColumn(_("Description"), format=wx.LIST_FORMAT_LEFT, width=-1)
        attachments_sizer.Add(self.attachments, 1, wx.EXPAND, 0)
        self.remove_attachment = wx.Button(self, wx.ID_ANY, _("Remove Attachment"))
        self.remove_attachment.Enable(False)
        attachments_sizer.Add(self.remove_attachment, 0, 0, 0)
        posts_sizer = wx.WrapSizer(wx.VERTICAL)
        lists_sizer.Add(posts_sizer, 1, wx.EXPAND, 0)
        posts_label = wx.StaticText(self, wx.ID_ANY, _("Post in the thread"))
        posts_sizer.Add(posts_label, 0, 0, 0)
        self.posts = wx.ListCtrl(self, wx.ID_ANY, style=wx.LC_HRULES | wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_VRULES)
        self.posts.Enable(False)
        self.posts.AppendColumn(_("Text"), format=wx.LIST_FORMAT_LEFT, width=-1)
        self.posts.AppendColumn(_("Attachments"), format=wx.LIST_FORMAT_LEFT, width=-1)
        posts_sizer.Add(self.posts, 1, wx.EXPAND, 0)
        self.remove_post = wx.Button(self, wx.ID_ANY, _("Remove post"))
        self.remove_post.Enable(False)
        posts_sizer.Add(self.remove_post, 0, 0, 0)
        post_actions_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(post_actions_sizer, 1, wx.EXPAND, 0)
        visibility_sizer = wx.BoxSizer(wx.HORIZONTAL)
        post_actions_sizer.Add(visibility_sizer, 1, wx.EXPAND, 0)
        label_1 = wx.StaticText(self, wx.ID_ANY, _("&Visibility"))
        visibility_sizer.Add(label_1, 0, 0, 0)
        self.visibility = wx.ComboBox(self, wx.ID_ANY, choices=[_("Public"), _("Not listed"), _("Followers only"), _("Direct")], style=wx.CB_DROPDOWN | wx.CB_READONLY | wx.CB_SIMPLE)
        self.visibility.SetSelection(0)
        visibility_sizer.Add(self.visibility, 0, 0, 0)
        self.add = wx.Button(self, wx.ID_ANY, _("A&dd"))
        self.sensitive = wx.CheckBox(self, wx.ID_ANY, _("S&ensitive content"))
        self.sensitive.SetValue(False)
        self.sensitive.Bind(wx.EVT_CHECKBOX, self.on_sensitivity_changed)
        main_sizer.Add(self.sensitive, 0, wx.ALL, 5)
        spoiler_box = wx.BoxSizer(wx.HORIZONTAL)
        spoiler_label = wx.StaticText(self, wx.ID_ANY, _("Content warning"))
        self.spoiler = wx.TextCtrl(self, wx.ID_ANY)
        self.spoiler.Enable(False)
        spoiler_box.Add(spoiler_label, 0, wx.ALL, 5)
        spoiler_box.Add(self.spoiler, 0, wx.ALL, 10)
        main_sizer.Add(spoiler_box, 0, wx.ALL, 5)
        post_actions_sizer.Add(self.add, 0, 0, 0)
        self.add_post = wx.Button(self, wx.ID_ANY, _("Add p&ost"))
        post_actions_sizer.Add(self.add_post, 0, 0, 0)
        text_actions_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(text_actions_sizer, 1, wx.EXPAND, 0)
        self.autocomplete_users = wx.Button(self, wx.ID_ANY, _("Auto&complete users"))
        text_actions_sizer.Add(self.autocomplete_users, 0, 0, 0)
        self.spellcheck = wx.Button(self, wx.ID_ANY, _("Check &spelling"))
        text_actions_sizer.Add(self.spellcheck, 0, 0, 0)
        self.translate = wx.Button(self, wx.ID_ANY, _("&Translate"))
        text_actions_sizer.Add(self.translate, 0, 0, 0)
        btn_sizer = wx.StdDialogButtonSizer()
        main_sizer.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 4)
        self.send = wx.Button(self, wx.ID_OK, "")
        self.send.SetDefault()
        btn_sizer.AddButton(self.send)
        self.close = wx.Button(self, wx.ID_CLOSE, "")
        btn_sizer.AddButton(self.close)
        btn_sizer.Realize()
        self.SetSizer(main_sizer)
        main_sizer.Fit(self)
        self.SetEscapeId(self.close.GetId())
        self.Layout()

    def handle_keys(self, event: wx.Event, *args, **kwargs) -> None:
        """ Allows to react to certain keyboard events from the text control. """
        shift=event.ShiftDown()
        if event.GetKeyCode() == wx.WXK_RETURN and shift==False and hasattr(self,'send'):
            self.EndModal(wx.ID_OK)
        else:
            event.Skip()

    def on_sensitivity_changed(self, *args, **kwargs):
        self.spoiler.Enable(self.sensitive.GetValue())

    def set_title(self, chars):
        self.SetTitle(_("Post - {} characters").format(chars))

    def reset_controls(self):
        self.text.ChangeValue("")
        self.attachments.DeleteAllItems()

    def add_item(self, list_type="attachment", item=[]):
        if list_type == "attachment":
            self.attachments.Append(item)
        else:
            self.posts.Append(item)

    def remove_item(self, list_type="attachment"):
        if list_type == "attachment":
            item = self.attachments.GetFocusedItem()
            if item > -1:
                self.attachments.DeleteItem(item)
        else:
            item = self.posts.GetFocusedItem()
            if item > -1:
                self.posts.DeleteItem(item)

    def attach_menu(self, event=None, enabled=True, *args, **kwargs):
        menu = wx.Menu()
        self.add_image = menu.Append(wx.ID_ANY, _("Image"))
        self.add_image.Enable(enabled)
        self.add_video = menu.Append(wx.ID_ANY, _("Video"))
        self.add_video.Enable(enabled)
        self.add_audio = menu.Append(wx.ID_ANY, _("Audio"))
        self.add_audio.Enable(enabled)
        self.add_poll = menu.Append(wx.ID_ANY, _("Poll"))
        self.add_poll.Enable(enabled)
        return menu

    def ask_description(self):
        dlg = wx.TextEntryDialog(self, _(u"please provide a description"), _(u"Description"))
        dlg.ShowModal()
        result = dlg.GetValue()
        dlg.Destroy()
        return result

    def get_image(self):
        openFileDialog = wx.FileDialog(self, _(u"Select the picture to be uploaded"), "", "", _("Image files (*.png, *.jpg, *.gif)|*.png; *.jpg; *.gif"), wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            return (None, None)
        dsc = self.ask_description()
        return (openFileDialog.GetPath(), dsc)

    def get_video(self):
        openFileDialog = wx.FileDialog(self, _("Select the video to be uploaded"), "", "", _("Video files (*.mp4, *.mov, *.m4v, *.webm)| *.mp4; *.m4v; *.mov; *.webm"), wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            return (None, None)
        dsc = self.ask_description()
        return (openFileDialog.GetPath(), dsc)

    def get_audio(self):
        openFileDialog = wx.FileDialog(self, _("Select the audio file to be uploaded"), "", "", _("Audio files (*.mp3, *.ogg, *.wav, *.flac, *.opus, *.aac, *.m4a, *.3gp)|*.mp3; *.ogg; *.wav; *.flac; *.opus; *.aac; *.m4a; *.3gp"), wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            return (None, None)
        dsc = self.ask_description()
        return (openFileDialog.GetPath(), dsc)

    def unable_to_attach_file(self, *args, **kwargs):
        return wx.MessageDialog(self, _("It is not possible to add more attachments. Please take into account that You can add only a maximum of 4 images, or one audio, video or poll  per post. Please remove other attachments before continuing."), _("Error adding attachment"), wx.ICON_ERROR).ShowModal()

    def unable_to_attach_poll(self, *args, **kwargs):
        return wx.MessageDialog(self, _("You can add a poll or media files. In order to add your poll, please remove other attachments first."), _("Error adding poll"), wx.ICON_ERROR).ShowModal()

class viewPost(wx.Dialog):
    def set_title(self, lenght):
        self.SetTitle(_("Post - %i characters ") % (lenght,))

    def __init__(self, text="", boosts_count=0, favs_count=0, source="", date="", privacy="", *args, **kwargs):
        super(viewPost, self).__init__(parent=None, id=wx.ID_ANY, size=(850,850))
        panel = wx.Panel(self)
        label = wx.StaticText(panel, -1, _("Post"))
        self.text = wx.TextCtrl(panel, -1, text, style=wx.TE_READONLY|wx.TE_MULTILINE, size=(250, 180))
        self.text.SetFocus()
        textBox = wx.BoxSizer(wx.HORIZONTAL)
        textBox.Add(label, 0, wx.ALL, 5)
        textBox.Add(self.text, 1, wx.EXPAND, 5)
        mainBox = wx.BoxSizer(wx.VERTICAL)
        mainBox.Add(textBox, 0, wx.ALL, 5)
        label2 = wx.StaticText(panel, -1, _("Image description"))
        self.image_description = wx.TextCtrl(panel, -1, style=wx.TE_READONLY|wx.TE_MULTILINE, size=(250, 180))
        self.image_description.Enable(False)
        iBox = wx.BoxSizer(wx.HORIZONTAL)
        iBox.Add(label2, 0, wx.ALL, 5)
        iBox.Add(self.image_description, 1, wx.EXPAND, 5)
        mainBox.Add(iBox, 0, wx.ALL, 5)
        privacyLabel = wx.StaticText(panel, -1, _("Privacy"))
        privacy = wx.TextCtrl(panel, -1, privacy, size=wx.DefaultSize, style=wx.TE_READONLY|wx.TE_MULTILINE)
        privacyBox = wx.BoxSizer(wx.HORIZONTAL)
        privacyBox.Add(privacyLabel, 0, wx.ALL, 5)
        privacyBox.Add(privacy, 0, wx.ALL, 5)
        boostsCountLabel = wx.StaticText(panel, -1, _(u"Boosts: "))
        boostsCount = wx.TextCtrl(panel, -1, str(boosts_count), size=wx.DefaultSize, style=wx.TE_READONLY|wx.TE_MULTILINE)
        boostBox = wx.BoxSizer(wx.HORIZONTAL)
        boostBox.Add(boostsCountLabel, 0, wx.ALL, 5)
        boostBox.Add(boostsCount, 0, wx.ALL, 5)
        favsCountLabel = wx.StaticText(panel, -1, _("Favorites: "))
        favsCount = wx.TextCtrl(panel, -1, str(favs_count), size=wx.DefaultSize, style=wx.TE_READONLY|wx.TE_MULTILINE)
        favsBox = wx.BoxSizer(wx.HORIZONTAL)
        favsBox.Add(favsCountLabel, 0, wx.ALL, 5)
        favsBox.Add(favsCount, 0, wx.ALL, 5)
        sourceLabel = wx.StaticText(panel, -1, _("Source: "))
        source = wx.TextCtrl(panel, -1, source, size=wx.DefaultSize, style=wx.TE_READONLY|wx.TE_MULTILINE)
        sourceBox = wx.BoxSizer(wx.HORIZONTAL)
        sourceBox.Add(sourceLabel, 0, wx.ALL, 5)
        sourceBox.Add(source, 0, wx.ALL, 5)
        dateLabel = wx.StaticText(panel, -1, _(u"Date: "))
        date = wx.TextCtrl(panel, -1, date, size=wx.DefaultSize, style=wx.TE_READONLY|wx.TE_MULTILINE)
        dateBox = wx.BoxSizer(wx.HORIZONTAL)
        dateBox.Add(dateLabel, 0, wx.ALL, 5)
        dateBox.Add(date, 0, wx.ALL, 5)
        infoBox = wx.BoxSizer(wx.HORIZONTAL)
        infoBox.Add(privacyBox, 0, wx.ALL, 5)
        infoBox.Add(boostBox, 0, wx.ALL, 5)
        infoBox.Add(favsBox, 0, wx.ALL, 5)
        infoBox.Add(sourceBox, 0, wx.ALL, 5)
        mainBox.Add(infoBox, 0, wx.ALL, 5)
        mainBox.Add(dateBox, 0, wx.ALL, 5)
        self.share = wx.Button(panel, wx.ID_ANY, _("Copy link to clipboard"))
        self.share.Enable(False)
        self.spellcheck = wx.Button(panel, -1, _("Check &spelling..."), size=wx.DefaultSize)
        self.translateButton = wx.Button(panel, -1, _(u"&Translate..."), size=wx.DefaultSize)
        cancelButton = wx.Button(panel, wx.ID_CANCEL, _(u"C&lose"), size=wx.DefaultSize)
        cancelButton.SetDefault()
        buttonsBox = wx.BoxSizer(wx.HORIZONTAL)
        buttonsBox.Add(self.share, 0, wx.ALL, 5)
        buttonsBox.Add(self.spellcheck, 0, wx.ALL, 5)
        buttonsBox.Add(self.translateButton, 0, wx.ALL, 5)
        buttonsBox.Add(cancelButton, 0, wx.ALL, 5)
        mainBox.Add(buttonsBox, 0, wx.ALL, 5)
        selectId = wx.ID_ANY
        self.Bind(wx.EVT_MENU, self.onSelect, id=selectId)
        self.accel_tbl = wx.AcceleratorTable([
            (wx.ACCEL_CTRL, ord('A'), selectId),
        ])
        self.SetAcceleratorTable(self.accel_tbl)
        panel.SetSizer(mainBox)
        self.SetClientSize(mainBox.CalcMin())

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
        super(viewText, self).__init__(parent=None, id=wx.ID_ANY, size=(850,850), title=title)
        panel = wx.Panel(self)
        label = wx.StaticText(panel, -1, _("Text"))
        self.text = wx.TextCtrl(panel, -1, text, style=wx.TE_READONLY|wx.TE_MULTILINE, size=(250, 180))
        self.text.SetFocus()
        textBox = wx.BoxSizer(wx.HORIZONTAL)
        textBox.Add(label, 0, wx.ALL, 5)
        textBox.Add(self.text, 1, wx.EXPAND, 5)
        mainBox = wx.BoxSizer(wx.VERTICAL)
        mainBox.Add(textBox, 0, wx.ALL, 5)
        self.spellcheck = wx.Button(panel, -1, _("Check &spelling..."), size=wx.DefaultSize)
        self.translateButton = wx.Button(panel, -1, _(u"&Translate..."), size=wx.DefaultSize)
        cancelButton = wx.Button(panel, wx.ID_CANCEL, _(u"C&lose"), size=wx.DefaultSize)
        cancelButton.SetDefault()
        buttonsBox = wx.BoxSizer(wx.HORIZONTAL)
        buttonsBox.Add(self.spellcheck, 0, wx.ALL, 5)
        buttonsBox.Add(self.translateButton, 0, wx.ALL, 5)
        buttonsBox.Add(cancelButton, 0, wx.ALL, 5)
        mainBox.Add(buttonsBox, 0, wx.ALL, 5)
        panel.SetSizer(mainBox)
        self.SetClientSize(mainBox.CalcMin())

class poll(wx.Dialog):
    def __init__(self, *args, **kwds):
        super(poll, self).__init__(parent=None, id=wx.NewId(), title=_("Add a poll"))
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        period_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1.Add(period_sizer, 1, wx.EXPAND, 0)
        label_period = wx.StaticText(self, wx.ID_ANY, _("Participation time"))
        period_sizer.Add(label_period, 0, 0, 0)
        self.period = wx.ComboBox(self, wx.ID_ANY, choices=[_("5 minutes"), _("30 minutes"), _("1 hour"), _("6 hours"), _("1 day"), _("2 days"), _("3 days"), _("4 days"), _("5 days"), _("6 days"), _("7 days")], style=wx.CB_DROPDOWN | wx.CB_READONLY | wx.CB_SIMPLE)
        self.period.SetFocus()
        self.period.SetSelection(0)
        period_sizer.Add(self.period, 0, 0, 0)
        sizer_2 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, _("Choices")), wx.VERTICAL)
        sizer_1.Add(sizer_2, 1, wx.EXPAND, 0)
        option1_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(option1_sizer, 1, wx.EXPAND, 0)
        label_2 = wx.StaticText(self, wx.ID_ANY, _("Option 1"))
        option1_sizer.Add(label_2, 0, 0, 0)
        self.option1 = wx.TextCtrl(self, wx.ID_ANY, "")
        self.option1.SetMaxLength(25)
        option1_sizer.Add(self.option1, 0, 0, 0)
        option2_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(option2_sizer, 1, wx.EXPAND, 0)
        label_3 = wx.StaticText(self, wx.ID_ANY, _("Option 2"))
        option2_sizer.Add(label_3, 0, 0, 0)
        self.option2 = wx.TextCtrl(self, wx.ID_ANY, "")
        self.option2.SetMaxLength(25)
        option2_sizer.Add(self.option2, 0, 0, 0)
        option3_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(option3_sizer, 1, wx.EXPAND, 0)
        label_4 = wx.StaticText(self, wx.ID_ANY, _("Option 3"))
        option3_sizer.Add(label_4, 0, 0, 0)
        self.option3 = wx.TextCtrl(self, wx.ID_ANY, "")
        self.option3.SetMaxLength(25)
        option3_sizer.Add(self.option3, 0, 0, 0)
        option4_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(option4_sizer, 1, wx.EXPAND, 0)
        label_5 = wx.StaticText(self, wx.ID_ANY, _("Option 4"))
        option4_sizer.Add(label_5, 0, 0, 0)
        self.option4 = wx.TextCtrl(self, wx.ID_ANY, "")
        self.option4.SetMaxLength(25)
        option4_sizer.Add(self.option4, 0, 0, 0)
        self.multiple = wx.CheckBox(self, wx.ID_ANY, _("Allow multiple choices per user"))
        self.multiple.SetValue(False)
        sizer_1.Add(self.multiple, 0, wx.ALL, 5)
        self.hide_votes = wx.CheckBox(self, wx.ID_ANY, _("Hide votes count until the poll expires"))
        self.hide_votes.SetValue(False)
        sizer_1.Add(self.hide_votes, 0, wx.ALL, 5)
        btn_sizer = wx.StdDialogButtonSizer()
        sizer_1.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 4)
        self.button_OK = wx.Button(self, wx.ID_OK)
        self.button_OK.SetDefault()
        self.button_OK.Bind(wx.EVT_BUTTON, self.validate_data)
        btn_sizer.AddButton(self.button_OK)
        self.button_CANCEL = wx.Button(self, wx.ID_CANCEL, "")
        btn_sizer.AddButton(self.button_CANCEL)
        btn_sizer.Realize()
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.SetAffirmativeId(self.button_OK.GetId())
        self.SetEscapeId(self.button_CANCEL.GetId())
        self.Layout()

    def get_options(self):
        controls = [self.option1, self.option2, self.option3, self.option4]
        options = [option.GetValue() for option in controls if option.GetValue() != ""]
        return options

    def validate_data(self, *args, **kwargs):
        options = self.get_options()
        if len(options) < 2:
            return wx.MessageDialog(self, _("Please make sure you have provided at least two options for the poll."), _("Not enough information"), wx.ICON_ERROR).ShowModal()
        self.EndModal(wx.ID_OK)

class attachedPoll(wx.Dialog):
    def __init__(self, poll_options, multiple=False, *args, **kwds):
        super(attachedPoll, self).__init__(parent=None, id=wx.NewId(), title=_("Vote in this poll"))
        self.poll_options = poll_options
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, _("Options")), wx.VERTICAL)
        sizer_1.Add(sizer_2, 1, wx.EXPAND, 0)
        if multiple == False:
            for option in range(len(self.poll_options)):
                if option == 0:
                    setattr(self, "option{}".format(option), wx.RadioButton(self, wx.ID_ANY, poll_options[option],  style=wx.RB_GROUP))
                else:
                    setattr(self, "option{}".format(option), wx.RadioButton(self, wx.ID_ANY, poll_options[option]))
        else:
            for option in range(len(self.poll_options)):
                setattr(self, "option{}".format(option), wx.CheckBox(self, wx.ID_ANY, poll_options[option]))
            sizer_2.Add(getattr(self, "option{}".format(option)), 1, wx.EXPAND, 0)
        btn_sizer = wx.StdDialogButtonSizer()
        sizer_1.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 4)
        self.button_OK = wx.Button(self, wx.ID_OK)
        self.button_OK.SetDefault()
        btn_sizer.AddButton(self.button_OK)
        self.button_CANCEL = wx.Button(self, wx.ID_CANCEL, "")
        btn_sizer.AddButton(self.button_CANCEL)
        btn_sizer.Realize()
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.SetAffirmativeId(self.button_OK.GetId())
        self.SetEscapeId(self.button_CANCEL.GetId())
        self.Layout()

    def get_selected(self):
        options = []
        for option in range(len(self.poll_options)):
            if getattr(self, "option{}".format(option)).GetValue() == True:
                options.append(option)
        return options

