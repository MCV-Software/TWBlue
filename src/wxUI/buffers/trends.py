# -*- coding: utf-8 -*-
import wx
from multiplatform_widgets import widgets

class trendsPanel(wx.Panel):
 def create_list(self):
  """ Returns the list for put the tweets here."""
  self.list = widgets.list(self, _("Trending topic"), style=wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.LC_VRULES)
  self.list.set_windows_size(0, 30)
  self.list.set_size()

 def __init__(self, parent, name):
  super(trendsPanel, self).__init__(parent)
  self.type = "trends"
  self.sizer = wx.BoxSizer(wx.VERTICAL)
  self.create_list()
  self.tweet = wx.Button(self, -1, _("Tweet"))
  self.tweetTrendBtn = wx.Button(self, -1, _("Tweet about this trend"))
  self.search_topic = wx.Button(self, -1, _("Search topic"))
  btnSizer = wx.BoxSizer(wx.HORIZONTAL)
  btnSizer.Add(self.tweet, 0, wx.ALL, 5)
  btnSizer.Add(self.tweetTrendBtn, 0, wx.ALL, 5)
  btnSizer.Add(self.search_topic, 0, wx.ALL, 5)
  self.sizer.Add(btnSizer, 0, wx.ALL, 5)
  self.sizer.Add(self.list.list, 0, wx.ALL, 5)
  self.SetSizer(self.sizer)

 def set_position(self, reversed=False):
  if reversed == False:
   self.list.select_item(self.list.get_count()-1)
  else:
   self.list.select_item(0)
   