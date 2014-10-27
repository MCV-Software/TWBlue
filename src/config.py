# -*- coding: cp1252 -*-
from config_utils import Configuration, ConfigurationResetException
import paths

MAINFILE = "session.conf"
MAINSPEC = "Conf.defaults"

main = None

def setup ():
 global main
 try:
  main = Configuration(paths.config_path(MAINFILE), paths.app_path(MAINSPEC))
 except ConfigurationResetException:
  pass
# return main