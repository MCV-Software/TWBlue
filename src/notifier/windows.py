# -*- coding: utf-8 -*-
from builtins import object
import wx

class notification(object):

 def notify(self, title, text):
  wx.NotificationMessage(title, text).Show()