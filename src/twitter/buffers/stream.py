# -*- coding: utf-8 -*-
from twitter import compose, utils
from twython import TwythonStreamer
import sound
from mysc import event
import wx
import config
import logging as original_logger
log = original_logger.getLogger("MainStream")
import output

class streamer(TwythonStreamer):
 def __init__(self, app_key, app_secret, oauth_token, oauth_token_secret, timeout=300, retry_count=None, retry_in=10, client_args=None, handlers=None, chunk_size=1, parent=None):
  self.db = parent.db
  self.parent = parent
  TwythonStreamer.__init__(self, app_key, app_secret, oauth_token, oauth_token_secret, timeout=480, retry_count=0, retry_in=60, client_args=None, handlers=None, chunk_size=1)
  self.muted_users = self.db.settings["muted_users"]
#  self.blocked_users = []

 def on_error(self, status_code, data):
  log.debug("Error %s: %s" % (status_code, data))

 def block_user(self, data):
  id = data["target"]["id"]
  if id in self.friends:
   self.friends.remove(id)
  if config.main["other_buffers"]["show_blocks"] == True:
   tweet_event = event.event(event.EVT_OBJECT, 1)
   tweet_event.SetItem(data["target"])
   wx.PostEvent(self.parent.search_buffer("people", "blocks"), tweet_event)

 def unblock(self, data):
  if config.main["other_buffers"]["show_blocks"] == True:
   item = utils.find_item(data["target"]["id"], self.db.settings["blocks"])
   self.db.settings["blocks"].pop(item)
   deleted_event = event.event(event.EVT_DELETED, 1)
   deleted_event.SetItem(item)
   wx.PostEvent(self.parent.search_buffer("people", "blocks"), deleted_event)
   wx.PostEvent(self.parent, event.ResultEvent())

 def check_send(self, data):
  if self.db.settings["user_name"] == data["user"]["screen_name"]:
   tweet_event = event.event(event.EVT_OBJECT, 1)
   tweet_event.SetItem(data)
   wx.PostEvent(self.parent.search_buffer("buffer", "sent"), tweet_event)

 def check_favs(self, data):
  if data["source"]["screen_name"] == self.db.settings["user_name"]:
   tweet_event = event.event(event.EVT_OBJECT, 1)
   tweet_event.SetItem(data["target_object"])
   wx.PostEvent(self.parent.search_buffer("buffer", "favs"), tweet_event)

 def check_mentions(self, data):
  if "@%s" % (self.db.settings["user_name"].lower()) in data["text"].lower():
   tweet_event = event.event(event.EVT_OBJECT, 1)
   tweet_event.SetItem(data)
   text = _(u"One mention from %s ") % (data["user"]["name"])
   tweet_event.SetAnnounce(text)
   wx.PostEvent(self.parent.search_buffer("buffer", "mentions"), tweet_event)

 def process_dm(self, data):
  if self.db.settings["user_name"] == data["direct_message"]["sender"]["screen_name"]:
   tweet_event = event.event(event.EVT_OBJECT, 1)
   tweet_event.SetItem(data["direct_message"])
   wx.PostEvent(self.parent.search_buffer("buffer", "sent"), tweet_event)
  if self.db.settings["user_name"] != data["direct_message"]["sender"]["screen_name"]:
   tweet_event = event.event(event.EVT_OBJECT, 1)
   tweet_event.SetItem(data["direct_message"])
   text = _(u"One direct message")
   tweet_event.SetAnnounce(text)
   wx.PostEvent(self.parent.search_buffer("direct_message", "direct_messages"), tweet_event)

 def check_follower(self, data):
  if data["target"]["screen_name"] == self.db.settings["user_name"] and config.main["other_buffers"]["show_followers"] == True:
   tweet_event = event.event(event.EVT_OBJECT, 1)
   tweet_event.SetItem(data["source"])
   wx.PostEvent(self.parent.search_buffer("people", "followers"), tweet_event)
  elif data["source"]["screen_name"] == self.db.settings["user_name"]:
   tweet_event = event.event(event.EVT_OBJECT, 1)
   tweet_event.SetItem(data["target"])
   wx.PostEvent(self.parent.search_buffer("people", "friends"), tweet_event)

 def remove_fav(self, data):
  if self.db.settings["user_name"] == data["source"]["screen_name"]:
   self.db.settings.update()
   item = utils.find_item(data["target_object"]["id"], self.db.settings["favs"])
   self.db.settings["favs"].pop(item)
   deleted_event = event.event(event.EVT_DELETED, 1)
   deleted_event.SetItem(item)
   wx.PostEvent(self.parent.search_buffer("buffer", "favs"), deleted_event)

 def remove_friend(self, data):
  if config.main["other_buffers"]["show_friends"] == True:
   item = utils.find_item(data["target"]["id"], self.db.settings["friends"])
   if item > 0:
    deleted_event = event.event(event.EVT_DELETED, 1)
    deleted_event.SetItem(item)
    self.friends.pop(item)
    self.db.settings["friends"].pop(item)
    wx.PostEvent(self.parent.search_buffer("people", "friends"), deleted_event)

 def on_success(self, data):
  try:
   if "direct_message" in data:
    self.process_dm(data)
   elif "friends" in data:
    self.friends = data["friends"]
   elif "text" in data and utils.is_allowed(data) == True:
    if data["user"]["id"] in self.muted_users: return
    self.check_mentions(data)
    self.check_send(data)
    if data["user"]["id"] in self.friends or data["user"]["screen_name"] == self.db.settings["user_name"]:
     tweet_event = event.event(event.EVT_OBJECT, 1)
     tweet_event.SetItem(data)
     wx.PostEvent(self.parent.search_buffer("buffer", "home_timeline"), tweet_event)
   elif data.has_key("event"):
    if "favorite" == data["event"] and config.main["other_buffers"]["show_favourites"] == True:
     self.check_favs(data)
    elif "unfavorite" == data["event"] and config.main["other_buffers"]["show_favourites"] == True:
     self.remove_fav(data)
    elif "follow" == data["event"]:
     self.check_follower(data)
    elif "unfollow" == data["event"] and config.main["other_buffers"]["show_followers"] == True:
     self.remove_friend(data)
    elif "block" == data["event"]:
     self.block_user(data)
    elif "unblock" in data["event"]:
     self.unblock(data)
    elif "list_created" == data["event"]:
     item = utils.find_item(data["target_object"]["id"], self.db.settings["lists"])
     if item != None: self.db.settings["lists"].append(data["target_object"])
    elif "list_destroyed" == data["event"]:
     item = utils.find_item(data["target_object"]["id"], self.db.settings["lists"])
     if item != None: self.db.settings["lists"].pop(item)
     self.parent.remove_list(data["target_object"]["id"])
    elif "list_member_added" == data["event"] and data["source"]["screen_name"] == self.db.settings["user_name"]:
     if len(config.main["other_buffers"]["lists"]) > 0:
      for i in range(0, self.parent.nb.GetPageCount()):
       if self.parent.nb.GetPage(i).type == "list":
        if str(data["target_object"]["id"]) == str(self.parent.nb.GetPage(i).argumento):
         self.parent.nb.GetPage(i).users.append(data["target"]["id"])
         wx.PostEvent(self.parent, event.ResultEvent())
    elif "list_member_added" == data["event"] and data["target"]["screen_name"] == self.db.settings["user_name"]:
     self.db.settings["lists"].append(data["target_object"])
    elif "list_member_removed" == data["event"] and data["source"]["screen_name"] == self.db.settings["user_name"]:
     if len(config.main["other_buffers"]["lists"]) > 0:
      for i in range(0, self.parent.nb.GetPageCount()):
       if self.parent.nb.GetPage(i).type == "list":
        if str(data["target_object"]["id"]) == str(self.parent.nb.GetPage(i).argumento):
         self.parent.nb.GetPage(i).users.remove(data["target"]["id"])
         wx.PostEvent(self.parent, event.ResultEvent())
    elif "list_member_removed" == data["event"] and data["target"] == self.db.settings["user_name"]:
     id = data["target_object"]["id"]
     list = utils.find_item(id, self.db.settings["lists"])
     if list != None: self.db.settings["lists"].pop(list)
     self.parent.remove_list(data["target_object"]["id"])
    if config.main["other_buffers"]["show_events"] == True:
     evento = compose.compose_event(data, self.db.settings["user_name"])
     tweet_event = event.event(event.EVT_OBJECT, 1)
     tweet_event.SetItem(evento)
     text = evento[1]
     tweet_event.SetAnnounce(text)
#     deleted_event = event.event(event.EVT_DELETED, 1)
#     deleted_event.SetItem(evento)
     wx.PostEvent(self.parent.search_buffer("event", "events"), tweet_event)
#     self.sound.play("new_event.ogg")
  except:
   pass
