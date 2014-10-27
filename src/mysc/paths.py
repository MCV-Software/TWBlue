import platform
import os
import sys

from functools import wraps

def merge_paths(func):
 @wraps(func)
 def merge_paths_wrapper(*a):
  return unicode(os.path.join(func(), *a))
 return merge_paths_wrapper

@merge_paths
def app_path():
 if hasattr(sys, "frozen"):
  from win32api import GetModuleFileName #We should only be here if using py2exe hence windows
  app_path = os.path.dirname(GetModuleFileName(0))
 else:
  app_path = os.path.normpath(os.path.dirname(__file__))
 return app_path

@merge_paths
def config_path():
 path = app_path(u"config")
 if not os.path.exists(path):
  os.mkdir(path)
 return path

@merge_paths
def data_path(app_name='Blu JM'):
# if platform.system() == "Windows":
#  import shlobj
#  data_path = os.path.join(shlobj.SHGetFolderPath(0, shlobj.CSIDL_APPDATA), app_name)
# else:
 data_path = os.path.join(os.environ['HOME'], ".%s" % app_name)
 if not os.path.exists(data_path):
  os.mkdir(data_path)
 return data_path
