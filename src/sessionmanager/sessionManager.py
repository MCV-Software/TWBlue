# -*- coding: utf-8 -*-

from builtins import str
from builtins import object
import shutil
import widgetUtils
import platform
import output
if platform.system() == "Windows":
 from . import wxUI as view
 from controller import settings
elif platform.system() == "Linux":
 from . import gtkUI as view
import paths
import time
import os
import logging
from . import session
from . import manager
import config_utils
import config

log = logging.getLogger("sessionmanager.sessionManager")

class sessionManagerController(object):
 def __init__(self, started=False):
  super(sessionManagerController, self).__init__()
  log.debug("Setting up the session manager.")
  self.started = started
  manager.setup()
  self.view = view.sessionManagerWindow()
  widgetUtils.connect_event(self.view.new, widgetUtils.BUTTON_PRESSED, self.manage_new_account)
  widgetUtils.connect_event(self.view.remove, widgetUtils.BUTTON_PRESSED, self.remove)
  if self.started == False:
   widgetUtils.connect_event(self.view.configuration, widgetUtils.BUTTON_PRESSED, self.configuration)
  else:
   self.view.hide_configuration()
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
    if len(config_test) == 0:
     try:
      log.debug("Deleting session %s" % (i,))
      shutil.rmtree(paths.config_path(i))
      continue
     except:
      output.speak("An exception was raised while attempting to clean malformed session data. See the error log for details. If this message persists, contact the developers.",True)
      os.exception("Exception thrown while removing malformed session")
      continue
    name = config_test["twitter"]["user_name"]
    if config_test["twitter"]["user_key"] != "" and config_test["twitter"]["user_secret"] != "":
     sessionsList.append(name)
     self.sessions.append(i)
    else:
     try:
      log.debug("Deleting session %s" % (i,))
      shutil.rmtree(paths.config_path(i))
     except:
      output.speak("An exception was raised while attempting to clean malformed session data. See the error log for details. If this message persists, contact the developers.",True)
      os.exception("Exception thrown while removing malformed session")
  self.view.fill_list(sessionsList)

 def show(self):
  if self.view.get_response() == widgetUtils.OK:
   self.do_ok()
#  else:
  self.view.destroy()

 def do_ok(self):
  log.debug("Starting sessions...")
  for i in self.sessions:
   if (i in session.sessions) == True: continue
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
   s.settings.write()
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


 def configuration(self, *args, **kwargs):
  """ Opens the global settings dialogue."""
  d = settings.globalSettingsController()
  if d.response == widgetUtils.OK:
   d.save_configuration()
