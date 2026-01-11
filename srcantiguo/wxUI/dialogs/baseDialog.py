# -*- coding: utf-8 -*-
import wx

class BaseWXDialog(wx.Dialog):
    def __init__(self, *args, **kwargs):
        super(BaseWXDialog, self).__init__(*args, **kwargs)

    def get_response(self):
        return self.ShowModal()

    def get(self, control):
        if hasattr(self, control):
            control = getattr(self, control)
            if hasattr(control, "GetValue"): return getattr(control, "GetValue")()
            elif hasattr(control, "GetLabel"): return getattr(control, "GetLabel")()
            else: return -1
        else: return 0

    def set(self, control, text):
        if hasattr(self, control):
            control = getattr(self, control)
            if hasattr(control, "SetValue"): return getattr(control, "SetValue")(text)
            elif hasattr(control, "SetLabel"): return getattr(control, "SetLabel")(text)
            elif hasattr(control, "ChangeValue"): return getattr(control, "ChangeValue")(text)
            else: return -1
        else: return 0

    def set_title(self, title):
        self.SetTitle(title)
