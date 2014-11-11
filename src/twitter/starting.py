# -*- config: utf-8 -*-
from twython import Twython, TwythonError
import config
#import sound
import time
import utils

friends_cursor = followers_cursor = None

def get_more_items(update_function, twitter_object, users=False, name=None, *args, **kwargs):
 results = []
 data = update_function(*args, **kwargs)
 if users == True:
  global friends_cursor, followers_cursor
  if name == "friends":
   friends_cursor = data["next_cursor"]
  elif name == "followers":
   followers_cursor = data["next_cursor"]
  for i in data["users"]: results.append(i)
 else:
  results.extend(data[1:])
 return results

def call_paged(update_function, twitter_object, *args, **kwargs):
 max = int(config.main["general"]["max_api_calls"])-1
 results = []
 data = update_function(*args, **kwargs)
 results.extend(data)
 for i in range(0, max):
  if i == 0: max_id = results[-1]["id"]
  else: max_id = results[0]["id"]
  data = update_function(max_id=max_id, *args, **kwargs)
  results.extend(data)
 results.reverse()
 return results

def start_user_info(config, twitter):
 f = twitter.twitter.get_account_settings()
 sn = f["screen_name"]
 config.settings["user_name"] = sn
 config.settings["user_id"] = twitter.twitter.show_user(screen_name=sn)["id_str"]
 try:
  config.settings["utc_offset"] = f["time_zone"]["utc_offset"]
 except KeyError:
  config.settings["utc_offset"] = -time.timezone
 get_lists(config, twitter)
 get_muted_users(config, twitter)

def get_lists(config, twitter):
 config.settings["lists"] = twitter.twitter.show_lists(reverse=True)

def get_muted_users(config, twitter):
 config.settings["muted_users"] = twitter.twitter.get_muted_users_ids()["ids"]

def start_stream(db, twitter, name, function, param=None):
 num = 0
 if db.settings.has_key(name):
  try:
   if db.settings[name][0]["id"] > db.settings[name][-1]["id"]:
    last_id = db.settings[name][0]["id"]
   else:
    last_id = db.settings[name][-1]["id"]
  except IndexError:
   pass
  if param != None:
   tl = call_paged(function, twitter, sinze_id=last_id, screen_name=param, count=config.main["general"]["max_tweets_per_call"])
  else:
   tl = call_paged(function, twitter, sinze_id=last_id, count=config.main["general"]["max_tweets_per_call"])
 else:
  if param != None:
   tl = call_paged(function, twitter,  screen_name=param, count=config.main["general"]["max_tweets_per_call"])
  else:
   tl = call_paged(function, twitter, count=config.main["general"]["max_tweets_per_call"])
  db.settings[name] = []
  last_id = 0
 if len(db.settings[name]) > 0:
  for i in tl:
   if int(i["id"]) > int(last_id):
    if config.main["general"]["reverse_timelines"] == False: db.settings[name].append(i)
    else: db.settings[name].insert(0, i)
    num = num+1
 elif len(db.settings[name]) == 0:
  for i in tl:
   if config.main["general"]["reverse_timelines"] == False: db.settings[name].append(i)
   else: db.settings[name].insert(0, i)
   num = num+1
# db.settings.update()
 return num

def start_followers(db, twitter, name, function, param=None):
 global friends_cursor, followers_cursor
 num = 0
 db.settings[name] = []
# next_cursor = -1
# while(next_cursor):
 tl = function(screen_name=param, count=config.main["general"]["max_tweets_per_call"])
 for i in tl['users']:
  if config.main["general"]["reverse_timelines"] == False: db.settings[name].append(i)
  else: db.settings[name].insert(0, i)
  num = num+1
#  next_cursor = tl["next_cursor"]
 db.settings[name].reverse()
# if config.main["streams"]["reverse_timelines"] == True: db.settings[name].reverse()
 if name == "followers": followers_cursor = tl["next_cursor"]
 elif name == "friends": friends_cursor = tl["next_cursor"]
 return num

def get_users_list(twitter, list_id):
 answers = []
 next_cursor = -1
 while(next_cursor):
  users = twitter.twitter.get_list_members(list_id=list_id, cursor=next_cursor, include_entities=False, skip_status=True)
  for i in users['users']:
   answers.append(i["id"])
  next_cursor = users["next_cursor"]
 return answers

def update_stream(config, twitter, name, function, param=None, sndFile=""):
 num = 0
 sounded = False
 tl = function(sinze_id=config.settings[name][-1]["id"], screen_name=param, count=config.main["general"]["max_tweets_per_call"])
 tl.reverse()
 for i in tl:
  if i["id"] > config.settings[name][-1]["id"]:
   config.settings[name].append(i)
   sounded = True
   num = num+1
 if sounded == True:
  sound.play(sndFile)
 return num

def start_sent(db, twitter, name, function, param=None):
 num = 0
 if db.settings.has_key(name):
  try:
   if db.settings[name][0]["id"] > db.settings[name][-1]["id"]:
    last_id = db.settings[name][0]["id"]
   else:
    last_id = db.settings[name][-1]["id"]
  except IndexError:
   return 0
  if param != None:
   tl = function(sinze_id=last_id, screen_name=param, count=config.main["general"]["max_tweets_per_call"])
   tl2 = twitter.twitter.get_sent_messages(sinze_id=last_id, count=config.main["general"]["max_tweets_per_call"])
  else:
   tl = function(sinze_id=last_id, count=config.main["general"]["max_tweets_per_call"])
   tl2 = twitter.twitter.get_sent_messages(sinze_id=last_id, count=config.main["general"]["max_tweets_per_call"])
 else:
  if param != None:
   tl = function(screen_name=param, count=config.main["general"]["max_tweets_per_call"])
   tl2 = twitter.twitter.get_sent_messages(count=config.main["general"]["max_tweets_per_call"])
  else:
   tl = function(count=config.main["general"]["max_tweets_per_call"])
   tl2 = twitter.twitter.get_sent_messages(sinze_id=last_id, count=config.main["general"]["max_tweets_per_call"])
  db.settings[name] = []
  last_id = 0
 tl.extend(tl2)
# tl.reverse()
 tl.sort(key=lambda tup: tup["id"]) 
 if len(db.settings[name]) > 0:
  for i in tl:
#   print last_id, i["id"]
   if int(i["id"]) > int(last_id):
    if config.main["general"]["reverse_timelines"] == False: db.settings[name].append(i)
    else: db.settings[name].insert(0, i)
    num = num+1
 elif len(db.settings[name]) == 0:
  for i in tl:
   if config.main["general"]["reverse_timelines"] == False: db.settings[name].append(i)
   else: db.settings[name].insert(0, i)
   num = num+1
 return num

def start_list(db, twitter, name, list_id):
 num = 0
 if db.settings.has_key(name):
  try:
   if db.settings[name][0]["id"] > db.settings[name][-1]["id"]:
    last_id = db.settings[name][0]["id"]
   else:
    last_id = db.settings[name][-1]["id"]
  except IndexError:
   pass
  tl = twitter.twitter.get_list_statuses(list_id=list_id, count=200)
 else:
  tl = twitter.twitter.get_list_statuses(list_id=list_id, count=200)
  tl.reverse()
  db.settings[name] = []
  last_id = 0
 if len(db.settings[name]) > 0:
  for i in tl:
   if int(i["id"]) > int(last_id):
    if config.main["general"]["reverse_timelines"] == False: db.settings[name].append(i)
    else: db.settings[name].insert(0, i)
    num = num+1
 elif len(db.settings[name]) == 0:
  for i in tl:
   if config.main["general"]["reverse_timelines"] == False: db.settings[name].append(i)
   else: db.settings[name].insert(0, i)
   num = num+1
 db.settings.update()
 return num

def search(db, twitter, name, *args, **kwargs):
 num = 0
 if db.settings.has_key(name) == False:
  db.settings[name] = []
 tl = twitter.twitter.search(*args, **kwargs)
 tl["statuses"].reverse()
 if len(db.settings[name]) > 0:
  for i in tl["statuses"]:
   if utils.find_item(i["id"], db.settings[name]) == None:
    if config.main["general"]["reverse_timelines"] == False: db.settings[name].append(i)
    else: db.settings[name].insert(0, i)
    num = num+1
 elif len(db.settings[name]) == 0:
  for i in tl["statuses"]:
   if config.main["general"]["reverse_timelines"] == False: db.settings[name].append(i)
   else: db.settings[name].insert(0, i)
   num = num+1
 return num

def search_users(db, twitter, name, *args, **kwargs):
 num = 0
 if db.settings.has_key(name) == False:
  db.settings[name] = []
 tl = twitter.twitter.search_users(*args, **kwargs)
 tl.reverse()
 if len(db.settings[name]) > 0:
  for i in tl:
   if utils.find_item(i["id"], db.settings[name]) == None:
    if config.main["general"]["reverse_timelines"] == False: db.settings[name].append(i)
    else: db.settings[name].insert(0, i)
    num = num+1
 elif len(db.settings[name]) == 0:
  for i in tl:
   if config.main["general"]["reverse_timelines"] == False: db.settings[name].append(i)
   else: db.settings[name].insert(0, i)
   num = num+1
 return num

def get_favourites_timeline(db, twitter, name, param, *args, **kwargs):
 num = 0
 if db.settings.has_key(name) == False:
  db.settings[name] = []
 tl = twitter.twitter.get_favorites(screen_name=param, *args, **kwargs)
 tl.reverse()
 if len(db.settings[name]) > 0:
  for i in tl:
   if utils.find_item(i["id"], db.settings[name]) == None:
    if config.main["general"]["reverse_timelines"] == False: db.settings[name].append(i)
    else: db.settings[name].insert(0, i)
    num = num+1
 elif len(db.settings[name]) == 0:
  for i in tl:
   if config.main["general"]["reverse_timelines"] == False: db.settings[name].append(i)
   else: db.settings[name].insert(0, i)
   num = num+1
 return num