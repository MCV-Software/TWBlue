# -*- coding: utf-8 -*-
from twitter import compose
from twython import TwythonStreamer
import sound
from mysc import event
import wx
import config
import output
import logging as original_logger
log = original_logger.getLogger("MainStream")

class streamer(TwythonStreamer):
 def __init__(self, app_key, app_secret, oauth_token, oauth_token_secret, timeout=300, retry_count=None, retry_in=10, client_args=None, handlers=None, chunk_size=1, parent=None):
  self.db = parent.db
  self.parent = parent
  TwythonStreamer.__init__(self, app_key, app_secret, oauth_token, oauth_token_secret, timeout=60, retry_count=None, retry_in=180, client_args=None, handlers=None, chunk_size=1)

 def on_error(self, status_code, data):
  log.debug("%s: %s" % (status_code, data))

 def check_tls(self, data):
  for i in config.main["other_buffers"]["timelines"]:
   if data["user"]["screen_name"] == i:
    tweet_event = event.event(event.EVT_OBJECT, 1)
    tweet_event.SetItem(data)
    announce = _(u"One tweet from %s") % (data["user"]["name"])
    tweet_event.SetAnnounce(announce)
    wx.PostEvent(self.parent.search_buffer(buffer_type="timeline", name_buffer=data["user"]["screen_name"]), tweet_event)
  for i in range(0, self.parent.nb.GetPageCount()):
   if self.parent.nb.GetPage(i).type == "list":
    try:
     self.parent.nb.GetPage(i).users.index(data["user"]["id"])
     tweet_event = event.event(event.EVT_OBJECT, 1)
     tweet_event.SetItem(data)
     announce = _(u"One tweet from %s in the list %s") % (data["user"]["name"], self.parent.nb.GetPage(i).name_buffer[:-5])
     tweet_event.SetAnnounce(announce)
     usr = data["in_reply_to_user_id"]
     if (usr != None and usr in self.friends) or data.has_key("retweeted_status"):
      wx.PostEvent(self.parent.nb.GetPage(i), tweet_event)
     elif usr == None:
      wx.PostEvent(self.parent.nb.GetPage(i), tweet_event)
    except ValueError:
     pass

 def on_success(self, data):
  try:
   if data.has_key("text"):
    self.check_tls(data)
   elif "friends" in data:
    self.friends = data["friends"]
  except:
   pass