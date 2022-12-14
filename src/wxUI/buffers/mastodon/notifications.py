# -*- coding: utf-8 -*-
import wx
from multiplatform_widgets import widgets

class notificationsPanel(wx.Panel):

    def set_focus_function(self, f):
        self.list.list.Bind(wx.EVT_LIST_ITEM_FOCUSED, f)

    def create_list(self):
        self.list = widgets.list(self, _("Text"), _("Date"), style=wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.LC_VRULES)
        self.list.set_windows_size(0, 320)
        self.list.set_windows_size(2, 110)
        self.list.set_size()

    def __init__(self, parent, name):
        super(notificationsPanel, self).__init__(parent)
        self.name = name
        self.type = "baseBuffer"
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.create_list()
        self.post = wx.Button(self, -1, _("Post"))
        self.dismiss = wx.Button(self, -1, _("Dismiss"))
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSizer.Add(self.post, 0, wx.ALL, 5)
        btnSizer.Add(self.dismiss, 0, wx.ALL, 5)
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
