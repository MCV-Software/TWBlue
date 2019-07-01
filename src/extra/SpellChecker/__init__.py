from __future__ import absolute_import
from __future__ import unicode_literals
from . import spellchecker
import platform
if platform.system() == "Windows":
 from .wx_ui import *