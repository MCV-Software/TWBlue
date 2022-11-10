""" GUI dialogs for tweet writing and displaying. """
import wx

class viewToot(wx.Dialog):
    def set_title(self, lenght):
        self.SetTitle(_("Toot - %i characters ") % (lenght,))

    def __init__(self, text="", boosts_count=0, favs_count=0, source="", date="", privacy="", *args, **kwargs):
        super(viewToot, self).__init__(parent=None, id=wx.ID_ANY, size=(850,850))
        panel = wx.Panel(self)
        label = wx.StaticText(panel, -1, _("Toot"))
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
