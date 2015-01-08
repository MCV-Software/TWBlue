# -*- coding: utf-8 -*-
import wx
import widgetUtils
import arrow
import webbrowser
import output
import config
import sound
import messages
import languageHandler
from twitter import compose, utils
from wxUI import buffers, dialogs, commonMessageDialogs
from mysc.thread_utils import call_threaded
from twython import TwythonError

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
  elif ev.GetKeyCode() == wx.WXK_DELETE: event = "destroy_status"
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

 def get_message(self):
  pass

 def set_list_position(self, reversed=False):
  if reversed == False:
   self.buffer.list.select_item(-1)
  else:
   self.buffer.list.select_item(0)

 def reply(self):
  pass

 def direct_message(self):
  pass

 def retweet(self):
  pass

 def destroy_status(self):
  pass

 def post_tweet(self, *args, **kwargs):
  title = _(u"Tweet")
  caption = _(u"Write the tweet here")
  tweet = messages.tweet(self.session, title, caption, "")
  if tweet.message.get_response() == widgetUtils.OK:
   text = tweet.message.get_text()
   if tweet.image == None:
    call_threaded(self.session.api_call, call_name="update_status", status=text)
   else:
    call_threaded(self.session.api_call, call_name="update_status_with_media", status=text, media=tweet.image)

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

 def get_message(self):
  return " ".join(self.compose_function(self.get_right_tweet(), self.session.db, self.session.settings["general"]["relative_times"])[1:-2])

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
  widgetUtils.connect_event(self.buffer, widgetUtils.BUTTON_PRESSED, self.post_tweet, self.buffer.tweet)
#  if self.type == "baseBuffer":
  widgetUtils.connect_event(self.buffer, widgetUtils.BUTTON_PRESSED, self.retweet, self.buffer.retweet)
  widgetUtils.connect_event(self.buffer, widgetUtils.BUTTON_PRESSED, self.direct_message, self.buffer.dm)
  widgetUtils.connect_event(self.buffer, widgetUtils.BUTTON_PRESSED, self.reply, self.buffer.reply)

 def get_tweet(self):
  if self.session.db[self.name][self.buffer.list.get_selected()].has_key("retweeted_status"):
   tweet = self.session.db[self.name][self.buffer.list.get_selected()]["retweeted_status"]
  else:
   tweet = self.session.db[self.name][self.buffer.list.get_selected()]
  return tweet

 def get_right_tweet(self):
  tweet = self.session.db[self.name][self.buffer.list.get_selected()]
  return tweet

 def reply(self, *args, **kwargs):
  tweet = self.get_right_tweet()
  screen_name = tweet["user"]["screen_name"]
  id = tweet["id"]
  users =  utils.get_all_mentioned(tweet, self.session.db)
  message = messages.reply(self.session, _(u"Reply"), _(u"Reply to %s") % (screen_name,), "@%s" % (screen_name,), users)
  if message.message.get_response() == widgetUtils.OK:
   if message.image == None:
    call_threaded(self.session.twitter.api_call, call_name="update_status", _sound="reply_send.ogg", in_reply_to_status_id=id, status=message.message.get_text())
   else:
    call_threaded(self.session.twitter.api_call, call_name="update_status_with_media", _sound="reply_send.ogg", in_reply_to_status_id=id, status=message.message.get_text(), media=message.file)

 def direct_message(self, *args, **kwargs):
  tweet = self.get_tweet()
  if self.type == "dm":
   screen_name = tweet["sender"]["screen_name"]
   users = utils.get_all_users(tweet, self.session.db)
  elif self.type == "people":
   screen_name = tweet["screen_name"]
   users = [screen_name]
  else:
   screen_name = tweet["user"]["screen_name"]
   users = utils.get_all_users(tweet, self.session.db)
  dm = messages.dm(self.session, _(u"Direct message to %s") % (screen_name,), _(u"New direct message"), users)
  if dm.message.get_response() == widgetUtils.OK:
   call_threaded(self.session.api_call, call_name="send_direct_message", text=dm.message.get_text(), screen_name=dm.message.get("cb"))

 def retweet(self, *args, **kwargs):
  tweet = self.get_right_tweet()
  id = tweet["id"]
  answer = commonMessageDialogs.retweet_question(self.buffer)
  if answer == widgetUtils.YES:
   retweet = messages.tweet(self.session, _(u"Retweet"), _(u"Add your comment to the tweet"), u"“@%s: %s ”" % (tweet["user"]["screen_name"], tweet["text"]))
   if retweet.message.get_response() == widgetUtils.OK:
    if retweet.image == None:
     call_threaded(self.session.api_call, call_name="update_status", _sound="retweet_send.ogg", status=retweet.message.get_text(), in_reply_to_status_id=id)
    else:
     call_threaded(self.session.api_call, call_name="update_status", _sound="retweet_send.ogg", status=retweet.message.get_text(), in_reply_to_status_id=id, media=retweet.image)
  elif answer == widgetUtils.NO:
   call_threaded(self.session.api_call, call_name="retweet", _sound="retweet_send.ogg", id=id)

 def onFocus(self, ev):
  tweet = self.get_tweet()
  if self.session.settings["general"]["relative_times"] == True:
   # fix this:
   original_date = arrow.get(self.session.db[self.name_buffer][self.list.get_selected()]["created_at"], "ddd MMM D H:m:s Z YYYY", locale="en")
   ts = original_date.humanize(locale=languageHandler.getLanguage())
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

 def destroy_status(self, *args, **kwargs):
  index = self.buffer.list.get_selected()
  if self.type == "events" or self.type == "people" or self.type == "empty" or self.type == "account": return
  answer = commonMessageDialogs.delete_tweet_dialog(None)
  if answer == widgetUtils.YES:
#   try:
   if self.name == "direct_messages":
    self.session.twitter.twitter.destroy_direct_message(id=self.get_right_tweet()["id"])
   else:
    self.session.twitter.twitter.destroy_status(id=self.get_right_tweet()["id"])
   self.session.db[self.name].pop(index)
   self.buffer.list.remove_item(index)
   if index > 0:
    self.buffer.list.select_item(index-1)
#   except TwythonError:
#    sound.player.play("error.ogg")

class eventsBufferController(bufferController):
 def __init__(self, parent, name, session, account, *args, **kwargs):
  super(eventsBufferController, self).__init__(parent, *args, **kwargs)
  self.buffer = buffers.eventsPanel(parent, name)
  self.name = name
  self.account = account
  self.id = self.buffer.GetId()
  self.buffer.account = self.account
  self.compose_function = compose.compose_event
  self.session = session
  self.type = self.buffer.type

 def get_message(self):
  if self.list.get_count() == 0: return _(u"Empty")
  # fix this:
  if platform.system() == "Windows":
   return "%s. %s" % (self.buffer.list.list.GetItemText(self.buffer.list.get_selected()), self.buffer.list.list.GetItemText(self.buffer.list.get_selected(), 1))
  else:
   return self.buffer.list.list.GetStringSelection()

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
  self.get_tweet = self.get_right_tweet

 def onFocus(self, ev):
  pass

 def get_message(self):
  return " ".join(self.compose_function(self.get_tweet(), self.session.db, self.session.settings["general"]["relative_times"]))

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

 def get_right_tweet(self):
  tweet = self.session.db[self.name]["items"][self.buffer.list.get_selected()]
  return tweet

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
