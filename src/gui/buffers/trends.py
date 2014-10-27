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
import sound
import config
import twitter
import gui.dialogs
import logging as original_logger
from base import basePanel
log = original_logger.getLogger("buffers.base")

class trendPanel(basePanel):
 def __init__(self, parent, window, name_buffer, *args, **kwargs):
  super(searchPanel, self).__init__(parent, window, name_buffer, sound)
  self.type = "trend"
  self.args = kwargs

 def start_streams(self):
  num = twitter.starting.search(self.db, self.twitter, self.name_buffer, **self.args)
  if num > 0: sound.player.play("search_updated.ogg")
  self.put_items(num)
  return num

 def remove_buffer(self):
  dlg = wx.MessageDialog(self, _(u"Do you really want to delete this search term?"), _(u"Attention"), style=wx.ICON_QUESTION|wx.YES_NO)
  if dlg.ShowModal() == wx.ID_YES:
    names = config.main["other_buffers"]["tweet_searches"]
    user = self.name_buffer[:-7]
    log.info(u"Deleting %s's search term" % user)
    if user in names:
     names.remove(user)
     self.db.settings.pop(self.name_buffer)
     pos = self.db.settings["buffers"].index(self.name_buffer)
     self.db.settings["buffers"].remove(self.name_buffer)
     return pos