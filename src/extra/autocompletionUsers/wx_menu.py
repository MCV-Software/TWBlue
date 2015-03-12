# -*- coding: utf-8 -*-
import wx

class menu(wx.Menu):
 def __init__(self, window, pattern, mode):
  super(menu, self).__init__()
  self.window = window
  self.pattern = pattern
  self.mode = mode

 def append_options(self, options):
  for i in options:
   item = wx.MenuItem(self, wx.NewId(), "%s (@%s)" % (i[1], i[0]))
   self.AppendItem(item)
   self.Bind(wx.EVT_MENU, lambda evt, temp=i[0]: self.select_text(evt, temp), item)

 def select_text(self, ev, text):
  if self.mode == "tweet":
   self.window.ChangeValue(self.window.GetValue().replace("@"+self.pattern, "@"+text+" "))
  elif self.mode == "dm":
   self.window.SetValue(self.window.GetValue().replace(self.pattern, text))
  self.window.SetInsertionPointEnd()

 def destroy(self):
  self.Destroy()