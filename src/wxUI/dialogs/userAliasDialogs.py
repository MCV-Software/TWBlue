# -*- coding: utf-8 -*-
import wx
from . import baseDialog

class addAliasDialog(baseDialog.BaseWXDialog):
    def __init__(self, title, users):
        super(addAliasDialog, self).__init__(parent=None, id=wx.ID_ANY, title=title)
        panel = wx.Panel(self)
        userSizer = wx.BoxSizer()
        self.cb = wx.ComboBox(panel, -1, choices=users, value=users[0], size=wx.DefaultSize)
        self.cb.SetFocus()
        self.autocompletion = wx.Button(panel, -1, _(u"&Autocomplete users"))
        userSizer.Add(wx.StaticText(panel, -1, _(u"User")), 0, wx.ALL, 5)
        userSizer.Add(self.cb, 0, wx.ALL, 5)
        userSizer.Add(self.autocompletion, 0, wx.ALL, 5)
        aliasSizer = wx.BoxSizer(wx.HORIZONTAL)
        aliasLabel = wx.StaticText(panel, wx.ID_ANY, _("Alias"))
        self.alias = wx.TextCtrl(panel, wx.ID_ANY)
        aliasSizer.Add(aliasLabel, 0, wx.ALL, 5)
        aliasSizer.Add(self.alias, 0, wx.ALL, 5)
        sizer = wx.BoxSizer(wx.VERTICAL)
        ok = wx.Button(panel, wx.ID_OK, _(u"OK"))
        ok.SetDefault()
        cancel = wx.Button(panel, wx.ID_CANCEL, _(u"Close"))
        btnsizer = wx.BoxSizer()
        btnsizer.Add(ok, 0, wx.ALL, 5)
        btnsizer.Add(cancel, 0, wx.ALL, 5)
        sizer.Add(userSizer, 0, wx.ALL, 5)
        sizer.Add(aliasSizer, 0, wx.ALL, 5)
        sizer.Add(btnsizer, 0, wx.ALL, 5)
        panel.SetSizer(sizer)
        self.SetClientSize(sizer.CalcMin())

    def get_user(self):
        return (self.cb.GetValue(), self.alias.GetValue())

