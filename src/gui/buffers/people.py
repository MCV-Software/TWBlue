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
import output
from multiplatform_widgets import widgets
from mysc import event
from base import basePanel
from mysc.thread_utils import call_threaded
from twython import TwythonError
log = original_logger.getLogger("buffers.base")

class peoplePanel(basePanel):
 """ Buffer used to show people."""
 def bind_events(self):
  self.Bind(event.MyEVT_OBJECT, self.update)
  self.Bind(event.MyEVT_DELETED, self.Remove)
  self.list.list.Bind(wx.EVT_CHAR_HOOK, self.interact)

 def create_list(self):
  self.list = widgets.list(self, _(u"User"), style=wx.LC_REPORT|wx.LC_SINGLE_SEL, size=(800, 800))

 def __init__(self, parent, window, name_buffer, function, argumento=None, sound="", timeline=False):
  super(peoplePanel, self).__init__(parent, window, name_buffer, function, argumento=argumento, sound=sound)
  self.type = "people"
  self.responseBtn.SetLabel(_(u"Mention"))
  self.retweetBtn.Disable()
  self.compose_function = twitter.compose.compose_followers_list

 def onDm(self, ev):
  if self.name_buffer == "sent": return
  if self.name_buffer == "direct_messages":
   self.onResponse(ev)
  else:
   user = self.db.settings[self.name_buffer][self.list.get_selected()]["screen_name"]
   dlg = gui.dialogs.message.dm(_("Direct message to %s") % (user,), _(u"New direct message"), "", self)
   if dlg.ShowModal() == wx.ID_OK:
    call_threaded(self.twitter.api_call, call_name="send_direct_message", _sound="dm_sent.ogg", text=dlg.text.GetValue(), screen_name=dlg.cb.GetValue())
#   dlg.Destroy()
  if ev != None:
   self.list.list.SetFocus()

 def onResponse(self, ev):
  dlg = gui.dialogs.message.reply(_(u"Mention to %s") % (self.db.settings[self.name_buffer][self.list.get_selected()]["screen_name"]), _(u"Mention"), u"@%s " % (self.db.settings[self.name_buffer][self.list.get_selected()]["screen_name"]), self)
  if dlg.ShowModal() == wx.ID_OK:
   if dlg.image == None:
    call_threaded(self.twitter.api_call, call_name="update_status", _sound="reply_send.ogg", in_reply_to_status_id=dlg.in_reply_to, status=dlg.text.GetValue())
   else:
    call_threaded(self.twitter.api_call, call_name="update_status_with_media", _sound="reply_send.ogg", in_reply_to_status_id=dlg.in_reply_to, status=dlg.text.GetValue(), media=dlg.file)
#  dlg.Destroy()
  if ev != None:   self.list.list.SetFocus()

 def Remove(self, ev):
  try:
   index = self.list.get_selected()
   self.list.remove_item(ev.GetItem())
  except:
   log.error("Unable to delete element %s from the list %s" % (str(ev.GetItem(), self.name_buffer)))

 def start_streams(self):
  num = twitter.starting.start_followers(self.db, self.twitter, self.name_buffer, self.function, param=self.argumento)
#   sound.player.play(self.sound)
  return num

 def put_items(self, num):
  if self.list.get_count() > 0:
   self.list.clear()
  for i in self.db.settings[self.name_buffer]:
   f = self.compose_function(i, self.db)
   self.list.insert_item(False, *f)
  self.set_list_position()

 def get_more_items(self):
  if self.name_buffer == "followers": cursor = twitter.starting.followers_cursor
  elif self.name_buffer == "friends": cursor = twitter.starting.friends_cursor
  try:
   items = twitter.starting.get_more_items(self.function, self.twitter, users=True, name=self.name_buffer, count=config.main["general"]["max_tweets_per_call"], cursor=cursor)
  except TwythonError as e:
   output.speak(e.message)
   return
  for i in items:
   if config.main["general"]["reverse_timelines"] == False:
    self.db.settings[self.name_buffer].insert(0, i)
   else:
    self.db.settings[self.name_buffer].append(i)
  if config.main["general"]["reverse_timelines"] == False:
   for i in items:
    tweet = self.compose_function(i, self.db)
    self.list.insert_item(True, *tweet)
  else:
   for i in items:
    tweet = self.compose_function(i, self.db)
    self.list.insert_item(False, *tweet)
  output.speak(_(u"%s items retrieved") % (len(items)))

 def interact(self, ev):
  if type(ev) is str: event = ev
  else:
   if ev.GetKeyCode() == wx.WXK_RETURN:
    event = "url"
   elif ev.GetKeyCode() == wx.WXK_F5:
    event = "volume_down"
   elif ev.GetKeyCode() == wx.WXK_F6:
    event = "volume_down"
   else:
    ev.Skip()
    return
  if event == "url":
   gui.dialogs.show_user.showUserProfile(self.parent.twitter, self.db.settings[self.name_buffer][self.list.get_selected()]["screen_name"]).ShowModal()
  elif event == "volume_down":
   if config.main["sound"]["volume"] > 0.05:
    config.main["sound"]["volume"] = config.main["sound"]["volume"]-0.05
    sound.player.play("volume_changed.ogg")
  elif event == "volume_up":
   if config.main["sound"]["volume"] < 0.95:
    config.main["sound"]["volume"] = config.main["sound"]["volume"]+0.05
    sound.player.play("volume_changed.ogg")
  if type(ev) is not str: ev.Skip()

 def remove_buffer(self):
  pos = None
  return pos

 def get_message(self, dialog=False):
  if dialog == False: return " ".join(self.compose_function(self.db.settings[self.name_buffer][self.list.get_selected()], self.db))
  else:
   list = self.compose_function(self.db.settings[self.name_buffer][self.list.get_selected()], self.db)
   return " ".join(list)
