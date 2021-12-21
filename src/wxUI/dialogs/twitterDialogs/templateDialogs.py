# -*- coding: UTF-8 -*-
import wx

class EditTemplateDialog(wx.Dialog):
    def __init__(self, template, variables=[], *args, **kwds):
        super(EditTemplateDialog, self).__init__(parent=None, title=_("Edit Template"), *args, **kwds)
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
        sizer_3.Realize()
        self.SetSizer(mainSizer)
        mainSizer.Fit(self)
        self.SetAffirmativeId(self.button_SAVE.GetId())
        self.SetEscapeId(self.button_CANCEL.GetId())
        self.Layout()

    def on_keypress(self, event, *args, **kwargs):
        if event.GetKeyCode() == wx.WXK_RETURN:
            self.template.ChangeValue(self.template.GetValue()+self.variables.GetStringSelection()+", ")
            return
        event.Skip()