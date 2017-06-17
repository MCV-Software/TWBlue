# -*- coding: utf-8 -*-
import wx
from multiplatform_widgets import widgets

class basePanel(wx.Panel):
 
 def set_focus_function(self, f):
  self.list.list.Bind(wx.EVT_LIST_ITEM_FOCUSED, f)

 def create_list(self):
  self.list = widgets.list(self, _("User"), _("Text"), _("Date"), _("Client"), style=wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.LC_VRULES)
  self.list.set_windows_size(0, 60)
  self.list.set_windows_size(1, 320)
  self.list.set_windows_size(2, 110)
  self.list.set_windows_size(3, 84)
  self.list.set_size()

 def __init__(self, parent, name):
  super(basePanel, self).__init__(parent)
  self.name = name
  self.type = "baseBuffer"
  self.sizer = wx.BoxSizer(wx.VERTICAL)
  self.create_list()
  self.tweet = wx.Button(self, -1, _("Tweet"))
  self.retweet = wx.Button(self, -1, _("Retweet"))
  self.reply = wx.Button(self, -1, _("Reply"))
  self.dm = wx.Button(self, -1, _("Direct message"))
  btnSizer = wx.BoxSizer(wx.HORIZONTAL)
  btnSizer.Add(self.tweet, 0, wx.ALL, 5)
  btnSizer.Add(self.retweet, 0, wx.ALL, 5)
  btnSizer.Add(self.reply, 0, wx.ALL, 5)
  btnSizer.Add(self.dm, 0, wx.ALL, 5)
  self.sizer.Add(btnSizer, 0, wx.ALL, 5)
  self.sizer.Add(self.list.list, 0, wx.ALL|wx.EXPAND, 5)
  self.SetSizer(self.sizer)
  self.SetClientSize(self.sizer.CalcMin())

 def set_position(self, reversed=False):
  if reversed == False:
   self.list.select_item(self.list.get_count()-1)
  else:
   self.list.select_item(0)

 def set_focus_in_list(self):
  self.list.list.SetFocus()