# -*- coding: cp1252 -*-
#from config_utils import Configuration, ConfigurationResetException

from builtins import object
import config
import paths
import os
import logging
log = logging.getLogger("sessionmanager.manager")
from . import session_exceptions

manager = None
def setup():
 global manager
 if not manager:
  manager = sessionManager()

class sessionManager(object):
# def __init__(self):
#  FILE = "sessions.conf"
#  SPEC = "app-configuration.defaults"
#  try:
#   self.main = Configuration(paths.config_path(FILE), paths.app_path(SPEC))
#  except ConfigurationResetException:
#   pass

 def get_current_session(self):
  if self.is_valid(config.app["sessions"]["current_session"]):
   return config.app["sessions"]["current_session"]
  else:
   return False

 def add_session(self, id):
  log.debug("Adding a new session: %s" % (id,))
  path = paths.config_path(id)
  if not os.path.exists(path):
   log.debug("Creating %s path" % (paths.config_path(path),))
   os.mkdir(path)
   config.app["sessions"]["sessions"].append(id)

 def set_current_session(self, sessionID):
  config.app["sessions"]["current_session"] = sessionID
  config.app.write()

 def is_valid(self, id):
  if not os.path.exists(paths.config_path(id)):
   raise session_exceptions.NonExistentSessionError("That session does not exist.")
   config.app["sessions"]["current_session"] = ""
   return False
  else:
   return True