import _winreg
import os
import sys
from platform_utils import paths

RUN_REGKEY = ur"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"

def is_installed(app_subkey):
 """Checks if the currently running copy is installed or portable variant. Requires the name of the application subkey found under the uninstall section in Windows registry."""

 try:
  key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\%s" % app_subkey)
  inst_dir = _winreg.QueryValueEx(key,"InstallLocation")[0]
 except WindowsError:
  return False
 _winreg.CloseKey(key)
 try:
  return os.stat(inst_dir) == os.stat(paths.app_path())
 except WindowsError:
  return False

def getAutoStart(app_name):
 """Queries if the automatic startup should be set for the application or not, depending on it's current state."""

 try:
  key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, RUN_REGKEY)
  val = _winreg.QueryValueEx(key, unicode(app_name))[0]
  return os.stat(val) == os.stat(sys.argv[0])
 except (WindowsError, OSError):
  return False

def setAutoStart(app_name, enable=True):
 """Configures automatic startup for the application, if the enable argument is set to True. If set to False, deletes the application AutoStart value."""

 if getAutoStart(app_name) == enable:
  return
 key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, RUN_REGKEY, 0, _winreg.KEY_WRITE)
 if enable:
  _winreg.SetValueEx(key, unicode(app_name), None, _winreg.REG_SZ, sys.argv[0])
 else:
  _winreg.DeleteValue(key, unicode(app_name))
