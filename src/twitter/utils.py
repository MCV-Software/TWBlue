# -*- coding: utf-8 -*-
import url_shortener, re
""" Some utilities for the twitter interface."""
import output
from twython import TwythonError
import config

__version__ = 0.1
__doc__ = "Find urls in tweets and #audio hashtag."

url_re = re.compile(r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))")
#"(?:\w+://|www\.)[^ ,.?!#%=+][^ ]*")
#bad_chars = '\'\\.,[](){}:;"'

url_re2 = re.compile("(?:\w+://|www\.)[^ ,.?!#%=+][^ ]*")
bad_chars = '\'\\.,[](){}:;"'

def find_urls_in_text(text):
 return [s.strip(bad_chars) for s in url_re2.findall(text)]

def find_urls (tweet):
 urls = []
# for i in tweet["entities"]["urls"]:
#  unshortened = url_shortener.unshorten(i["expanded_url"])
#  if unshortened == None:
#   urls.append(i["expanded_url"])
#  else:
#   urls.append(unshortened)
# return urls
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
# r = range(0, len(listItem))
# r.reverse()
# for i in r:
 for i in range(0, len(listItem)):
  if listItem[i]["in_reply_to_status_id_str"] == str(id): return i
 return None

def is_audio(tweet):
 if len(tweet["entities"]["hashtags"]) > 0:
  for i in tweet["entities"]["hashtags"]:
   if i["text"] == "audio":
    return True
 return False

def is_geocoded(tweet):
 if tweet.has_key("coordinates") and tweet["coordinates"] != None:
  return True

def get_all_mentioned(tweet, config):
 """ Gets all users that has been mentioned."""
 if tweet.has_key("retweeted_status"): tweet = tweet["retweeted_status"]
 string = []
 for i in tweet["entities"]["user_mentions"]:
  if i["screen_name"] != config.settings["user_name"] and i["screen_name"] != tweet["user"]["screen_name"]:
   if "@"+i["screen_name"] not in string:
    string.append("@"+i["screen_name"])
 return " ".join(string)+" "

def get_all_users(tweet, config):
 string = []
 if tweet.has_key("retweeted_status"):
  string.append(tweet["user"]["screen_name"])
  tweet = tweet["retweeted_status"]
 if tweet.has_key("sender"):
  string.append(tweet["sender"]["screen_name"])
 else:
  if tweet["user"]["screen_name"] != config.settings["user_name"]:
   string.append(tweet["user"]["screen_name"])
  for i in tweet["entities"]["user_mentions"]:
   if i["screen_name"] != config.settings["user_name"] and i["screen_name"] != tweet["user"]["screen_name"]:
    if i["screen_name"] not in string:
     string.append(i["screen_name"])
 if len(string) == 0:
  string.append(tweet["user"]["screen_name"])
 return string

def if_user_exists(twitter, user):
 try:
  data = twitter.show_user(screen_name=user)
  return data["screen_name"]
 except:
  return None

def api_call(parent=None, call_name=None, preexec_message="", success="", success_snd="", *args, **kwargs):
 if preexec_message:
  output.speak(preexec_message, True)
 try:
  val = getattr(parent.twitter.twitter, call_name)(*args, **kwargs)
  output.speak(success)
  parent.parent.sound.play(success_snd)
 except TwythonError as e:
  output.speak("Error %s: %s" % (e.error_code, e.msg), True)
  parent.parent.sound.play("error.wav")
 return val

def is_allowed(tweet):
 allowed = True
 if tweet.has_key("retweeted_status"): tweet = tweet["retweeted_status"]
 source = re.sub(r"(?s)<.*?>", "", tweet["source"])
 for i in config.main["twitter"]["ignored_clients"]:
  if i.lower() == source.lower(): allowed = False
 return allowed