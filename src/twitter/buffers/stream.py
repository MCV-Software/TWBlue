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
  args = None
  if config.app["proxy"]["server"] != "" and config.app["proxy"]["port"] != "":
   args = {"proxies": {"http": "http://{0}:{1}".format(config.app["proxy"]["server"], config.app["proxy"]["port"]),
  "https": "https://{0}:{1}".format(config.app["proxy"]["server"], config.app["proxy"]["port"])}}
   if config.app["proxy"]["user"] != "" and config.app["proxy"]["password"] != "":
    auth = HTTPProxyAuth(config.app["proxy"]["user"], config.app["proxy"]["password"])
    args["auth"] = auth
  super(streamer, self).__init__(app_key, app_secret, oauth_token, oauth_token_secret, client_args=args, *a, **kw)
  self.session = sessionObject
  self.muted_users = self.session.db["muted_users"]
#  self.blocked_users = []

 def on_timeout(self, *args, **kwargs):
  log.debug("Twitter timeout Error")
  pub.sendMessage("stream-error")

 def on_error(self, status_code, data):
  log.debug("Error %s: %s" % (status_code, data))

 def get_user(self):
  return self.session.db["user_name"]

 def put_data(self, place, data):
  if self.session.db.has_key(place):
   if self.session.settings["general"]["reverse_timelines"] == False:
    self.session.db[place].append(data)
   else:
    self.session.db[place].insert(0, data)

 def block_user(self, data):
  id = data["target"]["id"]
  if id in self.friends:
   self.friends.remove(id)
  if self.session.settings["other_buffers"]["show_blocks"] == True:
   self.session.db["blocked"]["items"].append(data["target"])
   pub.sendMessage("blocked-user", data=data["target"], user=self.get_user())

 def unblock(self, data):
  if self.session.settings["other_buffers"]["show_blocks"] == True:
   item = utils.find_item(data["target"]["id"], self.session.db["blocked"]["items"])
   self.session.db["blocked"]["items"].pop(item)
   pub.sendMessage("unblocked-user", item=item, user=self.get_user())

 def check_send(self, data):
  if self.session.db["user_name"] == data["user"]["screen_name"]:
   self.put_data("sent_tweets", data)
   pub.sendMessage("sent-tweet", data=data, user=self.get_user())

 def check_favs(self, data):
  if data["source"]["screen_name"] == self.session.db["user_name"]:
   self.put_data("favourites", data["target_object"])
   pub.sendMessage("favourite", data=data["target_object"], user=self.get_user())

 def check_mentions(self, data):
  if "@%s" % (self.session.db["user_name"]) in data["text"]:
   self.put_data("mentions", data)   
   pub.sendMessage("mention", data=data, user=self.get_user())
 
 def process_dm(self, data):
  if self.session.db["user_name"] == data["direct_message"]["sender"]["screen_name"]:
   self.put_data("sent_direct_messages", data["direct_message"])
   pub.sendMessage("sent-dm", data=data["direct_message"], user=self.get_user())
  else:
   self.put_data("direct_messages", data["direct_message"])
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
  if self.session.settings["other_buffers"]["show_friends"] == True:
   item = utils.find_item(data["target"]["id"], self.session.db["friends"]["items"])
   if item > 0:
    self.friends["items"].pop(item)
    pub.sendMessage("unfollowing", item=item, user=self.get_user())

 def on_success(self, data):
  try:
   if "direct_message" in data:
    self.process_dm(data)
   elif "friends" in data:
    self.friends = data["friends"]
    pub.sendMessage("friends-receibed")
   elif "text" in data and utils.is_allowed(data, self.session.settings["twitter"]["ignored_clients"]) == True:
    if data["user"]["id"] in self.muted_users: return
    self.check_mentions(data)
    self.check_send(data)
    if data["user"]["id"] in self.friends or data["user"]["screen_name"] == self.session.db["user_name"]:
     self.put_data("home_timeline", data)
     pub.sendMessage("item-in-home", data=data, user=self.get_user())
   elif data.has_key("event"):
    if "favorite" == data["event"] and self.session.settings["other_buffers"]["show_favourites"] == True:
     self.check_favs(data)
    elif "unfavorite" == data["event"] and self.session.settings["other_buffers"]["show_favourites"] == True:
     self.remove_fav(data)
    elif "follow" == data["event"] and self.session.settings["other_buffers"]["show_followers"] == True:
     self.check_follower(data)
    elif "unfollow" == data["event"] and self.session.settings["other_buffers"]["show_followers"] == True:
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
    if self.session.settings["other_buffers"]["show_events"] == True:
     pub.sendMessage("event", data= data, user= self.get_user())
#     self.sound.play("new_event.ogg")
  except KeyboardInterrupt:
   pass
