# -*- coding: utf-8 -*-
import storage
import wx
import wx_manage

class autocompletionManage(object):
 def __init__(self, window):
  super(autocompletionManage, self).__init__()
  self.window = window
  self.dialog = wx_manage.autocompletionManageDialog()
  self.database = storage.storage()
  self.users = self.database.get_all_users()
  self.dialog.put_users(self.users)
  self.dialog.add.Bind(wx.EVT_BUTTON, self.add_user)
  self.dialog.remove.Bind(wx.EVT_BUTTON, self.remove_user)
  self.dialog.ShowModal()

 def update_list(self):
  item = self.dialog.users.get_selected()
  self.dialog.users.clear()
  self.users = self.database.get_all_users()
  self.dialog.put_users(self.users)
  self.dialog.users.select_item(item)

 def add_user(self, event=None):
  usr = self.dialog.get_user()
  if usr == False:
   return
  try:
   data = self.window.twitter.twitter.show_user(screen_name=usr)
  except:
   self.dialog.show_invalid_user_error()
   return
  self.database.set_user(data["screen_name"], data["name"], 0)
  self.update_list()

 def remove_user(self, ev):
  ask = wx.MessageDialog(None, _(u"Are you sure you want to delete this user from the database? This user will not appear on the autocomplete results anymore."), _(u"Confirm"), wx.YES_NO|wx.ICON_QUESTION)
  if ask.ShowModal() == wx.ID_YES:
   item = self.dialog.users.get_selected()
   user = self.users[item]
   self.database.remove_user(user[0])
   self.update_list()