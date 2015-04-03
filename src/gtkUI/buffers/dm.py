# -*- coding: utf-8 -*-
from gi.repository import Gtk
import widgetUtils
from base import basePanel

class dmPanel(basePanel):
 def __init__(self, parent, name):
  """ Class to DM'S. Reply and retweet buttons are not showed and they have your delete method for dm's."""
  super(dmPanel, self).__init__(parent, name)
  self.retweet.hide()
  self.retweet.set_no_show_all(True)
  self.reply.hide()
  self.reply.set_no_show_all(True)
  self.type = "dm"
