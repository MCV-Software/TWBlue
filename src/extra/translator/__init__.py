# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals
from . import translator
import platform
if platform.system() == "Windows":
    from . import wx_ui as gui

