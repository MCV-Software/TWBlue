# -*- coding: utf-8 -*-
import baseDialog
import wx

class searchDialog(baseDialog.BaseWXDialog):
 def __init__(self, value=""):
  super(searchDialog, self).__init__(None, -1)
  panel = wx.Panel(self)
  sizer = wx.BoxSizer(wx.VERTICAL)
  self.SetTitle(_(u"Search on Twitter"))
  label = wx.StaticText(panel, -1, _(u"Search"))
  self.term = wx.TextCtrl(panel, -1, value)
  dc = wx.WindowDC(self.term)
  dc.SetFont(self.term.GetFont())
  self.term.SetSize(dc.GetTextExtent("0"*40))
  sizer.Add(label, 0, wx.ALL, 5)
  sizer.Add(self.term, 0, wx.ALL, 5)
  self.tweets = wx.RadioButton(panel, -1, _(u"Tweets"), style=wx.RB_GROUP)
  self.users = wx.RadioButton(panel, -1, _(u"Users"))
  radioSizer = wx.BoxSizer(wx.HORIZONTAL)
  radioSizer.Add(self.tweets, 0, wx.ALL, 5)
  radioSizer.Add(self.users, 0, wx.ALL, 5)
  sizer.Add(radioSizer, 0, wx.ALL, 5)
  ok = wx.Button(panel, wx.ID_OK, _(u"OK"))
  ok.SetDefault()
  cancel = wx.Button(panel, wx.ID_CANCEL, _(u"Close"))
  btnsizer = wx.BoxSizer()
  btnsizer.Add(ok, 0, wx.ALL, 5)
  btnsizer.Add(cancel, 0, wx.ALL, 5)
  sizer.Add(btnsizer, 0, wx.ALL, 5)
  panel.SetSizer(sizer)
  self.SetClientSize(sizer.CalcMin())