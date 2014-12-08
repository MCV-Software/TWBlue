# -*- coding: utf-8 -*-
import wx
import gui
import config
from sessionmanager import gui as sessionManagerUI

class switcher(object):
 def __init__(self, window):
  self.hold_window = window
  self.hold_window.Hide()
  sessionManagerWindow = sessionManagerUI.sessionManagerWindow()
  if sessionManagerWindow.ShowModal() == wx.ID_OK:
   self.hold_window.Destroy()
   self.window = gui.main.mainFrame()
   self.window.Show()
   self.window.showing = True
   if config.main != None and config.main["general"]["hide_gui"] == True:
    self.window.show_hide()
    self.window.Hide()
   wx.GetApp().SetTopWindow(self.window)
  else:
   self.hold_window.Show()
   