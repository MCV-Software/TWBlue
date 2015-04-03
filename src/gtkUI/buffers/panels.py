# -*- coding: utf-8 -*-
from gi.repository import Gtk
import widgetUtils

class accountPanel(Gtk.VBox):
 def __init__(self, parent, name=None):
  super(accountPanel, self).__init__(spacing=5)
  self.name = name
  self.type = "account"
  self.login = Gtk.Button(_(u"Login"))
  self.add(self.login)
  self.autostart_account = Gtk.ToggleButton(_(u"Start account automatically"))
  self.add(self.autostart_account)

 def change_login(self, login=True):
  if login == True:
   self.login.set_label(_(u"Login"))
  else:
   self.login.set_label(_(u"Logout"))

 def change_autostart(self, autostart=True):
  self.autostart_account.set_active(autostart)

 def get_autostart(self):
  return self.autostart_account.get_active()

class emptyPanel(Gtk.VBox):
 def __init__(self, parent, name):
  super(emptyPanel, self).__init__(spacing=6)
  self.name = name
  self.type = "account"

