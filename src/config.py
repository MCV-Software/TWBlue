# -*- coding: cp1252 -*-
import config_utils
import paths
import logging

log = logging.getLogger("config")

MAINFILE = "twblue.conf"
MAINSPEC = "app-configuration.defaults"

app = None

def setup ():
 global app
 log.debug("Loading global app settings...")
 app = config_utils.load_config(paths.config_path(MAINFILE), paths.app_path(MAINSPEC))
