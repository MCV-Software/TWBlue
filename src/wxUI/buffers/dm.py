# -*- coding: utf-8 -*-
import wx
from base import basePanel

class dmPanel(basePanel):
 def __init__(self, parent, name):
  """ Class to DM'S. Reply and retweet buttons are not showed and they have your delete method for dm's."""
  super(dmPanel, self).__init__(parent, name)
  self.retweetBtn.Disable()
  self.responseBtn.Disable()
  self.type = "dm"