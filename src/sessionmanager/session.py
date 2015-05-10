# -*- coding: utf-8 -*-
""" The main session object. Here are the twitter functions to interact with the "model" of TWBlue."""
import urllib2
import twitter
from keys import keyring
import session_exceptions as Exceptions
import paths
import output
import time
import sound
import logging
from twitter import utils
from twython import TwythonError, TwythonRateLimitError, TwythonAuthError
import config_utils
import shelve
import application
import os
from mysc.thread_utils import stream_threaded
from pubsub import pub
log = logging.getLogger("sessionmanager.session")

sessions = {}

class Session(object):
 """ A session object where we will save configuration, the twitter object and a local storage for saving the items retrieved through the Twitter API methods"""

 # Decorators.

 def _require_login(fn):

  """ Decorator for checking if the user is logged in(a twitter object has credentials) on twitter.
  Some functions may need this to avoid making unneeded twitter API calls."""

  def f(self, *args, **kwargs):
   if self.logged == True:
    fn(self, *args, **kwargs)
   else:
    raise Exceptions.NotLoggedSessionError("You are not logged in yet.")
  return f

 def _require_configuration(fn):

  """ Check if the user has a configured session."""

  def f(self, *args, **kwargs):
   if self.settings != None:
    fn(self, *args, **kwargs)
   else:
    raise Exceptions.NotConfiguredSessionError("Not configured.")
  return f

 def order_buffer(self, name, data):

  """ Put the new items in the local database.
  name str: The name for the buffer stored in the dictionary.
  data list: A list with tweets.
  returns the number of items that have been added in this execution"""

  num = 0
  if self.db.has_key(name) == False:
   self.db[name] = []
  for i in data:
   if utils.find_item(i["id"], self.db[name]) == None:
    if self.settings["general"]["reverse_timelines"] == False: self.db[name].append(i)
    else: self.db[name].insert(0, i)
    num = num+1
  return num

 def order_cursored_buffer(self, name, data):

  """ Put the new items on the local database. Useful for cursored buffers (followers, friends, users of a list and searches)
  name str: The name for the buffer stored in the dictionary.
  data list: A list with items and some information about cursors.
  returns the number of items that have been added in this execution"""

  num = 0
  if self.db.has_key(name) == False:
   self.db[name] = {}
   self.db[name]["items"] = []
#  if len(self.db[name]["items"]) > 0:
  for i in data:
   if utils.find_item(i["id"], self.db[name]["items"]) == None:
    if self.settings["general"]["reverse_timelines"] == False: self.db[name]["items"].append(i)
    else: self.db[name]["items"].insert(0, i)
    num = num+1
  return num

 def __init__(self, session_id):

  """ session_id (str): The name of the folder inside the config directory where the session is located."""

  super(Session, self).__init__()
  self.session_id = session_id
  self.logged = False
  self.settings = None
  self.twitter = twitter.twitter.twitter()
  self.db={}
  self.reconnection_function_active = False
  self.counter = 0
  self.lists = []
  pub.subscribe(self.add_friends, "friends-receibed")

 @property
 def is_logged(self):
  return self.logged

 def get_configuration(self):

   """ Gets settings for a session."""
 
   file_ = "%s/session.conf" % (self.session_id,)
#  try:
   log.debug("Creating config file %s" % (file_,))
   self.settings = config_utils.load_config(paths.config_path(file_), paths.app_path("Conf.defaults"))
   self.init_sound()
   self.deshelve()
#  except:
#   log.exception("The session configuration has failed.")
#   self.settings = None

 def init_sound(self):
  self.sound = sound.soundSystem(self.settings["sound"])

 @_require_configuration
 def login(self, verify_credentials=True):

  """ Log into twitter using  credentials from settings.
  if the user account isn't authorised, it needs to call self.authorise() before login."""

  if self.settings["twitter"]["user_key"] != None and self.settings["twitter"]["user_secret"] != None:
   log.debug("Logging in to twitter...")
   self.twitter.login(self.settings["twitter"]["user_key"], self.settings["twitter"]["user_secret"], verify_credentials)
   self.logged = True
   log.debug("Logged.")
   self.counter = 0
  else:
   self.logged = False
   raise Exceptions.RequireCredentialsSessionError

 @_require_configuration
 def authorise(self):

  """ Authorises a Twitter account. This function needs to be called for each new session, after self.get_configuration() and before self.login()"""

  if self.logged == True:
   raise Exceptions.AlreadyAuthorisedError("The authorisation process is not needed at this time.")
  else:
   self.twitter.authorise(self.settings)

 def get_more_items(self, update_function, users=False, name=None, *args, **kwargs):
  results = []
  data = getattr(self.twitter.twitter, update_function)(*args, **kwargs)
  if users == True:
   self.db[name]["cursor"] = data["next_cursor"]
   for i in data["users"]: results.append(i)
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
    val = getattr(self.twitter.twitter, call_name)(*args, **kwargs)
    finished = True
   except TwythonError as e:
    output.speak(e.message)
    if e.error_code != 403 and e.error_code != 404:
     tries = tries+1
     time.sleep(5)
    elif report_failure and hasattr(e, 'message'):
     output.speak(_("%s failed.  Reason: %s") % (action, e.message))
    finished = True
   except:
    tries = tries + 1
    time.sleep(5)
  if report_success:
   output.speak(_("%s succeeded.") % action)
  if _sound != None: self.sound.play(_sound)

 def search(self, name, *args, **kwargs):
  tl = self.twitter.twitter.search(*args, **kwargs)
  tl["statuses"].reverse()
  return tl["statuses"]

 @_require_login
 def get_favourites_timeline(self, name, *args, **kwargs):

  """ Gets favourites for the authenticated user or a friend or follower.
  name str: Name for storage in the database."""

  tl = self.call_paged(self.twitter.twitter.get_favorites, *args, **kwargs)
  return self.order_buffer(name, tl)

 def call_paged(self, update_function, *args, **kwargs):

  """ Makes a call to the Twitter API methods several times. Useful for get methods.
  this function is needed for retrieving more than 200 items.
  update_function str: The function to call. This function must be child of self.twitter.twitter
  returns a list with all items retrieved."""

  max = int(self.settings["general"]["max_api_calls"])-1
  results = []
  data = getattr(self.twitter.twitter, update_function)(count=self.settings["general"]["max_tweets_per_call"], *args, **kwargs)
  results.extend(data)
  for i in range(0, max):
   if i == 0: max_id = results[-1]["id"]
   else: max_id = results[0]["id"]
   data = getattr(self.twitter.twitter, update_function)(max_id=max_id, count=self.settings["general"]["max_tweets_per_call"], *args, **kwargs)
   results.extend(data)
  results.reverse()
  return results

 @_require_login
 def get_user_info(self):

  """ Retrieves some information required by TWBlue for setup."""
  f = self.twitter.twitter.get_account_settings()
  sn = f["screen_name"]
  self.settings["twitter"]["user_name"] = sn
  self.db["user_name"] = sn
  self.db["user_id"] = self.twitter.twitter.show_user(screen_name=sn)["id_str"]
  try:
   self.db["utc_offset"] = f["time_zone"]["utc_offset"]
  except KeyError:
   self.db["utc_offset"] = -time.timezone
  self.get_lists()
  self.get_muted_users()
  self.settings.write()

 @_require_login
 def get_lists(self):

  """ Gets the lists that the user is subscribed to and stores them in the database. Returns None."""
  
  self.db["lists"] = self.twitter.twitter.show_lists(reverse=True)

 @_require_login
 def get_muted_users(self):

  """ Gets muted users (oh really?)."""

#  self.db["muted_users"] = self.twitter.twitter.get_muted_users_ids()["ids"]
  pass
 @_require_login
 def get_stream(self, name, function, *args, **kwargs):

  """ Retrieves the items for a regular stream.
  name str: Name to save items to the database.
  function str: A function to get the items."""

  last_id = -1
  if self.db.has_key(name):
   try:
    if self.db[name][0]["id"] > self.db[name][-1]["id"]:
     last_id = self.db[name][0]["id"]
    else:
     last_id = self.db[name][-1]["id"]
   except IndexError:
    pass
  tl = self.call_paged(function, sinze_id=last_id, *args, **kwargs)
  self.order_buffer(name, tl)

 @_require_login
 def get_cursored_stream(self, name, function, items="users", *args, **kwargs):

  """ Gets items for API calls that require using cursors to paginate the results.
  name str: Name to save it in the database.
  function str: Function that provides the items.
  items: When the function returns the list with results, items will tell how the order function should be look.
    for example get_followers_list returns a list and users are under list["users"], here the items should point to "users"."""

  items_ = []
  try:
   if self.db[name].has_key("cursor"):
    cursor = self.db[name]["cursor"]
   else:
    cursor = -1
  except KeyError:
   cursor = -1
  tl = getattr(self.twitter.twitter, function)(cursor=cursor, count=self.settings["general"]["max_tweets_per_call"], *args, **kwargs)
  tl[items].reverse()
  num = self.order_cursored_buffer(name, tl[items])
  self.db[name]["cursor"] = tl["next_cursor"]
  return num

 def start_streaming(self):

  """ Start the streaming for sending tweets in realtime."""
  self.get_timelines()
  self.get_main_stream()

 def get_main_stream(self):
  log.debug("Starting the main stream...")
  self.main_stream = twitter.buffers.stream.streamer(keyring.get("api_key"), keyring.get("api_secret"), self.settings["twitter"]["user_key"], self.settings["twitter"]["user_secret"], self)
  stream_threaded(self.main_stream.user, self.session_id)

 def get_timelines(self):
  log.debug("Starting the timelines stream...")
  self.timelinesStream = twitter.buffers.indibidual.timelinesStreamer(keyring.get("api_key"), keyring.get("api_secret"), self.settings["twitter"]["user_key"], self.settings["twitter"]["user_secret"], session=self)
  ids = ""
  for i in self.settings["other_buffers"]["timelines"]:
   ids = ids + "%s, " % (self.db[i+"-timeline"][0]["user"]["id_str"])
  for i in self.lists:
   for z in i.users:
    ids += str(z) + ", "
  if ids != "":
   stream_threaded(self.timelinesStream.statuses.filter, self.session_id, follow=ids)

 def add_friends(self):
  try:
   self.timelinesStream.set_friends(self.main_stream.friends)
  except AttributeError:
   pass

 def listen_stream_error(self):
  if hasattr(self, "main_stream"):
   log.debug("Disconnecting the main stream...")
   self.main_stream.disconnect()
   del self.main_stream
  if hasattr(self, "timelinesStream"):
   log.debug("disconnecting the timelines stream...")
   self.timelinesStream.disconnect()
   del self.timelinesStream

 def check_connection(self):
  instan = 0
  self.counter += 1
  if self.counter >= 4:
   del self.twitter
   self.logged = False
   self.twitter = twitter.twitter.twitter()
   self.login(False)
  if self.reconnection_function_active == True:  return
  self.reconnection_function_active = True
  if not hasattr(self, "main_stream"):
   self.get_main_stream()
  if not hasattr(self, "timelinesStream"):
   self.get_timelines()
  self.reconnection_function_active = False
  if hasattr(self, "timelinesStream") and not hasattr(self.timelinesStream, "friends"):
   self.add_friends()
  try:
   urllib2.urlopen("http://74.125.228.231", timeout=5)
  except urllib2.URLError:
   pub.sendMessage("stream-error", session=self.session_id)

 def remove_stream(self, stream):
  if stream == "timelinesStream":
   self.timelinesStream.disconnect()
   del self.timelinesStream
  else:
   self.main_stream.disconnect()
   del self.main_stream

 def shelve(self):
  "Shelve the database to allow for persistance."
  shelfname=paths.config_path(str(self.session_id)+".db")
  if self.settings["general"]["persist_size"] == 0:
   if os.path.exists(shelfname):
    os.remove(shelfname)
   return
  try:
   if not os.path.exists(shelfname):
    output.speak("Generating database, this might take a while.",True)
   shelf=shelve.open(paths.config_path(shelfname),'c')
   for key,value in self.db.items():
    if type(key) != str and type(key) != unicode:
        output.speak("Uh oh, while shelving the database, a key of type " + str(type(key)) + " has been found. It will be converted to type str, but this will cause all sorts of problems on deshelve. Please bring this to the attention of the " + application.name + " developers immediately. More information about the error will be written to the error log.",True)
        log.error("Uh oh, " + str(key) + " is of type " + str(type(key)) + "!")
    if type(value) == List and self.settings["general"]["persist_size"] != -1 and len(type) > self.settings["general"]["persist_size"]:
        shelf[str(key)]=value[self.settings["general"]["persist_size"]:]
    else:
        shelf[str(key)]=value
   shelf.close()
  except:
   output.speak("An exception occurred while shelving the " + application.name + " database. It will be deleted and rebuilt automatically. If this error persists, send the error log to the " + application.name + " developers.",True)
   log.exception("Exception while shelving" + shelfname)
   os.remove(shelfname)

 def deshelve(self):
  "Import a shelved database."
  shelfname=paths.config_path(str(self.session_id)+".db")
  if self.settings["general"]["persist_size"] == 0:
   if os.path.exists(shelfname):
    os.remove(shelfname)
   return
  try:
   shelf=shelve.open(paths.config_path(shelfname),'c')
   for key,value in shelf.items():
    self.db[unicode(key)]=value
   shelf.close()
  except:
   output.speak("An exception occurred while deshelving the " + application.name + " database. It will be deleted and rebuilt automatically. If this error persists, send the error log to the " + application.name + " developers.",True)
   log.exception("Exception while deshelving" + shelfname)
   os.remove(shelfname)
