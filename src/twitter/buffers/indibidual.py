# -*- coding: utf-8 -*-
import config
from requests.auth import HTTPProxyAuth
from twitter import compose, utils
from twython import TwythonStreamer
from pubsub import pub
import logging as original_logger
log = original_logger.getLogger("TimelinesStream")

class timelinesStreamer(TwythonStreamer):
 def __init__(self, app_key, app_secret, oauth_token, oauth_token_secret, timeout=300, retry_count=None, retry_in=10, client_args=None, handlers=None, chunk_size=1, session=None):
  self.session = session
  args = None
  if config.app["proxy"]["server"] != "" and config.app["proxy"]["port"] != "":
   args = {"proxies": {"http": "http://{0}:{1}".format(config.app["proxy"]["server"], config.app["proxy"]["port"]),
  "https": "https://{0}:{1}".format(config.app["proxy"]["server"], config.app["proxy"]["port"])}}
   if config.app["proxy"]["user"] != "" and config.app["proxy"]["password"] != "":
    auth = HTTPProxyAuth(config.app["proxy"]["user"], config.app["proxy"]["password"])
    args["auth"] = auth
  super(timelinesStreamer, self).__init__(app_key, app_secret, oauth_token, oauth_token_secret, timeout=60, retry_count=None, retry_in=180, client_args=args, handlers=None, chunk_size=1)
  self.lists = self.session.lists

 def on_error(self, status_code, data):
  log.error("error in stream: %s: %s" % (status_code, data))
#  pub.sendMessage("stream-error", session=self.session.session_id)

 def on_timeout(self, *args, **kwargs):
  log.error("Twitter timeout Error")
#  pub.sendMessage("stream-error", session=self.session.session_id)

 def check_tls(self, data):
  for i in self.session.settings["other_buffers"]["timelines"]:
   if data["user"]["screen_name"] == i:
    if utils.find_item(data["id"], self.session.db["%s-timeline" % (i,)]) != None:
     log.error("duplicated tweet. Ignoring it...")
     return
    try:
     data_ = self.session.check_quoted_status(data)
     data = data_
    except:
     pass
    if self.session.settings["general"]["reverse_timelines"] == False: self.session.db["%s-timeline" % (i,)].append(data)
    else: self.session.db["%s-timeline" % (i,)].insert(0, data)
    pub.sendMessage("item-in-timeline", data= data, user= self.session.db["user_name"], who= i)
  for i in self.session.lists:
   try:
    i.users.index(data["user"]["id"])
    usr = data["in_reply_to_user_id"]
    if (usr != None and usr in self.friends) or data.has_key("retweeted_status"):
     data = self.session.check_quoted_status(data)
     if self.session.settings["general"]["reverse_timelines"] == False: self.session.db["%s" % (i.name,)].append(data)
     else: self.session.db["%s" % (i,)].insert(0, data)
     pub.sendMessage("item-in-list", data= data, user= self.session.db["user_name"], where= i.name)
    elif usr == None:
     if self.session.settings["general"]["reverse_timelines"] == False: self.session.db["%s" % (i.name,)].append(data)
     else: self.session.db["%s" % (i,)].insert(0, data)
     pub.sendMessage("item-in-list", data= data, user= self.session.db["user_name"], where= i.name)
   except ValueError:
    pass

 def set_friends(self, friends):
  self.friends = friends

 def on_success(self, data):
  try:
   if "text" in data and utils.is_allowed(data, self.session.settings["twitter"]["ignored_clients"]) == True:
    self.check_tls(data)
  except:
   pass
