# -*- coding: utf-8 -*-
import wx

class UserListDialog(wx.Dialog):
    def __init__(self, parent=None, title="", users=[]):
        super(UserListDialog, self).__init__(parent=parent, title=title, size=(400, 300))
        self.users = users
        self.init_ui()

    def init_ui(self):
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        title_text = wx.StaticText(panel, label=self.GetTitle())
        title_font = title_text.GetFont()
        title_font.PointSize += 2
        title_font = title_font.Bold()
        title_text.SetFont(title_font)
        main_sizer.Add(title_text, 0, wx.ALIGN_CENTER | wx.TOP, 10)
        user_list_box = wx.StaticBox(panel, wx.ID_ANY, "Users")
        user_list_sizer = wx.StaticBoxSizer(user_list_box, wx.VERTICAL)
        self.user_list = wx.ListBox(panel, wx.ID_ANY, choices=self.users, style=wx.LB_SINGLE)
        user_list_sizer.Add(self.user_list, 1, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(user_list_sizer, 1, wx.EXPAND | wx.ALL, 15)
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.actions_button = wx.Button(panel, wx.ID_ANY, "&Actions")
        buttons_sizer.Add(self.actions_button, 0, wx.RIGHT, 10)
        self.details_button = wx.Button(panel, wx.ID_ANY, _("&View profile"))
        buttons_sizer.Add(self.details_button, 0, wx.RIGHT, 10)
        close_button = wx.Button(panel, wx.ID_CANCEL, "&Close")
        buttons_sizer.Add(close_button, 0)
        main_sizer.Add(buttons_sizer, 0, wx.ALIGN_CENTER | wx.BOTTOM, 15)
        panel.SetSizer(main_sizer)
#        self.SetSizerAndFit(main_sizer)
