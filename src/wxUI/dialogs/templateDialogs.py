# -*- coding: UTF-8 -*-
import wx
import output
from typing import List

class EditTemplateDialog(wx.Dialog):
    def __init__(self, template: str, variables: List[str] = [], default_template: str = "", *args, **kwds) -> None:
        super(EditTemplateDialog, self).__init__(parent=None, title=_("Edit Template"), *args, **kwds)
        self.default_template = default_template
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        mainSizer.Add(sizer_1, 1, wx.EXPAND, 0)
        label_1 = wx.StaticText(self, wx.ID_ANY, _("Edit template"))
        sizer_1.Add(label_1, 0, 0, 0)
        self.template = wx.TextCtrl(self, wx.ID_ANY, template)
        sizer_1.Add(self.template, 0, 0, 0)
        sizer_2 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, _("Available variables")), wx.HORIZONTAL)
        mainSizer.Add(sizer_2, 1, wx.EXPAND, 0)
        self.variables = wx.ListBox(self, wx.ID_ANY, choices=["$"+v for v in variables])
        self.variables.Bind(wx.EVT_CHAR_HOOK, self.on_keypress)
        sizer_2.Add(self.variables, 0, 0, 0)
        sizer_3 = wx.StdDialogButtonSizer()
        mainSizer.Add(sizer_3, 0, wx.ALIGN_RIGHT | wx.ALL, 4)
        self.button_SAVE = wx.Button(self, wx.ID_SAVE)
        self.button_SAVE.SetDefault()
        sizer_3.AddButton(self.button_SAVE)
        self.button_CANCEL = wx.Button(self, wx.ID_CANCEL)
        sizer_3.AddButton(self.button_CANCEL)
        self.button_RESTORE = wx.Button(self, wx.ID_ANY, _("Restore template"))
        self.button_RESTORE.Bind(wx.EVT_BUTTON, self.on_restore)
        sizer_3.AddButton(self.button_CANCEL)
        sizer_3.Realize()
        self.SetSizer(mainSizer)
        mainSizer.Fit(self)
        self.SetAffirmativeId(self.button_SAVE.GetId())
        self.SetEscapeId(self.button_CANCEL.GetId())
        self.Layout()

    def on_keypress(self, event, *args, **kwargs):
        if event.GetKeyCode() == wx.WXK_RETURN:
            self.template.ChangeValue(self.template.GetValue()+self.variables.GetStringSelection()+", ")
            output.speak(self.template.GetValue()+self.variables.GetStringSelection()+", ")
            return
        event.Skip()

    def on_restore(self, *args, **kwargs) -> None:
        self.template.ChangeValue(self.default_template)
        output.speak(_("Restored template to {}.").format(self.default_template))
        self.template.SetFocus()

def invalid_template() -> None:
    wx.MessageDialog(None, _("the template you have specified include variables that do not exists for the object. Please fix the template and try again. For your reference, you can see a list of all available variables in the variables list while editing your template."), _("Invalid template"), wx.ICON_ERROR).ShowModal()