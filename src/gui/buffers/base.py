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
import webbrowser
import config
import sound
import url_shortener
import logging as original_logger
import output
import platform
import datetime
from twitter import prettydate
from multiplatform_widgets import widgets
from mysc import event
from mysc.thread_utils import call_threaded
from twython import TwythonError
log = original_logger.getLogger("buffers.base")

class basePanel(wx.Panel):
 
 def bind_events(self):
  self.Bind(event.MyEVT_OBJECT, self.update)
  self.Bind(event.MyEVT_DELETED, self.Remove)
  self.list.list.Bind(wx.EVT_CHAR_HOOK, self.interact)
  if self.system == "Windows":
   self.list.list.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.onFocus)
  else:
   self.list.list.Bind(wx.EVT_LISTBOX, self.onFocus)

 def get_message(self, dialog=False):
  if dialog == False: return " ".join(self.compose_function(self.db.settings[self.name_buffer][self.list.get_selected()], self.db))
  else:
   list = self.compose_function(self.db.settings[self.name_buffer][self.list.get_selected()], self.db)
   return " ".join(list[1:-2])

 def create_list(self):
  self.list = widgets.list(self, _(u"User"), _(u"Text"), _(u"Date"), _(u"Client"), style=wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.LC_VRULES)
  if self.system == "Windows":
   self.list.set_windows_size(0, 30)
   self.list.set_windows_size(1, 160)
   self.list.set_windows_size(2, 55)
   self.list.set_windows_size(3, 42)
   self.list.set_size()

 def __init__(self, parent, window, name_buffer, function=None, argumento=None, sound="", timeline=False):
  if timeline == False:
   self.type = "buffer"
  elif timeline == True:
   self.type = "timeline"
  self.db = window.db
  self.twitter = window.twitter
  self.name_buffer = name_buffer
  self.function = function
  self.argumento = argumento
  self.sound = sound
  self.parent = window
  self.compose_function = twitter.compose.compose_tweet
  self.system = platform.system()
  wx.Panel.__init__(self, parent)
  self.sizer = wx.BoxSizer(wx.VERTICAL)
  self.create_list()
  self.btn = wx.Button(self, -1, _(u"Tweet"))
  self.btn.Bind(wx.EVT_BUTTON, self.post_status)
  self.retweetBtn = wx.Button(self, -1, _(u"Retweet"))
  self.retweetBtn.Bind(wx.EVT_BUTTON, self.onRetweet)
  self.responseBtn = wx.Button(self, -1, _(u"Reply"))
  self.responseBtn.Bind(wx.EVT_BUTTON, self.onResponse)
  self.dmBtn = wx.Button(self, -1, _(u"Direct message"))
  self.dmBtn.Bind(wx.EVT_BUTTON, self.onDm)
  btnSizer = wx.BoxSizer(wx.HORIZONTAL)
  btnSizer.Add(self.btn, 0, wx.ALL, 5)
  btnSizer.Add(self.retweetBtn, 0, wx.ALL, 5)
  btnSizer.Add(self.responseBtn, 0, wx.ALL, 5)
  btnSizer.Add(self.dmBtn, 0, wx.ALL, 5)
  self.sizer.Add(btnSizer, 0, wx.ALL, 5)
  self.sizer.Add(self.list.list, 0, wx.ALL, 5)
  self.bind_events()
  self.SetSizer(self.sizer)

 def remove_buffer(self):
  if self.type == "timeline":
   dlg = wx.MessageDialog(self, _(u"Do you really want to delete this timeline?"), _(u"Attention"), style=wx.ICON_QUESTION|wx.YES_NO)
   if dlg.ShowModal() == wx.ID_YES:
    names = config.main["other_buffers"]["timelines"]
    user = self.name_buffer
    log.info(u"Deleting %s's timeline" % user)
    if user in names:
     names.remove(user)
     self.db.settings.pop(user)
     pos = self.db.settings["buffers"].index(user)
     self.db.settings["buffers"].remove(user)
     return pos
  elif self.type == "buffer":
   output.speak(_(u"This buffer is not a timeline; it can't be deleted."))
   return None

 def remove_invalid_buffer(self):
  if self.type == "timeline":
   names = config.main["other_buffers"]["timelines"]
   user = self.name_buffer
   log.info(u"Deleting %s's timeline" % user)
   if user in names:
    names.remove(user)
    self.db.settings.pop(user)
    pos = self.db.settings["buffers"].index(user)
    self.db.settings["buffers"].remove(user)
    return pos

 def Remove(self, ev):
#  try:
  self.list.remove_item(ev.GetItem())
#  except:
#   log.error(u"Cannot delete the %s item from list " % str(ev.GetItem()))

 def destroy_status(self, ev):
  index = self.list.get_selected()
  try:
   self.twitter.twitter.destroy_status(id=self.db.settings[self.name_buffer][index]["id"])
   self.db.settings[self.name_buffer].pop(index)
   self.list.remove_item(index)
   if index > 0:
    self.list.select_item(index-1)
  except:
   sound.player.play("error.ogg")

 def onFocus(self, ev):
  if self.db.settings[self.name_buffer][self.list.get_selected()].has_key("retweeted_status"): tweet = self.db.settings[self.name_buffer][self.list.get_selected()]["retweeted_status"]
  else: tweet = self.db.settings[self.name_buffer][self.list.get_selected()]
  if config.main["general"]["relative_times"] == True:
   # On windows we need only put the new date on the column, but under linux and mac it isn't possible.
   if self.system == "Windows":
    original_date = datetime.datetime.strptime(tweet["created_at"], "%a %b %d %H:%M:%S +0000 %Y")
    date = original_date-datetime.timedelta(seconds=-self.db.settings["utc_offset"])
    ts = prettydate(original_date)
    self.list.list.SetStringItem(self.list.get_selected(), 2, ts)
   else:
    self.list.list.SetString(self.list.get_selected(), " ".join(self.compose_function(self.db.settings[self.name_buffer][self.list.get_selected()], self.db)))
  if twitter.utils.is_audio(tweet):
   sound.player.play("audio.ogg", False)

 def start_streams(self):
  if self.name_buffer == "sent":
   num = twitter.starting.start_sent(self.db, self.twitter, self.name_buffer, self.function, param=self.argumento)
  else:
#   try:
   if self.argumento != None:
    num = twitter.starting.start_stream(self.db, self.twitter, self.name_buffer, self.function, param=self.argumento)
   else:
    num = twitter.starting.start_stream(self.db, self.twitter, self.name_buffer, self.function)
#   except TwythonError:
#    raise TwythonError
#    self.parent.delete_invalid_timeline()
   if self.sound != "" and num > 0 and self.name_buffer != "home_timeline" and self.name_buffer != "sent": sound.player.play(self.sound)
  return num

 def get_more_items(self):
  if config.main["general"]["reverse_timelines"] == False:
   last_id = self.db.settings[self.name_buffer][0]["id"]
  else:
   last_id = self.db.settings[self.name_buffer][-1]["id"]
  try:
   items = twitter.starting.get_more_items(self.function, self.twitter, count=config.main["general"]["max_tweets_per_call"], max_id=last_id)
  except TwythonError as e:
   output.speak(e.message)
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

 def put_items(self, num):
  if self.list.get_count() == 0:
   for i in self.db.settings[self.name_buffer]:
    tweet = self.compose_function(i, self.db)
    self.list.insert_item(False, *tweet)
   self.set_list_position()
  elif self.list.get_count() > 0:
   if config.main["general"]["reverse_timelines"] == False:
    for i in self.db.settings[self.name_buffer][:num]:
     tweet = self.compose_function(i, self.db)
     self.list.insert_item(False, *tweet)
   else:
    for i in self.db.settings[self.name_buffer][0:num]:
     tweet = self.compose_function(i, self.db)
     self.list.insert_item(True, *tweet)

 def onDm(self, ev):
  if self.name_buffer == "sent": return
  if self.name_buffer == "direct_messages":
   self.onResponse(ev)
  else:
   user = self.db.settings[self.name_buffer][self.list.get_selected()]["user"]["screen_name"]
   dlg = gui.dialogs.message.dm(_("Direct message to %s") % (user,), "", "", self)
   if dlg.ShowModal() == wx.ID_OK:
    call_threaded(self.twitter.api_call, call_name="send_direct_message", _sound="dm_sent.ogg", text=dlg.text.GetValue(), screen_name=dlg.cb.GetValue())
#   dlg.Destroy()
  if ev != None:
   self.list.list.SetFocus()

 def post_status(self, ev=None):
  text = gui.dialogs.message.tweet(_(u"Write the tweet here"), _(u"Tweet"), "", self)
  if text.ShowModal() == wx.ID_OK:
   if text.image == None:
    call_threaded(self.twitter.api_call, call_name="update_status", _sound="tweet_send.ogg", status=text.text.GetValue())
   else:
    call_threaded(self.twitter.api_call, call_name="update_status_with_media", _sound="tweet_send.ogg", status=text.text.GetValue(), media=text.file)
#  text.Destroy()
  if ev != None: self.list.list.SetFocus()

 def onRetweet(self, ev):
  if self.name_buffer != "direct_messages":
   id=self.db.settings[self.name_buffer][self.list.get_selected()]["id"]
   ask = wx.MessageDialog(self.parent, _(u"Would you like to add a comment to this tweet?"), _("Retweet"), wx.YES_NO|wx.CANCEL|wx.ICON_QUESTION)
   response = ask.ShowModal()
   if response == wx.ID_YES:
    dlg = gui.dialogs.message.retweet(_(u"Add your comment to the tweet"), "", u"“@%s: %s ”" % (self.db.settings[self.name_buffer][self.list.get_selected()]["user"]["screen_name"], self.db.settings[self.name_buffer][self.list.get_selected()]["text"]), self)
    if dlg.ShowModal() == wx.ID_OK:
     if dlg.image == None:
      call_threaded(self.twitter.api_call, call_name="update_status", _sound="retweet_send.ogg", status=dlg.text.GetValue(), in_reply_to_status_id=dlg.in_reply_to)
     else:
      call_threaded(self.twitter.call_api, call_name="update_status_with_media", _sound="retweet_send.ogg", status=dlg.text.GetValue(), in_reply_to_status_id=text.in_reply_to, media=dlg.file)
#     dlg.Destroy()
    if ev != None:
     self.list.list.SetFocus()
   elif response == wx.ID_NO:
    call_threaded(self.twitter.api_call, call_name="retweet", _sound="retweet_send.ogg", id=id)
   if ev != None: self.list.list.SetFocus()
   ask.Destroy()

 def onResponse(self, ev):
  if self.name_buffer == "sent": return
  dlg = gui.dialogs.message.reply(_(u"Reply to %s") % (self.db.settings[self.name_buffer][self.list.get_selected()]["user"]["screen_name"]), "", u"@%s " % (self.db.settings[self.name_buffer][self.list.get_selected()]["user"]["screen_name"]), self)
  if dlg.ShowModal() == wx.ID_OK:
   if dlg.image == None:
    call_threaded(self.twitter.api_call, call_name="update_status", _sound="reply_send.ogg", in_reply_to_status_id=dlg.in_reply_to, status=dlg.text.GetValue())
   else:
    call_threaded(self.twitter.api_call, call_name="update_status_with_media", _sound="reply_send.ogg", in_reply_to_status_id=dlg.in_reply_to, status=dlg.text.GetValue(), media=dlg.file)
#  dlg.Destroy()
  if ev != None:   self.list.list.SetFocus()

 def update(self, ev):
  data = ev.GetItem()
  announce = ev.GetAnnounce()
  if config.main["general"]["reverse_timelines"] == False: self.db.settings[self.name_buffer].append(data)
  else: self.db.settings[self.name_buffer].insert(0, data)
  tweet = self.compose_function(data, self.db)
  self.list.insert_item(config.main["general"]["reverse_timelines"], *tweet)
  if self.name_buffer not in config.main["other_buffers"]["muted_buffers"]:
   if self.sound != "":  sound.player.play(self.sound)
   if announce != "": output.speak(announce)
   if self.name_buffer in config.main["other_buffers"]["autoread_buffers"]:
    output.speak(" ".join(tweet[:2]))

 def interact(self, ev):
  try:
   if self.db.settings[self.name_buffer][self.list.get_selected()].has_key("retweeted_status"):  tweet = self.db.settings[self.name_buffer][self.list.get_selected()]["retweeted_status"]
   else: tweet = self.db.settings[self.name_buffer][self.list.get_selected()]
   urls = twitter.utils.find_urls_in_text(tweet["text"])
  except:
   urls = []
  if type(ev) is str: event = ev
  else:
   if ev.GetKeyCode() == wx.WXK_RETURN and ev.ControlDown(): event = "audio"
   elif ev.GetKeyCode() == wx.WXK_RETURN: event = "url"
   elif ev.GetKeyCode() == wx.WXK_F5: event = "volume_down"
   elif ev.GetKeyCode() == wx.WXK_F6: event = "volume_up"
   elif ev.GetKeyCode() == wx.WXK_DELETE and ev.ShiftDown(): event = "clear_list"
   elif ev.GetKeyCode() == wx.WXK_DELETE: event = "delete_item"
   else:
    ev.Skip()
    return
  if event == "audio"  and len(urls) > 0:
   self.streamer(urls[0])
  elif event == "url":
   if len(urls) == 0: return
   elif len(urls) == 1:
    output.speak(_(u"Opening URL..."), True)
    webbrowser.open(urls[0])
   elif len(urls) > 1:
    gui.dialogs.urlList.urlList(urls).ShowModal()
  elif event == "volume_down":
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
   dlg = wx.MessageDialog(self, _(u"Do you really want to empty this buffer? It's tweets will be removed from the list but not from Twitter"), _(u"Empty buffer"), wx.ICON_QUESTION|wx.YES_NO)
   if dlg.ShowModal() == wx.ID_YES:
    self.db.settings[self.name_buffer] = []
    self.list.clear()
  elif event == "delete_item":
   dlg = wx.MessageDialog(self, _(u"Do you really want to delete this message?"), _(u"Delete"), wx.ICON_QUESTION|wx.YES_NO)
   if dlg.ShowModal() == wx.ID_YES:
    self.destroy_status(wx.EVT_MENU)
   else:
    return
  try:
   ev.Skip()
  except:
   pass

 def streamer(self, url):
  if hasattr(self.parent, "audioStream"):
   if self.parent.audioStream.stream.is_active() == 0:
    output.speak(_(u"Playing..."))
    self.parent.audioStream = sound.urlStream(url)
    try:
     self.parent.audioStream.prepare()
     self.parent.audioStream.play()
    except:
     del self.parent.audioStream
     output.speak(_(u"Unable to play audio."))
   else:
    output.speak(_(u"Audio stopped."))
    self.parent.audioStream.stream.stop()
  else:
   output.speak(_(u"Playing..."))
   self.parent.audioStream = sound.urlStream(url)
   try:
    self.parent.audioStream.prepare()
    self.parent.audioStream.play()
   except:
    output.speak(_(u"Unable to play audio."))
    del self.parent.audioStream

 def set_list_position(self):
  if config.main["general"]["reverse_timelines"] == False:
   self.list.select_item(len(self.db.settings[self.name_buffer])-1)
  else:
   self.list.select_item(0)
