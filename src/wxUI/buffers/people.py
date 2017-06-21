# -*- coding: utf-8 -*-

import wx
from multiplatform_widgets import widgets
from .base import basePanel

class peoplePanel(basePanel):
 """ Buffer used to show people."""

 def create_list(self):
  self.list = widgets.list(self, _("User"), style=wx.LC_REPORT|wx.LC_SINGLE_SEL, size=(800, 800))

 def __init__(self, parent, name):
  super(peoplePanel, self).__init__(parent, name)
  self.type = "people"
  self.reply.SetLabel(_("Mention"))
  self.retweet.Disable()
