# -*- coding: utf-8 -*-

from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import chr
from builtins import range
import platform
system = platform.system()
from . import utils
import re
import html.entities
import time
import output
import languageHandler
import arrow
import logging
import config
from long_tweets import twishort, tweets
log = logging.getLogger("compose")

def StripChars(s):
 """Converts any html entities in s to their unicode-decoded equivalents and returns a string."""
 entity_re = re.compile(r"&(#\d+|\w+);")
 def matchFunc(match):
  """Nested function to handle a match object.
 If we match &blah; and it's not found, &blah; will be returned.
 if we match #\d+, unichr(digits) will be returned.
 Else, a unicode string will be returned."""
  if match.group(1).startswith('#'): return chr(int(match.group(1)[1:]))
  replacement = html.entities.entitydefs.get(match.group(1), "&%s;" % match.group(1))
  return replacement
 return str(entity_re.sub(matchFunc, s))

chars = "abcdefghijklmnopqrstuvwxyz"

def compose_tweet(tweet, db, relative_times, show_screen_names=False):
 """ It receives a tweet and returns a list with the user, text for the tweet or message, date and the client where user is."""
 if system == "Windows":
  original_date = arrow.get(tweet["created_at"], "ddd MMM DD H:m:s Z YYYY", locale="en")
  if relative_times == True:
   ts = original_date.humanize(locale=languageHandler.getLanguage())
  else:
   ts = original_date.replace(seconds=db["utc_offset"]).format(_("dddd, MMMM D, YYYY H:m:s"), locale=languageHandler.getLanguage())
 else:
  ts = tweet["created_at"]
 if "message" in tweet:
  value = "message"
 elif "full_text" in tweet:
  value = "full_text"
 else:
  value = "text"
#  log.exception(tweet.keys())
 text = StripChars(tweet[value])
 if show_screen_names:
  user = tweet["user"]["screen_name"]
 else:
  user = tweet["user"]["name"]
 source = re.sub(r"(?s)<.*?>", "", tweet["source"])
 if "retweeted_status" in tweet:
  if ("message" in tweet) == False and tweet["retweeted_status"]["is_quote_status"] == False:
   text = "RT @%s: %s" % (tweet["retweeted_status"]["user"]["screen_name"], StripChars(tweet["retweeted_status"][value]))
  elif tweet["retweeted_status"]["is_quote_status"]:
   text = "%s" % (StripChars(tweet[value]))
  else:
   text = "RT @%s: %s" % (tweet["retweeted_status"]["user"]["screen_name"], StripChars(tweet[value]))
# if text[-1] in chars: text=text+"."
 if ("message" in tweet) == False:
  urls = utils.find_urls_in_text(text)
  for url in range(0, len(urls)):
   try:
    text = text.replace(urls[url], tweet["entities"]["urls"][url]["expanded_url"])
   except: pass
  if config.app['app-settings']['handle_longtweets']: pass
#   return [user+", ", text, ts+", ", source]
 return [user+", ", text, ts+", ", source]

def compose_dm(tweet, db, relative_times, show_screen_names=False):
 """ It receives a tweet and returns a list with the user, text for the tweet or message, date and the client where user is."""
 if system == "Windows":
  original_date = arrow.get(tweet["created_at"], "ddd MMM DD H:m:s Z YYYY", locale="en")
  if relative_times == True:
   ts = original_date.humanize(locale=languageHandler.getLanguage())
  else:
   ts = original_date.replace(seconds=db["utc_offset"]).format(_("dddd, MMMM D, YYYY H:m:s"), locale=languageHandler.getLanguage())
 else:
  ts = tweet["created_at"]
 text = StripChars(tweet["text"])
 source = "DM"
 if db["user_name"] == tweet["sender"]["screen_name"]:
  if show_screen_names:
   user = _("Dm to %s ") % (tweet["recipient"]["screen_name"],)
  else:
   user = _("Dm to %s ") % (tweet["recipient"]["name"],)
 else:
  if show_screen_names:
   user = tweet["sender"]["screen_name"]
  else:
   user = tweet["sender"]["name"]
 if text[-1] in chars: text=text+"."
 urls = utils.find_urls_in_text(text)
 for url in range(0, len(urls)):
  try:  text = text.replace(urls[url], tweet["entities"]["urls"][url]["expanded_url"])
  except IndexError: pass
 return [user+", ", text, ts+", ", source]

def compose_quoted_tweet(quoted_tweet, original_tweet, show_screen_names=False):
 """ It receives a tweet and returns a list with the user, text for the tweet or message, date and the client where user is."""
 if "full_text" in quoted_tweet:
  value = "full_text"
 else:
  value = "text"
 text = StripChars(quoted_tweet[value])
 if show_screen_names:
  quoting_user = quoted_tweet["user"]["screen_name"]
 else:
  quoting_user = quoted_tweet["user"]["name"]
 source = re.sub(r"(?s)<.*?>", "", quoted_tweet["source"])
 try: text = "rt @%s: %s" % (quoted_tweet["retweeted_status"]["user"]["screen_name"], StripChars(quoted_tweet["retweeted_status"][value]))
 except KeyError: text = "%s" % (StripChars(quoted_tweet[value]))
 if text[-1] in chars: text=text+"."
 original_user = original_tweet["user"]["screen_name"]
 if "message" in original_tweet:
  original_text = StripChars(original_tweet["message"])
 elif "full_text" in original_tweet:
  original_text = StripChars(original_tweet["full_text"])
 else:
   original_text = StripChars(original_tweet["text"])
 quoted_tweet["message"] = _("{0}. Quoted  tweet from @{1}: {2}").format( quoted_tweet[value], original_user, original_text)
 quoted_tweet = tweets.clear_url(quoted_tweet)
 return quoted_tweet

def compose_followers_list(tweet, db, relative_times=True, show_screen_names=False):
 if system == "Windows":
  original_date = arrow.get(tweet["created_at"], "ddd MMM D H:m:s Z YYYY", locale="en")
  if relative_times == True:
   ts = original_date.humanize(locale=languageHandler.getLanguage())
  else:
   ts = original_date.replace(seconds=db["utc_offset"]).format(_("dddd, MMMM D, YYYY H:m:s"), locale=languageHandler.getLanguage())
 else:
  ts = tweet["created_at"]
 if "status" in tweet:
  if len(tweet["status"]) > 4 and system == "Windows":
   original_date2 = arrow.get(tweet["status"]["created_at"], "ddd MMM D H:m:s Z YYYY", locale="en")
   if relative_times:
    ts2 = original_date2.humanize(locale=languageHandler.getLanguage())
   else:
    ts2 = original_date2.replace(seconds=db["utc_offset"]).format(_("dddd, MMMM D, YYYY H:m:s"), locale=languageHandler.getLanguage())
  else:
   ts2 = _("Unavailable")
 else:
  ts2 = _("Unavailable")
 return [_("%s (@%s). %s followers, %s friends, %s tweets. Last tweeted %s. Joined Twitter %s") % (tweet["name"], tweet["screen_name"], tweet["followers_count"], tweet["friends_count"],  tweet["statuses_count"], ts2, ts)]

def compose_event(data, username, show_screen_names=False):
 if show_screen_names:
  value = "screen_name"
 else:
  value = "name"
 if data["event"] == "block":
  event = _("You've blocked %s") % (data["target"][value])
 elif data["event"] == "unblock":
  event = _("You've unblocked %s") % (data["target"][value])
 elif data["event"] == "follow":
  if data["target"]["screen_name"] == username:
   event = _("%s(@%s) has followed you") % (data["source"]["name"], data["source"]["screen_name"])
  elif data["source"]["screen_name"] == username:
   event = _("You've followed %s(@%s)") % (data["target"]["name"], data["target"]["screen_name"])
 elif data["event"] == "unfollow":
  event = _("You've unfollowed %s (@%s)") % (data["target"]["name"], data["target"]["screen_name"])
 elif data["event"] == "favorite":
  if data["source"]["screen_name"] == username:
   event = _("You've liked: %s, %s") % (data["target"][value], data["target_object"]["text"])
  else:
   event = _("%s(@%s) has liked: %s") % (data["source"]["name"], data["source"]["screen_name"], data["target_object"]["text"])
 elif data["event"] == "unfavorite":
  if data["source"]["screen_name"] == username: event = _("You've unliked: %s, %s") % (data["target"][value], data["target_object"]["text"])
  else: event = _("%s(@%s) has unliked: %s") % (data["source"]["name"], data["source"]["screen_name"], data["target_object"]["text"])
 elif data["event"] == "list_created":
  event = _("You've created the list %s") % (data["target_object"]["name"])
 elif data["event"] == "list_destroyed":
  event = _("You've deleted the list %s") % (data["target_object"]["name"])
 elif data["event"] == "list_updated":
  event = _("You've updated the list %s") % (data["target_object"]["name"])
 elif data["event"] == "list_member_added":
  if data["source"]["screen_name"] == username: event = _("You've added %s(@%s) to the list %s") % (data["target"]["name"], data["target"]["screen_name"], data["target_object"]["name"])
  else: event = _("%s(@%s) has added you to the list %s") % (data["source"]["name"], data["source"]["screen_name"], data["target_object"]["name"])
 elif data["event"] == "list_member_removed":
  if data["source"]["screen_name"] == username: event = _("You'be removed %s(@%s) from the list %s") % (data["target"]["name"], data["target"]["screen_name"], data["target_object"]["name"])
  else: event = _("%s(@%s) has removed you from the list %s") % (data["source"]["name"], data["source"]["screen_name"], data["target_object"]["name"])
 elif data["event"] == "list_user_subscribed":
  if data["source"]["screen_name"] == username: event = _("You've subscribed to the list %s, which is owned by %s(@%s)") % (data["target_object"]["name"], data["target"]["name"], data["target"]["screen_name"])
  else: event = _("%s(@%s) has suscribed you to the list %s") % (data["source"]["name"], data["source"]["screen_name"], data["target_object"]["name"])
 elif data["event"] == "list_user_unsubscribed":
  if data["source"]["screen_name"] == username: event = _("You've unsubscribed from the list %s, which is owned by %s(@%s)") % (data["target_object"]["name"], data["target"]["name"], data["target"]["screen_name"])
  else: event = _("You've been unsubscribed from the list %s, which is owned by %s(@%s)") % (data["target_object"]["name"], data["source"]["name"], data["source"]["screen_name"])
 elif data["event"] == "retweeted_retweet":
  if data["source"]["screen_name"] == username: event = _("You have retweeted a retweet from %s(@%s): %s") % (data["target"]["name"], data["target"]["screen_name"], data["target_object"]["retweeted_status"]["text"])
  else: event = _("%s(@%s) has retweeted your retweet: %s") % (data["source"]["name"], data["source"]["screen_name"], data["target_object"]["retweeted_status"]["text"])
 elif data["event"] == "quoted_tweet":
   event = _("@{0} quoted your tweet: {1}").format(data["source"]["screen_name"], data["target_object"]["text"])
 else:
  event = _("Unknown")
  log.error("event: %s\n target: %s\n source: %s\n target_object: %s" % (data["event"], data["target"], data["source"], data["target_object"]))
 return [time.strftime("%I:%M %p"), event]

def compose_list(list):
 name = list["name"]
 if list["description"] == None: description = _("No description available")
 else: description = list["description"]
 user = list["user"]["name"]
 members = str(list["member_count"])
 if list["mode"] == "private": status = _("private")
 else: status = _("public")
 return [name, description, user, members, status]
