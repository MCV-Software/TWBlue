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
from long_tweets import twishort
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

def compose_tweet(tweet, db, relative_times):
 """ It receives a tweet and returns a list with the user, text for the tweet or message, date and the client where user is."""
 long = twishort.is_long(tweet)
 if long != False:
  tweet["long_uri"] = long
 if system == "Windows":
  original_date = arrow.get(tweet["created_at"], "ddd MMM DD H:m:s Z YYYY", locale="en")
  if relative_times == True:
   ts = original_date.humanize(locale=languageHandler.getLanguage())
  else:
   ts = original_date.replace(seconds=db["utc_offset"]).format(_(u"dddd, MMMM D, YYYY H:m:s"), locale=languageHandler.getLanguage())
 else:
  ts = tweet["created_at"]
 text = StripChars(tweet["text"])
 if tweet.has_key("sender"):
  source = "DM"
  if db["user_name"] == tweet["sender"]["screen_name"]: user = _(u"Dm to %s ") % (tweet["recipient"]["name"],)
  else: user = tweet["sender"]["name"]
 elif tweet.has_key("user"):
  user = tweet["user"]["name"]
  source = re.sub(r"(?s)<.*?>", "", tweet["source"])
  try: text = "rt @%s: %s" % (tweet["retweeted_status"]["user"]["screen_name"], StripChars(tweet["retweeted_status"]["text"]))
  except KeyError: text = "%s" % (StripChars(tweet["text"]))
  if text[-1] in chars: text=text+"."
 urls = utils.find_urls_in_text(text)
 for url in range(0, len(urls)):
  try:  text = text.replace(urls[url], tweet["entities"]["urls"][url]["expanded_url"])
  except IndexError: pass
 tweet["text"] = text
 return [user+", ", tweet["text"], ts+", ", source]

def compose_followers_list(tweet, db, relative_times=True):
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

def compose_event(data, username):
 if data["event"] == "block":
  event = _("You've blocked %s") % (data["target"]["name"])
 elif data["event"] == "unblock":
  event = _(u"You've unblocked %s") % (data["target"]["name"])
 elif data["event"] == "follow":
  if data["target"]["screen_name"] == username:
   event = _(u"%s(@%s) has followed you") % (data["source"]["name"], data["source"]["screen_name"])
  elif data["source"]["screen_name"] == username:
   event = _(u"You've followed %s(@%s)") % (data["target"]["name"], data["target"]["screen_name"])
 elif data["event"] == "unfollow":
  event = _(u"You've unfollowed %s (@%s)") % (data["target"]["name"], data["target"]["screen_name"])
 elif data["event"] == "favorite":
  if data["source"]["screen_name"] == username:
   event = _(u"You've added to favourites: %s, %s") % (data["target"]["name"], data["target_object"]["text"])
  else:
   event = _(u"%s(@%s) has marked as favourite: %s") % (data["source"]["name"], data["source"]["screen_name"], data["target_object"]["text"])
 elif data["event"] == "unfavorite":
  if data["source"]["screen_name"] == username: event = _(u"You've removed from favourites: %s, %s") % (data["target"]["name"], data["target_object"]["text"])
  else: event = _(u"%s(@%s) has removed from favourites: %s") % (data["source"]["name"], data["source"]["screen_name"], data["target_object"]["text"])
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
  else: event = _(u"%s(@%s) has suscribed you to the list %s") % (data["source"]["name"], data["source"]["screen_name"], data["target_object"]["name"])
 elif data["event"] == "list_user_unsubscribed":
  if data["source"]["screen_name"] == username: event = _(u"You've unsubscribed from the list %s, which is owned by %s(@%s)") % (data["target_object"]["name"], data["target"]["name"], data["target"]["screen_name"])
  else: event = _("You've been unsubscribed from the list %s, which is owned by %s(@%s)") % (data["target_object"]["name"], data["source"]["name"], data["source"]["screen_name"])
 elif data["event"] == "retweeted_retweet":
  if data["source"]["screen_name"] == username: event = _(u"You have retweeted a retweet from %s(@%s): %s" % (data["target"]["name"], data["target"]["screen_name"], data["target_object"]["text"]))
  else: event = _(u"%s(@%s) has retweeted your retweet: %s" % (data["source"]["name"], data["source"]["screen_name"], data["target_object"]["text"]))
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
