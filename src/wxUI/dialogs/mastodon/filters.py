# -*- coding: utf-8 -*-
import wx

class FilterKeywordPanel(wx.Panel):
    """panel to handle filter's keywords. """
    def __init__(self, parent):
        super(FilterKeywordPanel, self).__init__(parent)
        self.keywords = []
        # Add widgets
        list_panel = wx.Panel(self)
        self.keyword_list = wx.ListCtrl(list_panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.keyword_list.InsertColumn(0, _("Keyword"))
        self.keyword_list.InsertColumn(1, _("Whole word"))
        self.keyword_list.SetColumnWidth(0, wx.LIST_AUTOSIZE_USEHEADER)
        self.keyword_list.SetColumnWidth(1, wx.LIST_AUTOSIZE_USEHEADER)
        list_sizer = wx.BoxSizer(wx.VERTICAL)
        list_sizer.Add(self.keyword_list, 1, wx.EXPAND)
        list_panel.SetSizer(list_sizer)
        keyword_label = wx.StaticText(self, label=_("Keyword:"))
        self.keyword_text = wx.TextCtrl(self)
        keyword_sizer = wx.BoxSizer(wx.VERTICAL)
        keyword_sizer.Add(keyword_label, 0, wx.RIGHT, 5)
        keyword_sizer.Add(self.keyword_text, 0, wx.EXPAND)
        self.whole_word_checkbox = wx.CheckBox(self, label=_("Whole word"))
        self.add_button = wx.Button(self, label=_("Add"))
        self.remove_button = wx.Button(self, label=_("Remove"))
        input_sizer = wx.BoxSizer(wx.HORIZONTAL)
        input_sizer.Add(keyword_sizer, 1, wx.RIGHT, 5)
        input_sizer.Add(self.whole_word_checkbox, 0)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(self.add_button, 0, wx.RIGHT, 5)
        button_sizer.Add(self.remove_button, 0)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(wx.StaticText(self, label=_("Palabras clave a filtrar:")), 0, wx.BOTTOM, 5)
        main_sizer.Add(list_panel, 1, wx.EXPAND | wx.BOTTOM, 5)
        main_sizer.Add(input_sizer, 0, wx.EXPAND | wx.BOTTOM, 5)
        main_sizer.Add(button_sizer, 0, wx.ALIGN_RIGHT)
        self.SetSizer(main_sizer)

    def add_keyword(self, keyword, whole_word=False):
        """ Adds a keyword to the list. """
        index = self.keyword_list.InsertItem(self.keyword_list.GetItemCount(), keyword)
        self.keyword_list.SetItem(index, 1, _("Yes") if whole_word else _("No"))
        self.keyword_list.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.keyword_list.SetColumnWidth(1, wx.LIST_AUTOSIZE_USEHEADER)
        self.keyword_text.Clear()
        self.whole_word_checkbox.SetValue(False)

    def remove_keyword(self):
        """ Remove a keyword from the list. """
        selection = self.keyword_list.GetFirstSelected()
        if selection != -1:
            self.keyword_list.DeleteItem(selection)
            return selection

    def set_keywords(self, keywords):
        """ Set the list of keyword. """
        self.keyword_list.DeleteAllItems()
        for keyword_data in keywords:
            if isinstance(keyword_data, dict):
                kw = keyword_data.get('keyword', '')
                whole_word = keyword_data.get('whole_word', False)
                self.keywords.append({'keyword': kw, 'whole_word': whole_word})
                index = self.keyword_list.InsertItem(self.keyword_list.GetItemCount(), kw)
                self.keyword_list.SetItem(index, 1, _("Yes") if whole_word else _("No"))
            else:
                self.keywords.append({'keyword': keyword_data, 'whole_word': False})
                index = self.keyword_list.InsertItem(self.keyword_list.GetItemCount(), keyword_data)
                self.keyword_list.SetItem(index, 1, _("No"))
        self.keyword_list.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.keyword_list.SetColumnWidth(1, wx.LIST_AUTOSIZE_USEHEADER)

class MastodonFilterDialog(wx.Dialog):
    def __init__(self, parent, title=_("New filter")):
        super(MastodonFilterDialog, self).__init__(parent, title=title, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.contexts = ["home", "public", "notifications", "thread", "account"]
        self.context_labels = {
            "home": _("Home timeline"),
            "public": _("Public statuses"),
            "notifications": _("Notifications"),
            "thread": _("Threads"),
            "account": _("Profiles")
        }
        self.actions = ["hide", "warn"]
        self.action_labels = {
            "hide": _("Hide posts"),
            "warn": _("Set a content warning to posts")
        }
        self.expiration_options = [
            ("never", _("Never")),
            ("hours", _("Hours")),
            ("days", _("Days")),
            ("weeks", _("Weeks")),
            ("months", _("months"))
        ]
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        name_label = wx.StaticText(self, label=_("Title:"))
        self.name_ctrl = wx.TextCtrl(self)
        name_sizer = wx.BoxSizer(wx.HORIZONTAL)
        name_sizer.Add(name_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        name_sizer.Add(self.name_ctrl, 1, wx.EXPAND)
        main_sizer.Add(name_sizer, 0, wx.EXPAND | wx.ALL, 10)
        static_box = wx.StaticBox(self, label=_("Apply to:"))
        context_sizer = wx.StaticBoxSizer(static_box, wx.VERTICAL)
        self.context_checkboxes = {}
        context_grid = wx.FlexGridSizer(rows=3, cols=2, vgap=5, hgap=10)
        for context in self.contexts:
            checkbox = wx.CheckBox(static_box, label=self.context_labels[context])
            self.context_checkboxes[context] = checkbox
            context_grid.Add(checkbox)
        context_sizer.Add(context_grid, 0, wx.ALL, 10)
        main_sizer.Add(context_sizer, 0, wx.EXPAND | wx.ALL, 10)
        action_label = wx.StaticText(self, label=_("Action:"))
        self.action_choice = wx.Choice(self)
        for action in self.actions:
            self.action_choice.Append(self.action_labels[action])
        action_sizer = wx.BoxSizer(wx.HORIZONTAL)
        action_sizer.Add(action_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        action_sizer.Add(self.action_choice, 1)
        main_sizer.Add(action_sizer, 0, wx.EXPAND | wx.ALL, 10)
        expiration_label = wx.StaticText(self, label=_("Expires in:"))
        self.expiration_choice = wx.Choice(self)
        for e, label in self.expiration_options:
            self.expiration_choice.Append(label)
        self.expiration_value = wx.SpinCtrl(self, min=1, max=9999, initial=1)
        self.expiration_value.Enable(False)
        self.expiration_choice.Bind(wx.EVT_CHOICE, self.on_expiration_changed)
        expiration_sizer = wx.BoxSizer(wx.HORIZONTAL)
        expiration_sizer.Add(expiration_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        expiration_sizer.Add(self.expiration_choice, 1, wx.RIGHT, 5)
        expiration_sizer.Add(self.expiration_value, 0)
        main_sizer.Add(expiration_sizer, 0, wx.EXPAND | wx.ALL, 10)
        self.keyword_panel = FilterKeywordPanel(self)
        main_sizer.Add(self.keyword_panel, 1, wx.EXPAND | wx.ALL, 10)
        button_sizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        main_sizer.Add(button_sizer, 0, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(main_sizer)
        self.SetSize((450, 550))
        self.action_choice.SetSelection(0)
        self.expiration_choice.SetSelection(0)

    def on_expiration_changed(self, event):
        selection = self.expiration_choice.GetSelection()
        self.expiration_value.Enable(selection != 0)

