# -*- coding: utf-8 -*-
import wx
from multiplatform_widgets import widgets

class accountPanel(wx.Panel):
 def __init__(self, parent, name=None):
  super(accountPanel, self).__init__(parent=parent)
  self.name = name
  self.type = "account"
  sizer = wx.BoxSizer(wx.VERTICAL)
  self.login = wx.Button(self, -1, _("Login"))
  sizer.Add(self.login, 0, wx.ALL, 5)
  self.autostart_account = wx.CheckBox(self, -1, _("Log in automatically"))
  sizer.Add(self.autostart_account, 0, wx.ALL, 5)
  self.SetSizer(sizer)

 def change_login(self, login=True):
  if login == True:
   self.login.SetLabel(_("Login"))
  else:
   self.login.SetLabel(_("Logout"))

 def change_autostart(self, autostart=True):
  self.autostart_account.SetValue(autostart)

 def get_autostart(self):
  return self.autostart_account.GetValue()

class emptyPanel(wx.Panel):
 def __init__(self, parent, name):
  super(emptyPanel, self).__init__(parent=parent, name=name)
  self.name = name
  self.type = "account"
  sizer = wx.BoxSizer(wx.VERTICAL)
  self.SetSizer(sizer)
