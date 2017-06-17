# -*- coding: utf-8 -*-

from . import translator
import platform
if platform.system() == "Windows":
 from . import wx_ui as gui
 