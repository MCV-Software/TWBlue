# -*- coding: utf-8 -*-
import languageHandler
import wx
import paths
import commandline
import config
import sound
import output
from logger import logger
import logging
import platform
import application
import keys
from mysc.thread_utils import call_threaded
log = logging.getLogger("main")

def setup():
 log.debug("Starting TWBlue %s" % (application.version,))
 config.setup()
 log.debug("Using %s %s" % (platform.system(), platform.architecture()[0]))
 log.debug("Application path is %s" % (paths.app_path(),))
 log.debug("Data path is %s" % (paths.data_path(),))
 sound.setup()
 output.setup()
 languageHandler.setLanguage(config.app["app-settings"]["language"])
 keys.setup()
 from controller import mainController
 from sessionmanager import sessionManager
 app = wx.App()
 sm = sessionManager.sessionManagerController()
 sm.fill_list()
 if len(sm.sessions) == 0: sm.show()
 else:
  sm.do_ok()
 del sm
 r = mainController.Controller()
 r.view.Show()
 r.do_work()
 call_threaded(r.start)
 app.MainLoop()

setup()