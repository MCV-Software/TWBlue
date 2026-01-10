# -*- coding: utf-8 -*-
import wx
import languageHandler


class AccountSettingsDialog(wx.Dialog):
    def __init__(self, parent=None, ask_before_boost=True):
        super(AccountSettingsDialog, self).__init__(parent, title=_("Bluesky Account Settings"))
        panel = wx.Panel(self)

        sizer = wx.BoxSizer(wx.VERTICAL)

        # Ask before boost/share
        self.ask_before_boost = wx.CheckBox(panel, wx.ID_ANY, _("Ask confirmation before sharing a post"))
        self.ask_before_boost.SetValue(bool(ask_before_boost))
        sizer.Add(self.ask_before_boost, 0, wx.ALL, 8)

        # Buttons
        btn_sizer = self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL)

        panel.SetSizer(sizer)

        main = wx.BoxSizer(wx.VERTICAL)
        main.Add(panel, 1, wx.EXPAND | wx.ALL, 10)
        if btn_sizer:
            main.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 10)
        self.SetSizerAndFit(main)

    def get_values(self):
        return {
            "ask_before_boost": self.ask_before_boost.GetValue(),
        }

