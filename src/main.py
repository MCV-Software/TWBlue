# -*- coding: utf-8 -*-
import platform
from win32com.client import GetObject

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
# ToDo: Remove this soon as this is done already when importing the paths module.
if os.path.exists(os.path.join(paths.app_path(), "Uninstall.exe")):
 paths.mode="installed"
import commandline
import config
import output
import logging
import application
import keys
from mysc.thread_utils import call_threaded
import fixes
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
  sys.stderr = open(os.path.join(paths.logs_path(), "stderr.log"), 'w')
  sys.stdout = open(os.path.join(paths.logs_path(), "stdout.log"), 'w')
 else:
  sys.stdout=stdout
  sys.stderr=stderr
  # We are running from source, let's prepare vlc module for that situation
  if system=="Windows":
   arch="x86"
   if platform.architecture()[0][:2] == "64":
    arch="x64"
   os.environ['PYTHON_VLC_MODULE_PATH']=os.path.abspath(os.path.join(paths.app_path(), "..", "windows-dependencies", arch))
   os.environ['PYTHON_VLC_LIB_PATH']=os.path.abspath(os.path.join(paths.app_path(), "..", "windows-dependencies", arch, "libvlc.dll"))
 #the final log files have been opened succesfully, let's close the temporary files
 stdout_temp.close()
 stderr_temp.close()
 #finally, remove the temporary files. TW Blue doesn't need them anymore, and we will get more free space on the harddrive
 os.remove(stdout_temp.name)
 os.remove(stderr_temp.name)
import sound
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
 languageHandler.setLanguage(config.app["app-settings"]["language"])
 fixes.setup() 
 output.setup()
 keys.setup()
 from controller import settings
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
 check_pid()
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

def is_running(pid):
 "Check if the process with ID pid is running. Adapted from https://stackoverflow.com/a/568589"
 WMI = GetObject('winmgmts:')
 processes = WMI.InstancesOf('Win32_Process')
 return [process.Properties_('ProcessID').Value for process in processes if process.Properties_('ProcessID').Value == pid]

def check_pid():
 "Insures that only one copy of the application is running at a time."
 pidpath = os.path.join(os.getenv("temp"), "{}.pid".format(application.name))
 if os.path.exists(pidpath):
  with open(pidpath) as fin:
   pid = int(fin.read())
  if is_running(pid):
   # Display warning dialog
   commonMessageDialogs.common_error(_(u"{0} is already running. Close the other instance before starting this one. If you're sure that {0} isn't running, try deleting the file at {1}. If you're unsure of how to do this, contact the {0} developers.").format(application.name, pidpath))
   sys.exit(1)
  else:
   commonMessageDialogs.dead_pid()
 # Write the new PID
 with open(pidpath,"w") as cam:
  cam.write(str(os.getpid()))

setup()
