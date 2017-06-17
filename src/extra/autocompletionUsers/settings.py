# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
from builtins import object
from . import storage
import widgetUtils
from . import wx_settings
from . import manage
import output
from mysc.thread_utils import call_threaded

class autocompletionSettings(object):
 def __init__(self, config, buffer, window):
  super(autocompletionSettings, self).__init__()
  self.config = config
  self.buffer = buffer
  self.window = window
  self.dialog = wx_settings.autocompletionSettingsDialog()
  self.dialog.set("friends_buffer", self.config["mysc"]["save_friends_in_autocompletion_db"])
  self.dialog.set("followers_buffer", self.config["mysc"]["save_followers_in_autocompletion_db"])
  widgetUtils.connect_event(self.dialog.viewList, widgetUtils.BUTTON_PRESSED, self.view_list)
  if self.dialog.get_response() == widgetUtils.OK:
   call_threaded(self.add_users_to_database)

 def add_users_to_database(self):
  self.config["mysc"]["save_friends_in_autocompletion_db"] = self.dialog.get("friends_buffer")
  self.config["mysc"]["save_followers_in_autocompletion_db"] = self.dialog.get("followers_buffer")
  output.speak(_("Updating database... You can close this window now. A message will tell you when the process finishes."))
  database = storage.storage(self.buffer.session.session_id)
  if self.dialog.get("followers_buffer") == True:
   buffer = self.window.search_buffer("followers", self.config["twitter"]["user_name"])
   for i in buffer.session.db[buffer.name]["items"]:
    database.set_user(i["screen_name"], i["name"], 1)
  else:
   database.remove_by_buffer(1)
  if self.dialog.get("friends_buffer") == True:
   buffer = self.window.search_buffer("friends", self.config["twitter"]["user_name"])
   for i in buffer.session.db[buffer.name]["items"]:
    database.set_user(i["screen_name"], i["name"], 2)
  else:
   database.remove_by_buffer(2)
  wx_settings.show_success_dialog()
  self.dialog.destroy()
  
 def view_list(self, ev):
  q = manage.autocompletionManage(self.buffer.session)


def execute_at_startup(window, buffer, config):
 database = storage.storage(buffer.session.session_id)
 if config["mysc"]["save_followers_in_autocompletion_db"] == True and config["other_buffers"]["show_followers"] == True:
  buffer = window.search_buffer("followers", config["twitter"]["user_name"])
  for i in buffer.session.db[buffer.name]:
   database.set_user(i["screen_name"], i["name"], 1)
 else:
  database.remove_by_buffer(1)
 if config["mysc"]["save_friends_in_autocompletion_db"] == True and config["other_buffers"]["show_friends"] == True:
  buffer = window.search_buffer("friends", config["twitter"]["user_name"])
  for i in buffer.session.db[buffer.name]:
   database.set_user(i["screen_name"], i["name"], 2)
 else:
  database.remove_by_buffer(2)  