# -*- coding: utf-8 -*-
from gi.repository import Gtk
import widgetUtils
from base import basePanel

class peoplePanel(basePanel):
 """ Buffer used to show people."""

 def create_list(self):
  self.list = widgetUtils.list(_(u"User"))

 def __init__(self, parent, name):
  super(peoplePanel, self).__init__(parent, name)
  self.type = "people"
  self.reply.set_label(_(u"Mention"))
  self.retweet.hide()
  self.retweet.set_no_show_all(True)
