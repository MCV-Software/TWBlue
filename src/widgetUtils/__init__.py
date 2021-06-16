from __future__ import absolute_import
from __future__ import unicode_literals
import platform
if platform.system() == "Windows":
    from .wxUtils import *
#elif platform.system() == "Linux":
# from gtkUtils import *
