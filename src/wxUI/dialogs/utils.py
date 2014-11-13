# -*- coding: utf-8 -*-
import wx

class selectUserDialog(wx.Dialog):
 def __init__(self, users, *args, **kwargs):
  super(selectUserDialog, self).__init__(self, None, -1, *args, **kwargs)
  panel = wx.Panel(self)
  userSizer = wx.BoxSizer()
  self.cb = wx.ComboBox(panel, -1, choices=users, value=users[0], size=wx.DefaultSize)
  self.cb.SetFocus()
  userSizer.Add(wx.StaticText(panel, -1, _(u"User")), 0, wx.ALL, 5)
  userSizer.Add(self.cb)
  sizer = wx.BoxSizer(wx.VERTICAL)
  ok = wx.Button(panel, wx.ID_OK, _(u"OK"))
  ok.SetDefault()
  cancel = wx.Button(panel, wx.ID_CANCEL, _(u"Close"))
  btnsizer = wx.BoxSizer()
  btnsizer.Add(ok, 0, wx.ALL, 5)
  btnsizer.Add(cancel, 0, wx.ALL, 5)
  sizer.Add(userSizer, 0, wx.ALL, 5)
  sizer.Add(btnsizer, 0, wx.ALL, 5)
  panel.SetSizer(sizer)
  self.SetClientSize(sizer.CalcMin())

 def get_selection(self):
  return self.cb.GetValue()

 def get_response(self):
  return self.ShowModal()