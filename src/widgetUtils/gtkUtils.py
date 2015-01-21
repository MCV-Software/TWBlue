from gi.repository import Gtk, Gdk

toolkit = "gtk"
# Code responses for GTK +3 dialogs.
# this is when an user presses OK on a dialogue.
OK = Gtk.ResponseType.OK
# This is when an user presses cancel on a dialogue.
CANCEL = Gtk.ResponseType.CANCEL
# This is when an user closes the dialogue or an id to create the close button.
CLOSE = Gtk.ResponseType.CLOSE
# The response for a "yes" Button pressed on a dialogue.
YES = Gtk.ResponseType.YES
# This is when the user presses No on a default dialogue.
NO = Gtk.ResponseType.NO

#events
# This is raised when the application must be closed.
CLOSE_EVENT = "delete-event"
# This is activated when a button  is pressed.
BUTTON_PRESSED = "clicked"
# This is activated when an user enter text on an edit box.
#ENTERED_TEXT = wx.EVT_TEXT
MENU = "activate"

#KEYPRESS = wx.EVT_CHAR_HOOK
#NOTEBOOK_PAGE_CHANGED = wx.EVT_NOTEBOOK_PAGE_CHANGED
def exit_application():
 """ Closes the current window cleanly. """
 Gtk.main_quit()

def connect_event(parent, event, func, menuitem=None, *args, **kwargs):
 """ Connects an event to a function.
  parent Gtk.widget: The widget that will listen for the event.
  event widgetUtils.event: The event that will be listened for the parent. The event should be one of the widgetUtils events.
  function func: The function that will be connected to the event."""
 if menuitem == None:
  return getattr(parent, "connect")(event, func, *args, **kwargs)
 else:
  return getattr(menuitem, "connect")(event, func, *args, **kwargs)
