# -*- coding: utf-8 -*-
import storage
import wx
import wx_settings
import output
from mysc.thread_utils import call_threaded

class autocompletionSettings(object):
 def __init__(self, window):
  super(autocompletionSettings, self).__init__()
  self.window = window
  self.dialog = wx_settings.autocompletionSettingsDialog()
  if self.dialog.ShowModal() == wx.ID_OK:
   call_threaded(self.add_users_to_database)

 def add_users_to_database(self):
  output.speak(_(u"Updating database... You can close this window now. A message will tell you when the process finishes."))
  database = storage.storage()
  if self.dialog.followers_buffer.GetValue() == True:
   buffer = self.window.search_buffer("people", "followers")
   for i in buffer.db.settings[buffer.name_buffer]:
    database.set_user(i["screen_name"], i["name"])
  if self.dialog.friends_buffer.GetValue() == True:
   buffer = self.window.search_buffer("people", "friends")
   for i in buffer.db.settings[buffer.name_buffer]:
    database.set_user(i["screen_name"], i["name"])
  wx_settings.show_success_dialog()
  self.dialog.Destroy()
  