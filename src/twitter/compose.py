# -*- coding: utf-8 -*-
import platform
system = platform.system()
import utils
import re
import htmlentitydefs
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
  if match.group(1).startswith('#'): return unichr(int(match.group(1)[1:]))
  replacement = htmlentitydefs.entitydefs.get(match.group(1), "&%s;" % match.group(1))
  return replacement.decode('iso-8859-1')
 return unicode(entity_re.sub(matchFunc, s))

chars = "abcdefghijklmnopqrstuvwxyz"

def compose_tweet(tweet, db, relative_times, show_screen_names=False, session=None):
 """ It receives a tweet and returns a list with the user, text for the tweet or message, date and the client where user is."""
 if system == "Windows":
  original_date = arrow.get(tweet["created_at"], "ddd MMM DD H:m:s Z YYYY", locale="en")
  if relative_times == True:
   ts = original_date.humanize(locale=languageHandler.getLanguage())
  else:
   ts = original_date.replace(seconds=db["utc_offset"]).format(_(u"dddd, MMMM D, YYYY H:m:s"), locale=languageHandler.getLanguage())
 else:
  ts = tweet["created_at"]
 if tweet.has_key("message"):
  value = "message"
 elif tweet.has_key("full_text"):
  value = "full_text"
 else:
  value = "text"
 if tweet.has_key("retweeted_status") and value != "message":
  text = StripChars(tweet["retweeted_status"][value])
 else:
  text = StripChars(tweet[value])
 if show_screen_names:
  user = tweet["user"]["screen_name"]
 else:
  user = tweet["user"]["name"]
 source = re.sub(r"(?s)<.*?>", "", tweet["source"])
 if tweet.has_key("retweeted_status"):
  if tweet.has_key("message") == False and tweet["retweeted_status"]["is_quote_status"] == False:
   text = "RT @%s: %s" % (tweet["retweeted_status"]["user"]["screen_name"], text)
  elif tweet["retweeted_status"]["is_quote_status"]:
   text = "%s" % (text)
  else:
   text = "RT @%s: %s" % (tweet["retweeted_status"]["user"]["screen_name"], text)
 if tweet.has_key("message") == False:
  urls = utils.find_urls_in_text(text)
  if tweet.has_key("retweeted_status"):
   for url in range(0, len(urls)):
    try:
     text = text.replace(urls[url], tweet["retweeted_status"]["entities"]["urls"][url]["expanded_url"])
    except: pass
  else:
   for url in range(0, len(urls)):
    try:
     text = text.replace(urls[url], tweet["entities"]["urls"][url]["expanded_url"])
    except: pass
  if config.app['app-settings']['handle_longtweets']: pass
 return [user+", ", text, ts+", ", source]

def compose_direct_message(item, db, relative_times, show_screen_names=False, session=None):
 # for a while this function will be together with compose_dm.
 # this one composes direct messages based on events (new API Endpoints).
 if system == "Windows":
   # Let's remove the last 3 digits in the timestamp string.
   # Twitter sends their "epoch" timestamp with 3 digits for milliseconds and arrow doesn't like it.
  original_date = arrow.get(item["created_timestamp"][:-3])
  if relative_times == True:
   ts = original_date.humanize(locale=languageHandler.getLanguage())
  else:
   ts = original_date.replace(seconds=db["utc_offset"]).format(_(u"dddd, MMMM D, YYYY H:m:s"), locale=languageHandler.getLanguage())
 else:
  ts = item["created_timestamp"]
 text = StripChars(item["message_create"]["message_data"]["text"])
 source = "DM"
 sender = session.get_user(item["message_create"]["sender_id"])
 if db["user_name"] == sender["screen_name"]:
  if show_screen_names:
   user = _(u"Dm to %s ") % (session.get_user(item["message_create"]["target"]["recipient_id"])["screen_name"])
  else:
   user = _(u"Dm to %s ") % (session.get_user(item["message_create"]["target"]["recipient_id"])["name"])
 else:
  if show_screen_names:
   user = sender["screen_name"]
  else:
   user = sender["name"]
 if text[-1] in chars: text=text+"."
 urls = utils.find_urls_in_text(text)
 for url in range(0, len(urls)):
  try:  text = text.replace(urls[url], item["message_create"]["message_data"]["entities"]["urls"][url]["expanded_url"])
  except IndexError: pass
 return [user+", ", text, ts+", ", source]

def compose_quoted_tweet(quoted_tweet, original_tweet, show_screen_names=False, session=None):
 """ It receives a tweet and returns a list with the user, text for the tweet or message, date and the client where user is."""
 if quoted_tweet.has_key("retweeted_status"):
  if quoted_tweet["retweeted_status"].has_key("full_text"):
   value = "full_text"
  else:
   value = "text"
  text = StripChars(quoted_tweet["retweeted_status"][value])
 else:
  if quoted_tweet.has_key("full_text"):
   value = "full_text"
  else:
   value = "text"
  text = StripChars(quoted_tweet[value])
 if show_screen_names:
  quoting_user = quoted_tweet["user"]["screen_name"]
 else:
  quoting_user = quoted_tweet["user"]["name"]
 source = re.sub(r"(?s)<.*?>", "", quoted_tweet["source"])
 if quoted_tweet.has_key("retweeted_status"):
  text = "rt @%s: %s" % (quoted_tweet["retweeted_status"]["user"]["screen_name"], text)
 if text[-1] in chars: text=text+"."
 original_user = original_tweet["user"]["screen_name"]
 if original_tweet.has_key("message"):
  original_text = original_tweet["message"]
 elif original_tweet.has_key("full_text"):
  original_text = StripChars(original_tweet["full_text"])
 else:
   original_text = StripChars(original_tweet["text"])
 quoted_tweet["message"] = _(u"{0}. Quoted  tweet from @{1}: {2}").format( text, original_user, original_text)
 quoted_tweet = tweets.clear_url(quoted_tweet)
 quoted_tweet["entities"]["urls"].extend(original_tweet["entities"]["urls"])
 return quoted_tweet

def compose_followers_list(tweet, db, relative_times=True, show_screen_names=False, session=None):
 if system == "Windows":
  original_date = arrow.get(tweet["created_at"], "ddd MMM D H:m:s Z YYYY", locale="en")
  if relative_times == True:
   ts = original_date.humanize(locale=languageHandler.getLanguage())
  else:
   ts = original_date.replace(seconds=db["utc_offset"]).format(_(u"dddd, MMMM D, YYYY H:m:s"), locale=languageHandler.getLanguage())
 else:
  ts = tweet["created_at"]
 if tweet.has_key("status"):
  if len(tweet["status"]) > 4 and system == "Windows":
   original_date2 = arrow.get(tweet["status"]["created_at"], "ddd MMM D H:m:s Z YYYY", locale="en")
   if relative_times:
    ts2 = original_date2.humanize(locale=languageHandler.getLanguage())
   else:
    ts2 = original_date2.replace(seconds=db["utc_offset"]).format(_(u"dddd, MMMM D, YYYY H:m:s"), locale=languageHandler.getLanguage())
  else:
   ts2 = _("Unavailable")
 else:
  ts2 = _("Unavailable")
 return [_(u"%s (@%s). %s followers, %s friends, %s tweets. Last tweeted %s. Joined Twitter %s") % (tweet["name"], tweet["screen_name"], tweet["followers_count"], tweet["friends_count"],  tweet["statuses_count"], ts2, ts)]

def compose_list(list):
 name = list["name"]
 if list["description"] == None: description = _(u"No description available")
 else: description = list["description"]
 user = list["user"]["name"]
 members = str(list["member_count"])
 if list["mode"] == "private": status = _(u"private")
 else: status = _(u"public")
 return [name, description, user, members, status]
