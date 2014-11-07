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
import gui.dialogs
import logging as original_logger
from base import basePanel
from mysc.thread_utils import call_threaded
log = original_logger.getLogger("buffers.base")

class dmPanel(basePanel):
 def __init__(self, parent, window, name_buffer, function, argumento=None, sound=""):
  """ Class to DM'S. Reply and retweet buttons are not showed and they have your delete method for dm's."""
  super(dmPanel, self).__init__(parent, window, name_buffer, function, argumento=argumento, sound=sound)
  self.retweetBtn.Disable()
  self.responseBtn.Disable()

 def destroy_status(self, ev):
  index = self.list.get_selected()
  try:
   self.twitter.twitter.destroy_direct_message(id=self.db.settings[self.name_buffer][index]["id"])
   self.db.settings[self.name_buffer].pop(index)
   self.remove_item(index)
  except:
   sound.player.play("error.ogg")

 def onResponse(self, ev):
  dlg = gui.dialogs.message.dm(_("Direct message to %s") % (self.db.settings[self.name_buffer][self.list.get_selected()]["sender"]["screen_name"]), _(u"New direct message"), "", self)
  if dlg.ShowModal() == wx.ID_OK:
   call_threaded(self.twitter.api_call, call_name="send_direct_message", _sound="dm_sent.ogg", text=dlg.text.GetValue(), screen_name=dlg.cb.GetValue())
  if ev != None:
   self.list.list.SetFocus()