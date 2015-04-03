# -*- coding: utf-8 -*-
import widgetUtils
from gi.repository import Gtk

class basePanel(Gtk.VBox):
 
 def create_list(self):
  self.list = widgetUtils.list(_(u"User"), _(u"Text"), _(u"Date"), _(u"Client"))

 def __init__(self, parent, name):
  super(basePanel, self).__init__(spacing=6)
  self.name = name
  self.type = "baseBuffer"
  self.create_list()
  self.tweet = Gtk.Button(_(u"Tweet"))
  self.retweet = Gtk.Button(_(u"Retweet"))
  self.reply = Gtk.Button(_(u"Reply"))
  self.dm = Gtk.Button(_(u"Direct message"))
  btnSizer = Gtk.Box(spacing=6)
  btnSizer.add(self.tweet)
  btnSizer.add(self.retweet)
  btnSizer.add(self.reply)
  btnSizer.add(self.dm)
  self.add(self.list.list)
  self.add(btnSizer)

 def set_position(self, reversed=False):
  if reversed == False:
   self.list.select_item(self.list.get_count()-1)
  else:
   self.list.select_item(0)
