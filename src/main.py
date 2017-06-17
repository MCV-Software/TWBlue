# -*- coding: utf-8 -*-
import platform
""" there are lots of things not implemented for Gtk+ yet.
    We've started this effort 1 Apr 2015 so it isn't fully functional. We will remove the ifs statements when are no needed"""

system = platform.system()
if system == "Windows":
 import sys
 import os
 #redirect the original stdout and stderr
 stdout=sys.stdout
 stderr=sys.stderr
 sys.stdout = open(os.path.join(os.getenv("temp"), "stdout.log"), "w")
 sys.stderr = open(os.path.join(os.getenv("temp"), "stderr.log"), "w")
import languageHandler
import paths
#check if TWBlue is installed (Windows only)
if os.path.exists(paths.app_path("Uninstall.exe")):
 paths.mode="installed"
import commandline
import config
import sound
import output
import logging
import application
import keys
from mysc.thread_utils import call_threaded
import fixes
#extra variables to control the temporary stdout and stderr, while the final files are opened. We understand that some errors could happen while all outputs are closed, so let's try to avoid it.
import widgetUtils
import webbrowser
from wxUI import commonMessageDialogs
if system == "Windows":
 from logger import logger
 from update import updater
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
if system == "Linux":
 from gi.repository import Gdk, GObject, GLib

log = logging.getLogger("main")

def setup():
 log.debug("Starting " + application.name + " %s" % (application.version,))
 config.setup()
 log.debug("Using %s %s" % (platform.system(), platform.architecture()[0]))
 log.debug("Application path is %s" % (paths.app_path(),))
 log.debug("config path  is %s" % (paths.config_path(),))
 sound.setup()
 output.setup()
 languageHandler.setLanguage(config.app["app-settings"]["language"])
 fixes.setup() 
 keys.setup()
 from controller import mainController
 from sessionmanager import sessionManager
 app = widgetUtils.mainLoopObject()
 if system == "Windows":
  if config.app["app-settings"]["donation_dialog_displayed"] == False:
   donation()
  if config.app['app-settings']['check_for_updates']:
   updater.do_update()
 sm = sessionManager.sessionManagerController()
 sm.fill_list()
 if len(sm.sessions) == 0: sm.show()
 else:
  sm.do_ok()
 if hasattr(sm.view, "destroy"):
  sm.view.destroy()
 del sm
 r = mainController.Controller()
 r.view.show()
 r.do_work()
 r.check_invisible_at_startup()
 if system == "Windows":
  call_threaded(r.start)
 elif system == "Linux":
  GLib.idle_add(r.start)
 app.run()

def donation():
 dlg = commonMessageDialogs.donation()
 if dlg == widgetUtils.YES:
  webbrowser.open_new_tab(_("https://twblue.es/donate"))
 config.app["app-settings"]["donation_dialog_displayed"] = True

setup()
