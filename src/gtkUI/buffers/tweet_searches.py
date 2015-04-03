# -*- coding: utf-8 -*-
from gi.repository import Gtk
from base import basePanel

class searchPanel(basePanel):
 def __init__(self, parent, name):
  super(searchPanel, self).__init__(parent, name)
  self.type = "search"
