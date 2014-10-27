# -*- coding: utf-8 -*-
import dbus
import application

class notifications(object):
 """Supports notifications on Linux.
 """

 def __init__(self):
  super(notifications, self).__init__()
  self.item              = "org.freedesktop.Notifications"
  self.path              = "/org/freedesktop/Notifications"
  self.interface         = "org.freedesktop.Notifications"
  self.app_name          = application.name
  self.id_num_to_replace = 0
  self.icon              = "/usr/share/icons/Tango/32x32/status/sunny.png"

 def notify(self, title="", text=""):
  actions_list      = ''
  hint              = ''
  time              = 5000   # Use seconds x 1000
  bus = dbus.SessionBus()
  notif = bus.get_object(self.item, self.path)
  notify = dbus.Interface(notif, self.interface)
  notify.Notify(self.app_name, self.id_num_to_replace, self.icon, title, text, actions_list, hint, time)