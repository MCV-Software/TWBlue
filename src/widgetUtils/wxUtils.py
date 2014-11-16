import wx

# Code responses for WX dialogs.
OK = wx.ID_OK
CANCEL = wx.ID_CANCEL
CLOSE = wx.ID_CLOSE
YES = wx.ID_YES
NO = wx.ID_NO

#events
CLOSE_EVENT = wx.EVT_CLOSE
BUTTON_PRESSED = wx.EVT_BUTTON
ENTERED_TEXT = wx.EVT_TEXT

def exit_application():
 wx.GetApp().ExitMainLoop()

def connect_event(parent, event, func):
 return getattr(parent, "Bind")(event, func)