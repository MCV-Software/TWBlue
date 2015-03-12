import wx

toolkit = "wx"
# Code responses for WX dialogs.
# this is when an user presses OK on a dialogue.
OK = wx.ID_OK
# This is when an user presses cancel on a dialogue.
CANCEL = wx.ID_CANCEL
# This is when an user closes the dialogue or an id to create the close button.
CLOSE = wx.ID_CLOSE
# The response for a "yes" Button pressed on a dialogue.
YES = wx.ID_YES
# This is when the user presses No on a default dialogue.
NO = wx.ID_NO

#events
# This is raised when the application must be closed.
CLOSE_EVENT = wx.EVT_CLOSE
# This is activated when a button  is pressed.
BUTTON_PRESSED = wx.EVT_BUTTON
CHECKBOX = wx.EVT_CHECKBOX
# This is activated when an user enter text on an edit box.
ENTERED_TEXT = wx.EVT_TEXT
MENU = wx.EVT_MENU
KEYPRESS = wx.EVT_CHAR_HOOK
KEYUP = wx.EVT_KEY_UP
NOTEBOOK_PAGE_CHANGED = wx.EVT_TREEBOOK_PAGE_CHANGED
RADIOBUTTON = wx.EVT_RADIOBUTTON
TASKBAR_RIGHT_CLICK = wx.EVT_TASKBAR_RIGHT_DOWN
TASKBAR_LEFT_CLICK = wx.EVT_TASKBAR_LEFT_DOWN
def exit_application():
 """ Closes the current window cleanly. """
 wx.GetApp().ExitMainLoop()

def connect_event(parent, event, func, menuitem=None, *args, **kwargs):
 """ Connects an event to a function.
  parent wx.window: The widget that will listen for the event.
  event widgetUtils.event: The event that will be listened for the parent. The event should be one of the widgetUtils events.
  function func: The function that will be connected to the event."""
 if menuitem == None:
  return getattr(parent, "Bind")(event, func, *args, **kwargs)
 else:
  return getattr(parent, "Bind")(event, func, menuitem, *args, **kwargs)

def connectExitFunction(exitFunction):
  wx.GetApp().Bind(wx.EVT_QUERY_END_SESSION, exitFunction)
  wx.GetApp().Bind(wx.EVT_END_SESSION, exitFunction)