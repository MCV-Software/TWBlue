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
  self.list = widgets.list(self, _(u"Date"), _(u"Event"), size=(600,600), style=wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.LC_VRULES)
  self.tweet = wx.Button(self, -1, _(u"Tweet"))
  self.delete_event = wx.Button(self, -1, _(u"Remove event"))
