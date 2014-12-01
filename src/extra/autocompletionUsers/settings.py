# -*- coding: utf-8 -*-
import storage
import wx
import config
import wx_settings
import output
from mysc.thread_utils import call_threaded

class autocompletionSettings(object):
 def __init__(self, window):
  super(autocompletionSettings, self).__init__()
  self.window = window
  self.dialog = wx_settings.autocompletionSettingsDialog()
  self.dialog.friends_buffer.SetValue(config.main["mysc"]["save_friends_in_autocompletion_db"])
  self.dialog.followers_buffer.SetValue(config.main["mysc"]["save_followers_in_autocompletion_db"])
  if self.dialog.ShowModal() == wx.ID_OK:
   call_threaded(self.add_users_to_database)

 def add_users_to_database(self):
  config.main["mysc"]["save_friends_in_autocompletion_db"] = self.dialog.friends_buffer.GetValue()
  config.main["mysc"]["save_followers_in_autocompletion_db"] = self.dialog.friends_buffer.GetValue()
  output.speak(_(u"Updating database... You can close this window now. A message will tell you when the process finishes."))
  database = storage.storage()
  if self.dialog.followers_buffer.GetValue() == True:
   buffer = self.window.search_buffer("people", "followers")
   for i in buffer.db.settings[buffer.name_buffer]:
    database.set_user(i["screen_name"], i["name"], 1)
  else:
   database.remove_by_buffer(1)
  if self.dialog.friends_buffer.GetValue() == True:
   buffer = self.window.search_buffer("people", "friends")
   for i in buffer.db.settings[buffer.name_buffer]:
    database.set_user(i["screen_name"], i["name"], 2)
  else:
   database.remove_by_buffer(2)
  wx_settings.show_success_dialog()
  self.dialog.Destroy()
  