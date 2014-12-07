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
import gui.dialogs
import twitter
import config
import sound
import logging as original_logger
import output
import platform
import menus
from multiplatform_widgets import widgets
from mysc.thread_utils import call_threaded
log = original_logger.getLogger("buffers.base")

class trendsPanel(wx.Panel):
 
 def compose_function(self, trend):
  return [trend["name"]]

 def bind_events(self):
  self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.showMenu, self.list.list)
  self.Bind(wx.EVT_LIST_KEY_DOWN, self.showMenuByKey, self.list.list)
  self.list.list.Bind(wx.EVT_CHAR_HOOK, self.interact)

 def get_message(self, dialog=False):
  return self.compose_function(self.trends[self.list.get_selected()])[0]


 def create_list(self):
  self.list = widgets.list(self, _(u"Trending topic"), style=wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.LC_VRULES)
  if self.system == "Windows":
   self.list.set_windows_size(0, 30)
   self.list.set_size()

 def __init__(self, parent, window, name_buffer, argumento=None, sound=""):
  self.type = "trends"
  self.twitter = window.twitter
  self.name_buffer = name_buffer
  self.argumento = argumento
  self.sound = sound
  self.parent = window
  self.system = platform.system()
  wx.Panel.__init__(self, parent)
  self.trends = []
  self.sizer = wx.BoxSizer(wx.VERTICAL)
  self.create_list()
  self.btn = wx.Button(self, -1, _(u"Tweet"))
  self.btn.Bind(wx.EVT_BUTTON, self.post_status)
  self.tweetTrendBtn = wx.Button(self, -1, _(u"Tweet about this trend"))
  self.tweetTrendBtn.Bind(wx.EVT_BUTTON, self.onResponse)
  btnSizer = wx.BoxSizer(wx.HORIZONTAL)
  btnSizer.Add(self.btn, 0, wx.ALL, 5)
  btnSizer.Add(self.tweetTrendBtn, 0, wx.ALL, 5)
  self.sizer.Add(btnSizer, 0, wx.ALL, 5)
  self.sizer.Add(self.list.list, 0, wx.ALL, 5)
  self.bind_events()
  self.SetSizer(self.sizer)

 def remove_buffer(self):
  dlg = wx.MessageDialog(self, _(u"Do you really want to delete this buffer?"), _(u"Attention"), style=wx.ICON_QUESTION|wx.YES_NO)
  if dlg.ShowModal() == wx.ID_YES:
   topics = config.main["other_buffers"]["trending_topic_buffers"]
   topic = self.name_buffer[:-3]
   log.info(u"Deleting %s's trending topics buffer" % topic)
   if topic in topics:
    topics.remove(topic)
   return 0

 def start_streams(self):
  data = self.twitter.twitter.get_place_trends(id=self.argumento)
  if not hasattr(self, "name"):
   self.name = data[0]["locations"][0]["name"]
  self.trends = data[0]["trends"]
  # We need to get the trends sound, so the next line is commented.
#  sound.player.play(self.sound)
  return len(self.trends)

 def get_more_items(self):
  output.speak(_(u"This action is not supported for this buffer"))

 def put_items(self, num):
  selected_item = self.list.get_selected()
  self.list.clear()
  for i in self.trends:
   tweet = self.compose_function(i)
   self.list.insert_item(False, *tweet)
   self.set_list_position()
  self.list.select_item(selected_item)

 def post_status(self, ev=None):
  text = gui.dialogs.message.tweet(_(u"Write the tweet here"), _(u"Tweet"), "", self)
  if text.ShowModal() == wx.ID_OK:
   if text.image == None:
    call_threaded(self.twitter.api_call, call_name="update_status", _sound="tweet_send.ogg", status=text.text.GetValue())
   else:
    call_threaded(self.twitter.api_call, call_name="update_status_with_media", _sound="tweet_send.ogg", status=text.text.GetValue(), media=text.file)
  if ev != None: self.list.list.SetFocus()

 def onRetweet(self, event=None): pass

 def onResponse(self, ev):
  trend = self.trends[self.list.get_selected()]["name"]
  text = gui.dialogs.message.tweet(_(u"Write the tweet here"), _(u"Tweet"), trend, self)
  if text.ShowModal() == wx.ID_OK:
   if text.image == None:
    call_threaded(self.twitter.api_call, call_name="update_status", _sound="tweet_send.ogg", status=text.text.GetValue())
   else:
    call_threaded(self.twitter.api_call, call_name="update_status_with_media", _sound="tweet_send.ogg", status=text.text.GetValue(), media=text.file)
  if ev != None: self.list.list.SetFocus()

 def interact(self, ev):
  if type(ev) is str: event = ev
  else:
   if ev.GetKeyCode() == wx.WXK_F5: event = "volume_down"
   elif ev.GetKeyCode() == wx.WXK_F6: event = "volume_up"
   elif ev.GetKeyCode() == wx.WXK_DELETE and ev.ShiftDown(): event = "clear_list"
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
  elif event == "clear_list" and self.list.get_count() > 0:
   dlg = wx.MessageDialog(self, _(u"Do you really want to empty this buffer? It's items will be removed from the list"), _(u"Empty buffer"), wx.ICON_QUESTION|wx.YES_NO)
   if dlg.ShowModal() == wx.ID_YES:
    self.trends = []
    self.list.clear()
  try:
   ev.Skip()
  except:
   pass

 def set_list_position(self):
  if config.main["general"]["reverse_timelines"] == False:
   self.list.select_item(len(self.trends)-1)
  else:
   self.list.select_item(0)

 def showMenu(self, ev):
  if self.list.get_count() == 0: return
  self.PopupMenu(menus.trendsPanelMenu(self), ev.GetPosition())

 def showMenuByKey(self, ev):
  if self.list.get_count() == 0: return
  if ev.GetKeyCode() == wx.WXK_WINDOWS_MENU:
   self.PopupMenu(menus.trendsPanelMenu(self), self.list.list.GetPosition())
