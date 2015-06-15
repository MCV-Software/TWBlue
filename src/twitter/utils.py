# -*- coding: utf-8 -*-
import url_shortener, re
import output
from twython import TwythonError
import config
import logging
import requests
import time
import sound
log = logging.getLogger("twitter.utils")
""" Some utilities for the twitter interface."""

__version__ = 0.1
__doc__ = "Find urls in tweets and #audio hashtag."

url_re = re.compile(r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))")

url_re2 = re.compile("(?:\w+://|www\.)[^ ,.?!#%=+][^ ]*")
bad_chars = '\'\\.,[](){}:;"'

def find_urls_in_text(text):
 return [s.strip(bad_chars) for s in url_re2.findall(text)]

def find_urls (tweet):
 urls = []
 return [s[0] for s in url_re.findall(tweet["text"])]

def find_item(id, listItem):
 for i in range(0, len(listItem)):
  if listItem[i]["id"] == id: return i
 return None

def find_list(name, lists):
 for i in range(0, len(lists)):
  if lists[i]["slug"] == name:  return lists[i]["id"]

def find_previous_reply(id, listItem):
 for i in range(0, len(listItem)):
  if listItem[i]["id_str"] == str(id): return i
 return None

def find_next_reply(id, listItem):
 for i in range(0, len(listItem)):
  if listItem[i]["in_reply_to_status_id_str"] == str(id): return i
 return None

def is_audio(tweet):
 try:
  if len(find_urls(tweet)) < 1:
   return False
  if len(tweet["entities"]["hashtags"]) > 0:
   for i in tweet["entities"]["hashtags"]:
    if i["text"] == "audio":
     return True
 except:
  log.exception("Exception while executing is_audio hashtag algorithm")

def is_geocoded(tweet):
 if tweet.has_key("coordinates") and tweet["coordinates"] != None:
  return True

def get_all_mentioned(tweet, conf):
 """ Gets all users that has been mentioned."""
 string = []
 for i in tweet["entities"]["user_mentions"]:
  if i["screen_name"] != conf["user_name"] and i["screen_name"] != tweet["user"]["screen_name"]:
   if "@"+i["screen_name"] not in string:
    string.append("@"+i["screen_name"])
 return " ".join(string)+" "

def get_all_users(tweet, conf):
 string = []
 if tweet.has_key("retweeted_status"):
  string.append(tweet["user"]["screen_name"])
  tweet = tweet["retweeted_status"]
 if tweet.has_key("sender"):
  string.append(tweet["sender"]["screen_name"])
 else:
  if tweet["user"]["screen_name"] != conf["user_name"]:
   string.append(tweet["user"]["screen_name"])
  for i in tweet["entities"]["user_mentions"]:
   if i["screen_name"] != conf["user_name"] and i["screen_name"] != tweet["user"]["screen_name"]:
    if i["screen_name"] not in string:
     string.append(i["screen_name"])
 if len(string) == 0:
  string.append(tweet["user"]["screen_name"])
 return string

def if_user_exists(twitter, user):
 try:
  data = twitter.show_user(screen_name=user)
  return data
 except TwythonError as err:
  if err.error_code == 404:
   return None
  else:
   return user

def api_call(parent=None, call_name=None, preexec_message="", success="", success_snd="", *args, **kwargs):
 if preexec_message:
  output.speak(preexec_message, True)
 try:
  val = getattr(parent.twitter.twitter, call_name)(*args, **kwargs)
  output.speak(success)
  parent.parent.sound.play(success_snd)
 except TwythonError as e:
  output.speak("Error %s: %s" % (e.error_code, e.msg), True)
  parent.parent.sound.play("error.ogg")
 return val

def is_allowed(tweet, clients):
 if tweet.has_key("sender"): return True
 allowed = True
 if tweet.has_key("retweeted_status"): tweet = tweet["retweeted_status"]
 source = re.sub(r"(?s)<.*?>", "", tweet["source"])
 for i in clients:
  if i.lower() == source.lower():
   allowed = False
   log.exception("Tuit not allowed: %s" % (tweet["text"],))
 return allowed

def twitter_error(error):
 if error.error_code == 403:
  msg = _(u"Sorry, you are not authorised to see this status.")
 elif error.error_code == 404:
  msg = _(u"No status found with that ID")
 else:
  msg = _(u"Error code {0}").format(error.error_code,)
 output.speak(msg)