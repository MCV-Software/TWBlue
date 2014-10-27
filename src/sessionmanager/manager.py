# -*- coding: cp1252 -*-
from config_utils import Configuration, ConfigurationResetException
import paths
import os
import session_exceptions

manager = None
def setup():
 global manager
 manager = sessionManager()

class sessionManager(object):
 def __init__(self):
  FILE = "sessions.conf"
  SPEC = "sessions.defaults"
  try:
   self.main = Configuration(paths.config_path(FILE), paths.app_path(SPEC))
  except ConfigurationResetException:
   pass

 def get_current_session(self):
  if self.is_valid(self.main["sessions"]["current_session"]):
   return self.main["sessions"]["current_session"]
  else:
   return False

 def add_session(self, id):
  path = paths.config_path(id)
  if not os.path.exists(path):
   os.mkdir(path)
   self.main["sessions"]["sessions"].append(id)

 def set_current_session(self, sessionID):
  self.main["sessions"]["current_session"] = sessionID
  self.main.write()

 def is_valid(self, id):
  if not os.path.exists(paths.config_path(id)):
   raise session_exceptions.NonExistentSessionError("That session does not exist.")
   self.main["sessions"]["current_session"] = ""
   return False
  else:
   return True