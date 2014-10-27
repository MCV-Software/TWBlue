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
import platform
import gui.dialogs
import output
import logging as original_logger
from multiplatform_widgets import widgets
from mysc import event
from mysc.thread_utils import call_threaded
log = original_logger.getLogger("buffers.base")

class eventsPanel(wx.Panel):
 """ Buffer to show events. Different than tweets or people."""

 def get_more_items(self):
  output.speak(_(u"This action is not supported for this buffer"))

 def bind_events(self):
  self.Bind(event.MyEVT_OBJECT, self.update)

 def put_items(self, items):
  pass

 def get_selected_text(self):
  if self.list.get_count() == 0: return _(u"Empty")
  if self.system == "Windows":
   return "%s. %s" % (self.list.list.GetItemText(self.list.get_selected()), self.list.list.GetItemText(self.list.get_selected(), 1))
  else:
   return self.list.list.GetStringSelection()

 def get_message(self, dialog=False):
  return self.get_selected_text()

 def __init__(self, parent, window, sound=""):
  self.type = "event"
  self.system = platform.system()
  self.name_buffer = "events"
  self.parent = window
  self.sound = "new_event.ogg"
  wx.Panel.__init__(self, parent)
  sizer = wx.BoxSizer()
  self.list = widgets.list(self, _(u"Date"), _(u"Event"), size=(600,600), style=wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.LC_VRULES)
  self.tweet = wx.Button(self, -1, _(u"Tweet"))
  self.tweet.Bind(wx.EVT_BUTTON, self.post_status)
  self.delete_event = wx.Button(self, -1, _(u"Remove event"))
  self.delete_event.Bind(wx.EVT_BUTTON, self.on_delete_event)
  self.bind_events()

 def on_delete_event(self, ev):
  self.list.remove_item(self.get_selected())

 def remove_buffer(self):
  return None

 def start_streams(self):
  return 0

 def post_status(self, ev=None):
  text = gui.dialogs.message.tweet(_(u"Write the tweet here"), _(u"Tweet"), "", self.parent)
  if text.ShowModal() == wx.ID_OK:
   if text.image == None:
    call_threaded(self.parent.twitter.api_call, call_name="update_status", _sound="tweet_send.ogg", status=text.text.GetValue())
   else:
    call_threaded(self.parent.twitter.api_call, call_name="update_status_with_media", _sound="tweet_send.ogg", status=text.text.GetValue(), media=text.file)
#  text.Destroy()
  if ev != None: self.list.list.SetFocus()

 def update(self, ev):
  tweet = ev.GetItem()
  announce = ev.GetAnnounce()
  self.list.insert_item(config.main["general"]["reverse_timelines"], *tweet)
  if self.list.get_count() == 1:
   self.list.select_item(0)
  if self.name_buffer not in config.main["other_buffers"]["muted_buffers"]:
   if self.sound != "":  sound.player.play(self.sound)
#   if announce != "": output.speak(announce)
  if self.name_buffer in config.main["other_buffers"]["autoread_buffers"]:
   output.speak(" ".join(tweet))

 def interact(self, ev):
  if type(ev) is str: event = ev
  else:
   if ev.GetKeyCode() == wx.WXK_F5: event = "volume_down"
   elif ev.GetKeyCode() == wx.WXK_F6: event = "volume_up"
   elif ev.GetKeyCode() == wx.WXK_DELETE and ev.ShiftDown(): event = "clear_list"
   elif ev.GetKeyCode() == wx.WXK_DELETE: event = "delete_item"
   else:
    ev.Skip()
    return
  if event == "volume_down":
   if config.main["sound"]["volume"] > 0.05:
    config.main["sound"]["volume"] = config.main["sound"]["volume"]-0.05
    sound.player.play("volume_changed.ogg", False)
    if hasattr(self.parent, "audioStream"):
     self.parent.audioStream.stream.volume = config.main["sound"]["volume"]
  elif event == "volume_up":
   if config.main["sound"]["volume"] < 0.95:
    config.main["sound"]["volume"] = config.main["sound"]["volume"]+0.05
    sound.player.play("volume_changed.ogg", False)
    if hasattr(self.parent, "audioStream"):
     self.parent.audioStream.stream.volume = config.main["sound"]["volume"]
  elif event == "clear_list" and self.get_count() > 0:
   dlg = wx.MessageDialog(self, _(u"Do you really want to empty this buffer? It's tweets will be removed from the list but not from Twitter"), _(u"Empty buffer"), wx.ICON_QUESTION|wx.YES_NO)
   if dlg.ShowModal() == wx.ID_YES:
    self.list.clear()
  elif event == "delete_item":
   dlg = wx.MessageDialog(self, _(u"Do you really want to delete this message?"), _(u"Delete"), wx.ICON_QUESTION|wx.YES_NO)
   if dlg.ShowModal() == wx.ID_YES:
    self.list.remove_item(self.list.get_selected())
   else:
    return
  try:
   ev.Skip()
  except:
   pass