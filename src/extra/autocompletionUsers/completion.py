# -*- coding: utf-8 -*-
import storage
import output
import wx_menu

class autocompletionUsers(object):
 def __init__(self, window):
  super(autocompletionUsers, self).__init__()
  self.window = window

 def show_menu(self):
  position = self.window.text.GetInsertionPoint()
  text = self.window.text.GetValue()
  text = text[:position]
  try:
   pattern = text.split()[-1]
  except IndexError:
   output.speak(_(u"You have to start to write"))
   return
  if pattern.startswith("@") == True:
   db = storage.storage()
   menu = wx_menu.menu(self.window.text, pattern[1:])
   users = db.get_users(pattern[1:])
   if len(users) > 0:
    menu.append_options(users)
    self.window.PopupMenu(menu, self.window.text.GetPosition())
    menu.Destroy()
   else:
    output.speak(_(u"There is not results in your users database"))
  else:
   output.speak(_(u"Autocompletion only works for users."))