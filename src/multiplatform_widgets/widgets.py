# -*- coding: utf-8 -*-
from builtins import str
from builtins import range
from builtins import object
import wx
import platform
import logging
log = logging.getLogger("multiplatform_widgets.widgets")

class list(object):
 def __init__(self, parent, *columns, **listArguments):
  self.system = platform.system()
  self.columns = columns
  self.listArguments = listArguments
  log.debug("Creating list: Columns: %s, arguments: %s" % (self.columns, self.listArguments))
  self.create_list(parent)
#  self.set_size()

 def set_windows_size(self, column, characters_max):
#  it = wx.ListItem()
#  dc = wx.WindowDC(self.list)
#  dc.SetFont(it.GetFont())
#  (x, y) = dc.GetTextExtent("r"*characters_max)
  self.list.SetColumnWidth(column, characters_max*2)

 def set_size(self):
  self.list.SetSize((self.list.GetBestSize()[0], 728))
#  self.list.SetSize((1439, 1000))

 def create_list(self, parent):
  if self.system == "Windows":
   self.list = wx.ListCtrl(parent, -1, **self.listArguments)
   for i in range(0, len(self.columns)):
    self.list.InsertColumn(i, "%s" % (self.columns[i]))
  else:
   self.list = wx.ListBox(parent, -1, choices=[])

 def insert_item(self, reversed, *item):
  """ Inserts an item on the list, depending on the OS."""
  if self.system == "Windows":
   if reversed == False: items = self.list.GetItemCount()
   else: items = 0
   self.list.InsertItem(items, str(item[0]))
   for i in range(1, len(self.columns)):
    self.list.SetItem(items, i, str(item[i]))
  else:
   self.list.Append(" ".join(item))

 def remove_item(self, pos):
  """ Deletes an item from the list."""
  if self.system == "Windows":
   if pos > 0: self.list.Focus(pos-1)
   self.list.DeleteItem(pos)
  else:
   if pos > 0: self.list.SetSelection(pos-1)
   self.list.Delete(pos)

 def clear(self):
  if self.system == "Windows":
   self.list.DeleteAllItems()
  else:
   self.list.Clear()

 def get_selected(self):
  if self.system == "Windows":
   return self.list.GetFocusedItem()
  else:
   return self.list.GetSelection()

 def select_item(self, pos):
  if self.system == "Windows":
   self.list.Focus(pos)
  else:
   self.list.SetSelection(pos)

 def get_count(self):
  if self.system == "Windows":
   selected = self.list.GetItemCount()
  else:
   selected = self.list.GetCount()
  if selected == -1:
   return 0
  else:
   return selected

 def get_text_column(self, indexId, column):
  item = self.list.GetItem(indexId, column)
  return item.GetText()

 def set_text_column(self, indexId, column, text):
  item = self.list.SetItem(indexId, column, str(text))
  return item