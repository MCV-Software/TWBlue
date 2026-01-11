# -*- coding: utf-8 -*-
import sys
import os
import platform
#redirect the original stdout and stderr
stdout=sys.stdout
stderr=sys.stderr
sys.stdout = open(os.path.join(os.getenv("temp"), "stdout.log"), "w")
sys.stderr = open(os.path.join(os.getenv("temp"), "stderr.log"), "w")
import languageHandler
import paths
#check if TWBlue is installed
# ToDo: Remove this soon as this is done already when importing the paths module.
if os.path.exists(os.path.join(paths.app_path(), "Uninstall.exe")):
    paths.mode="installed"
import psutil
import commandline
import config
import output
import logging
import application
from mysc.thread_utils import call_threaded
import fixes
import widgetUtils
import webbrowser
from wxUI import commonMessageDialogs
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

log = logging.getLogger("main")

def setup():
    log.debug("Starting " + application.name + " %s" % (application.version,))
    config.setup()
    proxy_setup()
    log.debug("Using %s %s" % (platform.system(), platform.architecture()[0]))
    log.debug("Application path is %s" % (paths.app_path(),))
    log.debug("config path  is %s" % (paths.config_path(),))
    sound.setup()
    languageHandler.setLanguage(config.app["app-settings"]["language"])
    fixes.setup() 
    output.setup()
    from controller import settings
    from controller import mainController
    from sessionmanager import sessionManager
    app = widgetUtils.mainLoopObject()
    check_pid()
    if config.app["app-settings"]["donation_dialog_displayed"] == False:
        donation()
    if config.app['app-settings']['check_for_updates']:
        updater.do_update()
    sm = sessionManager.sessionManagerController()
    sm.fill_list()
    if len(sm.sessions) == 0:
        sm.show()
    else:
        sm.do_ok()
    if hasattr(sm.view, "destroy"):
        sm.view.destroy()
    del sm
    r = mainController.Controller()
    r.view.show()
    r.do_work()
    r.check_invisible_at_startup()
    call_threaded(r.start)
    app.run()

def proxy_setup():
    if config.app["proxy"]["server"] != "" and config.app["proxy"]["type"] > 0:
        log.debug("Loading proxy settings")
        proxy_url = config.app["proxy"]["server"] + ":" + str(config.app["proxy"]["port"])
        if config.app["proxy"]["user"] != "" and config.app["proxy"]["password"] != "":
            proxy_url = config.app["proxy"]["user"] + ":" + config.app["proxy"]["password"] + "@" + proxy_url
        elif config.app["proxy"]["user"] != "" and config.proxyTypes[config.app["proxy"]["type"]] in ["socks4", "socks4a"]:
            proxy_url = config.app["proxy"]["user"] + "@" + proxy_url
        proxy_url = config.proxyTypes[config.app["proxy"]["type"]] + "://" + proxy_url
        os.environ["HTTP_PROXY"] = proxy_url
        os.environ["HTTPS_PROXY"] = proxy_url

def donation():
    dlg = commonMessageDialogs.donation()
    if dlg == widgetUtils.YES:
        webbrowser.open_new_tab(_("https://twblue.mcvsoftware.com/donate"))
    config.app["app-settings"]["donation_dialog_displayed"] = True

def check_pid():
    "Ensures that only one copy of the application is running at a time."
    pidpath = os.path.join(os.getenv("temp"), "{}.pid".format(application.name))
    if os.path.exists(pidpath):
        with open(pidpath) as fin:
            pid = int(fin.read())
        try:
            p = psutil.Process(pid=pid)
            if p.is_running():
                # Display warning dialog
                commonMessageDialogs.common_error(_("{0} is already running. Close the other instance before starting this one. If you're sure that {0} isn't running, try deleting the file at {1}. If you're unsure of how to do this, contact the {0} developers.").format(application.name, pidpath))
                sys.exit(1)
        except psutil.NoSuchProcess:
            commonMessageDialogs.dead_pid()
    # Write the new PID
    with open(pidpath,"w") as cam:
        cam.write(str(os.getpid()))

setup()
