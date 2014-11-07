# -*- coding: utf-8 -*-
############################################################
#    Copyright (c) 2013, 2014 Manuel Eduardo Cortéz Vallejo <manuel@manuelcortez.net>
#       
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
############################################################
import wx
import twitter
import logging as original_logger
import sound
from people import peoplePanel
from mysc import event
from multiplatform_widgets import widgets
log = original_logger.getLogger("buffers.base")

class searchUsersPanel(peoplePanel):
 def create_list(self):
  """ Returns the list for put the tweets here."""
  self.list = widgets.list(self, _(u"User"), style=wx.LC_REPORT|wx.LC_SINGLE_SEL, size=(800, 800))

# def bind_events(self):
#  self.Bind(event.MyEVT_OBJECT, self.update)
#  self.list.list.Bind(wx.EVT_CHAR_HOOK, self.interact)

 def __init__(self, parent, window, name_buffer, *args, **kwargs):
  super(searchUsersPanel, self).__init__(parent, window, name_buffer, function=None)
  self.compose_function = twitter.compose.compose_followers_list
  self.create_list()
  self.args = args
  self.kwargs = kwargs
  self.type = "timeline"

 def start_streams(self):
  num = twitter.starting.search_users(self.db, self.twitter, self.name_buffer, **self.kwargs)
  if num > 0: sound.player.play("search_updated.ogg")
#  self.put_items(num)
  return num

 def load_search(self):
  num = self.start_streams()
  self.put_items(num)

 def remove_buffer(self):
  dlg = wx.MessageDialog(self, _(u"Do you really want to delete this search term?"), _(u"Attention"), style=wx.ICON_QUESTION|wx.YES_NO)
  if dlg.ShowModal() == wx.ID_YES:
     self.db.settings.pop(self.name_buffer)
     pos = self.db.settings["buffers"].index(self.name_buffer)
     self.db.settings["buffers"].remove(self.name_buffer)
     return pos

 def get_more_items(self):
  output.speak(_(u"This action is not supported for this buffer"))