# -*- coding: utf-8 -*-
import config
from requests.auth import HTTPProxyAuth
from twitter import utils
from twython import TwythonStreamer
from pubsub import pub
import logging as original_logger
log = original_logger.getLogger("MainStream")

class streamer(TwythonStreamer):
 def __init__(self, app_key, app_secret, oauth_token, oauth_token_secret, sessionObject, *a, **kw):
  super(streamer, self).__init__(app_key, app_secret, oauth_token, oauth_token_secret, *a, **kw)
  self.session = sessionObject
  self.muted_users = self.session.db["muted_users"]
#  self.blocked_users = []

 def on_timeout(self, *args, **kwargs):
  log.error("Twitter timeout Error")
#  pub.sendMessage("stream-error", session=self.session.session_id)

 def on_error(self, status_code, data):
  log.error("Error %s: %s" % (status_code, data))
#  pub.sendMessage("stream-error", session=self.session.session_id)

 def get_user(self):
  return self.session.db["user_name"]

 def put_data(self, place, data):
  if place in self.session.db:
   if utils.find_item(data["id"], self.session.db[place]) != None:
    log.error("duplicated tweet. Ignoring it...")
    return False
#   try:
   data_ = self.session.check_quoted_status(data)
   data_ = self.session.check_long_tweet(data_)
   data = data_
#   except:
#    pass
   if self.session.settings["general"]["reverse_timelines"] == False:
    self.session.db[place].append(data)
   else:
    self.session.db[place].insert(0, data)
  utils.is_audio(data)
  return True

 def block_user(self, data):
  id = data["target"]["id"]
  if id in self.friends:
   self.friends.remove(id)
  if "blocks" in self.session.settings["general"]["buffer_order"]:
   self.session.db["blocked"]["items"].append(data["target"])
   pub.sendMessage("blocked-user", data=data["target"], user=self.get_user())

 def unblock(self, data):
  if "blocks" in self.session.settings["general"]["buffer_order"] == True:
   item = utils.find_item(data["target"]["id"], self.session.db["blocked"]["items"])
   self.session.db["blocked"]["items"].pop(item)
   pub.sendMessage("unblocked-user", item=item, user=self.get_user())

 def check_send(self, data):
  if self.session.db["user_name"] == data["user"]["screen_name"]:
   d = self.put_data("sent_tweets", data)
   if d != False:
    pub.sendMessage("sent-tweet", data=data, user=self.get_user())

 def check_favs(self, data):
  if data["source"]["screen_name"] == self.session.db["user_name"]:
   d = self.put_data("favourites", data["target_object"])
   if d != False:
    pub.sendMessage("favourite", data=data["target_object"], user=self.get_user())

 def check_mentions(self, data):
  if "@%s" % (self.session.db["user_name"]) in data["text"]:
   d = self.put_data("mentions", data)
   if d != False:
    pub.sendMessage("mention", data=data, user=self.get_user())

 def set_quoted_tweet(self, data):
  if data["source"]["screen_name"] != self.session.db["user_name"]:
   d = self.put_data("mentions", data["target_object"])   
   if d != False:
    pub.sendMessage("mention", data=data["target_object"], user=self.get_user())

 def process_dm(self, data):
  if self.session.db["user_name"] != data["direct_message"]["sender"]["screen_name"]:
#   d = self.put_data("sent_direct_messages", data["direct_message"])
#   if d != False:
#    pub.sendMessage("sent-dm", data=data["direct_message"], user=self.get_user())
#  else:
   d = self.put_data("direct_messages", data["direct_message"])
   if d != False:
    pub.sendMessage("direct-message", data=data["direct_message"], user=self.get_user())
   
 def check_follower(self, data):
  if data["target"]["screen_name"] == self.session.db["user_name"]:
   if self.session.settings["general"]["reverse_timelines"] == False:
    self.session.db["followers"]["items"].append(data["source"])
   else:
    self.session.db["followers"]["items"].insert(0, data["source"])
   pub.sendMessage("follower", data=data["source"], user = self.get_user())
  else:
   if self.session.settings["general"]["reverse_timelines"] == False:
    self.session.db["friends"]["items"].append(data["target"])
   else:
    self.session.db["friends"]["items"].insert(0, data["target"])
   pub.sendMessage("friend", data=data["target"], user=self.get_user())

###
 def remove_fav(self, data):
  if self.session.db["user_name"] == data["source"]["screen_name"]:
   item = utils.find_item(data["target_object"]["id"], self.session.db["favourites"])
   self.session.db["favourites"].pop(item)
   pub.sendMessage("unfavourite", item=item, user=self.get_user())

 def remove_friend(self, data):
  if "friends" in self.session.settings["general"]["buffer_order"]:
   item = utils.find_item(data["target"]["id"], self.session.db["friends"]["items"])
   if item > 0:
    self.friends.pop(item)
    pub.sendMessage("unfollowing", item=item, user=self.get_user())

 def on_success(self, data):
  try:
#   if "delete" in data:
#    pub.sendMessage("tweet-deleted", data=data)
   if "direct_message" in data:
    self.process_dm(data)
   elif "friends" in data:
    self.friends = data["friends"]
    pub.sendMessage("friends-receibed")
   elif "text" in data and utils.is_allowed(data, self.session.settings["twitter"]["ignored_clients"]) == True:
    if "extended_tweet" in data:
     data["full_text"] = data["extended_tweet"]["full_text"]
     data["entities"] = data["extended_tweet"]["entities"]
#     log.error(data["extended_tweet"])
#	log.error("Extended tweet")
    if data["user"]["id"] in self.muted_users: return
    self.check_mentions(data)
    self.check_send(data)
    if data["user"]["id"] in self.friends or data["user"]["screen_name"] == self.session.db["user_name"]:
     d = self.put_data("home_timeline", data)
     if d != False:
      pub.sendMessage("item-in-home", data=data, user=self.get_user())
   elif "event" in data:
    if "favorite" == data["event"] and "favorites" in self.session.settings["general"]["buffer_order"]:
     self.check_favs(data)
    elif "unfavorite" == data["event"] and "favorites" in self.session.settings["general"]["buffer_order"]:
     self.remove_fav(data)
    elif "follow" == data["event"] and "followers" in self.session.settings["general"]["buffer_order"]:
     self.check_follower(data)
    elif "unfollow" == data["event"] and "friends" in self.session.settings["general"]["buffer_order"]:
     self.remove_friend(data)
    elif "block" == data["event"]:
     self.block_user(data)
    elif "unblock" == data["event"]:
     self.unblock(data)
    elif "list_created" == data["event"]:
     item = utils.find_item(data["target_object"]["id"], self.session.db["lists"])
     if item != None: self.session.db["lists"].append(data["target_object"])
    elif "list_destroyed" == data["event"]:
     item = utils.find_item(data["target_object"]["id"], self.session.db["lists"])
     if item != None: self.session.db["lists"].pop(item)
     self.parent.remove_list(data["target_object"]["id"])
    elif "list_member_added" == data["event"] and data["source"]["screen_name"] == self.get_user():
     pub.sendMessage("new-list-member-added", **{"id":str(data["target"]["id"]), "list":data["target_object"], "user":self.get_user()})
    elif "list_member_added" == data["event"] and data["target"]["screen_name"] == self.get_user():
     self.session.db["lists"].append(data["target_object"])
    elif "list_member_removed" == data["event"] and data["source"]["screen_name"] == self.get_user():
     pub.sendMessage("list-member-deleted", **{"id":str(data["target"]["id"]), "list":data["target_object"], "user":self.get_user()})
    elif "list_member_removed" == data["event"] and data["target"] == self.get_user():
     id = data["target_object"]["id"]
     list = utils.find_item(id, self.session.db["lists"])
     if list != None: self.session.db["lists"].pop(list)
     pub.sendMessage("list-deleted", **{"item":list, "user":self.get_user()})
    elif "quoted_tweet" == data["event"]:
     self.set_quoted_tweet(data)

    if "events" in self.session.settings["general"]["buffer_order"]:
     pub.sendMessage("event", data= data, user= self.get_user())
#     self.sound.play("new_event.ogg")
  except KeyboardInterrupt:
   pass
