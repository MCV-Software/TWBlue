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