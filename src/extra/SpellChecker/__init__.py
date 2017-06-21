
from . import spellchecker
import platform
if platform.system() == "Windows":
 from .wx_ui import *