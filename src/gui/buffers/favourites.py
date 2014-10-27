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
import config
import sound
import logging as original_logger
from base import basePanel
log = original_logger.getLogger("buffers.base")

class favsPanel(basePanel):
 def __init__(self, parent, window, name_buffer, argumento=None, sound=""):
  super(favsPanel, self).__init__(parent, window, name_buffer, function="", argumento=argumento, sound=sound)
  self.type = "favourites_timeline"

 def start_streams(self):
  num = twitter.starting.get_favourites_timeline(self.db, self.twitter, self.name_buffer, param=self.argumento, count=200)
  if self.sound != "" and num > 0: 
   sound.player.play(self.sound)
   if self.list.get_count() > 0: self.put_items(num)
   return num
  return num

 def remove_buffer(self):
  dlg = wx.MessageDialog(self, _(u"Do you really want to delete this favourites timeline?"), _(u"Attention"), style=wx.ICON_QUESTION|wx.YES_NO)
  if dlg.ShowModal() == wx.ID_YES:
   names = config.main["other_buffers"]["favourites_timelines"]
   user = self.argumento
   log.info(u"Deleting %s's timeline" % user)
   if user in names:
    names.remove(user)
    self.db.settings.pop(self.name_buffer)
    pos = self.db.settings["buffers"].index(self.name_buffer)
    self.db.settings["buffers"].remove(self.name_buffer)
    return pos

 def remove_invalid_buffer(self):
  names = config.main["other_buffers"]["favourites_timelines"]
  user = self.name_buffer[:-5]
  log.info(u"Deleting %s's timeline" % user)
  if user in names:
   names.remove(user)
   self.db.settings.pop(self.name_buffer)
   pos = self.db.settings["buffers"].index(self.name_buffer)
   self.db.settings["buffers"].remove(self.name_buffer)
   return pos