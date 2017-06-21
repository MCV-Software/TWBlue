# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
from builtins import object
from . import storage
import widgetUtils
from . import wx_manage
from wxUI import commonMessageDialogs

class autocompletionManage(object):
 def __init__(self, session):
  super(autocompletionManage, self).__init__()
  self.session = session
  self.dialog = wx_manage.autocompletionManageDialog()
  self.database = storage.storage(self.session.session_id)
  self.users = self.database.get_all_users()
  self.dialog.put_users(self.users)
  widgetUtils.connect_event(self.dialog.add, widgetUtils.BUTTON_PRESSED, self.add_user)
  widgetUtils.connect_event(self.dialog.remove, widgetUtils.BUTTON_PRESSED, self.remove_user)
  self.dialog.get_response()

 def update_list(self):
  item = self.dialog.users.get_selected()
  self.dialog.users.clear()
  self.users = self.database.get_all_users()
  self.dialog.put_users(self.users)
  self.dialog.users.select_item(item)

 def add_user(self, *args, **kwargs):
  usr = self.dialog.get_user()
  if usr == False:
   return
  try:
   data = self.session.twitter.twitter.show_user(screen_name=usr)
  except:
   self.dialog.show_invalid_user_error()
   return
  self.database.set_user(data["screen_name"], data["name"], 0)
  self.update_list()

 def remove_user(self, ev):
  if commonMessageDialogs.delete_user_from_db() == widgetUtils.YES:
   item = self.dialog.users.get_selected()
   user = self.users[item]
   self.database.remove_user(user[0])
   self.update_list()