# -*- coding: utf-8 -*-

import wx
from . import baseDialog

class showUserProfile(baseDialog.BaseWXDialog):
 def __init__(self):
  super(showUserProfile, self).__init__(parent=None, id=wx.NewId())
  panel = wx.Panel(self)
  sizer = wx.BoxSizer(wx.VERTICAL)
  static = wx.StaticText(panel, -1, _("Details"))
  sizer.Add(static, 0, wx.ALL, 5)
  self.text = wx.TextCtrl(panel, -1, style=wx.TE_MULTILINE|wx.TE_READONLY, size=(350, 250))
  self.text.SetFocus()
  sizer.Add(self.text, 0, wx.ALL|wx.EXPAND, 5)
  self.url = wx.Button(panel, -1, _("&Go to URL"), size=wx.DefaultSize)
  self.url.Disable()
  close = wx.Button(panel, wx.ID_CANCEL, _("&Close"))
  btnSizer = wx.BoxSizer(wx.HORIZONTAL)
  btnSizer.Add(self.url, 0, wx.ALL, 5)
  btnSizer.Add(close, 0, wx.ALL, 5)
  sizer.Add(btnSizer, 0, wx.ALL, 5)
  panel.SetSizer(sizer)
  self.SetClientSize(sizer.CalcMin())

 def enable_url(self, enabled=True):
  self.url.Enable(enabled)