# -*- coding: utf-8 -*-
import wx
import wxUI as view
import paths
import time
import os
import session
import manager
from config_utils import Configuration
import config

class sessionManagerController(object):
 def __init__(self):
  super(sessionManagerController, self).__init__()
  manager.setup()

 def fill_list(self):
  sessionsList = []
  self.sessions = []
  for i in os.listdir(paths.config_path()):
   if os.path.isdir(paths.config_path(i)) and i not in config.app["sessions"]["ignored_sessions"]:
    strconfig = "%s/session.conf" % (paths.config_path(i))
    config_test = Configuration(strconfig)
    name = config_test["twitter"]["user_name"]
    if name != "" and config_test["twitter"]["user_key"] != "" and config_test["twitter"]["user_secret"] != "":
     sessionsList.append(name)
     self.sessions.append(i)
  if hasattr(self, "view"): self.view.fill_list(sessionsList)

 def show(self):
  self.view = view.sessionManagerWindow(self)
  if self.view.ShowModal() == wx.ID_CANCEL:
   self.view.Destroy()

 def do_ok(self):
  for i in self.sessions:
   s = session.Session(i)
   s.get_configuration()
   s.login()
   session.sessions[i] = s

 def manage_new_account(self):
  location = (str(time.time())[:6])
  s = session.Session(location)
  manager.manager.add_session(location)
  s.get_configuration()
  try:
   s.authorise()
   self.sessions.append(location)
   self.view.add_new_session_to_list()
  except:
   self.view.show_unauthorised_error()
   return