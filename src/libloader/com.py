from pywintypes import com_error
import win32com
import paths
win32com.__gen_path__=paths.com_path()
import sys
import os
sys.path.append(os.path.join(win32com.__gen_path__, "."))
from win32com.client import gencache
fixed=False

def prepare_gencache():
 gencache.is_readonly = False
 gencache.GetGeneratePath()

def patched_getmodule(modname):
 mod=__import__(modname)
 return sys.modules[modname]

def load_com(*names):
 global fixed
 if fixed==False:
  gencache._GetModule=patched_getmodule
  prepare_gencache()
  fixed=True
 result = None
 for name in names:
  try:
   result = gencache.EnsureDispatch(name)
   break
  except com_error:
   continue
 if result is None:
  raise com_error("Unable to load any of the provided com objects.")
 return result

