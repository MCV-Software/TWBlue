# -*- coding: utf-8 -*-
""" This is the main session needed to access all Twitter Features."""
from __future__ import absolute_import
from __future__ import unicode_literals
from builtins import range
import os
import time
import logging
import webbrowser
import wx
import config
import output
import application
from pubsub import pub
from twython import Twython
import tweepy
from mysc.thread_utils import call_threaded
from keys import keyring
from sessions import base
from sessions.twitter import utils, compose
from sessions.twitter.long_tweets import tweets, twishort
from .wxUI import authorisationDialog

log = logging.getLogger("sessions.twitterSession")

class Session(base.baseSession):
 """ A session object where we will save configuration, the twitter object and a local storage for saving the items retrieved through the Twitter API methods"""

 def order_buffer(self, name, data, ignore_older=True):
  """ Put new items in the local database.
  name str: The name for the buffer stored in the dictionary.
  data list: A list with tweets.
  ignore_older bool: if set to True, items older than the first element on the list will be ignored.
  returns the number of items that have been added in this execution"""
  num = 0
  last_id = None
  if (name in self.db) == False:
   self.db[name] = []
  if ("users" in self.db) == False:
   self.db["users"] = {}
  if ignore_older and len(self.db[name]) > 0:
   if self.settings["general"]["reverse_timelines"] == False:
    last_id = self.db[name][0].id
   else:
    last_id = self.db[name][-1].id
  for i in data:
   if ignore_older and last_id != None:
    if i.id < last_id:
     log.error("Ignoring an older tweet... Last id: {0}, tweet id: {1}".format(last_id, i.id))
     continue
   if utils.find_item(i.id, self.db[name]) == None and     utils.is_allowed(i, self.settings, name) == True:
    i = self.check_quoted_status(i)
    i = self.check_long_tweet(i)
    if i == False: continue
    if self.settings["general"]["reverse_timelines"] == False: self.db[name].append(i)
    else: self.db[name].insert(0, i)
    num = num+1
    if hasattr(i, "user"):
     if (i.user.id in self.db["users"]) == False:
      self.db["users"][i.user.id] = i.user
  return num

 def order_cursored_buffer(self, name, data):
  """ Put new items on the local database. Useful for cursored buffers (followers, friends, users of a list and searches)
  name str: The name for the buffer stored in the dictionary.
  data list: A list with items and some information about cursors.
  returns the number of items that have been added in this execution"""
  # Direct messages should be added to db in other function.
  # Because they will be populating two buffers with one endpoint.
  if name == "direct_messages":
   return self.order_direct_messages(data)
  num = 0
  if (name in self.db) == False:
   self.db[name] = {}
   self.db[name]["items"] = []
  for i in data:
   if utils.find_item(i.id, self.db[name]["items"]) == None:
    if self.settings["general"]["reverse_timelines"] == False: self.db[name]["items"].append(i)
    else: self.db[name]["items"].insert(0, i)
    num = num+1
  return num

 def order_direct_messages(self, data):
  """ Add incoming and sent direct messages to their corresponding database items.
  data list: A list of direct messages to add.
  returns the number of incoming messages processed in this execution, and sends an event with data regarding amount of sent direct messages added."""
  incoming = 0
  sent = 0
  if ("direct_messages" in self.db) == False:
   self.db["direct_messages"] = {}
   self.db["direct_messages"]["items"] = []
  for i in data:
   if i.message_create.sender_id == self.db["user_id"]:
    if "sent_direct_messages" in self.db and utils.find_item(i.id, self.db["sent_direct_messages"]["items"]) == None:
     if self.settings["general"]["reverse_timelines"] == False: self.db["sent_direct_messages"]["items"].append(i)
     else: self.db["sent_direct_messages"]["items"].insert(0, i)
     sent = sent+1
   else:
    if utils.find_item(i.id, self.db["direct_messages"]["items"]) == None:
     if self.settings["general"]["reverse_timelines"] == False: self.db["direct_messages"]["items"].append(i)
     else: self.db["direct_messages"]["items"].insert(0, i)
     incoming = incoming+1
  pub.sendMessage("sent-dms-updated", total=sent, account=self.db["user_name"])
  return incoming

 def __init__(self, *args, **kwargs):
  super(Session, self).__init__(*args, **kwargs)
  self.reconnection_function_active = False
  self.counter = 0
  self.lists = []

# @_require_configuration
 def login(self, verify_credentials=True):
  """ Log into twitter using  credentials from settings.
  if the user account isn't authorised, it needs to call self.authorise() before login."""
  if self.settings["twitter"]["user_key"] != None and self.settings["twitter"]["user_secret"] != None:
   try:
    log.debug("Logging in to twitter...")
    self.auth = tweepy.OAuthHandler(keyring.get("api_key"), keyring.get("api_secret"))
    self.auth.set_access_token(self.settings["twitter"]["user_key"], self.settings["twitter"]["user_secret"])
    self.twitter = tweepy.API(self.auth)
    if verify_credentials == True:
     self.credentials = self.twitter.verify_credentials()
    self.logged = True
    log.debug("Logged.")
    self.counter = 0
   except IOError:
    log.error("The login attempt failed.")
    self.logged = False
  else:
   self.logged = False
   raise Exceptions.RequireCredentialsSessionError

# @_require_configuration
 def authorise(self):
  """ Authorises a Twitter account. This function needs to be called for each new session, after self.get_configuration() and before self.login()"""
  if self.logged == True:
   raise Exceptions.AlreadyAuthorisedError("The authorisation process is not needed at this time.")
  else:
   self.auth = tweepy.OAuthHandler(keyring.get("api_key"), keyring.get("api_secret"))
   redirect_url = self.auth.get_authorization_url()
   webbrowser.open_new_tab(redirect_url)
   self.authorisation_dialog = authorisationDialog()
   self.authorisation_dialog.cancel.Bind(wx.EVT_BUTTON, self.authorisation_cancelled)
   self.authorisation_dialog.ok.Bind(wx.EVT_BUTTON, self.authorisation_accepted)
   self.authorisation_dialog.ShowModal()

 def verify_authorisation(self, pincode):
  self.auth.get_access_token(pincode)
  self.settings["twitter"]["user_key"] = self.auth.access_token
  self.settings["twitter"]["user_secret"] = self.auth.access_token_secret
  self.settings.write()
  del self.auth

 def authorisation_cancelled(self, *args, **kwargs):
  """ Destroy the authorization dialog. """
  self.authorisation_dialog.Destroy()
  del self.authorisation_dialog 

 def authorisation_accepted(self, *args, **kwargs):
  """ Gets the PIN code entered by user and validate it through Twitter."""
  pincode = self.authorisation_dialog.text.GetValue()
  self.verify_authorisation(pincode)
  self.authorisation_dialog.Destroy()

 def get_more_items(self, update_function, users=False, dm=False, name=None, *args, **kwargs):
  """ Get more items for twitter objects.
  update_function str: function to call for getting more items. Must be member of self.twitter.
  users, dm bool: If any of these is set to True, the function will treat items as users or dm (they need different handling).
  name str: name of the database item to put new element in."""
  results = []
  if "cursor" in kwargs and kwargs["cursor"] == 0:
   output.speak(_(u"There are no more items to retrieve in this buffer."))
   return
  data = getattr(self.twitter, update_function)(*args, **kwargs)
  if users == True:
   if type(data) == dict and "next_cursor" in data:
    if "next_cursor" in data: # There are more objects to retrieve.
     self.db[name]["cursor"] = data["next_cursor"]
    else: # Set cursor to 0, wich means no more items available.
     self.db[name]["cursor"] = 0
    for i in data["users"]: results.append(i)
   elif type(data) == list:
    results.extend(data[1:])
  elif dm == True:
   if "next_cursor" in data: # There are more objects to retrieve.
    self.db[name]["cursor"] = data["next_cursor"]
   else: # Set cursor to 0, wich means no more items available.
    self.db[name]["cursor"] = 0
   for i in data["events"]: results.append(i)
  else:
   results.extend(data[1:])
  return results

 def api_call(self, call_name, action="", _sound=None, report_success=False, report_failure=True, preexec_message="", *args, **kwargs):
  """ Make a call to the Twitter API. If there is a connectionError or another exception not related to Twitter, It will call the method again at least 25 times, waiting a while between calls. Useful for  post methods.
  If twitter returns an error, it will not call the method anymore.
  call_name str: The method to call
  action str: What you are doing on twitter, it will be reported to the user if report_success is set to  True.
    for example "following @tw_blue2" will be reported as "following @tw_blue2 succeeded".
  _sound str: a sound to play if the call is executed properly.
  report_success and report_failure bool: These are self explanatory. True or False.
  preexec_message str: A message to speak to the user while the method is running, example: "trying to follow x user"."""
  finished = False
  tries = 0
  if preexec_message:
   output.speak(preexec_message, True)
  while finished==False and tries < 25:
   try:
    val = getattr(self.twitter, call_name)(*args, **kwargs)
    finished = True
   except TwythonError as e:
    output.speak(e.msg)
    val = None
    if e.error_code != 403 and e.error_code != 404:
     tries = tries+1
     time.sleep(5)
    elif report_failure and hasattr(e, 'message'):
     output.speak(_("%s failed.  Reason: %s") % (action, e.msg))
    finished = True
#   except:
#    tries = tries + 1
#    time.sleep(5)
  if report_success:
   output.speak(_("%s succeeded.") % action)
  if _sound != None: self.sound.play(_sound)
  return val

 def search(self, name, *args, **kwargs):
  """ Search in twitter, passing args and kwargs as arguments to the Twython function."""
  tl = self.twitter.search(*args, **kwargs)
  tl.reverse()
  return tl

# @_require_login
 def get_favourites_timeline(self, name, *args, **kwargs):
  """ Gets favourites for the authenticated user or a friend or follower.
  name str: Name for storage in the database.
  args and kwargs are passed directly to the Twython function."""
  tl = self.call_paged("favorites", *args, **kwargs)
  return self.order_buffer(name, tl)

 def call_paged(self, update_function, *args, **kwargs):
  """ Makes a call to the Twitter API methods several times. Useful for get methods.
  this function is needed for retrieving more than 200 items.
  update_function str: The function to call. This function must be child of self.twitter
  args and kwargs are passed to update_function.
  returns a list with all items retrieved."""
  max = 0
  results = []
  data = getattr(self.twitter, update_function)(count=self.settings["general"]["max_tweets_per_call"], *args, **kwargs)
  results.extend(data)
  for i in range(0, max):
   if i == 0: max_id = results[-1].id
   else: max_id = results[0].id
   data = getattr(self.twitter, update_function)(max_id=max_id, count=self.settings["general"]["max_tweets_per_call"], *args, **kwargs)
   results.extend(data)
  results.reverse()
  return results

# @_require_login
 def get_user_info(self):
  """ Retrieves some information required by TWBlue for setup."""
  f = self.twitter.get_settings()
  sn = f["screen_name"]
  self.settings["twitter"]["user_name"] = sn
  self.db["user_name"] = sn
  self.db["user_id"] = self.twitter.get_user(screen_name=sn).id
  try:
   self.db["utc_offset"] = f["time_zone"]["utc_offset"]
  except KeyError:
   self.db["utc_offset"] = -time.timezone
  # Get twitter's supported languages and save them in a global variable
  #so we won't call to this method once per session.
  if len(application.supported_languages) == 0:
   application.supported_languages = self.twitter.supported_languages
  self.get_lists()
  self.get_muted_users()
  self.settings.write()

# @_require_login
 def get_lists(self):
  """ Gets the lists that the user is subscribed to and stores them in the database. Returns None."""
  self.db["lists"] = self.twitter.lists_all(reverse=True)

# @_require_login
 def get_muted_users(self):
  """ Gets muted users (oh really?)."""
  self.db["muted_users"] = self.twitter.mutes_ids

# @_require_login
 def get_stream(self, name, function, *args, **kwargs):
  """ Retrieves the items for a regular stream.
  name str: Name to save items to the database.
  function str: A function to get the items."""
  last_id = -1
  if name in self.db:
   try:
    if self.db[name][0]["id"] > self.db[name][-1]["id"]:
     last_id = self.db[name][0]["id"]
    else:
     last_id = self.db[name][-1]["id"]
   except IndexError:
    pass
  tl = self.call_paged(function, sinze_id=last_id, *args, **kwargs)
  self.order_buffer(name, tl)

 def get_cursored_stream(self, name, function, items="users", get_previous=False, *args, **kwargs):
  """ Gets items for API calls that require using cursors to paginate the results.
  name str: Name to save it in the database.
  function str: Function that provides the items.
  items: When the function returns the list with results, items will tell how the order function should be look. for example get_followers_list returns a list and users are under list["users"], here the items should point to "users".
  get_previous bool: wether this function will be used to get previous items in a buffer or load the buffer from scratch.
  returns number of items retrieved."""
  items_ = []
  try:
   if "cursor" in self.db[name] and get_previous:
    cursor = self.db[name]["cursor"]
   else:
    cursor = -1
  except KeyError:
   cursor = -1
  if cursor != -1:
   tl = getattr(self.twitter, function)(cursor=cursor, count=self.settings["general"]["max_tweets_per_call"], *args, **kwargs)
  else:
   tl = getattr(self.twitter, function)(count=self.settings["general"]["max_tweets_per_call"], *args, **kwargs)
  tl[items].reverse()
  num = self.order_cursored_buffer(name, tl[items])
  # Recently, Twitter's new endpoints have cursor if there are more results.
  if "next_cursor" in tl:
   self.db[name]["cursor"] = tl["next_cursor"]
  else:
   self.db[name]["cursor"] = 0
  return num

 def check_connection(self):
  """ Restart the Twitter object every 5 executions. It is useful for dealing with requests timeout and other oddities."""
  log.debug("Executing check connection...")
  self.counter += 1
  if self.counter >= 4:
   log.debug("Restarting connection after 5 minutes.")
   del self.twitter
   self.logged = False
   self.login(False)
   self.counter = 0

 def check_quoted_status(self, tweet):
  """ Helper for get_quoted_tweet. Get a quoted status inside a tweet and create a special tweet with all info available.
  tweet dict: A tweet dictionary.
  Returns a quoted tweet or the original tweet if is not a quote"""
  status = tweets.is_long(tweet)
  if status != False and config.app["app-settings"]["handle_longtweets"]:
   quoted_tweet = self.get_quoted_tweet(tweet)
   return quoted_tweet
  return tweet

 def get_quoted_tweet(self, tweet):
  """ Process a tweet and extract all information related to the quote."""
  quoted_tweet = tweet
  if hasattr(tweet, "full_text"):
   value = "full_text"
  else:
   value = "text"
  setattr(quoted_tweet, value, utils.expand_urls(getattr(quoted_tweet, value), quoted_tweet.entities))
  if hasattr(quoted_tweet, "quoted_status"):
   original_tweet = quoted_tweet.quoted_status
  elif hasattr(quoted_tweet, "retweeted_status") and hasattr(quoted_tweet.retweeted_status, "quoted_status"):
   original_tweet = quoted_tweet.retweeted_status.quoted_status
  else:
   return quoted_tweet
  original_tweet = self.check_long_tweet(original_tweet)
  if hasattr(original_tweet, "full_text"):
   value = "full_text"
  elif hasattr(original_tweet, "message"):
   value = "message"
  else:
   value = "text"
  setattr(original_tweet, value, utils.expand_urls(getattr(original_tweet, value), original_tweet.entities))
  return compose.compose_quoted_tweet(quoted_tweet, original_tweet)

 def check_long_tweet(self, tweet):
  """ Process a tweet and add extra info if it's a long tweet made with Twyshort.
  tweet dict: a tweet object.
  returns a tweet with a new argument message, or original tweet if it's not a long tweet."""
  long = twishort.is_long(tweet)
  if long != False and config.app["app-settings"]["handle_longtweets"]:
   message = twishort.get_full_text(long)
   if hasattr(tweet, "quoted_status"):
    tweet.quoted_status.message = message
    if tweet.quoted_status.message == False: return False
    tweet.quoted_status.twishort = True
    for i in tweet.quoted_status.entities.user_mentions:
     if "@%s" % (i.screen_name) not in tweet.quoted_status.message and i.screen_name != tweet.user.screen_name:
      if hasattr(tweet["quoted_status"], "retweeted_status")  and tweet.retweeted_status.user.screen_name == i.screen_name:
       continue
     tweet.quoted_status.message = u"@%s %s" % (i.screen_name, tweet.message)
   else:
    tweet.message = message
    if tweet.message == False: return False
    tweet.twishort = True
    for i in tweet.entities.user_mentions:
     if "@%s" % (i.screen_name) not in tweet.message and i.screen_name != tweet.user.screen_name:
      if hasattr(tweet, "retweeted_status") and tweet.retweeted_status.user.screen_name == i.screen_name:
       continue
  return tweet

 def get_user(self, id):
  """ Returns an user object associated with an ID.
  id str: User identifier, provided by Twitter.
  returns an user dict."""
  if ("users" in self.db) == False or (id in self.db["users"]) == False:
   try:
    user = self.twitter.show_user(id=id)
   except TwythonError:
    user = dict(screen_name="deleted_account", name="Deleted account")
    return user
   self.db["users"][user["id_str"]] = user
   return user
  else:
   return self.db["users"][id]

 def get_user_by_screen_name(self, screen_name):
  """ Returns an user identifier associated with a screen_name.
  screen_name str: User name, such as tw_blue2, provided by Twitter.
  returns an user ID."""
  if ("users" in self.db) == False:
   user = utils.if_user_exists(self.twitter, screen_name)
   self.db["users"][user["id_str"]] = user
   return user["id_str"]
  else:
   for i in list(self.db["users"].keys()):
    if self.db["users"][i]["screen_name"] == screen_name:
     return self.db["users"][i]["id_str"]
   user = utils.if_user_exists(self.twitter, screen_name)
   self.db["users"][user["id_str"]] = user
   return user["id_str"]