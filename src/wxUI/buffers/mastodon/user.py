# -*- coding: utf-8 -*-
import wx
from multiplatform_widgets import widgets

class userPanel(wx.Panel):

    def create_list(self):
        self.list = widgets.list(self, _("User"), style=wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.LC_VRULES)
        self.list.set_windows_size(0, 320)
        self.list.set_size()

    def __init__(self, parent, name):
        super(userPanel, self).__init__(parent)
        self.name = name
        self.type = "baseBuffer"
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.create_list()
        self.toot = wx.Button(self, -1, _("Toot"))
        self.actions = wx.Button(self, -1, _("Actions"))
        self.message = wx.Button(self, -1, _("Message"))
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSizer.Add(self.toot, 0, wx.ALL, 5)
        btnSizer.Add(self.actions, 0, wx.ALL, 5)
        btnSizer.Add(self.message, 0, wx.ALL, 5)
        self.sizer.Add(btnSizer, 0, wx.ALL, 5)
        self.sizer.Add(self.list.list, 0, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(self.sizer)
        self.SetClientSize(self.sizer.CalcMin())

    def set_position(self, reversed=False):
        if reversed == False:
            self.list.select_item(self.list.get_count()-1)
        else:
            self.list.select_item(0)

    def set_focus_in_list(self):
        self.list.list.SetFocus()
