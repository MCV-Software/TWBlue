# -*- coding: utf-8 -*-
from __future__ import absolute_import
import wx
from .base import basePanel

class favsPanel(basePanel):
 def __init__(self, parent, name):
  super(favsPanel, self).__init__(parent, name)
  self.type = "favourites_timeline"