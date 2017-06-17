# -*- coding: utf-8 -*-
import wx
from multiplatform_widgets import widgets

class eventsPanel(wx.Panel):
 """ Buffer to show events. Different than tweets or people."""

 def __init__(self, parent, name):
  self.type = "event"
  super(eventsPanel, self).__init__(parent)
  self.name = name
  sizer = wx.BoxSizer()
  self.list = widgets.list(self, _("Date"), _("Event"), size=(600,600), style=wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.LC_VRULES)
  self.tweet = wx.Button(self, -1, _("Tweet"))
  self.delete_event = wx.Button(self, -1, _("Remove event"))

 def set_position(self, reversed=False):
  if reversed == False:
   self.list.select_item(self.list.get_count()-1)
  else:
   self.list.select_item(0)

 def set_focus_in_list(self):
  self.list.list.SetFocus()