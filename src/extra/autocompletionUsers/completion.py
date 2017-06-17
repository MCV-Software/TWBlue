# -*- coding: utf-8 -*-

from builtins import object
import output
from . import storage
from . import wx_menu

class autocompletionUsers(object):
 def __init__(self, window, session_id):
  super(autocompletionUsers, self).__init__()
  self.window = window
  self.db = storage.storage(session_id)

 def show_menu(self, mode="tweet"):
  position = self.window.get_position()
  if mode == "tweet":
   text = self.window.get_text()
   text = text[:position]
   try:
    pattern = text.split()[-1]
   except IndexError:
    output.speak(_("You have to start writing"))
    return
   if pattern.startswith("@") == True:
    menu = wx_menu.menu(self.window.text, pattern[1:], mode=mode)
    users = self.db.get_users(pattern[1:])
    if len(users) > 0:
     menu.append_options(users)
     self.window.popup_menu(menu)
     menu.destroy()
    else:
     output.speak(_("There are no results in your users database"))
   else:
    output.speak(_("Autocompletion only works for users."))
  elif mode == "dm":
   text = self.window.get_user()
   try:
    pattern = text.split()[-1]
   except IndexError:
    output.speak(_("You have to start writing"))
    return
   menu = wx_menu.menu(self.window.cb, pattern, mode=mode)
   users = self.db.get_users(pattern)
   if len(users) > 0:
    menu.append_options(users)
    self.window.popup_menu(menu)
    menu.destroy()
   else:
    output.speak(_("There are no results in your users database"))