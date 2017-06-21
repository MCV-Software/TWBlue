# -*- coding: utf-8 -*-
""" A cross platform notification system.
Under Linux, the wx.NotificationMessage does not show a notification on the taskbar, so we decided to use dbus for showing notifications for linux and wx for Windows."""

import platform

notify = None

def setup():
 global notify
 if platform.system() == "Windows":
  from . import windows
  notify = windows.notification()
 elif platform.system() == "Linux":
  from . import linux
  notify = linux.notification()

def send(title, text):
 global notify
 if not notify or notify is None:
  setup()
 notify.notify(title, text)