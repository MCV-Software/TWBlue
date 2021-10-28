# -*- coding: utf-8 -*-
import wx
import gettext
from . import baseDialog

class addAliasDialog(baseDialog.BaseWXDialog):
    def __init__(self, title, users):
        super(addAliasDialog, self).__init__(parent=None, id=wx.ID_ANY, title=title)
        panel = wx.Panel(self)
        userSizer = wx.BoxSizer()
        self.cb = wx.ComboBox(panel, -1, choices=users, value=users[0], size=wx.DefaultSize)
        self.cb.SetFocus()
        self.autocompletion = wx.Button(panel, -1, _(u"&Autocomplete users"))
        userSizer.Add(wx.StaticText(panel, -1, _(u"User")), 0, wx.ALL, 5)
        userSizer.Add(self.cb, 0, wx.ALL, 5)
        userSizer.Add(self.autocompletion, 0, wx.ALL, 5)
        aliasSizer = wx.BoxSizer(wx.HORIZONTAL)
        aliasLabel = wx.StaticText(panel, wx.ID_ANY, _("Alias"))
        self.alias = wx.TextCtrl(panel, wx.ID_ANY)
        aliasSizer.Add(aliasLabel, 0, wx.ALL, 5)
        aliasSizer.Add(self.alias, 0, wx.ALL, 5)
        sizer = wx.BoxSizer(wx.VERTICAL)
        ok = wx.Button(panel, wx.ID_OK, _(u"OK"))
        ok.SetDefault()
        cancel = wx.Button(panel, wx.ID_CANCEL, _(u"Close"))
        btnsizer = wx.BoxSizer()
        btnsizer.Add(ok, 0, wx.ALL, 5)
        btnsizer.Add(cancel, 0, wx.ALL, 5)
        sizer.Add(userSizer, 0, wx.ALL, 5)
        sizer.Add(aliasSizer, 0, wx.ALL, 5)
        sizer.Add(btnsizer, 0, wx.ALL, 5)
        panel.SetSizer(sizer)
        self.SetClientSize(sizer.CalcMin())

    def get_user(self):
        return (self.cb.GetValue(), self.alias.GetValue())

class userAliasEditorDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        super(userAliasEditorDialog, self).__init__(parent=None)
        self.SetTitle(_("Edit user aliases"))
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        userListSizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, _("Users")), wx.VERTICAL)
        main_sizer.Add(userListSizer, 1, wx.EXPAND, 0)
        self.users = wx.ListBox(self, wx.ID_ANY, choices=[])
        self.users.Bind(wx.EVT_LISTBOX, self.on_selection_changes)
        userListSizer.Add(self.users, 0, 0, 0)
        actionsSizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, _("Actions")), wx.HORIZONTAL)
        main_sizer.Add(actionsSizer, 1, wx.EXPAND, 0)
        self.add = wx.Button(self, wx.ID_ANY, _("Add alias"))
        self.add.SetToolTip(_("Adds a new user alias"))
        actionsSizer.Add(self.add, 0, 0, 0)
        self.edit = wx.Button(self, wx.ID_ANY, _("Edit"))
        self.edit.SetToolTip(_("Edit the currently focused user Alias."))
        self.edit.Enable(False)
        actionsSizer.Add(self.edit, 0, 0, 0)
        self.remove = wx.Button(self, wx.ID_ANY, _("Remove"))
        self.remove.SetToolTip(_("Remove the currently focused user alias."))
        self.remove.Enable(False)
        actionsSizer.Add(self.remove, 0, 0, 0)
        btnSizer = wx.StdDialogButtonSizer()
        main_sizer.Add(btnSizer, 0, wx.ALIGN_RIGHT | wx.ALL, 4)
        self.button_CLOSE = wx.Button(self, wx.ID_CLOSE, "")
        btnSizer.AddButton(self.button_CLOSE)
        btnSizer.Realize()
        self.SetSizer(main_sizer)
        main_sizer.Fit(self)
        self.SetEscapeId(self.button_CLOSE.GetId())
        self.Layout()

    def on_selection_changes(self, *args, **kwargs):
        selection = self.users.GetSelection()
        if selection == -1:
            self.enable_action_buttons(False)
        else:
            self.enable_action_buttons(True)

    def get_selected_user(self):
        return self.users.GetStringSelection()

    def remove_alias_dialog(self, *args, **kwargs):
        dlg = wx.MessageDialog(self, _("Are you sure you want to delete this user alias?"), _("Remove user alias"), wx.YES_NO)
        if dlg.ShowModal() == wx.ID_YES:
            return True
        else:
            return False

    def enable_action_buttons(self, enabled=True):
        self.edit.Enable(enabled)
        self.remove.Enable(enabled)

    def edit_alias_dialog(self, title):
        dlg = wx.TextEntryDialog(self, title, _("User alias"))
        if dlg.ShowModal() == wx.ID_OK:
            return dlg.GetValue()