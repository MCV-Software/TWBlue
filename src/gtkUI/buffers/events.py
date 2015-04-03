# -*- coding: utf-8 -*-
import widgetUtils
from gi.repository import Gtk

class eventsPanel(Gtk.VBox):
 """ Buffer to show events. Different than tweets or people."""

 def __init__(self, parent, name):
  self.type = "event"
  super(eventsPanel, self).__init__(spacing=6)
  self.name = name
  self.list = widgetUtils.list(_(u"Date"), _(u"Event"))
  self.add(self.list.list)
  self.tweet = Gtk.Button(_(u"Tweet"))
  self.delete_event = Gtk.Button(_(u"Remove event"))
  btnBox = Gtk.Box(spacing=6)
  btnBox.add(self.tweet)
  btnBox.add(self.delete_event)
  self.add(btnBox)

 def set_position(self, reversed=False):
  if reversed == False:
   self.list.select_item(self.list.get_count()-1)
  else:
   self.list.select_item(0)
