# -*- coding: cp1252 -*-
from config_utils import Configuration, ConfigurationResetException
import paths
import logging

log = logging.getLogger("config")

MAINFILE = "twblue.conf"
MAINSPEC = "app-configuration.defaults"

app = None

def setup ():
 global app
 log.debug("Loading global app settings...")
 try:
  app = Configuration(paths.config_path(MAINFILE), paths.app_path(MAINSPEC))
 except ConfigurationResetException:
  pass
