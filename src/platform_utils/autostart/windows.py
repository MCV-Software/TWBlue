
from builtins import str
import winreg
import os
import sys
from platform_utils import paths

RUN_REGKEY = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run"

def is_installed(app_subkey):
 """Checks if the currently running copy is installed or portable variant. Requires the name of the application subkey found under the uninstall section in Windows registry."""

 try:
  key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\%s" % app_subkey)
  inst_dir = winreg.QueryValueEx(key,"InstallLocation")[0]
 except WindowsError:
  return False
 winreg.CloseKey(key)
 try:
  return os.stat(inst_dir) == os.stat(paths.app_path())
 except WindowsError:
  return False

def getAutoStart(app_name):
 """Queries if the automatic startup should be set for the application or not, depending on it's current state."""

 try:
  key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_REGKEY)
  val = winreg.QueryValueEx(key, str(app_name))[0]
  return os.stat(val) == os.stat(sys.argv[0])
 except (WindowsError, OSError):
  return False

def setAutoStart(app_name, enable=True):
 """Configures automatic startup for the application, if the enable argument is set to True. If set to False, deletes the application AutoStart value."""
 print(paths.get_executable())
 if getAutoStart(app_name) == enable:
  return
 key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_REGKEY, 0, winreg.KEY_WRITE)
 if enable:
  winreg.SetValueEx(key, str(app_name), None, winreg.REG_SZ, paths.get_executable())
 else:
  winreg.DeleteValue(key, str(app_name))
