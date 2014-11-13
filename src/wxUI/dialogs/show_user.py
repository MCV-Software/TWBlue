# -*- coding: utf-8 -*-
import wx

class showUserProfile(wx.Dialog):
 def __init__(self, screen_name):
  super(showUserProfile, self).__init__(self, None, -1)
  self.SetTitle(_(u"Information for %s") % (screen_name))
  panel = wx.Panel(self)
  sizer = wx.BoxSizer(wx.VERTICAL)
  static = wx.StaticText(panel, -1, _(u"Details"))
  sizer.Add(static, 0, wx.ALL, 5)
  text = wx.TextCtrl(panel, -1, style=wx.TE_MULTILINE|wx.TE_READONLY)
  text.SetFocus()
  sizer.Add(text, 0, wx.ALL|wx.EXPAND, 5)
  self.url = wx.Button(panel, -1, _(u"Go to URL"), size=wx.DefaultSize)
  self.url.Disable()
  close = wx.Button(panel, wx.ID_CANCEL, _(u"Close"))
  btnSizer = wx.BoxSizer(wx.HORIZONTAL)
  btnSizer.Add(self.url, 0, wx.ALL, 5)
  btnSizer.Add(close, 0, wx.ALL, 5)
  sizer.Add(btnSizer, 0, wx.ALL, 5)
  text.ChangeValue(self.compose_string())
  text.SetSize(text.GetBestSize())
  panel.SetSizer(sizer)
  self.SetClientSize(sizer.CalcMin())

 def get_response(self):
  return self.ShowModal()