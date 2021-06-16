# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import wx

class authorisationDialog(wx.Dialog):
    def __init__(self):
        super(authorisationDialog, self).__init__(parent=None, title=_(u"Authorising account..."))
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        static = wx.StaticText(panel, wx.NewId(), _(u"Enter your PIN code here"))
        self.text = wx.TextCtrl(panel, -1)
        self.ok = wx.Button(panel, wx.ID_OK)
        self.cancel = wx.Button(panel, wx.ID_CANCEL)
        sizer.Add(self.text, 0, wx.ALL, 5)
        sizer.Add(self.cancel, 0, wx.ALL, 5)
        panel.SetSizer(sizer)
        min = sizer.CalcMin()
        self.SetClientSize(min)
