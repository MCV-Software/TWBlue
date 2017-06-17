
import platform
if platform.system() == "Windows":
 from .wxUtils import *
#elif platform.system() == "Linux":
# from gtkUtils import *
