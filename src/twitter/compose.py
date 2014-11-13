# -*- coding: utf-8 -*-
import utils
import re
import htmlentitydefs
import datetime
import time
import output
import gettext, paths, locale, gettext_windows
import platform
system = platform.system()

def prettydate(d):
 """ Converts a string to the relative time."""
 diff = datetime.datetime.utcnow() - d
 s = diff.seconds
 if diff.days > 7 and diff.days < 14:
  return _(u"About a week ago")
 elif diff.days > 14 and diff.days < 31:
  return _(u"About {} weeks ago").format(diff.days/7)
 elif diff.days > 31 and diff.days <= 62:
  return _(u"A month ago")
 elif diff.days >62 and diff.days <= 365:
  return _(u"About {} months ago").format(diff.days/30)
 elif diff.days > 365 and diff.days <= 730:
  return _(u"About a year ago")
 elif diff.days > 730:
  return _(u"About {} years ago").format(diff.days/365)
 elif diff.days == 1:
  return _(u"About 1 day ago")
 elif diff.days > 1:
  return _(u"About {} days ago").format(diff.days)
 elif s <= 1:
  return _(u"just now")
 elif s < 60:
  return _(u"{} seconds ago").format(s)
 elif s < 120:
  return _(u"1 minute ago")
 elif s < 3600:
  return _(u"{} minutes ago").format(s/60)
 elif s < 7200:
  return _(u"About 1 hour ago")
 else:
  return _(u"About {} hours ago").format(s/3600)

# Months, days, short_months and short_days are used to translate the string that Twitter gives to us with the date and time.
months = {
"January": _(u"January"),
"February": _(u"February"),
"March": _(u"March"),
"April": _(u"April"),
"May": _(u"May"),
"June": _(u"June"),
"July": _(u"July"),
"August": _(u"August"),
"September": _(u"September"),
"October": _(u"October"),
"November": _(u"November"),
"December": _(u"December"),
}

days = {"Sunday": _(u"Sunday"),
"Monday": _(u"Monday"),
"Tuesday": _(u"Tuesday"),
"Wednesday": _(u"Wednesday"),
"Thursday": _(u"Thursday"),
"Friday": _(u"Friday"),
"Saturday": _(u"Saturday")}

short_days = {
	"Sun": _(u"sun"),
	"Mon": _(u"mon"),
	"Tue": _(u"tue"),
	"Wed": _(u"wed"),
	"Thu": _(u"thu"),
	"Fri": _(u"fri"),
	"Sat": _(u"sat")
	}

short_months = {
	"Jan": _(u"jan"),
	"Feb": _(u"feb"),
	"Mar": _(u"mar"),
	"Apr": _(u"apr"),
	"May": _(u"may"),
	"Jun": _(u"jun"),
	"Jul": _(u"jul"),
	"Aug": _(u"aug"),
	"Sep": _(u"sep"),
	"Oct": _(u"oct"),
	"Nov": _(u"nov"),
	"Dec": _(u"dec")}

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

def translate(string):
 """ Changes the days in English for the current language. Needed for Windows."""
 if system != "Windows": return string
 else:
  global months, days
  for d in months:
   string = string.replace(d, months[d])
  for d in days:
   string = string.replace(d, days[d])
  return string

def translate_short(string):
 """ Changes the English date from Twitter to a local date and time. Needed for datetime on Linux."""
 if system != "Linux": return string
 else:
# if 1 == 1:
  global short_months, short_days
  for d in short_months:
   string = string.replace(d, short_months[d])
  for d in short_days:
   string = string.replace(d, short_days[d])
  return string

chars = "abcdefghijklmnopqrstuvwxyz"

def compose_tweet(tweet, db, relative_times):
 """ It receives a tweet and returns a list with the user, text for the tweet or message, date and the client where user is."""
# original_date = datetime.datetime.strptime(translate_short(tweet["created_at"]).encode("utf-8"), "%a %b %d %H:%M:%S +0000 %Y")
 original_date = datetime.datetime.strptime(tweet["created_at"], "%a %b %d %H:%M:%S +0000 %Y")
# else:
#  original_date = datetime.datetime.strptime(tweet["created_at"], '%a %b %d %H:%M:%S +0000 %Y')
 date = original_date-datetime.timedelta(seconds=-db["utc_offset"])
 if relative_times == True:
  ts = prettydate(original_date)
 else:
#  ts = translate(datetime.datetime.strftime(date, _("%A, %B %d, %Y at %I:%M:%S %p".encode("utf-8"))).decode("utf-8"))
  ts = translate(datetime.datetime.strftime(date, _("%A, %B %d, %Y at %I:%M:%S %p")))
# ts = tweet["created_at"]
 text = StripChars(tweet["text"])
 if tweet.has_key("sender"):
  source = "DM"
  if db["user_name"] == tweet["sender"]["screen_name"]: user = _(u"Dm to %s ") % (tweet["recipient"]["name"],)
  else: user = tweet["sender"]["name"]
 elif tweet.has_key("user"):
  user = tweet["user"]["name"]
  source = re.sub(r"(?s)<.*?>", " ", tweet["source"])
  try: text = "rt @%s: %s" % (tweet["retweeted_status"]["user"]["screen_name"], StripChars(tweet["retweeted_status"]["text"]))
  except KeyError: text = "%s" % (StripChars(tweet["text"]))
  if text[-1] in chars: text=text+"."
 urls = utils.find_urls_in_text(text)
 for url in range(0, len(urls)):
  try:  text = text.replace(urls[url], tweet["entities"]["urls"][url]["expanded_url"])
  except IndexError: pass
 tweet["text"] = text
 return [user+", ", text, ts+", ", source]

def compose_followers_list(tweet, db, relative_time=True):
# original_date = datetime.datetime.strptime(translate_short(tweet["created_at"]).encode("utf-8"), '%a %b %d %H:%M:%S +0000 %Y')
 original_date = datetime.datetime.strptime(tweet["created_at"], '%a %b %d %H:%M:%S +0000 %Y')
 date = original_date-datetime.timedelta(seconds=-db["utc_offset"])
 if relative_time == True:
  ts = prettydate(original_date)
 else:
  ts = translate(datetime.datetime.strftime(date, _(u"%A, %B %d, %Y at %I:%M:%S %p")))
# ts = tweet["created_at"]
 if tweet.has_key("status"):
  if len(tweet["status"]) > 4:
#   original_date2 = datetime.datetime.strptime(translate_short(tweet["status"]["created_at"]).encode("utf-8"), '%a %b %d %H:%M:%S +0000 %Y')
   original_date2 = datetime.datetime.strptime(tweet["status"]["created_at"], '%a %b %d %H:%M:%S +0000 %Y')
   date2 = original_date2-datetime.timedelta(seconds=-db["utc_offset"])
   if relative_time == True:
    ts2 = prettydate(original_date2)
   else:
    ts2 = translate(datetime.datetime.strftime(date2, _(u"%A, %B %d, %Y at %I:%M:%S %p")))
 else:
  ts2 = _("Unavailable")
 return [_(u"%s (@%s). %s followers, %s friends, %s tweets. Last tweet on %s. Joined Twitter on %s") % (tweet["name"], tweet["screen_name"], tweet["followers_count"], tweet["friends_count"],  tweet["statuses_count"], ts2, ts)]

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
   event = _(u"%s(@%s) has marked as favorite: %s") % (data["source"]["name"], data["source"]["screen_name"], data["target_object"]["text"])
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
 else: event = _("Unknown")
# output.speak(event)
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
