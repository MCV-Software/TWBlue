# -*- coding: utf-8 -*-
from gi.repository import Gtk
from tweet_searches import searchPanel
import widgetUtils

class searchUsersPanel(searchPanel):
 def create_list(self):
  """ Returns the list for put the tweets here."""
  self.list = widgetUtils.list(_(u"User"))

 def __init__(self, parent, name):
  self.create_list()
  super(searchUsersPanel, self).__init__(parent, name)
  self.type = "user_searches"
