# -*- coding: utf-8 -*-
import shutil
import widgetUtils
import platform
if platform.system() == "Windows":
 import wxUI as view
elif platform.system() == "Linux":
 import gtkUI as view
import paths
import time
import os
import logging
import session
import manager
import config_utils
import config

log = logging.getLogger("sessionmanager.sessionManager")

class sessionManagerController(object):
 def __init__(self):
  super(sessionManagerController, self).__init__()
  log.debug("Setting up the session manager.")
  manager.setup()
  self.view = view.sessionManagerWindow()
  widgetUtils.connect_event(self.view.new, widgetUtils.BUTTON_PRESSED, self.manage_new_account)
  widgetUtils.connect_event(self.view.remove, widgetUtils.BUTTON_PRESSED, self.remove)
  self.new_sessions = {}
  self.removed_sessions = []

 def fill_list(self):
  sessionsList = []
  log.debug("Filling the sessions list.")
  self.sessions = []
  for i in os.listdir(paths.config_path()):
   if os.path.isdir(paths.config_path(i)):
    log.debug("Adding session %s" % (i,))
    strconfig = "%s/session.conf" % (paths.config_path(i))
    config_test = config_utils.load_config(strconfig)
    name = config_test["twitter"]["user_name"]
    if config_test["twitter"]["user_key"] != "" and config_test["twitter"]["user_secret"] != "":
     sessionsList.append(name)
     self.sessions.append(i)
#   else:
#    log.debug("Ignoring session %s" % (i,))
  self.view.fill_list(sessionsList)

 def show(self):
  if self.view.get_response() == widgetUtils.OK:
   self.do_ok()
#  else:
  self.view.destroy()

 def do_ok(self):
  log.debug("Starting sessions...")
  for i in self.sessions:
   if session.sessions.has_key(i) == True: continue
   s = session.Session(i)
   s.get_configuration()
   if i not in config.app["sessions"]["ignored_sessions"]:
    s.login()
   session.sessions[i] = s
   self.new_sessions[i] = s
#  self.view.destroy()

 def manage_new_account(self, *args, **kwargs):
  if self.view.new_account_dialog() == widgetUtils.YES:
   location = (str(time.time())[-6:])
   log.debug("Creating session in the %s path" % (location,))
   s = session.Session(location)
   manager.manager.add_session(location)
   s.get_configuration()
#   try:
   s.authorise()
   self.sessions.append(location)
   self.view.add_new_session_to_list()
#   except:
#    log.exception("Error authorising the session")
#    self.view.show_unauthorised_error()
#    return

 def remove(self, *args, **kwargs):
  if self.view.remove_account_dialog() == widgetUtils.YES:
   selected_account = self.sessions[self.view.get_selected()]
   self.view.remove_session(self.view.get_selected())
   self.removed_sessions.append(selected_account)
   self.sessions.remove(selected_account)
   shutil.rmtree(path=paths.config_path(selected_account), ignore_errors=True)

