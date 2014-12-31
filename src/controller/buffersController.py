# -*- coding: utf-8 -*-
import wx
import widgetUtils
import datetime
import webbrowser
import output
import config
import sound
from twitter import compose, prettydate, utils
from wxUI import buffers, dialogs

class bufferController(object):
 def __init__(self, parent=None, function=None, session=None, *args, **kwargs):
  super(bufferController, self).__init__()
  self.function = function
  self.compose_function = None
  self.args = args
  self.kwargs = kwargs
  self.buffer = None
  self.account = ""
  self.needs_init = True

 def get_event(self, ev):
  if ev.GetKeyCode() == wx.WXK_RETURN and ev.ControlDown(): event = "audio"
  elif ev.GetKeyCode() == wx.WXK_RETURN: event = "url"
  elif ev.GetKeyCode() == wx.WXK_F5: event = "volume_down"
  elif ev.GetKeyCode() == wx.WXK_F6: event = "volume_up"
  elif ev.GetKeyCode() == wx.WXK_DELETE and ev.ShiftDown(): event = "clear_list"
  elif ev.GetKeyCode() == wx.WXK_DELETE: event = "delete_item"
  else:
   event = None
   ev.Skip()
  if event != None:
#   try:
   getattr(self, event)()
#   except AttributeError:
   #pass
 
 def volume_down(self):
  if config.app["app-settings"]["volume"] > 0.0:
   if config.app["app-settings"]["volume"] <= 0.05:
    config.app["app-settings"]["volume"] = 0.0
   else:
    config.app["app-settings"]["volume"] -=0.05
  if hasattr(sound.URLStream, "stream"):
   sound.URLStream.stream.volume = config.app["app-settings"]["volume"]
  sound.player.play("volume_changed.ogg")

 def volume_up(self):
  if config.app["app-settings"]["volume"] < 1.0:
   if config.app["app-settings"]["volume"] >= 0.95:
    config.app["app-settings"]["volume"] = 1.0
   else:
    config.app["app-settings"]["volume"] +=0.05
  if hasattr(sound.URLStream, "stream"):
   sound.URLStream.stream.volume = config.app["app-settings"]["volume"]
  sound.player.play("volume_changed.ogg")

 def start_stream(self):
  pass

 def put_items_on_list(self, items):
  pass

 def remove_buffer(self):
  pass

 def remove_item(self, item):
  self.buffer.list.remove_item(item)

 def bind_events(self):
  pass

 def get_object(self):
  return self.buffer

 def set_list_position(self, reversed=False):
  if reversed == False:
   self.buffer.list.select_item(-1)
  else:
   self.buffer.list.select_item(0)

class accountPanel(bufferController):
 def __init__(self, parent, name, account):
  super(accountPanel, self).__init__(parent, None, name)
  self.buffer = buffers.accountPanel(parent, name)
  self.type = self.buffer.type
  self.compose_function = None
  self.session = None
  self.needs_init = False
  self.id = self.buffer.GetId()
  self.account = account
  self.buffer.account = account
  self.name = name

class emptyPanel(bufferController):
 def __init__(self, parent, name, account):
  super(emptyPanel, self).__init__(parent, None, name)
  self.buffer = buffers.emptyPanel(parent, name)
  self.type = self.buffer.type
  self.compose_function = None
  self.id = self.buffer.GetId()
  self.account = account
  self.buffer.account = account
  self.name = name
  self.session = None
  self.needs_init = True
class baseBufferController(bufferController):
 def __init__(self, parent, function, name, sessionObject, account, bufferType=None, *args, **kwargs):
  super(baseBufferController, self).__init__(parent, function, *args, **kwargs)
  if bufferType != None:
   self.buffer = getattr(buffers, bufferType)(parent, name)
  else:
   self.buffer = buffers.basePanel(parent, name)
  self.name = name
  self.type = self.buffer.type
  self.id = self.buffer.GetId()
  self.session = sessionObject
  self.compose_function = compose.compose_tweet
  self.account = account
  self.buffer.account = account
  self.bind_events()

 def start_stream(self):
  val = self.session.call_paged(self.function, *self.args, **self.kwargs)
  number_of_items = self.session.order_buffer(self.name, val)
  self.put_items_on_list(number_of_items)

 def put_items_on_list(self, number_of_items):
  if self.buffer.list.get_count() == 0:
   for i in self.session.db[self.name]:
    tweet = self.compose_function(i, self.session.db, self.session.settings["general"]["relative_times"])
    self.buffer.list.insert_item(False, *tweet)
#   self.buffer.set_list_position()
  elif self.buffer.list.get_count() > 0:
   if self.session.settings["general"]["reverse_timelines"] == False:
    for i in self.session.db[self.name][:number_of_items]:
     tweet = self.compose_function(i, self.session.db, self.session.settings["general"]["relative_times"])
     self.buffer.list.insert_item(False, *tweet)
   else:
    for i in self.session.db[self.name][0:number_of_items]:
     tweet = self.compose_function(i, self.session.db, self.session.settings["general"]["relative_times"])
     self.buffer.list.insert_item(True, *tweet)

 def add_new_item(self, item):
  tweet = self.compose_function(item, self.session.db, self.session.settings["general"]["relative_times"])
  if self.session.settings["general"]["reverse_timelines"] == False:
   self.buffer.list.insert_item(False, *tweet)
  else:
   self.buffer.list.insert_item(True, *tweet)

 def bind_events(self):
  self.buffer.list.list.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.onFocus)
  self.buffer.list.list.Bind(wx.EVT_CHAR_HOOK, self.get_event)

 def get_tweet(self):
  if self.session.db[self.name][self.buffer.list.get_selected()].has_key("retweeted_status"):
   tweet = self.session.db[self.name][self.buffer.list.get_selected()]["retweeted_status"]
  else:
   tweet = self.session.db[self.name][self.buffer.list.get_selected()]
  return tweet

 def onFocus(self, ev):
  tweet = self.get_tweet()
  if self.session.settings["general"]["relative_times"] == True:
   original_date = datetime.datetime.strptime(self.session.db[self.name][self.buffer.list.get_selected()]["created_at"], "%a %b %d %H:%M:%S +0000 %Y")
   ts = prettydate(original_date)
   self.buffer.list.list.SetStringItem(self.buffer.list.get_selected(), 2, ts)
  if utils.is_audio(tweet):
   sound.player.play("audio.ogg")

 def audio(self):
  tweet = self.get_tweet()
  urls = utils.find_urls(tweet)
  if len(urls) == 1:
   sound.URLPlayer.play(urls[0])
  else:
   urls_list = dialogs.urlList.urlList()
   urls_list.populate_list(urls)
   if urls_list.get_response() == widgetUtils.OK:
    sound.URLPlayer.play(urls_list.get_string())

 def url(self):
  tweet = self.get_tweet()
  urls = utils.find_urls(tweet)
  if len(urls) == 1:
   output.speak(_(u"Opening URL..."))
   webbrowser.open_new_tab(urls[0])
  elif len(urls) > 1:
   urls_list = dialogs.urlList.urlList()
   urls_list.populate_list(urls)
   if urls_list.get_response() == widgetUtils.OK:
    output.speak(_(u"Opening URL..."))
    webbrowser.open_new_tab(urls_list.get_string())

 def clear_list(self):
  dlg = wx.MessageDialog(None, _(u"Do you really want to empty this buffer? It's tweets will be removed from the list but not from Twitter"), _(u"Empty buffer"), wx.ICON_QUESTION|wx.YES_NO)
  if dlg.ShowModal() == widgetUtils.YES:
   self.session.db[self.name] = []
   self.buffer.list.clear()
  dlg.Destroy()

 def delete_item(self):
  dlg = wx.MessageDialog(None, _(u"Do you really want to delete this message?"), _(u"Delete"), wx.ICON_QUESTION|wx.YES_NO)
  if dlg.ShowModal() == widgetUtils.YES:
   index = self.buffer.list.get_selected()
   try:
    self.session.twitter.twitter.destroy_status(id=self.session.db[self.name][index]["id"])
    self.session.db[self.name].pop(index)
    self.buffer.list.remove_item(index)
    if index > 0:
     self.buffer.list.select_item(index-1)
   except:
    sound.player.play("error.ogg")

class eventsBufferController(bufferController):
 def __init__(self, parent, name, session, account, *args, **kwargs):
  super(eventsBufferController, self).__init__(parent, *args, **kwargs)
  self.buffer = buffers.eventsPanel(parent, name)
  self.name = name
  self.account = account
  self.id = self.buffer.GetId()
  self.compose_function = compose.compose_event
  self.session = session

 def add_new_item(self, item):
  tweet = self.compose_function(item, self.session.db["user_name"])
  if self.session.settings["general"]["reverse_timelines"] == False:
   self.buffer.list.insert_item(False, *tweet)
  else:
   self.buffer.list.insert_item(True, *tweet)

class peopleBufferController(baseBufferController):
 def __init__(self, parent, function, name, sessionObject, account, bufferType=None, *args, **kwargs):
  super(peopleBufferController, self).__init__(parent, function, name, sessionObject, account, bufferType="peoplePanel")
  self.compose_function = compose.compose_followers_list

 def onFocus(self, ev):
  pass

 def delete_item(self): pass

 def start_stream(self):
  val = self.session.get_cursored_stream(self.name, self.function, *self.args, **self.kwargs)
#  self.session.order_cursored_buffer(self.name, self.session.db[self.name])
  self.put_items_on_list(val)

 def put_items_on_list(self, number_of_items):
  if self.buffer.list.get_count() == 0:
   for i in self.session.db[self.name]["items"]:
    tweet = self.compose_function(i, self.session.db, self.session.settings["general"]["relative_times"])
    self.buffer.list.insert_item(False, *tweet)
#   self.buffer.set_list_position()
  elif self.buffer.list.get_count() > 0:
   if self.session.settings["general"]["reverse_timelines"] == False:
    for i in self.session.db[self.name]["items"][:number_of_items]:
     tweet = self.compose_function(i, self.session.db)
     self.buffers.list.insert_item(False, *tweet)
   else:
    for i in self.session.db[self.name]["items"][0:number_of_items]:
     tweet = self.compose_function(i, self.session.db)
     self.buffer.list.insert_item(True, *tweet)

class searchBufferController(baseBufferController):
 def start_stream(self):
  val = getattr(self.session.twitter.twitter, self.function)(*self.args, **self.kwargs)
  number_of_items = self.session.order_buffer(self.name, val["statuses"])
  self.put_items_on_list(number_of_items)
  if number_of_items > 0:
   sound.player.play("search_updated.ogg")

class searchPeopleBufferController(searchBufferController):

 def __init__(self, parent, function, name, sessionObject, account, bufferType="peoplePanel", *args, **kwargs):
  super(searchPeopleBufferController, self).__init__(parent, function, name, sessionObject, account, bufferType="peoplePanel", *args, **kwargs)
  self.compose_function = compose.compose_followers_list
  
 def start_stream(self):
  val = getattr(self.session.twitter.twitter, self.function)(*self.args, **self.kwargs)
  number_of_items = self.session.order_buffer(self.name, val)
  self.put_items_on_list(number_of_items)
  if number_of_items > 0:
   sound.player.play("search_updated.ogg")
