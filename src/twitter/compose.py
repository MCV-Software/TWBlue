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

def compose_tweet(tweet, db, relative_times, show_screen_names=False):
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
   ts = original_date.replace(seconds=db["utc_offset"]).format(_(u"dddd, MMMM D, YYYY H:m:s"), locale=languageHandler.getLanguage())
 else:
  ts = tweet["created_at"]
 text = StripChars(tweet["text"])
 source = "DM"
 if db["user_name"] == tweet["sender"]["screen_name"]:
  if show_screen_names:
   user = _(u"Dm to %s ") % (tweet["recipient"]["screen_name"],)
  else:
   user = _(u"Dm to %s ") % (tweet["recipient"]["name"],)
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
 try: text = "rt @%s: %s" % (quoted_tweet["retweeted_status"]["user"]["screen_name"], StripChars(quoted_tweet["retweeted_status"][value]))
 except KeyError: text = "%s" % (StripChars(quoted_tweet[value]))
 if text[-1] in chars: text=text+"."
 original_user = original_tweet["user"]["screen_name"]
 if original_tweet.has_key("message"):
  original_text = StripChars(original_tweet["message"])
 elif original_tweet.has_key("full_text"):
  original_text = StripChars(original_tweet["full_text"])
 else:
   original_text = StripChars(original_tweet["text"])
 quoted_tweet["message"] = _(u"{0}. Quoted  tweet from @{1}: {2}").format( quoted_tweet[value], original_user, original_text)
 quoted_tweet = tweets.clear_url(quoted_tweet)
 quoted_tweet["entities"]["urls"].extend(original_tweet["entities"]["urls"])
 return quoted_tweet

def compose_followers_list(tweet, db, relative_times=True, show_screen_names=False):
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

def compose_event(data, username, show_screen_names=False):
 if show_screen_names:
  value = "screen_name"
 else:
  value = "name"
 if data["event"] == "block":
  event = _("You've blocked %s") % (data["target"][value])
 elif data["event"] == "unblock":
  event = _(u"You've unblocked %s") % (data["target"][value])
 elif data["event"] == "follow":
  if data["target"]["screen_name"] == username:
   event = _(u"%s(@%s) has followed you") % (data["source"]["name"], data["source"]["screen_name"])
  elif data["source"]["screen_name"] == username:
   event = _(u"You've followed %s(@%s)") % (data["target"]["name"], data["target"]["screen_name"])
 elif data["event"] == "unfollow":
  event = _(u"You've unfollowed %s (@%s)") % (data["target"]["name"], data["target"]["screen_name"])
 elif data["event"] == "favorite":
  if data["source"]["screen_name"] == username:
   event = _(u"You've liked: %s, %s") % (data["target"][value], data["target_object"]["text"])
  else:
   event = _(u"%s(@%s) has liked: %s") % (data["source"]["name"], data["source"]["screen_name"], data["target_object"]["text"])
 elif data["event"] == "unfavorite":
  if data["source"]["screen_name"] == username: event = _(u"You've unliked: %s, %s") % (data["target"][value], data["target_object"]["text"])
  else: event = _(u"%s(@%s) has unliked: %s") % (data["source"]["name"], data["source"]["screen_name"], data["target_object"]["text"])
 elif data["event"] == "list_created":
  event = _(u"You've created the list %s") % (data["target_object"]["name"])
 elif data["event"] == "list_destroyed":
  event = _("You've deleted the list %s") % (data["target_object"]["name"])
 elif data["event"] == "list_updated":
  event = _("You've updated the list %s") % (data["target_object"]["name"])
 elif data["event"] == "list_member_added":
  if data["source"]["screen_name"] == username: event = _(u"You've added %s(@%s) to the list %s") % (data["target"]["name"], data["target"]["screen_name"], data["target_object"]["name"])
  else: event = _(u"%s(@%s) has added you to the list %s") % (data["source"]["name"], data["source"]["screen_name"], data["target_object"]["name"])
 elif data["event"] == "list_member_removed":
  if data["source"]["screen_name"] == username: event = _(u"You'be removed %s(@%s) from the list %s") % (data["target"]["name"], data["target"]["screen_name"], data["target_object"]["name"])
  else: event = _(u"%s(@%s) has removed you from the list %s") % (data["source"]["name"], data["source"]["screen_name"], data["target_object"]["name"])
 elif data["event"] == "list_user_subscribed":
  if data["source"]["screen_name"] == username: event = _(u"You've subscribed to the list %s, which is owned by %s(@%s)") % (data["target_object"]["name"], data["target"]["name"], data["target"]["screen_name"])
  else: event = _(u"%s(@%s) has subscribed you to the list %s") % (data["source"]["name"], data["source"]["screen_name"], data["target_object"]["name"])
 elif data["event"] == "list_user_unsubscribed":
  if data["source"]["screen_name"] == username: event = _(u"You've unsubscribed from the list %s, which is owned by %s(@%s)") % (data["target_object"]["name"], data["target"]["name"], data["target"]["screen_name"])
  else: event = _("You've been unsubscribed from the list %s, which is owned by %s(@%s)") % (data["target_object"]["name"], data["source"]["name"], data["source"]["screen_name"])
 elif data["event"] == "retweeted_retweet":
  if data["source"]["screen_name"] == username: event = _(u"You have retweeted a retweet from %s(@%s): %s") % (data["target"]["name"], data["target"]["screen_name"], data["target_object"]["retweeted_status"]["text"])
  else: event = _(u"%s(@%s) has retweeted your retweet: %s") % (data["source"]["name"], data["source"]["screen_name"], data["target_object"]["retweeted_status"]["text"])
 elif data["event"] == "quoted_tweet":
   event = _(u"@{0} quoted your tweet: {1}").format(data["source"]["screen_name"], data["target_object"]["text"])
 else:
  event = _("Unknown")
  log.error("event: %s\n target: %s\n source: %s\n target_object: %s" % (data["event"], data["target"], data["source"], data["target_object"]))
 return [time.strftime("%I:%M %p"), event]

def compose_list(list):
 name = list["name"]
 if list["description"] == None: description = _(u"No description available")
 else: description = list["description"]
 user = list["user"]["name"]
 members = str(list["member_count"])
 if list["mode"] == "private": status = _(u"private")
 else: status = _(u"public")
 return [name, description, user, members, status]
