# -*- coding: cp1252 -*-
import config_utils
import paths
import logging
import platform

log = logging.getLogger("config")

MAINFILE = "twblue.conf"
MAINSPEC = "app-configuration.defaults"
proxyTypes=["http", "https", "socks4", "socks5"]
app = None
keymap=None
changed_keymap = False

def setup ():
 global app
 log.debug("Loading global app settings...")
 app = config_utils.load_config(paths.config_path(MAINFILE), paths.app_path(MAINSPEC))
 log.debug("Loading keymap...")
 global keymap
 if float(platform.version()[:2]) >= 10 and app["app-settings"]["load_keymap"] == "default.keymap":
  app["app-settings"]["load_keymap"] = "Windows 10.keymap"
  app.write()
  global changed_keymap
  changed_keymap = True
 keymap = config_utils.load_config(paths.config_path("keymap.keymap"), paths.app_path("keymaps/"+app['app-settings']['load_keymap']), copy=False)
