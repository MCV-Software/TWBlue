# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals
import wx
from .tweet_searches import searchPanel
from multiplatform_widgets import widgets

class searchUsersPanel(searchPanel):
    def create_list(self):
        """ Returns the list for put the tweets here."""
        self.list = widgets.list(self, _(u"User"), style=wx.LC_REPORT|wx.LC_SINGLE_SEL, size=(800, 800))

    def __init__(self, parent, name):
        super(searchUsersPanel, self).__init__(parent, name)
        self.create_list()
        self.type = "user_searches"
