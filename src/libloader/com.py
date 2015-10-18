from pywintypes import com_error
import win32com
import paths
win32com.__gen_path__=paths.data_path("com_cache")
from win32com.client import gencache

def prepare_gencache():
 gencache.is_readonly = False
 gencache.GetGeneratePath()



def load_com(*names):
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

