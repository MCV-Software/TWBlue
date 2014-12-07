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
from mysc.thread_utils import call_threaded
log = original_logger.getLogger("buffers.base")

class listPanel(basePanel):
 def __init__(self, parent, window, name_buffer, argumento="", sound=""):
  super(listPanel, self).__init__(parent, window, name_buffer, argumento=argumento, sound=sound)
  self.type = "list"
  self.users = []
  self.sound = "list_tweet.ogg"

 def start_streams(self):
  self.retrieve_ids()
  num = twitter.starting.start_list(self.db, self.twitter, self.name_buffer, list_id=self.argumento, count=config.main["general"]["max_tweets_per_call"])
  return num

 def retrieve_ids(self):
  self.users = twitter.starting.get_users_list(self.twitter, self.argumento)

 def remove_buffer(self):
  if self.type == "list":
   dlg = wx.MessageDialog(self, _(u"Do you really want to delete this list?"), _(u"Attention"), style=wx.ICON_QUESTION|wx.YES_NO)
   if dlg.ShowModal() == wx.ID_YES:
    names = config.main["other_buffers"]["lists"]
    user = self.name_buffer[:-5]
    log.info(u"Deleting %s's list" % user)
    if user in names:
     names.remove(user)
     self.db.settings.pop(self.name_buffer)
     pos = self.db.settings["buffers"].index(self.name_buffer)
     self.db.settings["buffers"].remove(self.name_buffer)
     return pos

 def remove_invalid_buffer(self):
  if self.type == "list":
   names = config.main["other_buffers"]["lists"]
   user = self.name_buffer[:-5]
   log.info(u"Deleting %s's list" % user)
   if user in names:
    names.remove(user)
    self.db.settings.pop(self.name_buffer)
    pos = self.db.settings["buffers"].index(self.name_buffer)
    self.db.settings["buffers"].remove(self.name_buffer)
    return pos