# -*- coding: utf-8 -*-
import baseDialog
import wx

class findDialog(baseDialog.BaseWXDialog):
 def __init__(self, value=""):
  super(findDialog, self).__init__(None, -1)
  panel = wx.Panel(self)
  sizer = wx.BoxSizer(wx.VERTICAL)
  self.SetTitle(_(u"Find in current buffer"))
  label = wx.StaticText(panel, -1, _(u"String"))
  self.string = wx.TextCtrl(panel, -1, value)
  dc = wx.WindowDC(self.string)
  dc.SetFont(self.string.GetFont())
  self.string.SetSize(dc.GetTextExtent("0"*40))
  sizer.Add(label, 0, wx.ALL, 5)
  sizer.Add(self.string, 0, wx.ALL, 5)
  ok = wx.Button(panel, wx.ID_OK, _(u"OK"))
  ok.SetDefault()
  cancel = wx.Button(panel, wx.ID_CANCEL, _(u"Cancel"))
  btnsizer = wx.BoxSizer()
  btnsizer.Add(ok, 0, wx.ALL, 5)
  btnsizer.Add(cancel, 0, wx.ALL, 5)
  sizer.Add(btnsizer, 0, wx.ALL, 5)
  panel.SetSizer(sizer)
  self.SetClientSize(sizer.CalcMin())