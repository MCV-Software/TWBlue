#import platform
#if platform.system() == "Windows":
from wxUtils import *
from baseDialog import *
#elif platform.system() == "Linux":
#	from gtkUtils import *
