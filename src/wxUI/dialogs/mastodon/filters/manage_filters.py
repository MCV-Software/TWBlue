# -*- coding: utf-8 -*-
import wx

class ManageFiltersDialog(wx.Dialog):
    """
    A dialog that displays a list of Mastodon filters and provides controls
    to add, edit and remove them.
    """
    
    def __init__(self, parent, title=_("Filters"), *args, **kwargs):
        """Initialize the filters view dialog. """
        super(ManageFiltersDialog, self).__init__(parent, title=title, *args, **kwargs)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.filter_list = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_SUNKEN)
        self.filter_list.InsertColumn(0, _("Title"), width=150)
        self.filter_list.InsertColumn(1, _("Keywords"), width=80)
        self.filter_list.InsertColumn(2, _("Contexts"), width=150)
        self.filter_list.InsertColumn(3, _("Action"), width=100)
        self.filter_list.InsertColumn(4, _("Expires"), width=150)
        main_sizer.Add(self.filter_list, 1, wx.EXPAND | wx.ALL, 10)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.add_button = wx.Button(self, label=_("Add"))
        self.edit_button = wx.Button(self, label=_("Edit"))
        self.remove_button = wx.Button(self, label=_("Remove"))
        close_button = wx.Button(self, wx.ID_CLOSE)
        self.edit_button.Disable()
        self.remove_button.Disable()
        button_sizer.Add(self.add_button, 0, wx.RIGHT, 5)
        button_sizer.Add(self.edit_button, 0, wx.RIGHT, 5)
        button_sizer.Add(self.remove_button, 0, wx.RIGHT, 5)
        button_sizer.Add((0, 0), 1, wx.EXPAND)  # Spacer to push close button to right
        button_sizer.Add(close_button, 0)
        self.SetEscapeId(close_button.GetId())
        main_sizer.Add(button_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        self.SetSizer(main_sizer)
