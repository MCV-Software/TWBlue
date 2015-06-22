# -*- coding: utf-8 -*-
import platform
if platform.system() == "Windows":
 import wx
 from wxUI import buffers, dialogs, commonMessageDialogs
 import user
elif platform.system() == "Linux":
 from gi.repository import Gtk
 from gtkUI import buffers, dialogs, commonMessageDialogs
import messages
import widgetUtils
import arrow
import webbrowser
import output
import config
import sound
import languageHandler
import logging
from twitter import compose, utils
from mysc.thread_utils import call_threaded
from twython import TwythonError
from pubsub import pub
from long_tweets import twishort, tweets

log = logging.getLogger("controller.buffers")

def _tweets_exist(function):
 """ A decorator to execute a function only if the selected buffer contains at least one item."""
 def function_(self, *args, **kwargs):
  if self.buffer.list.get_count() > 0:
   function(self, *args, **kwargs)
 return function_

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
  self.invisible = False # False if the buffer will be ignored on the invisible interface.

 def clear_list(self): pass


 def get_event(self, ev):
  if ev.GetKeyCode() == wx.WXK_RETURN and ev.ControlDown(): event = "interact"
  elif ev.GetKeyCode() == wx.WXK_RETURN: event = "url"
  elif ev.GetKeyCode() == wx.WXK_F5: event = "volume_down"
  elif ev.GetKeyCode() == wx.WXK_F6: event = "volume_up"
  elif ev.GetKeyCode() == wx.WXK_DELETE and ev.ShiftDown(): event = "clear_list"
  elif ev.GetKeyCode() == wx.WXK_DELETE: event = "destroy_status"
  else:
   event = None
   ev.Skip()
  if event != None:
   try:
    getattr(self, event)()
   except AttributeError:
    pass
 
 def volume_down(self):
  if self.session.settings["sound"]["volume"] > 0.0:
   if self.session.settings["sound"]["volume"] <= 0.05:
    self.session.settings["sound"]["volume"] = 0.0
   else:
    self.session.settings["sound"]["volume"] -=0.05
  if hasattr(sound.URLPlayer, "stream"):
   sound.URLPlayer.stream.volume = self.session.settings["sound"]["volume"]
  self.session.sound.play("volume_changed.ogg")

 def volume_up(self):
  if self.session.settings["sound"]["volume"] < 1.0:
   if self.session.settings["sound"]["volume"] >= 0.95:
    self.session.settings["sound"]["volume"] = 1.0
   else:
    self.session.settings["sound"]["volume"] +=0.05
  if hasattr(sound.URLPlayer, "stream"):
   sound.URLPlayer.stream.volume = self.session.settings["sound"]["volume"]
  self.session.sound.play("volume_changed.ogg")

 def interact(self):
  tweet = self.get_tweet()
  url=None
  urls = utils.find_urls(tweet)
  if len(urls) == 1:
   url=urls[0]
  elif len(urls) > 1:
   urls_list = dialogs.urlList.urlList()
   urls_list.populate_list(urls)
   if urls_list.get_response() == widgetUtils.OK:
    url=urls_list.get_string()
   if hasattr(urls_list, "destroy"): urls_list.destroy()
  if url != None:
   output.speak(_(u"Opening media..."), True)
  if sound.URLPlayer.is_playable(url=url, play=True, volume=self.session.settings["sound"]["volume"]) == False:
    return webbrowser.open_new_tab(url)
#  else:
#   output.speak(_(u"Not actionable."), True)
#   self.session.sound.play("error.ogg")

 def start_stream(self):
  pass

 def get_more_items(self):
  output.speak(_(u"This action is not supported for this buffer"), True)

 def put_items_on_list(self, items):
  pass

 def remove_buffer(self):
  return False

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
  if hasattr(tweet.message, "destroy"): tweet.message.destroy()

class accountPanel(bufferController):
 def __init__(self, parent, name, account, account_id):
  super(accountPanel, self).__init__(parent, None, name)
  log.debug("Initializing buffer %s, account %s" % (name, account,))
  self.buffer = buffers.accountPanel(parent, name)
  self.type = self.buffer.type
  self.compose_function = None
  self.session = None
  self.needs_init = False
  self.account = account
  self.buffer.account = account
  self.name = name
  self.account_id = account_id

 def setup_account(self):
  widgetUtils.connect_event(self.buffer, widgetUtils.CHECKBOX, self.autostart, menuitem=self.buffer.autostart_account)
  if self.account_id in config.app["sessions"]["ignored_sessions"]:
   self.buffer.change_autostart(False)
  else:
   self.buffer.change_autostart(True)
  if not hasattr(self, "logged"):
   self.buffer.change_login(login=False)
   widgetUtils.connect_event(self.buffer.login, widgetUtils.BUTTON_PRESSED, self.logout)
  else:
   self.buffer.change_login(login=True)
   widgetUtils.connect_event(self.buffer.login, widgetUtils.BUTTON_PRESSED, self.login)

 def login(self, *args, **kwargs):
  del self.logged
  self.setup_account()
  pub.sendMessage("login", session_id=self.account_id)

 def logout(self, *args, **kwargs):
  self.logged = False
  self.setup_account()
  pub.sendMessage("logout", session_id=self.account_id)

 def autostart(self, *args, **kwargs):
  if self.account_id in config.app["sessions"]["ignored_sessions"]:
   self.buffer.change_autostart(True)
   config.app["sessions"]["ignored_sessions"].remove(self.account_id)
  else:
   self.buffer.change_autostart(False)
   config.app["sessions"]["ignored_sessions"].append(self.account_id)

class emptyPanel(bufferController):
 def __init__(self, parent, name, account):
  super(emptyPanel, self).__init__(parent, None, name)
  log.debug("Initializing buffer %s, account %s" % (name, account,))
  self.buffer = buffers.emptyPanel(parent, name)
  self.type = self.buffer.type
  self.compose_function = None
  self.account = account
  self.buffer.account = account
  self.name = name
  self.session = None
  self.needs_init = True

class baseBufferController(bufferController):
 def __init__(self, parent, function, name, sessionObject, account, sound=None, bufferType=None, *args, **kwargs):
  super(baseBufferController, self).__init__(parent, function, *args, **kwargs)
  log.debug("Initializing buffer %s, account %s" % (name, account,))
  if bufferType != None:
   self.buffer = getattr(buffers, bufferType)(parent, name)
  else:
   self.buffer = buffers.basePanel(parent, name)
  self.invisible = True
  self.name = name
  self.type = self.buffer.type
  self.session = sessionObject
  self.compose_function = compose.compose_tweet
  log.debug("Compose_function: %s" % (self.compose_function,))
  self.account = account
  self.buffer.account = account
  self.bind_events()
  self.sound = sound

 def get_formatted_message(self):
  if self.type == "dm" or self.name == "sent_tweets" or self.name == "sent_direct_messages":   return self.compose_function(self.get_right_tweet(), self.session.db, self.session.settings["general"]["relative_times"])[1]
  return self.get_message()

 def get_message(self):
  return " ".join(self.compose_function(self.get_right_tweet(), self.session.db, self.session.settings["general"]["relative_times"]))

 def get_full_tweet(self):
  tweet = self.get_right_tweet()
  tweetsList = []
  tweet_id = tweet["id"]
  uri = None
  if tweet.has_key("long_uri"):
   uri = tweet["long_uri"]
  try:
   tweet = self.session.twitter.twitter.show_status(id=tweet_id)
  except TwythonError as e:
   utils.twitter_error(e)
   return
  if uri != None:
   tweet["text"] = twishort.get_full_text(uri)
  l = tweets.is_long(tweet)
  while l != False:
   tweetsList.append(tweet)
   id = tweets.get_id(l)
   try:
    tweet = self.session.twitter.twitter.show_status(id=id)
   except TwythonError as e:
    utils.twitter_error(e)
    return
   l = tweets.is_long(tweet)
   if l == False:
    tweetsList.append(tweet)
  return (tweet, tweetsList)

 def start_stream(self):
  log.debug("Starting stream for buffer %s, account %s and type %s" % (self.name, self.account, self.type))
  log.debug("args: %s, kwargs: %s" % (self.args, self.kwargs))
  val = self.session.call_paged(self.function, *self.args, **self.kwargs)
  number_of_items = self.session.order_buffer(self.name, val)
  log.debug("Number of items retrieved: %d" % (number_of_items,))
  self.put_items_on_list(number_of_items)
  if self.sound == None: return
  if number_of_items > 0 and self.name != "sent_tweets" and self.name != "sent_direct_messages":
   self.session.sound.play(self.sound)

 def get_more_items(self):
  elements = []
  if self.session.settings["general"]["reverse_timelines"] == False:
   last_id = self.session.db[self.name][0]["id"]
  else:
   last_id = self.session.db[self.name][-1]["id"]
  try:
   items = self.session.get_more_items(self.function, count=self.session.settings["general"]["max_tweets_per_call"], max_id=last_id, *self.args, **self.kwargs)
  except TwythonError as e:
   output.speak(e.message, True)
  for i in items:
   if utils.is_allowed(i, self.session.settings["twitter"]["ignored_clients"]) == True:
    elements.append(i)
    if self.session.settings["general"]["reverse_timelines"] == False:
     self.session.db[self.name].insert(0, i)
    else:
     self.session.db[self.name].append(i)
  selection = self.buffer.list.get_selected()
  if self.session.settings["general"]["reverse_timelines"] == False:
   for i in elements:
    tweet = self.compose_function(i, self.session.db, self.session.settings["general"]["relative_times"])
    self.buffer.list.insert_item(True, *tweet)
  else:
   for i in items:
    tweet = self.compose_function(i, self.session.db, self.session.settings["general"]["relative_times"])
    self.buffer.list.insert_item(False, *tweet)
#   self.buffer.list.select_item(selection+elements)
#  else:
   self.buffer.list.select_item(selection)
  output.speak(_(u"%s items retrieved") % (str(len(elements))), True)

 def remove_buffer(self):
  if "-timeline" in self.name:
   dlg = commonMessageDialogs.remove_buffer()
   if dlg == widgetUtils.YES:
    if self.name[:-9] in self.session.settings["other_buffers"]["timelines"]:
     self.session.settings["other_buffers"]["timelines"].remove(self.name[:-9])
     return True
   elif dlg == widgetUtils.NO:
    return False
  elif "favorite" in self.name:
   dlg = commonMessageDialogs.remove_buffer()
   if dlg == widgetUtils.YES:
    if self.name[:-9] in self.session.settings["other_buffers"]["favourites_timelines"]:
     self.session.settings["other_buffers"]["favourites_timelines"].remove(self.name[:-9])
     return True
   elif dlg == widgetUtils.NO:
    return False
  else:
   output.speak(_(u"This buffer is not a timeline; it can't be deleted."), True)
   return False

 def put_items_on_list(self, number_of_items):
  log.debug("The list contains %d items " % (self.buffer.list.get_count(),))
  log.debug("Putting %d items on the list" % (number_of_items,))
  if self.buffer.list.get_count() == 0:
   for i in self.session.db[self.name]:
    tweet = self.compose_function(i, self.session.db, self.session.settings["general"]["relative_times"])
    self.buffer.list.insert_item(False, *tweet)
   self.buffer.set_position(self.session.settings["general"]["reverse_timelines"])
  elif self.buffer.list.get_count() > 0:
   if self.session.settings["general"]["reverse_timelines"] == False:
    for i in self.session.db[self.name][:number_of_items]:
     tweet = self.compose_function(i, self.session.db, self.session.settings["general"]["relative_times"])
     self.buffer.list.insert_item(False, *tweet)
   else:
    for i in self.session.db[self.name][0:number_of_items]:
     tweet = self.compose_function(i, self.session.db, self.session.settings["general"]["relative_times"])
     self.buffer.list.insert_item(True, *tweet)
  log.debug("Now the list contains %d items " % (self.buffer.list.get_count(),))

 def add_new_item(self, item):
  tweet = self.compose_function(item, self.session.db, self.session.settings["general"]["relative_times"])
  if self.session.settings["general"]["reverse_timelines"] == False:
   self.buffer.list.insert_item(False, *tweet)
  else:
   self.buffer.list.insert_item(True, *tweet)
  if self.name in self.session.settings["other_buffers"]["autoread_buffers"] and self.name not in self.session.settings["other_buffers"]["muted_buffers"] and self.session.settings["sound"]["session_mute"] == False:
   output.speak(" ".join(tweet[:2]))
  #Improve performance on Windows
  if platform.system() == "Windows":
   call_threaded(utils.is_audio,item)

 def bind_events(self):
  log.debug("Binding events...")
  self.buffer.set_focus_function(self.onFocus)
  widgetUtils.connect_event(self.buffer.list.list, widgetUtils.KEYPRESS, self.get_event)
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

 @_tweets_exist
 def reply(self, *args, **kwargs):
  tweet = self.get_right_tweet()
  screen_name = tweet["user"]["screen_name"]
  id = tweet["id"]
  users =  utils.get_all_mentioned(tweet, self.session.db)
  message = messages.reply(self.session, _(u"Reply"), _(u"Reply to %s") % (screen_name,), "@%s " % (screen_name,), users)
  if message.message.get_response() == widgetUtils.OK:
   if message.image == None:
    call_threaded(self.session.api_call, call_name="update_status", _sound="reply_send.ogg", in_reply_to_status_id=id, status=message.message.get_text())
   else:
    call_threaded(self.session.api_call, call_name="update_status_with_media", _sound="reply_send.ogg", in_reply_to_status_id=id, status=message.message.get_text(), media=message.file)
  if hasattr(message.message, "destroy"): message.message.destroy()

 @_tweets_exist
 def direct_message(self, *args, **kwargs):
  tweet = self.get_right_tweet()
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
  if hasattr(dm.message, "destroy"): dm.message.destroy()

 @_tweets_exist
 def retweet(self, *args, **kwargs):
  tweet = self.get_right_tweet()
  id = tweet["id"]
  if self.session.settings["general"]["retweet_mode"] == "ask":
   answer = commonMessageDialogs.retweet_question(self.buffer)
   if answer == widgetUtils.YES:
    self._retweet_with_comment(tweet, id)
   elif answer == widgetUtils.NO:
    self._direct_retweet(id)
  elif self.session.settings["general"]["retweet_mode"] == "direct":
   self._direct_retweet(id)
  else:
   self._retweet_with_comment(tweet, id)

 def _retweet_with_comment(self, tweet, id, comment=''):
  retweet = messages.tweet(self.session, _(u"Retweet"), _(u"Add your comment to the tweet"), u"“@%s: %s ”" % (tweet["user"]["screen_name"], tweet["text"]), max=116-len("@%s " % (tweet["user"]["screen_name"],)), messageType="retweet")
  if comment != '':
   retweet.message.set_text(comment)
  if retweet.message.get_response() == widgetUtils.OK:
   text = retweet.message.get_text()
   comments=text
   if len(text+ u"“@%s: %s ”" % (tweet["user"]["screen_name"], tweet["text"])) < 140:
    text = text+u"“@%s: %s ”" % (tweet["user"]["screen_name"], tweet["text"])
   else:
    answer = commonMessageDialogs.retweet_as_link(self.buffer)
    if answer == widgetUtils.YES:
     text = text+" @{2} https://twitter.com/{0}/status/{1}".format(tweet["user"]["screen_name"], id, tweet["user"]["screen_name"])
    else:
     return self._retweet_with_comment(tweet, id, comment=comments)
   if retweet.image == None:
    call_threaded(self.session.api_call, call_name="update_status", _sound="retweet_send.ogg", status=text, in_reply_to_status_id=id)
   else:
    call_threaded(self.session.api_call, call_name="update_status", _sound="retweet_send.ogg", status=text, media=retweet.image)
  if hasattr(retweet.message, "destroy"): retweet.message.destroy()

 def _direct_retweet(self, id):
  call_threaded(self.session.api_call, call_name="retweet", _sound="retweet_send.ogg", id=id)

 def onFocus(self, *args, **kwargs):
  tweet = self.get_tweet()
  if platform.system() == "Windows" and self.session.settings["general"]["relative_times"] == True:
   # fix this:
   original_date = arrow.get(self.session.db[self.name][self.buffer.list.get_selected()]["created_at"], "ddd MMM D H:m:s Z YYYY", locale="en")
   ts = original_date.humanize(locale=languageHandler.getLanguage())
   self.buffer.list.list.SetStringItem(self.buffer.list.get_selected(), 2, ts)
  if utils.is_audio(tweet):
   self.session.sound.play("audio.ogg")
  if utils.is_geocoded(tweet):
   self.session.sound.play("geo.ogg")
  self.session.db[str(self.name+"_pos")]=self.buffer.list.get_selected()

 @_tweets_exist
 def audio(self,url=''):
  if hasattr(sound.URLPlayer,'stream'):
   return sound.URLPlayer.stop_audio(delete=True)
  tweet = self.get_tweet()
  if tweet == None: return
  urls = utils.find_urls(tweet)
  if len(urls) == 1:
   url=urls[0]
  elif len(urls) > 1:
   urls_list = dialogs.urlList.urlList()
   urls_list.populate_list(urls)
   if urls_list.get_response() == widgetUtils.OK:
    url=urls_list.get_string()
   if hasattr(urls_list, "destroy"): urls_list.destroy()
  if url != '':
   try:
    sound.URLPlayer.play(url, self.session.settings["sound"]["volume"])
   except:
    log.error("Exception while executing audio method.")

 @_tweets_exist
 def url(self,url='',announce=True):
  if url == '':
   tweet = self.get_tweet()
   urls = utils.find_urls(tweet)
   if len(urls) == 1:
    url=urls[0]
   elif len(urls) > 1:
    urls_list = dialogs.urlList.urlList()
    urls_list.populate_list(urls)
    if urls_list.get_response() == widgetUtils.OK:
     url=urls_list.get_string()
    if hasattr(urls_list, "destroy"): urls_list.destroy()
   if url != '':
    if announce:
     output.speak(_(u"Opening URL..."), True)
    webbrowser.open_new_tab(url)

 def clear_list(self):
  dlg = commonMessageDialogs.clear_list()
  if dlg == widgetUtils.YES:
   self.session.db[self.name] = []
   self.buffer.list.clear()

 @_tweets_exist
 def destroy_status(self, *args, **kwargs):
  index = self.buffer.list.get_selected()
  if self.type == "events" or self.type == "people" or self.type == "empty" or self.type == "account": return
  answer = commonMessageDialogs.delete_tweet_dialog(None)
  if answer == widgetUtils.YES:
   try:
    if self.name == "direct_messages" or self.name == "sent_direct_messages":
     self.session.twitter.twitter.destroy_direct_message(id=self.get_right_tweet()["id"])
    else:
     self.session.twitter.twitter.destroy_status(id=self.get_right_tweet()["id"])
    self.session.db[self.name].pop(index)
    self.buffer.list.remove_item(index)
#    if index > 0:
   except TwythonError:
    self.session.sound.play("error")

 @_tweets_exist
 def user_details(self):
  tweet = self.get_right_tweet()
  if self.type == "dm":
   users = utils.get_all_users(tweet, self.session.db)
  elif self.type == "people":
   users = [tweet["screen_name"]]
  else:
   users = utils.get_all_users(tweet, self.session.db)
  dlg = dialogs.utils.selectUserDialog(title=_(u"User details"), users=users)
  if dlg.get_response() == widgetUtils.OK:
   user.profileController(session=self.session, user=dlg.get_user())
  if hasattr(dlg, "destroy"): dlg.destroy()

class listBufferController(baseBufferController):
 def __init__(self, parent, function, name, sessionObject, account, sound=None, bufferType=None, list_id=None, *args, **kwargs):
  super(listBufferController, self).__init__(parent, function, name, sessionObject, account, sound=None, bufferType=None, *args, **kwargs)
  self.users = []
  self.list_id = list_id
  self.kwargs["list_id"] = list_id

 def start_stream(self):
  self.get_user_ids()
  super(listBufferController, self).start_stream()

 def get_user_ids(self):
  self.users = []
  next_cursor = -1
  while(next_cursor):
   users = self.session.twitter.twitter.get_list_members(list_id=self.list_id, cursor=next_cursor, include_entities=False, skip_status=True)
   for i in users['users']:
    self.users.append(i["id"])
    next_cursor = users["next_cursor"]

 def remove_buffer(self):
  dlg = commonMessageDialogs.remove_buffer()
  if dlg == widgetUtils.YES:
   if self.name[:-5] in self.session.settings["other_buffers"]["lists"]:
    self.session.settings["other_buffers"]["lists"].remove(self.name[:-5])
    return True
  elif dlg == widgetUtils.NO:
   return False

class eventsBufferController(bufferController):
 def __init__(self, parent, name, session, account, *args, **kwargs):
  super(eventsBufferController, self).__init__(parent, *args, **kwargs)
  log.debug("Initializing buffer %s, account %s" % (name, account,))
  self.invisible = True
  self.buffer = buffers.eventsPanel(parent, name)
  self.name = name
  self.account = account
  self.buffer.account = self.account
  self.compose_function = compose.compose_event
  self.session = session
  self.type = self.buffer.type
  self.get_formatted_message = self.get_message

 def get_message(self):
  if self.buffer.list.get_count() == 0: return _(u"Empty")
  # fix this:
  return "%s. %s" % (self.buffer.list.list.GetItemText(self.buffer.list.get_selected()), self.buffer.list.list.GetItemText(self.buffer.list.get_selected(), 1))

 def add_new_item(self, item):
  tweet = self.compose_function(item, self.session.db["user_name"])
  if self.session.settings["general"]["reverse_timelines"] == False:
   self.buffer.list.insert_item(False, *tweet)
  else:
   self.buffer.list.insert_item(True, *tweet)
  if self.name in self.session.settings["other_buffers"]["autoread_buffers"] and self.name not in self.session.settings["other_buffers"]["muted_buffers"] and self.session.settings["sound"]["session_mute"] == False:
   output.speak(" ".join(tweet))
  if self.buffer.list.get_count() == 1:
   self.buffer.list.select_item(0)

 def clear_list(self):
  dlg = commonMessageDialogs.clear_list()
  if dlg == widgetUtils.YES:
   self.buffer.list.clear()

class peopleBufferController(baseBufferController):
 def __init__(self, parent, function, name, sessionObject, account, bufferType=None, *args, **kwargs):
  super(peopleBufferController, self).__init__(parent, function, name, sessionObject, account, bufferType="peoplePanel")
  log.debug("Initializing buffer %s, account %s" % (name, account,))
  self.compose_function = compose.compose_followers_list
  log.debug("Compose_function: %s" % (self.compose_function,))
  self.get_tweet = self.get_right_tweet
  self.url = self.interact

 def remove_buffer(self):
  return False

 def onFocus(self, ev):
  pass

 def get_message(self):
  return " ".join(self.compose_function(self.get_tweet(), self.session.db, self.session.settings["general"]["relative_times"]))

 def delete_item(self): pass

 @_tweets_exist
 def reply(self, *args, **kwargs):
  tweet = self.get_right_tweet()
  screen_name = tweet["screen_name"]
  message = messages.reply(self.session, _(u"Mention"), _(u"Mention to %s") % (screen_name,), "@%s " % (screen_name,), [screen_name,])
  if message.message.get_response() == widgetUtils.OK:
   if message.image == None:
    call_threaded(self.session.api_call, call_name="update_status", _sound="reply_send.ogg", status=message.message.get_text())
   else:
    call_threaded(self.session.api_call, call_name="update_status_with_media", _sound="reply_send.ogg", status=message.message.get_text(), media=message.file)
  if hasattr(message.message, "destroy"): message.message.destroy()

 def start_stream(self):
  log.debug("Starting stream for %s buffer, %s account" % (self.name, self.account,))
  log.debug("args: %s, kwargs: %s" % (self.args, self.kwargs))
  val = self.session.get_cursored_stream(self.name, self.function, *self.args, **self.kwargs)
#  self.session.order_cursored_buffer(self.name, self.session.db[self.name])
#  log.debug("Number of items retrieved:  %d" % (val,))
  self.put_items_on_list(val)

 def get_more_items(self):
  try:
   items = self.session.get_more_items(self.function, users=True, name=self.name, count=self.session.settings["general"]["max_tweets_per_call"], cursor=self.session.db[self.name]["cursor"])
  except TwythonError as e:
   output.speak(e.message, True)
   return
  for i in items:
   if self.session.settings["general"]["reverse_timelines"] == False:
    self.session.db[self.name]["items"].insert(0, i)
   else:
    self.session.db[self.name]["items"].append(i)
  selected = self.buffer.list.get_selected()
#  self.put_items_on_list(len(items))
  if self.session.settings["general"]["reverse_timelines"] == True:
   for i in items:
    tweet = self.compose_function(i, self.session.db, self.session.settings["general"]["relative_times"])
    self.buffer.list.insert_item(True, *tweet)
   self.buffer.list.select_item(selected)
  else:
   for i in items:
    tweet = self.compose_function(i, self.session.db, self.session.settings["general"]["relative_times"])
    self.buffer.list.insert_item(True, *tweet)
#   self.buffer.list.select_item(selection)
#  else:
#   self.buffer.list.select_item(selection-elements)
  output.speak(_(u"%s items retrieved") % (len(items)), True)

 def put_items_on_list(self, number_of_items):
  log.debug("The list contains %d items" % (self.buffer.list.get_count(),))
#  log.debug("Putting %d items on the list..." % (number_of_items,))
  if self.buffer.list.get_count() == 0:
   for i in self.session.db[self.name]["items"]:
    tweet = self.compose_function(i, self.session.db, self.session.settings["general"]["relative_times"])
    self.buffer.list.insert_item(False, *tweet)
   self.buffer.set_position(self.session.settings["general"]["reverse_timelines"])
#   self.buffer.set_list_position()
  elif self.buffer.list.get_count() > 0:
   if self.session.settings["general"]["reverse_timelines"] == False:
    for i in self.session.db[self.name]["items"][:number_of_items]:
     tweet = self.compose_function(i, self.session.db)
     self.buffer.list.insert_item(False, *tweet)
   else:
    for i in self.session.db[self.name]["items"][0:number_of_items]:
     tweet = self.compose_function(i, self.session.db)
     self.buffer.list.insert_item(True, *tweet)
  log.debug("now the list contains %d items" % (self.buffer.list.get_count(),))

 def get_right_tweet(self):
  tweet = self.session.db[self.name]["items"][self.buffer.list.get_selected()]
  return tweet

 def add_new_item(self, item):
  tweet = self.compose_function(item, self.session.db, self.session.settings["general"]["relative_times"])
  if self.session.settings["general"]["reverse_timelines"] == False:
   self.buffer.list.insert_item(False, *tweet)
  else:
   self.buffer.list.insert_item(True, *tweet)
  if self.name in self.session.settings["other_buffers"]["autoread_buffers"] and self.name not in self.session.settings["other_buffers"]["muted_buffers"] and self.session.settings["sound"]["session_mute"] == False:
   output.speak(" ".join(tweet))

 def clear_list(self):
  dlg = commonMessageDialogs.clear_list()
  if dlg == widgetUtils.YES:
   self.session.db[self.name]["items"] = []
   self.session.db[self.name]["cursor"] = -1
   self.buffer.list.clear()

 def interact(self):
  user.profileController(self.session, user=self.get_right_tweet()["screen_name"])

class searchBufferController(baseBufferController):
 def start_stream(self):
  log.debug("Starting stream for %s buffer, %s account and %s type" % (self.name, self.account, self.type))
  log.debug("args: %s, kwargs: %s" % (self.args, self.kwargs))
  log.debug("Function: %s" % (self.function,))
#  try:
  val = self.session.search(self.name, *self.args, **self.kwargs)
#  except:
#   return None
  num = self.session.order_buffer(self.name, val)
  self.put_items_on_list(num)
  if num > 0:
   self.session.sound.play("search_updated.ogg")

 def remove_buffer(self):
  dlg = commonMessageDialogs.remove_buffer()
  if dlg == widgetUtils.YES:
   if self.name[:-11] in self.session.settings["other_buffers"]["tweet_searches"]:
    self.session.settings["other_buffers"]["tweet_searches"].remove(self.name[:-11])
    self.timer.cancel()
    return True
  elif dlg == widgetUtils.NO:
   return False

class searchPeopleBufferController(peopleBufferController):

 def __init__(self, parent, function, name, sessionObject, account, bufferType="peoplePanel", *args, **kwargs):
  super(searchPeopleBufferController, self).__init__(parent, function, name, sessionObject, account, bufferType="peoplePanel", *args, **kwargs)
  log.debug("Initializing buffer %s, account %s" % (name, account,))
#  self.compose_function = compose.compose_followers_list
  log.debug("Compose_function: %s" % (self.compose_function,))
  self.args = args
  self.kwargs = kwargs
  self.function = function

 def start_stream(self):
  log.debug("starting stream for %s buffer, %s account and %s type" % (self.name, self.account, self.type))
  log.debug("args: %s, kwargs: %s" % (self.args, self.kwargs))
  log.debug("Function: %s" % (self.function,))
#  try:
  val = self.session.call_paged(self.function, *self.args, **self.kwargs)
#  except:
#   return
  number_of_items = self.session.order_cursored_buffer(self.name, val)
  log.debug("Number of items retrieved: %d" % (number_of_items,))
  self.put_items_on_list(number_of_items)
  if number_of_items > 0:
   self.session.sound.play("search_updated.ogg")

 def remove_buffer(self):
  dlg = commonMessageDialogs.remove_buffer()
  if dlg == widgetUtils.YES:
   if self.name[:-11] in self.session.settings["other_buffers"]["tweet_searches"]:
    self.session.settings["other_buffers"]["tweet_searches"].remove(self.name[:-11])
    self.timer.cancel()
    return True
  elif dlg == widgetUtils.NO:
   return False

class trendsBufferController(bufferController):
 def __init__(self, parent, name, session, account, trendsFor, *args, **kwargs):
  super(trendsBufferController, self).__init__(parent=parent, session=session)
  self.trendsFor = trendsFor
  self.session = session
  self.account = account
  self.invisible = True
  self.buffer = buffers.trendsPanel(parent, name)
  self.buffer.account = account
  self.type = self.buffer.type
  self.bind_events()
  self.sound = "trends_updated.ogg"
  self.trends = []
  self.name = name
  self.buffer.name = name
  self.compose_function = self.compose_function_
  self.get_formatted_message = self.get_message

 def start_stream(self):
  try:
   data = self.session.call_paged("get_place_trends", id=self.trendsFor)
  except:
   return
  if not hasattr(self, "name_"):
   self.name_ = data[0]["locations"][0]["name"]
  self.trends = data[0]["trends"]
  self.put_items_on_the_list()
  self.session.sound.play(self.sound)

 def put_items_on_the_list(self):
  selected_item = self.buffer.list.get_selected()
  self.buffer.list.clear()
  for i in self.trends:
   tweet = self.compose_function(i)
   self.buffer.list.insert_item(False, *tweet)
   self.buffer.set_position(self.session.settings["general"]["reverse_timelines"])

 def compose_function_(self, trend):
  return [trend["name"]]

 def bind_events(self):
  log.debug("Binding events...")
  self.buffer.list.list.Bind(wx.EVT_CHAR_HOOK, self.get_event)
#  widgetUtils.connect_event(self.buffer, widgetUtils.BUTTON_PRESSED, self.post_tweet, self.buffer.tweet)
#  widgetUtils.connect_event(self.buffer, widgetUtils.BUTTON_PRESSED, self.retweet, self.buffer.retweet)
#  widgetUtils.connect_event(self.buffer, widgetUtils.BUTTON_PRESSED, self.direct_message, self.buffer.dm)
#  widgetUtils.connect_event(self.buffer, widgetUtils.BUTTON_PRESSED, self.reply, self.buffer.reply)

 def get_message(self):
  return self.compose_function(self.trends[self.buffer.list.get_selected()])[0]

 def remove_buffer(self):
  dlg = commonMessageDialogs.remove_buffer()
  if dlg == widgetUtils.YES:
   if self.name[:-3] in self.session.settings["other_buffers"]["trending_topic_buffers"]:
    self.session.settings["other_buffers"]["trending_topic_buffers"].remove(self.name[:-3])
    self.timer.cancel()
    return True
  elif dlg == widgetUtils.NO:
   return False

 def interact(self, *args, **kwargs):
  self.searchfunction(value=self.get_message())

class conversationBufferController(searchBufferController):

 def start_stream(self, start=False):
  if start == True:
   self.statuses = []
   self.ids = []
   self.statuses.append(self.tweet)
   self.ids.append(self.tweet["id"])
   tweet = self.tweet
   while tweet["in_reply_to_status_id"] != None:
    tweet = self.session.twitter.twitter.show_status(id=tweet["in_reply_to_status_id"])
    self.statuses.insert(0, tweet)
    self.ids.append(tweet["id"])
   if tweet["in_reply_to_status_id"] == None:
    self.kwargs["since_id"] = tweet["id"]
    self.ids.append(tweet["id"])
  val2 = self.session.search(self.name, *self.args, **self.kwargs)
  for i in val2:
   if i["in_reply_to_status_id"] in self.ids:
    self.statuses.append(i)
    self.ids.append(i["id"])
    tweet = i
  number_of_items = self.session.order_buffer(self.name, self.statuses)
  log.debug("Number of items retrieved: %d" % (number_of_items,))
  self.put_items_on_list(number_of_items)
  if number_of_items > 0:
   self.session.sound.play("search_updated.ogg")

class pocketBufferController(baseBufferController):
 def __init__(self, parent, name, sessionObject, account, sound=None, function=None, bufferType=None, *args, **kwargs):
  super(pocketBufferController, self).__init__(parent, name, sessionObject, account, sound, function, bufferType, *args, **kwargs)
  self.type = "pocket"

 def start_stream(self):
  log.debug("Starting stream for buffer %s, account %s and type %s" % (self.name, self.account, self.type))
  log.debug("args: %s, kwargs: %s" % (self.args, self.kwargs))
