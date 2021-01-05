# -*- coding: utf-8 -*-
import url_shortener, re
import output
import config
import logging
import requests
import time
import sound
from tweepy.error import TweepError
log = logging.getLogger("twitter.utils")
""" Some utilities for the twitter interface."""

__version__ = 0.1
__doc__ = "Find urls in tweets and #audio hashtag."

url_re = re.compile(r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))")

url_re2 = re.compile("(?:\w+://|www\.)[^ ,.?!#%=+][^ \\n\\t]*")
bad_chars = '\'\\\n.,[](){}:;"'

def find_urls_in_text(text):
 return  url_re2.findall(text)

def find_urls (tweet):
 urls = []
 # Let's add URLS from tweet entities.
 if hasattr(tweet, "message_create"):
  entities = tweet.message_create["message_data"]["entities"]
 else:
  entities = tweet.entities
 for i in entities["urls"]:
  if i["expanded_url"] not in urls:
   urls.append(i["expanded_url"])
 if hasattr(tweet, "quoted_status"):
  for i in tweet.quoted_status.entities["urls"]:
   if i["expanded_url"] not in urls:
    urls.append(i["expanded_url"])
 if hasattr(tweet, "retweeted_status"):
  for i in tweet.retweeted_status.entities["urls"]:
   if i["expanded_url"] not in urls:
    urls.append(i["expanded_url"])
  if hasattr(tweet["retweeted_status"], "quoted_status"):
   for i in tweet.retweeted_status.quoted_status.entities["urls"]:
    if i["expanded_url"] not in urls:
     urls.append(i["expanded_url"])
 if hasattr(tweet, "message"):
  i = "message"
 elif hasattr(tweet, "full_text"):
  i = "full_text"
 else:
  i = "text"
 if hasattr(tweet, "message_create"):
  extracted_urls = find_urls_in_text(tweet.message_create["message_data"]["text"])
 else:
  extracted_urls = find_urls_in_text(getattr(tweet, i))
 # Don't include t.co links (mostly they are photos or shortened versions of already added URLS).
 for i in extracted_urls:
  if i not in urls and "https://t.co" not in i:
   urls.append(i)
 return urls

def find_item(id, listItem):
 for i in range(0, len(listItem)):
  if listItem[i].id == id: return i
 return None

def find_list(name, lists):
 for i in range(0, len(lists)):
  if lists[i].name == name:  return lists[i].id

def is_audio(tweet):
 try:
  if len(find_urls(tweet)) < 1:
   return False
  if hasattr(tweet, "message_create"):
   entities = tweet.message_create["message_data"]["entities"]
  else:
   entities = tweet.entities
  if len(entities["hashtags"]) > 0:
   for i in entities["hashtags"]:
    if i["text"] == "audio":
     return True
 except IndexError:
  print(tweet.entities["hashtags"])
  log.exception("Exception while executing is_audio hashtag algorithm")

def is_geocoded(tweet):
 if hasattr(tweet, "coordinates") and tweet.coordinates != None:
  return True

def is_media(tweet):
 if hasattr(tweet, "message_create"):
  entities = tweet.message_create["message_data"]["entities"]
 else:
  entities = tweet.entities
 if entities.get("media") == None:
  return False
 for i in entities["media"]:
  if i.get("type") != None and i.get("type") == "photo":
   return True
 return False

def get_all_mentioned(tweet, conf, field="screen_name"):
 """ Gets all users that have been mentioned."""
 results = []
 for i in tweet.entities["user_mentions"]:
  if i["screen_name"] != conf["user_name"] and i["screen_name"] != tweet.user.screen_name:
   if i.get(field) not in results:
    results.append(i.get(field))
 return results

def get_all_users(tweet, conf):
 string = []
 if hasattr(tweet, "retweeted_status"):
  string.append(tweet.user.screen_name)
  tweet = tweet.retweeted_status
 if hasattr(tweet, "sender"):
  string.append(tweet.sender.screen_name)
 else:
  if tweet.user.screen_name != conf["user_name"]:
   string.append(tweet.user.screen_name)
  for i in tweet.entities["user_mentions"]:
   if i["screen_name"] != conf["user_name"] and i["screen_name"] != tweet.user.screen_name:
    if i["screen_name"] not in string:
     string.append(i["screen_name"])
 if len(string) == 0:
  string.append(tweet.user.screen_name)
 return string

def if_user_exists(twitter, user):
 try:
  data = twitter.get_user(screen_name=user)
  return data
 except TweepError as err:
  if err.error_code == 50:
   return None
  else:
   return user

def is_allowed(tweet, settings, buffer_name):
 clients = settings["twitter"]["ignored_clients"]
 if hasattr(tweet, "sender"): return True
 allowed = True
 tweet_data = {}
 if hasattr(tweet, "retweeted_status"):
  tweet_data["retweet"] = True
 if tweet.in_reply_to_status_id_str != None:
  tweet_data["reply"] = True
 if hasattr(tweet, "quoted_status"):
  tweet_data["quote"] = True
 if hasattr(tweet, "retweeted_status"):
  tweet = tweet.retweeted_status
 source = tweet.source
 for i in clients:
  if i.lower() == source.lower():
   return False
 return filter_tweet(tweet, tweet_data, settings, buffer_name)

def filter_tweet(tweet, tweet_data, settings, buffer_name):
 if hasattr(tweet, "full_text"):
  value = "full_text"
 else:
  value = "text"
 for i in settings["filters"]:
  if settings["filters"][i]["in_buffer"] == buffer_name:
   regexp = settings["filters"][i]["regexp"]
   word = settings["filters"][i]["word"]
   # Added if/else for compatibility reasons.
   if "allow_rts" in settings["filters"][i]:
    allow_rts = settings["filters"][i]["allow_rts"]
   else:
    allow_rts = "True"
   if "allow_quotes" in settings["filters"][i]:
    allow_quotes = settings["filters"][i]["allow_quotes"]
   else:
    allow_quotes = "True"
   if "allow_replies" in settings["filters"][i]:
    allow_replies = settings["filters"][i]["allow_replies"]
   else:
    allow_replies = "True"
   if allow_rts == "False" and "retweet" in tweet_data:
    return False
   if allow_quotes == "False" and "quote" in tweet_data:
    return False
   if allow_replies == "False" and "reply" in tweet_data:
    return False
   if word != "" and settings["filters"][i]["if_word_exists"]:
    if word in getattr(tweet, value):
     return False
   elif word != "" and settings["filters"][i]["if_word_exists"] == False:
    if word not in getattr(tweet, value):
     return False
   if settings["filters"][i]["in_lang"] == "True":
    if getattr(tweet, lang) not in settings["filters"][i]["languages"]:
     return False
   elif settings["filters"][i]["in_lang"] == "False":
    if tweet.lang in settings["filters"][i]["languages"]:
     return False
 return True

def twitter_error(error):
 if error.api_code == 179:
  msg = _(u"Sorry, you are not authorised to see this status.")
 elif error.error_code == 144:
  msg = _(u"No status found with that ID")
 else:
  msg = _(u"Error code {0}").format(error.api_code,)
 output.speak(msg)

def expand_urls(text, entities):
 """ Expand all URLS present in text with information found in entities"""
 urls = find_urls_in_text(text)
 for url in entities["urls"]:
  if url["url"] in text:
   text = text.replace(url["url"], url["expanded_url"])
 return text
