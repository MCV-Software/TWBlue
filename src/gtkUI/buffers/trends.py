# -*- coding: utf-8 -*-
from gi.repository import Gtk
import widgetUtils

class trendsPanel(Gtk.VBox):
 def create_list(self):
  """ Returns the list for put the tweets here."""
  self.list = widgetUtils.list(_(u"Trending topic"))

 def __init__(self, parent, name):
  super(trendsPanel, self).__init__(spacing=6)
  self.type = "trends"
  self.create_list()
  self.tweet = Gtk.Button(_(u"Tweet"))
  self.tweetTrendBtn = Gtk.Button(_(u"Tweet about this trend"))
  btnSizer = Gtk.Box(spacing=3)
  btnSizer.add(self.tweet)
  btnSizer.add(self.tweetTrendBtn)
  self.add(btnSizer)
  self.Add(self.list.list)

 def set_position(self, reversed=False):
  if reversed == False:
   self.list.select_item(self.list.get_count()-1)
  else:
   self.list.select_item(0)
