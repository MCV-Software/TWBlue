# -*- coding: utf-8 -*-
import wx

class notification(object):

 def notify(self, title, text):
  wx.NotificationMessage(title, text).Show()