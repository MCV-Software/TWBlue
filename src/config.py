# -*- coding: cp1252 -*-
import config_utils
import paths
import logging

log = logging.getLogger("config")

MAINFILE = "twblue.conf"
MAINSPEC = "app-configuration.defaults"

app = None
keymap=None
def setup ():
 global app
 log.debug("Loading global app settings...")
 app = config_utils.load_config(paths.config_path(MAINFILE), paths.app_path(MAINSPEC))
 log.debug("Loading keymap...")
 global keymap
 keymap = config_utils.load_config(paths.app_path("keymaps/"+app['app-settings']['load_keymap']), paths.app_path('keymaps/base.template'))
