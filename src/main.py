# -*- coding: utf-8 -*-
import sys
import os
#redirect the original stdout and stderr
stdout=sys.stdout
stderr=sys.stderr
sys.stdout = open(os.path.join(os.getenv("temp"), "stdout.log"), "w")
sys.stderr = open(os.path.join(os.getenv("temp"), "stderr.log"), "w")
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
from update import updater
import fixes
#extra variables to control the temporal stdout and stderr, while the final files are opened. We understand that some errors could happen while all outputs are closed, so let's try to avoid it.
stdout_temp=sys.stdout
stderr_temp=sys.stderr
#if it's a binary version
if hasattr(sys, 'frozen'):
 sys.stderr = open(paths.logs_path("stderr.log"), 'w')
 sys.stdout = open(paths.logs_path("stdout.log"), 'w')
else:
 sys.stdout=stdout
 sys.stderr=stderr
#the final log files have been opened succesfully, let's close the temporal files
stdout_temp.close()
stderr_temp.close()
#finally, remove the temporal files. TW Blue doesn't need them anymore, and we will get more free space on the harddrive
os.remove(stdout_temp.name)
os.remove(stderr_temp.name)
log = logging.getLogger("main")

def setup():
 log.debug("Starting TWBlue %s" % (application.version,))
 config.setup()
 log.debug("Using %s %s" % (platform.system(), platform.architecture()[0]))
 log.debug("Application path is %s" % (paths.app_path(),))
 log.debug("config path  is %s" % (paths.config_path(),))
 sound.setup()
 output.setup()
 languageHandler.setLanguage(config.app["app-settings"]["language"])
 keys.setup()
 from controller import mainController
 from sessionmanager import sessionManager
 app = wx.App()
 updater.do_update()
 sm = sessionManager.sessionManagerController()
 sm.fill_list()
 if len(sm.sessions) == 0: sm.show()
 else:
  sm.do_ok()
 del sm
 fixes.setup()
 r = mainController.Controller()
 r.view.Show()
 r.do_work()
 call_threaded(r.start)
 app.MainLoop()

setup()