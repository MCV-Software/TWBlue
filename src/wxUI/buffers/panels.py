# -*- coding: utf-8 -*-
import wx
from multiplatform_widgets import widgets

class accountPanel(wx.Panel):
 def __init__(self, parent, name=None):
  super(accountPanel, self).__init__(parent=parent)
  self.name = name
  self.type = "account"
  sizer = wx.BoxSizer(wx.VERTICAL)
  self.list = widgets.list(self, _(u"Announce"))
  sizer.Add(self.list.list, 0, wx.ALL, 5)
  self.SetSizer(sizer)

class emptyPanel(accountPanel):
 def __init__(self, parent, name):
  super(emptyPanel, self).__init__(parent=parent, name=name)
  self.type = "empty"