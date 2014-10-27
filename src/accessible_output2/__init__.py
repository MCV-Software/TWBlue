import ctypes
import os
import types
from platform_utils import paths

def load_library(libname):
 if paths.is_frozen():
  libfile = os.path.join(paths.embedded_data_path(), 'accessible_output2', 'lib', libname)
 else:
  libfile = os.path.join(paths.module_path(), 'lib', libname)
 return ctypes.windll[libfile]

def get_output_classes():
 import outputs
 module_type = types.ModuleType
 classes = [m.output_class for m in outputs.__dict__.itervalues() if type(m) == module_type and hasattr(m, 'output_class')]
 return sorted(classes, key=lambda c: c.priority)

def find_datafiles():
 import os
 import platform
 from glob import glob
 import accessible_output2
 if platform.system() != 'Windows':
  return []
 path = os.path.join(accessible_output2.__path__[0], 'lib', '*.dll')
 results = glob(path)
 dest_dir = os.path.join('accessible_output2', 'lib')
 return [(dest_dir, results)]
