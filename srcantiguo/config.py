# -*- coding: cp1252 -*-
import os
import sys
import config_utils
import paths
import logging
import platform

log = logging.getLogger("config")

MAINFILE = "twblue.conf"
MAINSPEC = "app-configuration.defaults"
proxyTypes = ["system", "http", "socks4", "socks4a", "socks5", "socks5h"]
app = None
keymap=None
changed_keymap = False

def setup ():
    global app
    log.debug("Loading global app settings...")
    app = config_utils.load_config(os.path.join(paths.config_path(), MAINFILE), os.path.join(paths.app_path(), MAINSPEC))
    log.debug("Loading keymap...")
    global keymap
    if float(platform.version()[:2]) >= 10 and app["app-settings"]["load_keymap"] == "default.keymap":
        if sys.getwindowsversion().build > 22000:
            app["app-settings"]["load_keymap"] = "Windows11.keymap"
        else:
            app["app-settings"]["load_keymap"] = "Windows 10.keymap"
        app.write()
        global changed_keymap
        changed_keymap = True
    keymap = config_utils.load_config(os.path.join(paths.config_path(), "keymap.keymap"), os.path.join(paths.app_path(), "keymaps/"+app['app-settings']['load_keymap']), copy=False)
