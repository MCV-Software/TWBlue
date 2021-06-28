# -*- coding: utf-8 -*-
""" This is the main session needed to access all Twitter Features."""
import os
import time
import logging
import webbrowser
import wx
import config
import output
import application
from pubsub import pub
import tweepy
from tweepy.error import TweepError
from tweepy.models import User as UserModel
from mysc.thread_utils import call_threaded
from keys import keyring
from sessions import base
from sessions.twitter import utils, compose
from sessions.twitter.long_tweets import tweets, twishort
from . import reduce, streaming
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
        if name == "direct_messages":
            return self.order_direct_messages(data)
        num = 0
        last_id = None
        if (name in self.db) == False:
            self.db[name] = []
        if ("users" in self.db) == False:
            self.db["users"] = {}
        objects = self.db[name]
        if ignore_older and len(self.db[name]) > 0:
            if self.settings["general"]["reverse_timelines"] == False:
                last_id = self.db[name][0].id
            else:
                last_id = self.db[name][-1].id
        self.add_users_from_results(data)
        for i in data:
            if ignore_older and last_id != None:
                if i.id < last_id:
                    log.error("Ignoring an older tweet... Last id: {0}, tweet id: {1}".format(last_id, i.id))
                    continue
            if utils.find_item(i.id, self.db[name]) == None and     utils.is_allowed(i, self.settings, name) == True:
                if i == False: continue
                reduced_object = reduce.reduce_tweet(i)
                reduced_object = self.check_quoted_status(reduced_object)
                reduced_object = self.check_long_tweet(reduced_object)
                if self.settings["general"]["reverse_timelines"] == False: objects.append(reduced_object)
                else: objects.insert(0, reduced_object)
                num = num+1
        self.db[name] = objects
        return num

    def order_people(self, name, data):
        """ Put new items on the local database. Useful for cursored buffers (followers, friends, users of a list and searches)
        name str: The name for the buffer stored in the dictionary.
        data list: A list with items and some information about cursors.
        returns the number of items that have been added in this execution"""
        num = 0
        if (name in self.db) == False:
            self.db[name] = []
        objects = self.db[name]
        for i in data:
            if utils.find_item(i.id, self.db[name]) == None:
                if self.settings["general"]["reverse_timelines"] == False: objects.append(i)
                else: objects.insert(0, i)
                num = num+1
        self.db[name] = objects
        return num

    def order_direct_messages(self, data):
        """ Add incoming and sent direct messages to their corresponding database items.
        data list: A list of direct messages to add.
        returns the number of incoming messages processed in this execution, and sends an event with data regarding amount of sent direct messages added."""
        incoming = 0
        sent = 0
        if ("direct_messages" in self.db) == False:
            self.db["direct_messages"] = []
        if ("sent_direct_messages" in self.db) == False:
            self.db["sent_direct_messages"] = []
        objects = self.db["direct_messages"]
        sent_objects = self.db["sent_direct_messages"]
        for i in data:
            # Twitter returns sender_id as str, which must be converted to int in order to match to our user_id object.
            if int(i.message_create["sender_id"]) == self.db["user_id"]:
                if "sent_direct_messages" in self.db and utils.find_item(i.id, self.db["sent_direct_messages"]) == None:
                    if self.settings["general"]["reverse_timelines"] == False: sent_objects.append(i)
                    else: sent_objects.insert(0, i)
                    sent = sent+1
            else:
                if utils.find_item(i.id, self.db["direct_messages"]) == None:
                    if self.settings["general"]["reverse_timelines"] == False: objects.append(i)
                    else: objects.insert(0, i)
                    incoming = incoming+1
        self.db["direct_messages"] = objects

        self.db["sent_direct_messages"] = sent_objects
        pub.sendMessage("sent-dms-updated", total=sent, account=self.db["user_name"])


        return incoming

    def __init__(self, *args, **kwargs):
        super(Session, self).__init__(*args, **kwargs)
        # Adds here the optional cursors objects.
        cursors = dict(direct_messages=-1)
        self.db["cursors"] = cursors
        self.reconnection_function_active = False
        self.counter = 0
        self.lists = []
        # As users are cached for accessing them with not too many twitter calls,
        # there could be a weird situation where a deleted user who sent direct messages to the current account will not be able to be retrieved at twitter.
        # So we need to store an "user deleted" object in the cache, but have the ID of the deleted user in a local reference.
        # This will be especially useful because if the user reactivates their account later, TWblue will try to retrieve such user again at startup.
        # If we wouldn't implement this approach, TWBlue would save permanently the "deleted user" object.
        self.deleted_users = {}
        pub.subscribe(self.handle_new_status, "newStatus")

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
            except TweepError as e:
                output.speak(e.reason)
                val = None
                if e.error_code != 403 and e.error_code != 404:
                    tries = tries+1
                    time.sleep(5)
                elif report_failure and hasattr(e, 'reason'):
                    output.speak(_("%s failed.  Reason: %s") % (action, e.reason))
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
            application.supported_languages = self.twitter.supported_languages()
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
        self.db["muted_users"] = self.twitter.mutes_ids()

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
        """ Process a tweet and extract all information related to the quote. """
        quoted_tweet = tweet
        if hasattr(tweet, "full_text"):
            value = "full_text"
        else:
            value = "text"
        if hasattr(quoted_tweet, "entities"):
            setattr(quoted_tweet, value, utils.expand_urls(getattr(quoted_tweet, value), quoted_tweet.entities))
        if hasattr(quoted_tweet, "is_quote_status") == True and hasattr(quoted_tweet, "quoted_status"):
            original_tweet = quoted_tweet.quoted_status
        elif hasattr(quoted_tweet, "retweeted_status") and hasattr(quoted_tweet.retweeted_status, "is_quote_status") == True and hasattr(quoted_tweet.retweeted_status, "quoted_status"):
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
        if hasattr(original_tweet, "entities"):
            setattr(original_tweet, value, utils.expand_urls(getattr(original_tweet, value), original_tweet.entities))
        # ToDo: Shall we check whether we should add show_screen_names here?
        return compose.compose_quoted_tweet(quoted_tweet, original_tweet, session=self)

    def check_long_tweet(self, tweet):
        """ Process a tweet and add extra info if it's a long tweet made with Twyshort.
        tweet dict: a tweet object.
        returns a tweet with a new argument message, or original tweet if it's not a long tweet."""
        long = False
        if hasattr(tweet, "entities") and tweet.entities.get("urls"):
            long = twishort.is_long(tweet)
        if long != False and config.app["app-settings"]["handle_longtweets"]:
            message = twishort.get_full_text(long)
            if hasattr(tweet, "quoted_status"):
                tweet.quoted_status.message = message
                if tweet.quoted_status.message == False: return False
                tweet.quoted_status.twishort = True
                if hasattr(tweet.quoted_status, "entities") and tweet.quoted_status.entities.get("user_mentions"):
                    for i in tweet.quoted_status.entities["user_mentions"]:
                        if "@%s" % (i["screen_name"]) not in tweet.quoted_status.message and i["screen_name"] != self.get_user(tweet.user).screen_name:
                            if hasattr(tweet.quoted_status, "retweeted_status")  and self.get_user(tweet.retweeted_status.user).screen_name == i["screen_name"]:
                                continue
                        tweet.quoted_status.message = u"@%s %s" % (i["screen_name"], tweet.message)
            else:
                tweet.message = message
                if tweet.message == False: return False
                tweet.twishort = True
                if hasattr(tweet, "entities") and tweet.entities.get("user_mentions"):
                    for i in tweet.entities["user_mentions"]:
                        if "@%s" % (i["screen_name"]) not in tweet.message and i["screen_name"] != self.get_user(tweet.user).screen_name:
                            if hasattr(tweet, "retweeted_status") and self.get_user(tweet.retweeted_status.user).screen_name == i["screen_name"]:
                                continue
                            tweet.message = u"@%s %s" % (i["screen_name"], tweet.message)
        return tweet

    def get_user(self, id):
        """ Returns an user object associated with an ID.
        id str: User identifier, provided by Twitter.
        returns a tweepy user object."""
        if hasattr(id, "id_str"):
            log.error("Called get_user function by passing a full user id as a parameter.")
            id = id.id_str
        # Check if the user has been added to the list of deleted users previously.
        if id in self.deleted_users:
            log.debug("Returning user {} from the list of deleted users.".format(id))
            return self.deleted_users[id]
        if ("users" in self.db) == False or (str(id) in self.db["users"]) == False:
            log.debug("Requesting user id {} as it is not present in the users database.".format(id))
            try:
                user = self.twitter.get_user(id=id)
            except TweepError as err:
                user = UserModel(None)
                user.screen_name = "deleted_user"
                user.id = id
                user.name = _("Deleted account")
                if hasattr(err, "api_code") and err.api_code == 50:
                    self.deleted_users[id] = user
                    return user
                else:
                    log.exception("Error when attempting to retrieve an user from Twitter.")
                    return user
            users = self.db["users"]
            users[user.id_str] = user
            self.db["users"] = users
            return user
        else:
            return self.db["users"][str(id)]

    def get_user_by_screen_name(self, screen_name):
        """ Returns an user identifier associated with a screen_name.
        screen_name str: User name, such as tw_blue2, provided by Twitter.
        returns an user ID."""
        if ("users" in self.db) == False:
            user = utils.if_user_exists(self.twitter, screen_name)
            users = self.db["users"]
            users[user["id"]] = user
            self.db["users"] = users
            return user["id"]
        else:
            for i in list(self.db["users"].keys()):
                if self.db["users"][i].screen_name == screen_name:
                    return self.db["users"][i].id
            user = utils.if_user_exists(self.twitter, screen_name)
            users = self.db["users"]
            users[user.id] = user
            self.db["users"] = users
            return user.id

    def save_users(self, user_ids):
        """ Adds all new users to the users database. """
        if len(user_ids) == 0:
            return
        log.debug("Received %d user IDS to be added in the database." % (len(user_ids)))
        users_to_retrieve = [user_id for user_id in user_ids if (user_id not in self.db["users"] and user_id not in self.deleted_users)]
        # Remove duplicates
        users_to_retrieve = list(dict.fromkeys(users_to_retrieve))
        if len(users_to_retrieve) == 0:
            return
        log.debug("TWBlue will get %d new users from Twitter." % (len(users_to_retrieve)))
        try:
            users = self.twitter.lookup_users(user_ids=users_to_retrieve, tweet_mode="extended")
            users_db = self.db["users"]
            for user in users:
                users_db[user.id_str] = user
            log.debug("Added %d new users" % (len(users)))
            self.db["users"] = users_db
        except TweepError as err:
            if hasattr(err, "api_code") and err.api_code == 17: # Users not found.
                log.error("The specified users {} were not found in twitter.".format(user_ids))
                # Creates a deleted user object for every user_id not found here.
                # This will make TWBlue to not waste Twitter API calls when attempting to retrieve those users again.
                # As deleted_users is not saved across restarts, when restarting TWBlue, it will retrieve the correct users if they enabled their accounts.
                for id in users_to_retrieve:
                    user = UserModel(None)
                    user.screen_name = "deleted_user"
                    user.id = id
                    user.name = _("Deleted account")
                    self.deleted_users[id] = user
            else:
                log.exception("An exception happened while attempting to retrieve a list of users from direct messages in Twitter.")

    def add_users_from_results(self, data):
        users = self.db["users"]
        for i in data:
            if hasattr(i, "user"):
                if isinstance(i.user, str):
                    log.warning("A String was passed to be added as an user. This is normal only if TWBlue tried to load a conversation.")
                    continue
                if (i.user.id_str in self.db["users"]) == False:
                    users[i.user.id_str] = i.user
                if hasattr(i, "quoted_status") and (i.quoted_status.user.id_str in self.db["users"]) == False:
                    users[i.quoted_status.user.id_str] = i.quoted_status.user

                if hasattr(i, "retweeted_status") and (i.retweeted_status.user.id_str in self.db["users"]) == False:
                    users[i.retweeted_status.user.id_str] = i.retweeted_status.user
        self.db["users"] = users

    def start_streaming(self):
        self.stream_listener = streaming.StreamListener(twitter_api=self.twitter, user=self.db["user_name"])
        self.stream = tweepy.Stream(auth = self.auth, listener=self.stream_listener)
        call_threaded(self.stream.filter, follow=self.stream_listener.users)

    def handle_new_status(self, status, user):
        if self.db["user_name"] != user:
            return
        if hasattr(status, "retweeted_status") and status.retweeted_status.truncated:
            status.retweeted_status._json["full_text"] = status.retweeted_status.extended_tweet["full_text"]
        if hasattr(status, "quoted_status") and status.quoted_status.truncated:
            status.quoted_status._json["full_text"] = status.quoted_status.extended_tweet["full_text"]
        if status.truncated:
            status._json["full_text"] = status.extended_tweet["full_text"]
        num = self.order_buffer("home_timeline", [status])
        if num == 1:
            status = reduce.reduce_tweet(status)
            pub.sendMessage("tweet-in-home", data=status, user=self.db["user_name"])