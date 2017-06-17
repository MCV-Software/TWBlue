# -*- coding: utf-8 -*-

import wx
from .base import basePanel

class listPanel(basePanel):
 def __init__(self, parent, name):
  super(listPanel, self).__init__(parent, name)
  self.type = "list"
