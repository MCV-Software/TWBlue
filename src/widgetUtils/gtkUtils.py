from gi.repository import Gtk, Gdk
from gi.repository import GObject

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
ENTERED_TEXT = "changed"
MENU = "activate"

#KEYPRESS = wx.EVT_CHAR_HOOK
#NOTEBOOK_PAGE_CHANGED = wx.EVT_NOTEBOOK_PAGE_CHANGED
CHECKBOX = "toggled"

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

class list(object):
 def __init__(self, *columns, **listArguments):
  self.columns = columns
  self.list_arguments = listArguments
  self.create_list()

 def create_list(self):
  columns = []
  [columns.append(str) for i in self.columns]
  self.store = Gtk.ListStore(*columns)
  self.list = Gtk.TreeView(model=self.store)
  renderer = Gtk.CellRendererText()
  for i in range(0, len(self.columns)):
   column = Gtk.TreeViewColumn(self.columns[i], renderer, text=i)
#   column.set_sort_column_id(i)        
   self.list.append_column(column)

 def insert_item(self, reversed=False, *item):
  if reversed == False:
   self.store.append(row=item)
  else:
   self.store.insert(position=0, row=item)

 def get_selected(self):
  tree_selection = self.list.get_selection()
  (model, pathlist) = tree_selection.get_selected_rows()
  return int(pathlist[0].to_string() )

 def select_item(self, item):
  tree_selection = self.list.get_selection()
  tree_selection.select_path(item)

 def remove_item(self, item):
  self.store.remove(self.store.get_iter(item))

 def get_count(self):
  return len(self.store)

class baseDialog(Gtk.Dialog):
 def __init__(self, *args, **kwargs):
  super(baseDialog, self).__init__(*args, **kwargs)
  self.box = self.get_content_area()

 def get_response(self):
  answer = self.run()
  return answer

class buffer(GObject.GObject):
 name = GObject.property(type=str)

 def __init__(self, obj):
  super(buffer, self).__init__()
  self.buffer = obj

class notebook(object):

 def __init__(self):
  self.store = Gtk.TreeStore(buffer.__gtype__)
  self.view = Gtk.TreeView()
  self.view.set_model(self.store)

  column = Gtk.TreeViewColumn("Buffer")
  cell = Gtk.CellRendererText()
  column.pack_start(cell, True)
  column.set_cell_data_func(cell, self.get_buffer)
  self.view.append_column(column)

 def get_current_page(self):
  tree_selection = self.view.get_selection()
  (model, pathlist) = tree_selection.get_selected_rows()
  iter = pathlist[0]
  return self.store[iter][0].buffer

 def get_buffer(self, column, cell, model, iter, data):
  cell.set_property('text', self.store.get_value(iter, 0).name)

 def match_func(self, row, name_, account):
  name = name_
  account = account
  iter = self.store.get_iter(row.path)
  if self.store[iter][0].buffer.name == name and self.store[iter][0].buffer.account == account:
   return (row.path, iter)
  else:
   return (None, None)

 def search(self, rows, name_, account):
  if not rows: return None
  for row in rows:
   (path, iter) = self.match_func(row, name_, account)
   if iter != None:
    return (path, iter)
   (result_path, result_iter) = self.search(row.iterchildren(), name_, account)
   if result_path: return (result_path, result_iter)
  return (None, None)

class mainLoopObject(object):

 def run(self):
  GObject.type_register(buffer)
  Gtk.main()
