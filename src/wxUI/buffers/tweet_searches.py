# -*- coding: utf-8 -*-
from __future__ import absolute_import
import wx
from .base import basePanel

class searchPanel(basePanel):
 def __init__(self, parent, name):
  super(searchPanel, self).__init__(parent, name)
  self.type = "search"
