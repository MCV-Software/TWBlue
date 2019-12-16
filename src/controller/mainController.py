# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from builtins import str
from builtins import range
from builtins import object
import platform
system = platform.system()
import application
import requests
from audio_services import youtube_utils
import arrow
if system == "Windows":
 from update import updater
 from wxUI import (view, dialogs, commonMessageDialogs, sysTrayIcon)
 from . import settings
 from extra import SoundsTutorial, ocr
 import keystrokeEditor
 from keyboard_handler.wx_handler import WXKeyboardHandler
 from . import userActionsController
 from . import trendingTopics
 from . import user
 from . import listsController
 from . import filterController
# from issueReporter import issueReporter
elif system == "Linux":
 from gtkUI import (view, commonMessageDialogs)
from sessions.twitter import utils, compose
from sessionmanager import manager, sessionManager

from controller.buffers import baseBuffers, twitterBuffers
from . import messages
import sessions
from sessions.twitter  import session as session_
from pubsub import pub
import sound
import output
from twython import TwythonError, TwythonAuthError
from mysc.thread_utils import call_threaded
from mysc.repeating_timer import RepeatingTimer
from mysc import restart
import config
import widgetUtils
import pygeocoder
from pygeolib import GeocoderError
import logging
import webbrowser
from mysc import localization
import os
import languageHandler

log = logging.getLogger("mainController")

geocoder = pygeocoder.Geocoder()

class Controller(object):

 """ Main Controller for TWBlue. It manages the main window and sessions."""

 def search_buffer(self, name_, user):

  """ Searches a buffer.
 name_ str: The name for the buffer
 user str: The account for the buffer.
 for example you may want to search the home_timeline buffer for the tw_blue2 user.
  Return type: buffers.buffer object."""
  for i in self.buffers:
   if i.name == name_ and i.account == user: return i

 def get_current_buffer(self):
  """ Get the current focused bufferObject.
  Return type: buffers.buffer object."""
  buffer = self.view.get_current_buffer()
  if hasattr(buffer, "account"):
   buffer = self.search_buffer(buffer.name, buffer.account)
   return buffer

 def get_best_buffer(self):
  """ Get the best buffer for doing  something using the session object.
  This function is useful when you need to open a timeline or post a tweet, and the user is in a buffer without a session, for example the events buffer.
  Return type: twitterBuffers.buffer object."""
  # Gets the parent buffer to know what account is doing an action
  view_buffer = self.view.get_current_buffer()
  # If the account has no session attached, we will need to search the first available non-empty buffer for that account to use its session.
  if view_buffer.type == "account" or view_buffer.type == "empty":
   buffer = self.get_first_buffer(view_buffer.account)
  else:
   buffer = self.search_buffer(view_buffer.name, view_buffer.account)
  if buffer != None: return buffer

 def get_first_buffer(self, account):
  """ Gets the first valid buffer for an account.
  account str: A twitter username.
  The first valid buffer is the home timeline."""
  for i in self.buffers:
   if i.account == account and i.invisible == True and i.session != None:
    return i

 def get_last_buffer(self, account):
  """ Gets the last valid buffer for an account.
  account str: A twitter username.
  The last valid buffer is the last buffer that contains a session object assigned."""
  results = self.get_buffers_for_account(account)
  return results[-1]

 def get_first_buffer_index(self, account):
  buff = self.get_first_buffer(account)
  return self.view.search(buff.name, buff.account)

 def get_last_buffer_index(self, account):
  buff = self.get_last_buffer(account)
  return self.view.search(buff.name, buff.account)

 def get_buffers_for_account(self, account):
  results = []
  buffers = self.view.get_buffers()
  [results.append(self.search_buffer(i.name, i.account)) for i in buffers if i.account == account and (i.type != "account")]
  return results

 def bind_other_events(self):
  """ Binds the local application events with their functions."""
  log.debug("Binding other application events...")
  pub.subscribe(self.buffer_title_changed, "buffer-title-changed")
  pub.subscribe(self.manage_sent_dm, "sent-dm")
  widgetUtils.connect_event(self.view, widgetUtils.CLOSE_EVENT, self.exit_)
  pub.subscribe(self.logout_account, "logout")
  pub.subscribe(self.login_account, "login")
  pub.subscribe(self.create_new_buffer, "create-new-buffer")
  pub.subscribe(self.execute_action, "execute-action")
  pub.subscribe(self.search_topic, "search")
  pub.subscribe(self.update_sent_dms, "sent-dms-updated")
  pub.subscribe(self.more_dms, "more-sent-dms")
  pub.subscribe(self.manage_sent_tweets, "sent-tweet")
  pub.subscribe(self.manage_friend, "friend")
  pub.subscribe(self.manage_unfollowing, "unfollowing")
  pub.subscribe(self.manage_favourite, "favourite")
  pub.subscribe(self.manage_unfavourite, "unfavourite")
  pub.subscribe(self.manage_blocked_user, "blocked-user")
  pub.subscribe(self.manage_unblocked_user, "unblocked-user")
  if system == "Windows":
   pub.subscribe(self.invisible_shorcuts_changed, "invisible-shorcuts-changed")
   widgetUtils.connect_event(self.view, widgetUtils.MENU, self.show_hide, menuitem=self.view.show_hide)
   widgetUtils.connect_event(self.view, widgetUtils.MENU, self.search, menuitem=self.view.menuitem_search)
   widgetUtils.connect_event(self.view, widgetUtils.MENU, self.list_manager, menuitem=self.view.lists)
   widgetUtils.connect_event(self.view, widgetUtils.MENU, self.get_trending_topics, menuitem=self.view.trends)
   widgetUtils.connect_event(self.view, widgetUtils.MENU, self.filter, menuitem=self.view.filter)
   widgetUtils.connect_event(self.view, widgetUtils.MENU, self.manage_filters, menuitem=self.view.manage_filters)
   widgetUtils.connect_event(self.view, widgetUtils.MENU, self.find, menuitem=self.view.find)
   widgetUtils.connect_event(self.view, widgetUtils.MENU, self.accountConfiguration, menuitem=self.view.account_settings)
   widgetUtils.connect_event(self.view, widgetUtils.MENU, self.configuration, menuitem=self.view.prefs)
   widgetUtils.connect_event(self.view, widgetUtils.MENU, self.ocr_image, menuitem=self.view.ocr)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.learn_sounds, menuitem=self.view.sounds_tutorial)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.exit, menuitem=self.view.close)
  widgetUtils.connect_event(self.view, widgetUtils.CLOSE_EVENT, self.exit)
  if widgetUtils.toolkit == "wx":
   log.debug("Binding the exit function...")
   widgetUtils.connectExitFunction(self.exit_)
   widgetUtils.connect_event(self.view, widgetUtils.MENU, self.edit_keystrokes, menuitem=self.view.keystroke_editor)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.post_tweet, self.view.compose)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.post_reply, self.view.reply)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.post_retweet, self.view.retweet)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.add_to_favourites, self.view.fav)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.remove_from_favourites, self.view.unfav)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.view_item, self.view.view)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.reverse_geocode, menuitem=self.view.view_coordinates)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.delete, self.view.delete)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.follow, menuitem=self.view.follow)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.send_dm, self.view.dm)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.view_user_lists, menuitem=self.view.viewLists)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.get_more_items, menuitem=self.view.load_previous_items)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.view_user_lists, menuitem=self.view.viewLists)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.clear_buffer, menuitem=self.view.clear)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.remove_buffer, self.view.deleteTl)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.check_for_updates, self.view.check_for_updates)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.about, menuitem=self.view.about)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.visit_website, menuitem=self.view.visit_website)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.get_soundpacks, menuitem=self.view.get_soundpacks)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.manage_accounts, self.view.manage_accounts)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.update_profile, menuitem=self.view.updateProfile)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.user_details, menuitem=self.view.details)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.toggle_autoread, menuitem=self.view.autoread)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.toggle_buffer_mute, self.view.mute_buffer)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.open_timeline, self.view.timeline)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.open_favs_timeline, self.view.favs)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.open_conversation, menuitem=self.view.view_conversation)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.seekLeft, menuitem=self.view.seekLeft)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.seekRight, menuitem=self.view.seekRight)
  if widgetUtils.toolkit == "wx":
   widgetUtils.connect_event(self.view.nb, widgetUtils.NOTEBOOK_PAGE_CHANGED, self.buffer_changed)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.report_error, self.view.reportError)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.view_documentation, self.view.doc)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.view_changelog, self.view.changelog)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.add_to_list, self.view.addToList)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.remove_from_list, self.view.removeFromList)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.update_buffer, self.view.update_buffer)

 def set_systray_icon(self):
  self.systrayIcon = sysTrayIcon.SysTrayIcon()
  widgetUtils.connect_event(self.systrayIcon, widgetUtils.MENU, self.post_tweet, menuitem=self.systrayIcon.tweet)
  widgetUtils.connect_event(self.systrayIcon, widgetUtils.MENU, self.configuration, menuitem=self.systrayIcon.global_settings)
  widgetUtils.connect_event(self.systrayIcon, widgetUtils.MENU, self.accountConfiguration, menuitem=self.systrayIcon.account_settings)
  widgetUtils.connect_event(self.systrayIcon, widgetUtils.MENU, self.update_profile, menuitem=self.systrayIcon.update_profile)
  widgetUtils.connect_event(self.systrayIcon, widgetUtils.MENU, self.show_hide, menuitem=self.systrayIcon.show_hide)
  widgetUtils.connect_event(self.systrayIcon, widgetUtils.MENU, self.check_for_updates, menuitem=self.systrayIcon.check_for_updates)
  widgetUtils.connect_event(self.systrayIcon, widgetUtils.MENU, self.view_documentation, menuitem=self.systrayIcon.doc)
  widgetUtils.connect_event(self.systrayIcon, widgetUtils.MENU, self.exit, menuitem=self.systrayIcon.exit)
  widgetUtils.connect_event(self.systrayIcon, widgetUtils.TASKBAR_LEFT_CLICK, self.taskbar_left_click)
  widgetUtils.connect_event(self.systrayIcon, widgetUtils.TASKBAR_RIGHT_CLICK, self.taskbar_right_click)

 def taskbar_left_click(self, *args, **kwargs):
  if self.showing == True:
   self.view.set_focus()
  else:
   self.show_hide()

 def taskbar_right_click(self, *args, **kwargs):
  self.systrayIcon.show_menu()

 def __init__(self):
  super(Controller, self).__init__()
  # Visibility state.
  self.showing = True
  # main window
  self.view = view.mainFrame()
  # buffers list.
  self.buffers = []
  self.started = False
  # accounts list.
  self.accounts = []
  # This saves the current account (important in invisible mode)
  self.current_account = ""
  self.view.prepare()
  self.bind_other_events()
  if system == "Windows":
   self.set_systray_icon()

 def check_invisible_at_startup(self):
  # Visibility check. It does only work for windows.
  if system != "Windows": return
  if config.app["app-settings"]["hide_gui"] == True:
   self.show_hide()
   self.view.Show()
   self.view.Hide()
  # Invisible keyboard Shorcuts check.
  if config.app["app-settings"]["use_invisible_keyboard_shorcuts"] == True:
   km = self.create_invisible_keyboard_shorcuts()
   self.register_invisible_keyboard_shorcuts(km)

 def do_work(self):
  """ Creates the buffer objects for all accounts. This does not starts the buffer streams, only creates the objects."""
  log.debug("Creating buffers for all sessions...")
  for i in sessions.sessions:
   log.debug("Working on session %s" % (i,))
   if sessions.sessions[i].is_logged == False:
    self.create_ignored_session_buffer(sessions.sessions[i])
    continue
   self.create_buffers(sessions.sessions[i])

  # Connection checker executed each minute.
  self.checker_function = RepeatingTimer(60, self.check_connection)
  self.checker_function.start()
  self.save_db = RepeatingTimer(300, self.save_data_in_db)
  self.save_db.start()
  log.debug("Setting updates to buffers every %d seconds..." % (60*config.app["app-settings"]["update_period"],))
  self.update_buffers_function = RepeatingTimer(60*config.app["app-settings"]["update_period"], self.update_buffers)
  self.update_buffers_function.start()

 def start(self):
  """ Starts all buffer objects. Loads their items."""
  for i in sessions.sessions:
   if sessions.sessions[i].is_logged == False: continue
   self.start_buffers(sessions.sessions[i])
   self.set_buffer_positions(sessions.sessions[i])
  if config.app["app-settings"]["play_ready_sound"] == True:
   sessions.sessions[list(sessions.sessions.keys())[0]].sound.play("ready.ogg")
  if config.app["app-settings"]["speak_ready_msg"] == True:
   output.speak(_(u"Ready"))
  self.started = True

 def create_ignored_session_buffer(self, session):
  self.accounts.append(session.settings["twitter"]["user_name"])
  account = baseBuffers.accountPanel(self.view.nb, session.settings["twitter"]["user_name"], session.settings["twitter"]["user_name"], session.session_id)
  account.logged = False
  account.setup_account()
  self.buffers.append(account)
  self.view.add_buffer(account.buffer , name=session.settings["twitter"]["user_name"])

 def login_account(self, session_id):
  for i in sessions.sessions:
   if sessions.sessions[i].session_id == session_id: session = sessions.sessions[i]
  session.login()
  session.db = dict()
  self.create_buffers(session, False)
  self.start_buffers(session)

 def create_buffers(self, session, createAccounts=True):
  """ Generates buffer objects for an user account.
  session SessionObject: a sessionmanager.session.Session Object"""
  session.get_user_info()
  if createAccounts == True:
   self.accounts.append(session.db["user_name"])
   account = baseBuffers.accountPanel(self.view.nb, session.db["user_name"], session.db["user_name"], session.session_id)
   account.setup_account()
   self.buffers.append(account)
   self.view.add_buffer(account.buffer , name=session.db["user_name"])
  for i in session.settings['general']['buffer_order']:
   if i == 'home':
    home = twitterBuffers.baseBufferController(self.view.nb, "get_home_timeline", "home_timeline", session, session.db["user_name"], sound="tweet_received.ogg", tweet_mode="extended")
    self.buffers.append(home)
    self.view.insert_buffer(home.buffer, name=_(u"Home"), pos=self.view.search(session.db["user_name"], session.db["user_name"]))
   elif i == 'mentions':
    mentions = twitterBuffers.baseBufferController(self.view.nb, "get_mentions_timeline", "mentions", session, session.db["user_name"], sound="mention_received.ogg", tweet_mode="extended")
    self.buffers.append(mentions)
    self.view.insert_buffer(mentions.buffer, name=_(u"Mentions"), pos=self.view.search(session.db["user_name"], session.db["user_name"]))
   elif i == 'dm':
    dm = twitterBuffers.directMessagesController(self.view.nb, "get_direct_messages", "direct_messages", session, session.db["user_name"], bufferType="dmPanel", compose_func="compose_direct_message", sound="dm_received.ogg", full_text=True, items="events")
    self.buffers.append(dm)
    self.view.insert_buffer(dm.buffer, name=_(u"Direct messages"), pos=self.view.search(session.db["user_name"], session.db["user_name"]))
   elif i == 'sent_dm':
    sent_dm = twitterBuffers.sentDirectMessagesController(self.view.nb, "", "sent_direct_messages", session, session.db["user_name"], bufferType="dmPanel", compose_func="compose_direct_message")
    self.buffers.append(sent_dm)
    self.view.insert_buffer(sent_dm.buffer, name=_(u"Sent direct messages"), pos=self.view.search(session.db["user_name"], session.db["user_name"]))
   elif i == 'sent_tweets':
    sent_tweets = twitterBuffers.baseBufferController(self.view.nb, "get_user_timeline", "sent_tweets", session, session.db["user_name"], screen_name=session.db["user_name"], tweet_mode="extended")
    self.buffers.append(sent_tweets)
    self.view.insert_buffer(sent_tweets.buffer, name=_(u"Sent tweets"), pos=self.view.search(session.db["user_name"], session.db["user_name"]))
   elif i == 'favorites':
    favourites = twitterBuffers.baseBufferController(self.view.nb, "get_favorites", "favourites", session, session.db["user_name"], sound="favourite.ogg", tweet_mode="extended")
    self.buffers.append(favourites)
    self.view.insert_buffer(favourites.buffer, name=_(u"Likes"), pos=self.view.search(session.db["user_name"], session.db["user_name"]))
   elif i == 'followers':
    followers = twitterBuffers.peopleBufferController(self.view.nb, "get_followers_list", "followers", session, session.db["user_name"], sound="update_followers.ogg", screen_name=session.db["user_name"])
    self.buffers.append(followers)
    self.view.insert_buffer(followers.buffer, name=_(u"Followers"), pos=self.view.search(session.db["user_name"], session.db["user_name"]))
   elif i == 'friends':
    friends = twitterBuffers.peopleBufferController(self.view.nb, "get_friends_list", "friends", session, session.db["user_name"], screen_name=session.db["user_name"])
    self.buffers.append(friends)
    self.view.insert_buffer(friends.buffer, name=_(u"Friends"), pos=self.view.search(session.db["user_name"], session.db["user_name"]))
   elif i == 'blocks':
    blocks = twitterBuffers.peopleBufferController(self.view.nb, "list_blocks", "blocked", session, session.db["user_name"])
    self.buffers.append(blocks)
    self.view.insert_buffer(blocks.buffer, name=_(u"Blocked users"), pos=self.view.search(session.db["user_name"], session.db["user_name"]))
   elif i == 'muted':
    muted = twitterBuffers.peopleBufferController(self.view.nb, "list_mutes", "muted", session, session.db["user_name"])
    self.buffers.append(muted)
    self.view.insert_buffer(muted.buffer, name=_(u"Muted users"), pos=self.view.search(session.db["user_name"], session.db["user_name"]))
  timelines = baseBuffers.emptyPanel(self.view.nb, "timelines", session.db["user_name"])
  self.buffers.append(timelines)
  self.view.insert_buffer(timelines.buffer , name=_(u"Timelines"), pos=self.view.search(session.db["user_name"], session.db["user_name"]))
  for i in session.settings["other_buffers"]["timelines"]:
   tl = twitterBuffers.baseBufferController(self.view.nb, "get_user_timeline", "%s-timeline" % (i,), session, session.db["user_name"], sound="tweet_timeline.ogg", bufferType=None, user_id=i, tweet_mode="extended")
   self.buffers.append(tl)
   self.view.insert_buffer(tl.buffer, name=_(u"Timeline for {}").format(i,), pos=self.view.search("timelines", session.db["user_name"]))
  favs_timelines = baseBuffers.emptyPanel(self.view.nb, "favs_timelines", session.db["user_name"])
  self.buffers.append(favs_timelines)
  self.view.insert_buffer(favs_timelines.buffer , name=_(u"Likes timelines"), pos=self.view.search(session.db["user_name"], session.db["user_name"]))
  for i in session.settings["other_buffers"]["favourites_timelines"]:
   tl = twitterBuffers.baseBufferController(self.view.nb, "get_favorites", "%s-favorite" % (i,), session, session.db["user_name"], bufferType=None, sound="favourites_timeline_updated.ogg", user_id=i, tweet_mode="extended")
   self.buffers.append(tl)
   self.view.insert_buffer(tl.buffer, name=_(u"Likes for {}").format(i,), pos=self.view.search("favs_timelines", session.db["user_name"]))
  followers_timelines = baseBuffers.emptyPanel(self.view.nb, "followers_timelines", session.db["user_name"])
  self.buffers.append(followers_timelines)
  self.view.insert_buffer(followers_timelines.buffer , name=_(u"Followers' Timelines"), pos=self.view.search(session.db["user_name"], session.db["user_name"]))
  for i in session.settings["other_buffers"]["followers_timelines"]:
   tl = twitterBuffers.peopleBufferController(self.view.nb, "get_followers_list", "%s-followers" % (i,), session, session.db["user_name"], sound="new_event.ogg", user_id=i)
   self.buffers.append(tl)
   self.view.insert_buffer(tl.buffer, name=_(u"Followers for {}").format(i,), pos=self.view.search("followers_timelines", session.db["user_name"]))
  friends_timelines = baseBuffers.emptyPanel(self.view.nb, "friends_timelines", session.db["user_name"])
  self.buffers.append(friends_timelines)
  self.view.insert_buffer(friends_timelines.buffer , name=_(u"Friends' Timelines"), pos=self.view.search(session.db["user_name"], session.db["user_name"]))
  for i in session.settings["other_buffers"]["friends_timelines"]:
   tl = twitterBuffers.peopleBufferController(self.view.nb, "get_friends_list", "%s-friends" % (i,), session, session.db["user_name"], sound="new_event.ogg", user_id=i)
   self.buffers.append(tl)
   self.view.insert_buffer(tl.buffer, name=_(u"Friends for {}").format(i,), pos=self.view.search("friends_timelines", session.db["user_name"]))
  lists = baseBuffers.emptyPanel(self.view.nb, "lists", session.db["user_name"])
  self.buffers.append(lists)
  self.view.insert_buffer(lists.buffer , name=_(u"Lists"), pos=self.view.search(session.db["user_name"], session.db["user_name"]))
  for i in session.settings["other_buffers"]["lists"]:
   tl = twitterBuffers.listBufferController(self.view.nb, "get_list_statuses", "%s-list" % (i,), session, session.db["user_name"], bufferType=None, sound="list_tweet.ogg", list_id=utils.find_list(i, session.db["lists"]), tweet_mode="extended")
   session.lists.append(tl)
   self.buffers.append(tl)
   self.view.insert_buffer(tl.buffer, name=_(u"List for {}").format(i), pos=self.view.search("lists", session.db["user_name"]))
  searches = baseBuffers.emptyPanel(self.view.nb, "searches", session.db["user_name"])
  self.buffers.append(searches)
  self.view.insert_buffer(searches.buffer , name=_(u"Searches"), pos=self.view.search(session.db["user_name"], session.db["user_name"]))
  for i in session.settings["other_buffers"]["tweet_searches"]:
   tl = twitterBuffers.searchBufferController(self.view.nb, "search", "%s-searchterm" % (i,), session, session.db["user_name"], bufferType="searchPanel", sound="search_updated.ogg", q=i, tweet_mode="extended")
   self.buffers.append(tl)
   self.view.insert_buffer(tl.buffer, name=_(u"Search for {}").format(i), pos=self.view.search("searches", session.db["user_name"]))
  for i in session.settings["other_buffers"]["trending_topic_buffers"]:
   buffer = twitterBuffers.trendsBufferController(self.view.nb, "%s_tt" % (i,), session, session.db["user_name"], i, sound="trends_updated.ogg")
   buffer.start_stream(play_sound=False)
   buffer.searchfunction = self.search
   self.buffers.append(buffer)
   self.view.insert_buffer(buffer.buffer, name=_(u"Trending topics for %s") % (buffer.name_), pos=self.view.search(session.db["user_name"], session.db["user_name"]))

 def set_buffer_positions(self, session):
  "Sets positions for buffers if values exist in the database."
  for i in self.buffers:
   if i.account == session.db["user_name"] and i.name+"_pos" in session.db and hasattr(i.buffer,'list'):
    i.buffer.list.select_item(session.db[str(i.name+"_pos")])

 def logout_account(self, session_id):
  for i in sessions.sessions:
   if sessions.sessions[i].session_id == session_id: session = sessions.sessions[i]
  user = session.db["user_name"]
  delete_buffers = []
  for i in self.buffers:
   if i.account == user and i.name != user:
    delete_buffers.append(i.name)
  for i in delete_buffers:
   self.destroy_buffer(i, user)
  session.db = None

 def destroy_buffer(self, buffer_name, account):
  buffer = self.search_buffer(buffer_name, account)
  if buffer == None: return
  buff = self.view.search(buffer.name, buffer.account)
  if buff == None: return
  self.view.delete_buffer(buff)
  self.buffers.remove(buffer)
  del buffer

 def search_topic(self, term):
  self.search(value=term)

 def search(self, event=None, value="", *args, **kwargs):
  """ Searches words or users in twitter. This creates a new buffer containing the search results."""
  log.debug("Creating a new search...")
  dlg = dialogs.search.searchDialog(value)
  if dlg.get_response() == widgetUtils.OK and dlg.get("term") != "":
   term = dlg.get("term")
   buffer = self.get_best_buffer()
   if dlg.get("tweets") == True:
    if term not in buffer.session.settings["other_buffers"]["tweet_searches"]:
     buffer.session.settings["other_buffers"]["tweet_searches"].append(term)
     buffer.session.settings.write()
     args = {"lang": dlg.get_language(), "result_type": dlg.get_result_type()}
     search = twitterBuffers.searchBufferController(self.view.nb, "search", "%s-searchterm" % (term,), buffer.session, buffer.session.db["user_name"], bufferType="searchPanel", sound="search_updated.ogg", q=term, tweet_mode="extended", **args)
    else:
     log.error("A buffer for the %s search term is already created. You can't create a duplicate buffer." % (term,))
     return
   elif dlg.get("users") == True:
    search = twitterBuffers.searchPeopleBufferController(self.view.nb, "search_users", "%s-searchUser" % (term,), buffer.session, buffer.session.db["user_name"], bufferType=None, sound="search_updated.ogg", q=term)
   search.start_stream(mandatory=True)
   pos=self.view.search("searches", buffer.session.db["user_name"])
   self.insert_buffer(search, pos)
   self.view.insert_buffer(search.buffer, name=_(u"Search for {}").format(term), pos=pos)
  dlg.Destroy()

 def find(self, *args, **kwargs):
  if 'string' in kwargs:
   string=kwargs['string']
  else:
   string=''
  dlg = dialogs.find.findDialog(string)
  if dlg.get_response() == widgetUtils.OK and dlg.get("string") != "":
   string = dlg.get("string")
  #If we still have an empty string for some reason (I.E. user clicked cancel, etc), return here.
  if string == '':
   log.debug("Find canceled.")
   return
  page = self.get_current_buffer()
  if not hasattr(page.buffer, "list"):
   output.speak(_(u"No session is currently in focus. Focus a session with the next or previous session shortcut."), True)
   return
  count = page.buffer.list.get_count()
  if count < 1:
   output.speak(_(u"Empty buffer."), True)
   return
  start = page.buffer.list.get_selected()
  for i in range(start, count):
   if string.lower() in page.buffer.list.get_text_column(i, 1).lower():
    page.buffer.list.select_item(i)
    return output.speak(page.get_message(), True)
  output.speak(_(u"{0} not found.").format(string,), True)

 def filter(self, *args, **kwargs):
  page = self.get_current_buffer()
  if not hasattr(page.buffer, "list"):
   output.speak(_(u"No session is currently in focus. Focus a session with the next or previous session shortcut."), True)
   return
  # Let's prevent filtering of some buffers (people buffers, direct messages, events and sent items).
  # ToDo: Remove events from here after August 16.
  if (page.name == "direct_messages" or page.name == "sent_tweets" or page.name == "events") or page.type == "people":
   output.speak(_(u"Filters cannot be applied on this buffer"))
   return
  new_filter = filterController.filter(page)

 def manage_filters(self, *args, **kwargs):
  page = self.get_best_buffer()
  manage_filters = filterController.filterManager(page.session)

 def seekLeft(self, *args, **kwargs):
  try:
   sound.URLPlayer.seek(-5000)
  except:
   output.speak("Unable to seek.",True)

 def seekRight(self, *args, **kwargs):
  try:
   sound.URLPlayer.seek(5000)
  except:
   output.speak("Unable to seek.",True)

 def edit_keystrokes(self, *args, **kwargs):
  editor = keystrokeEditor.KeystrokeEditor()
  if editor.changed == True:
   config.keymap.write()
   register = False
   # determines if we need to reassign the keymap.
   if self.showing == False:
    register = True
   elif config.app["app-settings"]["use_invisible_keyboard_shorcuts"] == True:
    register = True
   # If there is a keyboard handler instance we need unregister all old keystrokes before register the new ones.
   if hasattr(self, "keyboard_handler"):
    keymap = {}
    for i in editor.hold_map:
     if hasattr(self, i): keymap[editor.hold_map[i]] = getattr(self, i)
    self.unregister_invisible_keyboard_shorcuts(keymap)
   self.invisible_shorcuts_changed(registered=register)

 def learn_sounds(self, *args, **kwargs):
  """ Opens the sounds tutorial for the current account."""
  buffer = self.get_best_buffer()
  SoundsTutorial.soundsTutorial(buffer.session)

 def view_user_lists(self, *args, **kwargs):
  buff = self.get_best_buffer()
  if not hasattr(buff, "get_right_tweet"): return
  tweet = buff.get_right_tweet()
  if buff.type == "people":
   users = [tweet["screen_name"]]
  elif buff.type == "dm":
   users = [buff.session.get_user(tweet["message_create"]["sender_id"])["screen_name"]]
  else:
   users = utils.get_all_users(tweet, buff.session.db)
  dlg = dialogs.utils.selectUserDialog(_(u"Select the user"), users)
  if dlg.get_response() == widgetUtils.OK:
   user = dlg.get_user()
  else:
   return
  l = listsController.listsController(buff.session, user=user)

 def add_to_list(self, *args, **kwargs):
  buff = self.get_best_buffer()
  if not hasattr(buff, "get_right_tweet"): return
  tweet = buff.get_right_tweet()
  if buff.type == "people":
   users = [tweet["screen_name"]]
  elif buff.type == "dm":
   users = [buff.session.get_user(tweet["message_create"]["sender_id"])["screen_name"]]
  else:
   users = utils.get_all_users(tweet, buff.session.db)
  dlg = dialogs.utils.selectUserDialog(_(u"Select the user"), users)
  if dlg.get_response() == widgetUtils.OK:
   user = dlg.get_user()
  else:
   return
  dlg = dialogs.lists.addUserListDialog()
  dlg.populate_list([compose.compose_list(item) for item in buff.session.db["lists"]])
  if dlg.get_response() == widgetUtils.OK:
   try:
    list = buff.session.twitter.add_list_member(list_id=buff.session.db["lists"][dlg.get_item()]["id"], screen_name=user)
    older_list = utils.find_item(buff.session.db["lists"][dlg.get_item()]["id"], buff.session.db["lists"])
    listBuffer = self.search_buffer("%s-list" % (buff.session.db["lists"][dlg.get_item()]["name"].lower()), buff.session.db["user_name"])
    if listBuffer != None: listBuffer.get_user_ids()
    buff.session.db["lists"].pop(older_list)
    buff.session.db["lists"].append(list)
   except TwythonError as e:
    output.speak("error %s: %s" % (e.error_code, e.msg))

 def remove_from_list(self, *args, **kwargs):
  buff = self.get_best_buffer()
  if not hasattr(buff, "get_right_tweet"): return
  tweet = buff.get_right_tweet()
  if buff.type == "people":
   users = [tweet["screen_name"]]
  elif buff.type == "dm":
   users = [buff.session.get_user(tweet["message_create"]["sender_id"])["screen_name"]]
  else:
   users = utils.get_all_users(tweet, buff.session.db)
  dlg = dialogs.utils.selectUserDialog(_(u"Select the user"), users)
  if dlg.get_response() == widgetUtils.OK:
   user = dlg.get_user()
  else:
   return
  dlg = dialogs.lists.removeUserListDialog()
  dlg.populate_list([compose.compose_list(item) for item in buff.session.db["lists"]])
  if dlg.get_response() == widgetUtils.OK:
   try:
    list = buff.session.twitter.delete_list_member(list_id=buff.session.db["lists"][dlg.get_item()]["id"], screen_name=user)
    older_list = utils.find_item(buff.session.db["lists"][dlg.get_item()]["id"], buff.session.db["lists"])
    listBuffer = self.search_buffer("%s-list" % (buff.session.db["lists"][dlg.get_item()]["name"].lower()), buff.session.db["user_name"])
    if listBuffer != None: listBuffer.get_user_ids()
    buff.session.db["lists"].pop(older_list)
    buff.session.db["lists"].append(list)
   except TwythonError as e:
    output.speak("error %s: %s" % (e.error_code, e.msg))

 def list_manager(self, *args, **kwargs):
  s = self.get_best_buffer().session
  l = listsController.listsController(s)

 def configuration(self, *args, **kwargs):
  """ Opens the global settings dialogue."""
  d = settings.globalSettingsController()
  if d.response == widgetUtils.OK:
   d.save_configuration()
   if d.needs_restart == True:
    commonMessageDialogs.needs_restart()
    restart.restart_program()

 def accountConfiguration(self, *args, **kwargs):
  """ Opens the account settings dialogue for the current account."""
  buff = self.get_best_buffer()
  manager.manager.set_current_session(buff.session.session_id)
  d = settings.accountSettingsController(buff, self)
  if d.response == widgetUtils.OK:
   d.save_configuration()
   if d.needs_restart == True:
    commonMessageDialogs.needs_restart()
    buff.session.settings.write()
    restart.restart_program()

 def report_error(self, *args, **kwargs):
  r = issueReporter.reportBug(self.get_best_buffer().session.db["user_name"])

 def check_for_updates(self, *args, **kwargs):
  update = updater.do_update()
  if update == False:
   view.no_update_available()

 def delete(self, *args, **kwargs):
  """ Deletes an item in the current buffer.
  Users can only remove their tweets and direct messages, other users' tweets and people (followers, friends, blocked, etc) can not be removed using this method."""
  buffer = self.view.get_current_buffer()
  if hasattr(buffer, "account"):
   buffer = self.search_buffer(buffer.name, buffer.account)
   buffer.destroy_status()

 def exit(self, *args, **kwargs):
  if config.app["app-settings"]["ask_at_exit"] == True:
   answer = commonMessageDialogs.exit_dialog(self.view)
   if answer == widgetUtils.YES:
    self.exit_()
  else:
   self.exit_()

 def exit_(self, *args, **kwargs):
  for i in self.buffers: i.save_positions()
  log.debug("Exiting...")
  log.debug("Saving global configuration...")
  for item in sessions.sessions:
   if sessions.sessions[item].logged == False: continue
   log.debug("Disconnecting streams for %s session" % (sessions.sessions[item].session_id,))
   sessions.sessions[item].sound.cleaner.cancel()
   log.debug("Shelving database for " +    sessions.sessions[item].session_id)
   sessions.sessions[item].shelve()
  if system == "Windows":
   self.systrayIcon.RemoveIcon()
   pidpath = os.path.join(os.getenv("temp"), "{}.pid".format(application.name))
   if os.path.exists(pidpath):
    os.remove(pidpath)
  widgetUtils.exit_application()

 def follow(self, *args, **kwargs):
  buff = self.get_current_buffer()
  if not hasattr(buff, "get_right_tweet"): return
  tweet = buff.get_right_tweet()
  if buff.type == "people":
   users = [tweet["screen_name"]]
  elif buff.type == "dm":
   users = [buff.session.get_user(tweet["message_create"]["sender_id"])["screen_name"]]
  else:
   users = utils.get_all_users(tweet, buff.session.db)
  u = userActionsController.userActionsController(buff, users)

 def unfollow(self, *args, **kwargs):
  buff = self.get_current_buffer()
  if not hasattr(buff, "get_right_tweet"): return
  tweet = buff.get_right_tweet()
  if buff.type == "people":
   users = [tweet["screen_name"]]
  elif buff.type == "dm":
   users = [buff.session.get_user(tweet["message_create"]["sender_id"])["screen_name"]]
  else:
   users = utils.get_all_users(tweet, buff.session.db)
  u = userActionsController.userActionsController(buff, users, "unfollow")

 def mute(self, *args, **kwargs):
  buff = self.get_current_buffer()
  if not hasattr(buff, "get_right_tweet"): return
  tweet = buff.get_right_tweet()
  if buff.type == "people":
   users = [tweet["screen_name"]]
  elif buff.type == "dm":
   users = [buff.session.get_user(tweet["message_create"]["sender_id"])["screen_name"]]
  else:
   users = utils.get_all_users(tweet, buff.session.db)
  u = userActionsController.userActionsController(buff, users, "mute")

 def unmute(self, *args, **kwargs):
  buff = self.get_current_buffer()
  if not hasattr(buff, "get_right_tweet"): return
  tweet = buff.get_right_tweet()
  if buff.type == "people":
   users = [tweet["screen_name"]]
  elif buff.type == "dm":
   users = [buff.session.get_user(tweet["message_create"]["sender_id"])["screen_name"]]
  else:
   users = utils.get_all_users(tweet, buff.session.db)
  u = userActionsController.userActionsController(buff, users, "unmute")

 def block(self, *args, **kwargs):
  buff = self.get_current_buffer()
  if not hasattr(buff, "get_right_tweet"): return
  tweet = buff.get_right_tweet()
  if buff.type == "people":
   users = [tweet["screen_name"]]
  elif buff.type == "dm":
   users = [buff.session.get_user(tweet["message_create"]["sender_id"])["screen_name"]]
  else:
   users = utils.get_all_users(tweet, buff.session.db)
  u = userActionsController.userActionsController(buff, users, "block")

 def unblock(self, *args, **kwargs):
  buff = self.get_current_buffer()
  if not hasattr(buff, "get_right_tweet"): return
  tweet = buff.get_right_tweet()
  if buff.type == "people":
   users = [tweet["screen_name"]]
  elif buff.type == "dm":
   users = [buff.session.get_user(tweet["message_create"]["sender_id"])["screen_name"]]
  else:
   users = utils.get_all_users(tweet, buff.session.db)
  u = userActionsController.userActionsController(buff, users, "unblock")

 def report(self, *args, **kwargs):
  buff = self.get_current_buffer()
  if not hasattr(buff, "get_right_tweet"): return
  tweet = buff.get_right_tweet()
  if buff.type == "people":
   users = [tweet["screen_name"]]
  elif buff.type == "dm":
   users = [buff.session.get_user(tweet["message_create"]["sender_id"])["screen_name"]]
  else:
   users = utils.get_all_users(tweet, buff.session.db)
  u = userActionsController.userActionsController(buff, users, "report")

 def post_tweet(self, event=None):
  buffer = self.get_best_buffer()
  buffer.post_status()

 def post_reply(self, *args, **kwargs):
  buffer = self.get_current_buffer()
  if buffer.name == "direct_messages":
   buffer.send_message()
  else:
   buffer.reply()

 def send_dm(self, *args, **kwargs):
  buffer = self.get_current_buffer()
  buffer.send_message()

 def post_retweet(self, *args, **kwargs):
  buffer = self.get_current_buffer()
  if buffer.type == "dm" or buffer.type == "people" or buffer.type == "events":
   return
  else:
   buffer.share_item()

 def add_to_favourites(self, *args, **kwargs):
  buffer = self.get_current_buffer()
  if buffer.type == "dm" or buffer.type == "people" or buffer.type == "events":
   return
  else:
   id = buffer.get_tweet()["id"]
   call_threaded(buffer.session.api_call, call_name="create_favorite", _sound="favourite.ogg", id=id)

 def remove_from_favourites(self, *args, **kwargs):
  buffer = self.get_current_buffer()
  if buffer.type == "dm" or buffer.type == "people" or buffer.type == "events":
   return
  else:
   id = buffer.get_tweet()["id"]
   call_threaded(buffer.session.api_call, call_name="destroy_favorite", id=id)

 def toggle_like(self, *args, **kwargs):
  buffer = self.get_current_buffer()
  if buffer.type == "dm" or buffer.type == "people" or buffer.type == "events":
   return
  else:
   id = buffer.get_tweet()["id"]
   tweet = buffer.session.twitter.show_status(id=id, include_ext_alt_text=True, tweet_mode="extended")
   if tweet["favorited"] == False:
    call_threaded(buffer.session.api_call, call_name="create_favorite", _sound="favourite.ogg", id=id)
   else:
    call_threaded(buffer.session.api_call, call_name="destroy_favorite", id=id)

 def view_item(self, *args, **kwargs):
  buffer = self.get_current_buffer()
  if buffer.type == "account" or buffer.type == "empty":
   return
  elif buffer.type == "baseBuffer" or buffer.type == "favourites_timeline" or buffer.type == "list" or buffer.type == "search":
   tweet, tweetsList = buffer.get_full_tweet()
   msg = messages.viewTweet(tweet, tweetsList, utc_offset=buffer.session.db["utc_offset"])
  elif buffer.type == "dm":
   non_tweet = buffer.get_formatted_message()
   item = buffer.get_right_tweet()
   original_date = arrow.get(int(item["created_timestamp"][:-3]))
   date = original_date.shift(seconds=buffer.session.db["utc_offset"]).format(_(u"MMM D, YYYY. H:m"), locale=languageHandler.getLanguage())
   msg = messages.viewTweet(non_tweet, [], False, date=date)
  else:
   non_tweet = buffer.get_formatted_message()
   msg = messages.viewTweet(non_tweet, [], False)

 def open_in_browser(self, *args, **kwargs):
  buffer = self.get_current_buffer()
  if hasattr(buffer, "open_in_browser"):
   buffer.open_in_browser()

 def open_favs_timeline(self, *args, **kwargs):
  self.open_timeline(default="favourites")

 def open_timeline(self, default="tweets", *args, **kwargs):
  buff = self.get_best_buffer()
  if not hasattr(buff, "get_right_tweet"): return
  tweet = buff.get_right_tweet()
  if buff.type == "people":
   users = [tweet["screen_name"]]
  elif buff.type == "dm":
   users = [buff.session.get_user(tweet["message_create"]["sender_id"])["screen_name"]]
  else:
   users = utils.get_all_users(tweet, buff.session.db)
  dlg = dialogs.userSelection.selectUserDialog(users=users, default=default)
  if dlg.get_response() == widgetUtils.OK:
   usr = utils.if_user_exists(buff.session.twitter, dlg.get_user())
   if usr != None:
    if usr == dlg.get_user():
     commonMessageDialogs.suspended_user()
     return
    if usr["protected"] == True:
     if usr["following"] == False:
      commonMessageDialogs.no_following()
      return
    tl_type = dlg.get_action()
    if tl_type  == "tweets":
     if usr["statuses_count"] == 0:
      commonMessageDialogs.no_tweets()
      return
     if usr["id_str"] in buff.session.settings["other_buffers"]["timelines"]:
      commonMessageDialogs.timeline_exist()
      return
     tl = twitterBuffers.baseBufferController(self.view.nb, "get_user_timeline", "%s-timeline" % (usr["id_str"],), buff.session, buff.session.db["user_name"], bufferType=None, sound="tweet_timeline.ogg", user_id=usr["id_str"], tweet_mode="extended")
     try:
      tl.start_stream(play_sound=False)
     except TwythonAuthError:
      commonMessageDialogs.unauthorized()
      return
     pos=self.view.search("timelines", buff.session.db["user_name"])
     self.insert_buffer(tl, pos+1)
     self.view.insert_buffer(tl.buffer, name=_(u"Timeline for {}").format(dlg.get_user()), pos=pos)
     buff.session.settings["other_buffers"]["timelines"].append(usr["id_str"])
     pub.sendMessage("buffer-title-changed", buffer=tl)
     buff.session.sound.play("create_timeline.ogg")
    elif tl_type == "favourites":
     if usr["favourites_count"] == 0:
      commonMessageDialogs.no_favs()
      return
     if usr["id_str"] in buff.session.settings["other_buffers"]["favourites_timelines"]:
      commonMessageDialogs.timeline_exist()
      return
     tl = twitterBuffers.baseBufferController(self.view.nb, "get_favorites", "%s-favorite" % (usr["id_str"],), buff.session, buff.session.db["user_name"], bufferType=None, sound="favourites_timeline_updated.ogg", user_id=usr["id_str"], tweet_mode="extended")
     try:
      tl.start_stream(play_sound=False)
     except TwythonAuthError:
      commonMessageDialogs.unauthorized()
      return
     pos=self.view.search("favs_timelines", buff.session.db["user_name"])
     self.insert_buffer(tl, pos+1)
     self.view.insert_buffer(buffer=tl.buffer, name=_(u"Likes for {}").format(dlg.get_user()), pos=pos)
     buff.session.settings["other_buffers"]["favourites_timelines"].append(usr["id_str"])
     pub.sendMessage("buffer-title-changed", buffer=buff)
     buff.session.sound.play("create_timeline.ogg")
    elif tl_type == "followers":
     if usr["followers_count"] == 0:
      commonMessageDialogs.no_followers()
      return
     if usr["id_str"] in buff.session.settings["other_buffers"]["followers_timelines"]:
      commonMessageDialogs.timeline_exist()
      return
     tl = twitterBuffers.peopleBufferController(self.view.nb, "get_followers_list", "%s-followers" % (usr["id_str"],), buff.session, buff.session.db["user_name"], sound="new_event.ogg", user_id=usr["id_str"])
     try:
      tl.start_stream(play_sound=False)
     except TwythonAuthError:
      commonMessageDialogs.unauthorized()
      return
     pos=self.view.search("followers_timelines", buff.session.db["user_name"])
     self.insert_buffer(tl, pos+1)
     self.view.insert_buffer(buffer=tl.buffer, name=_(u"Followers for {}").format(dlg.get_user()), pos=pos)
     buff.session.settings["other_buffers"]["followers_timelines"].append(usr["id_str"])
     buff.session.sound.play("create_timeline.ogg")
     pub.sendMessage("buffer-title-changed", buffer=i)
    elif tl_type == "friends":
     if usr["friends_count"] == 0:
      commonMessageDialogs.no_friends()
      return
     if usr["id_str"] in buff.session.settings["other_buffers"]["friends_timelines"]:
      commonMessageDialogs.timeline_exist()
      return
     tl = twitterBuffers.peopleBufferController(self.view.nb, "get_friends_list", "%s-friends" % (usr["id_str"],), buff.session, buff.session.db["user_name"], sound="new_event.ogg", user_id=usr["id_str"])
     try:
      tl.start_stream(play_sound=False)
     except TwythonAuthError:
      commonMessageDialogs.unauthorized()
      return
     pos=self.view.search("friends_timelines", buff.session.db["user_name"])
     self.insert_buffer(tl, pos+1)
     self.view.insert_buffer(buffer=tl.buffer, name=_(u"Friends for {}").format(dlg.get_user()), pos=pos)
     buff.session.settings["other_buffers"]["friends_timelines"].append(usr["id_str"])
     buff.session.sound.play("create_timeline.ogg")
     pub.sendMessage("buffer-title-changed", buffer=i)
   else:
    commonMessageDialogs.user_not_exist()
  buff.session.settings.write()

 def open_conversation(self, *args, **kwargs):
  buffer = self.get_current_buffer()
  id = buffer.get_right_tweet()["id_str"]
  user = buffer.get_right_tweet()["user"]["screen_name"]
  search = twitterBuffers.conversationBufferController(self.view.nb, "search", "%s-searchterm" % (id,), buffer.session, buffer.session.db["user_name"], bufferType="searchPanel", sound="search_updated.ogg", since_id=id, q="@{0}".format(user,))
  search.tweet = buffer.get_right_tweet()
  search.start_stream(start=True)
  pos=self.view.search("searches", buffer.session.db["user_name"])
  self.insert_buffer(search, pos)
  self.view.insert_buffer(search.buffer, name=_(u"Conversation with {0}").format(user), pos=pos)

 def show_hide(self, *args, **kwargs):
  km = self.create_invisible_keyboard_shorcuts()
  if self.showing == True:
   if config.app["app-settings"]["use_invisible_keyboard_shorcuts"] == False:
    self.register_invisible_keyboard_shorcuts(km)
   self.view.Hide()
   self.fix_wrong_buffer()
   self.showing = False
  else:
   if config.app["app-settings"]["use_invisible_keyboard_shorcuts"] == False:
    self.unregister_invisible_keyboard_shorcuts(km)
   self.view.Show()
   self.showing = True

 def get_trending_topics(self, *args, **kwargs):
  buff = self.get_best_buffer()
  trends = trendingTopics.trendingTopicsController(buff.session)
  if trends.dialog.get_response() == widgetUtils.OK:
   woeid = trends.get_woeid()
   if woeid in buff.session.settings["other_buffers"]["trending_topic_buffers"]: return
   buffer = twitterBuffers.trendsBufferController(self.view.nb, "%s_tt" % (woeid,), buff.session, buff.account, woeid, sound="trends_updated.ogg")
   buffer.searchfunction = self.search
   pos=self.view.search(buff.session.db["user_name"], buff.session.db["user_name"])
   self.view.insert_buffer(buffer.buffer, name=_(u"Trending topics for %s") % (trends.get_string()), pos=pos)
   self.buffers.append(buffer)
   buffer.start_stream()
   buffer.session.settings["other_buffers"]["trending_topic_buffers"].append(woeid)
   buffer.session.settings.write()

 def reverse_geocode(self, event=None):
  try:
   tweet = self.get_current_buffer().get_tweet()
   if tweet["coordinates"] != None:
    x = tweet["coordinates"]["coordinates"][0]
    y = tweet["coordinates"]["coordinates"][1]
    address = geocoder.reverse_geocode(y, x, language = languageHandler.curLang)
    if event == None: output.speak(address[0].__str__())
    else: self.view.show_address(address[0].__str__())
   else:
    output.speak(_(u"There are no coordinates in this tweet"))
  except GeocoderError:
   output.speak(_(u"There are no results for the coordinates in this tweet"))
  except ValueError:
   output.speak(_(u"Error decoding coordinates. Try again later."))
  except KeyError:
   pass
  except AttributeError:
   pass

 def view_reverse_geocode(self, event=None):
  try:
   tweet = self.get_current_buffer().get_right_tweet()
   if tweet["coordinates"] != None:
    x = tweet["coordinates"]["coordinates"][0]
    y = tweet["coordinates"]["coordinates"][1]
    address = geocoder.reverse_geocode(y, x, language = languageHandler.curLang)
    dlg = commonMessageDialogs.view_geodata(address[0].__str__())
   else:
    output.speak(_(u"There are no coordinates in this tweet"))
  except GeocoderError:
   output.speak(_(u"There are no results for the coordinates in this tweet"))
  except ValueError:
   output.speak(_(u"Error decoding coordinates. Try again later."))
  except KeyError:
   pass
  except AttributeError:
   pass

 def get_more_items(self, *args, **kwargs):
  self.get_current_buffer().get_more_items()

 def clear_buffer(self, *args, **kwargs):
  self.get_current_buffer().clear_list()

 def remove_buffer(self, *args, **kwargs):
  buffer = self.get_current_buffer()
  if not hasattr(buffer, "account"): return
  buff = self.view.search(buffer.name, buffer.account)
  answer = buffer.remove_buffer()
  if answer == False: return
  log.debug("destroying buffer...")
  if hasattr(buffer, "timer"):
   log.debug("Stopping timer...")
   buffer.timer.cancel()
   log.debug("Timer cancelled.")
  self.right()
  self.view.delete_buffer(buff)
  buffer.session.sound.play("delete_timeline.ogg")
  self.buffers.remove(buffer)
  del buffer

 def skip_buffer(self, forward=True):
  buff = self.get_current_buffer()
  if buff.invisible == False:
   self.view.advance_selection(forward)

 def buffer_changed(self, *args, **kwargs):
  buffer = self.get_current_buffer()
  if buffer.account != self.current_account:
   self.current_account = buffer.account
  if not hasattr(buffer, "session") or buffer.session == None: return
  muted = autoread = False
  if buffer.name in buffer.session.settings["other_buffers"]["muted_buffers"]:
   muted = True
  elif buffer.name in buffer.session.settings["other_buffers"]["autoread_buffers"]:
   autoread = True
  self.view.check_menuitem("mute_buffer", muted)
  self.view.check_menuitem("autoread", autoread)

 def fix_wrong_buffer(self):
  buf = self.get_best_buffer()
  if buf == None:
   for i in self.accounts:
    buffer = self.view.search("home_timeline", i)
    if buffer != None: break
  else:
   buffer = self.view.search("home_timeline", buf.session.db["user_name"])
  if buffer!=None:
   self.view.change_buffer(buffer)

 def up(self, *args, **kwargs):
  page = self.get_current_buffer()
  if not hasattr(page.buffer, "list"):
   output.speak(_(u"No session is currently in focus. Focus a session with the next or previous session shortcut."), True)
   return
  position = page.buffer.list.get_selected()
  index = position-1
  try:
   page.buffer.list.select_item(index)
  except:
   pass
  if position == page.buffer.list.get_selected():
   page.session.sound.play("limit.ogg")

  try:
   output.speak(page.get_message(), True)
  except:
   pass

 def down(self, *args, **kwargs):
  page = self.get_current_buffer()
  if not hasattr(page.buffer, "list"):
   output.speak(_(u"No session is currently in focus. Focus a session with the next or previous session shortcut."), True)
   return
  position = page.buffer.list.get_selected()
  index = position+1
  try:
   page.buffer.list.select_item(index)
  except:
   pass
  if position == page.buffer.list.get_selected():
   page.session.sound.play("limit.ogg")
  try:
   output.speak(page.get_message(), True)
  except:
   pass

 def left(self, *args, **kwargs):
  buff = self.view.get_current_buffer_pos()
  buffer = self.get_current_buffer()
  if not hasattr(buffer.buffer, "list"):
   output.speak(_(u"No session is currently in focus. Focus a session with the next or previous session shortcut."), True)
   return
  if buff == self.get_first_buffer_index(buffer.account) or buff == 0:
   self.view.change_buffer(self.get_last_buffer_index(buffer.account))
  else:
   self.view.change_buffer(buff-1)
  while self.get_current_buffer().invisible == False: self.skip_buffer(False)
  buffer = self.get_current_buffer()
  if self.showing == True: buffer.buffer.set_focus_in_list()
  try:
   msg = _(u"%s, %s of %s") % (self.view.get_buffer_text(), buffer.buffer.list.get_selected()+1, buffer.buffer.list.get_count())
  except:
   msg = _(u"%s. Empty") % (self.view.get_buffer_text(),)
  output.speak(msg, True)

 def right(self, *args, **kwargs):
  buff = self.view.get_current_buffer_pos()
  buffer = self.get_current_buffer()
  if not hasattr(buffer.buffer, "list"):
   output.speak(_(u"No session is currently in focus. Focus a session with the next or previous session shortcut."), True)
   return
  if buff == self.get_last_buffer_index(buffer.account) or buff+1 == self.view.get_buffer_count():
   self.view.change_buffer(self.get_first_buffer_index(buffer.account))
  else:
   self.view.change_buffer(buff+1)
  while self.get_current_buffer().invisible == False: self.skip_buffer(True)
  buffer = self.get_current_buffer()
  if self.showing == True: buffer.buffer.set_focus_in_list()
  try:
   msg = _(u"%s, %s of %s") % (self.view.get_buffer_text(), buffer.buffer.list.get_selected()+1, buffer.buffer.list.get_count())
  except:
   msg = _(u"%s. Empty") % (self.view.get_buffer_text(),)
  output.speak(msg, True)

 def next_account(self, *args, **kwargs):
  index = self.accounts.index(self.current_account)
  if index+1 == len(self.accounts):
   index = 0
  else:
   index = index+1
  account = self.accounts[index]
  self.current_account = account
  buffer_object = self.get_first_buffer(account)
  if buffer_object == None:
   output.speak(_(u"{0}: This account is not logged into Twitter.").format(account), True)
   return
  buff = self.view.search(buffer_object.name, account)
  if buff == None:
   output.speak(_(u"{0}: This account is not logged into Twitter.").format(account), True)
   return
  self.view.change_buffer(buff)
  buffer = self.get_current_buffer()
  if self.showing == True: buffer.buffer.set_focus_in_list()
  try:
   msg = _(u"%s. %s, %s of %s") % (buffer.account, self.view.get_buffer_text(), buffer.buffer.list.get_selected()+1, buffer.buffer.list.get_count())
  except:
   msg = _(u"%s. Empty") % (self.view.get_buffer_text(),)
  output.speak(msg, True)

 def previous_account(self, *args, **kwargs):
  index = self.accounts.index(self.current_account)
  if index-1 < 0:
   index = len(self.accounts)-1
  else:
   index = index-1
  account = self.accounts[index]
  self.current_account = account
  buffer_object = self.get_first_buffer(account)
  if buffer_object == None:
   output.speak(_(u"{0}: This account is not logged into Twitter.").format(account), True)
   return
  buff = self.view.search(buffer_object.name, account)
  if buff == None:
   output.speak(_(u"{0}: This account is not logged into twitter.").format(account), True)
   return
  self.view.change_buffer(buff)
  buffer = self.get_current_buffer()
  if self.showing == True: buffer.buffer.set_focus_in_list()
  try:
   msg = _(u"%s. %s, %s of %s") % (buffer.account, self.view.get_buffer_text(), buffer.buffer.list.get_selected()+1, buffer.buffer.list.get_count())
  except:
   msg = _(u"%s. Empty") % (self.view.get_buffer_text(),)
  output.speak(msg, True)

 def go_home(self):
  buffer = self.get_current_buffer()
  buffer.buffer.list.select_item(0)
  try:
   output.speak(buffer.get_message(), True)
  except:
   pass

 def go_end(self):
  buffer = self.get_current_buffer()
  buffer.buffer.list.select_item(buffer.buffer.list.get_count()-1)
  try:
   output.speak(buffer.get_message(), True)
  except:
   pass

 def go_page_up(self):
  buffer = self.get_current_buffer()
  if buffer.buffer.list.get_selected() <= 20:
   index = 0
  else:
   index = buffer.buffer.list.get_selected() - 20
  buffer.buffer.list.select_item(index)
  try:
   output.speak(buffer.get_message(), True)
  except:
   pass

 def go_page_down(self):
  buffer = self.get_current_buffer()
  if buffer.buffer.list.get_selected() >= buffer.buffer.list.get_count() - 20:
   index = buffer.buffer.list.get_count()-1
  else:
   index = buffer.buffer.list.get_selected() + 20
  buffer.buffer.list.select_item(index)
  try:
   output.speak(buffer.get_message(), True)
  except:
   pass

 def url(self, *args, **kwargs):
  buffer = self.get_current_buffer()
  buffer.url()

 def audio(self, *args, **kwargs):
  self.get_current_buffer().audio()

 def volume_down(self, *args, **kwargs):
  self.get_current_buffer().volume_down()

 def volume_up(self, *args, **kwargs):
  self.get_current_buffer().volume_up()

 def create_invisible_keyboard_shorcuts(self):
  keymap = {}
  for i in config.keymap["keymap"]:
   if hasattr(self, i):
    keymap[config.keymap["keymap"][i]] = getattr(self, i)
  return keymap

 def register_invisible_keyboard_shorcuts(self, keymap):
  if config.changed_keymap:
   commonMessageDialogs.changed_keymap()
  self.keyboard_handler = WXKeyboardHandler(self.view)
  self.keyboard_handler.register_keys(keymap)

 def unregister_invisible_keyboard_shorcuts(self, keymap):
  try:
   self.keyboard_handler.unregister_keys(keymap)
   del self.keyboard_handler
  except AttributeError:
   pass

 def notify(self, session, play_sound=None, message=None, notification=False):
  if session.settings["sound"]["session_mute"] == True: return
  if play_sound != None:
   session.sound.play(play_sound)
  if message != None:
   output.speak(message, speech=session.settings["reporting"]["speech_reporting"], braille=session.settings["reporting"]["braille_reporting"])

 def manage_sent_dm(self, data, user):
  buffer = self.search_buffer("sent_direct_messages", user)
  if buffer == None: return
  play_sound = "dm_sent.ogg"
  if "sent_direct_messages" not in buffer.session.settings["other_buffers"]["muted_buffers"]:
   self.notify(buffer.session, play_sound=play_sound)
  buffer.add_new_item(data)

 def manage_sent_tweets(self, data, user):
  buffer = self.search_buffer("sent_tweets", user)
  if buffer == None: return
#  if "sent_tweets" not in buffer.session.settings["other_buffers"]["muted_buffers"]:
#   self.notify(buffer.session, play_sound=play_sound)
  data = buffer.session.check_quoted_status(data)
  data = buffer.session.check_long_tweet(data)
  if data == False: # Long tweet deleted from twishort.
   return 
  if buffer.session.settings["general"]["reverse_timelines"] == False:
   buffer.session.db[buffer.name].append(data)
  else:
   buffer.session.db[buffer.name].insert(0, data)
  buffer.add_new_item(data)

 def manage_friend(self, data, user):
  buffer = self.search_buffer("friends", user)
  if buffer == None: return
  buffer.add_new_item(data)

 def manage_unfollowing(self, item, user):
  buffer = self.search_buffer("friends", user)
  if buffer == None: return
  buffer.remove_item(item)

 def manage_favourite(self, data, user):
  buffer = self.search_buffer("favourites", user)
  if buffer == None: return
  play_sound = "favourite.ogg"
  if "favourites" not in buffer.session.settings["other_buffers"]["muted_buffers"]:
   self.notify(buffer.session, play_sound=play_sound)
  buffer.add_new_item(data)

 def manage_unfavourite(self, item, user):
  buffer = self.search_buffer("favourites", user)
  if buffer == None: return
  buffer.remove_item(item)

 def manage_blocked_user(self, data, user):
  buffer = self.search_buffer("blocked", user)
  if buffer == None: return
  buffer.add_new_item(data)

 def manage_unblocked_user(self, item, user):
  buffer = self.search_buffer("blocked", user)
  if buffer == None: return
  buffer.remove_item(item)

 def start_buffers(self, session):
  log.debug("starting buffers... Session %s" % (session.session_id,))
  for i in self.buffers:
   if i.session == session and i.needs_init == True:
    if hasattr(i, "finished_timeline") and i.finished_timeline == False:
     change_title = True
    else:
     change_title = False
    try:
     if "mentions" in i.name or "direct_messages" in i.name:
      i.start_stream()
     else:
      i.start_stream(play_sound=False)
    except TwythonAuthError:
     buff = self.view.search(i.name, i.account)
     i.remove_buffer(force=True)
     commonMessageDialogs.blocked_timeline()
     if self.get_current_buffer() == i:
      self.right()
     self.view.delete_buffer(buff)
     self.buffers.remove(i)
     del i
     continue
    if change_title:
     pub.sendMessage("buffer-title-changed", buffer=i)

 def set_positions(self):
  for i in sessions.sessions:
   self.set_buffer_positions(i)

 def check_connection(self):
  if self.started == False:
   return
  for i in sessions.sessions:
   try:
    if sessions.sessions[i].is_logged == False: continue
    sessions.sessions[i].check_connection()
   except TwythonError: # We shouldn't allow this function to die.
    pass

 def create_new_buffer(self, buffer, account, create):
  buff = self.search_buffer("home_timeline", account)
  if create == True:
   if buffer == "favourites":
    favourites = twitterBuffers.baseBufferController(self.view.nb, "get_favorites", "favourites", buff.session, buff.session.db["user_name"], tweet_mode="extended")
    self.buffers.append(favourites)
    self.view.insert_buffer(favourites.buffer, name=_(u"Likes"), pos=self.view.search(buff.session.db["user_name"], buff.session.db["user_name"]))
    favourites.start_stream(play_sound=False)
   if buffer == "followers":
    followers = twitterBuffers.peopleBufferController(self.view.nb, "get_followers_list", "followers", buff.session, buff.session.db["user_name"], screen_name=buff.session.db["user_name"])
    self.buffers.append(followers)
    self.view.insert_buffer(followers.buffer, name=_(u"Followers"), pos=self.view.search(buff.session.db["user_name"], buff.session.db["user_name"]))
    followers.start_stream(play_sound=False)
   elif buffer == "friends":
    friends = twitterBuffers.peopleBufferController(self.view.nb, "get_friends_list", "friends", buff.session, buff.session.db["user_name"], screen_name=buff.session.db["user_name"])
    self.buffers.append(friends)
    self.view.insert_buffer(friends.buffer, name=_(u"Friends"), pos=self.view.search(buff.session.db["user_name"], buff.session.db["user_name"]))
    friends.start_stream(play_sound=False)
   elif buffer == "blocked":
    blocks = twitterBuffers.peopleBufferController(self.view.nb, "list_blocks", "blocked", buff.session, buff.session.db["user_name"])
    self.buffers.append(blocks)
    self.view.insert_buffer(blocks.buffer, name=_(u"Blocked users"), pos=self.view.search(buff.session.db["user_name"], buff.session.db["user_name"]))
    blocks.start_stream(play_sound=False)
   elif buffer == "muted":
    muted = twitterBuffers.peopleBufferController(self.view.nb, "get_muted_users_list", "muted", buff.session, buff.session.db["user_name"])
    self.buffers.append(muted)
    self.view.insert_buffer(muted.buffer, name=_(u"Muted users"), pos=self.view.search(buff.session.db["user_name"], buff.session.db["user_name"]))
    muted.start_stream(play_sound=False)
   elif buffer == "events":
    events = twitterBuffers.eventsBufferController(self.view.nb, "events", buff.session, buff.session.db["user_name"], bufferType="dmPanel", screen_name=buff.session.db["user_name"])
    self.buffers.append(events)
    self.view.insert_buffer(events.buffer, name=_(u"Events"), pos=self.view.search(buff.session.db["user_name"], buff.session.db["user_name"]))
  elif create == False:
   self.destroy_buffer(buffer, buff.session.db["user_name"])
  elif buffer == "list":
   if create in buff.session.settings["other_buffers"]["lists"]:
    output.speak(_(u"This list is already opened"), True)
    return
   tl = twitterBuffers.listBufferController(self.view.nb, "get_list_statuses", create+"-list", buff.session, buff.session.db["user_name"], bufferType=None, list_id=utils.find_list(create, buff.session.db["lists"]), tweet_mode="extended")
   buff.session.lists.append(tl)
   pos=self.view.search("lists", buff.session.db["user_name"])
   self.insert_buffer(tl, pos)
   self.view.insert_buffer(tl.buffer, name=_(u"List for {}").format(create), pos=self.view.search("lists", buff.session.db["user_name"]))
   tl.start_stream(play_sound=False)
   buff.session.settings["other_buffers"]["lists"].append(create)
   buff.session.settings.write()

 def invisible_shorcuts_changed(self, registered):
  if registered == True:
   km = self.create_invisible_keyboard_shorcuts()
   self.register_invisible_keyboard_shorcuts(km)
  elif registered == False:
   km = self.create_invisible_keyboard_shorcuts()
   self.unregister_invisible_keyboard_shorcuts(km)

 def about(self, *args, **kwargs):
  self.view.about_dialog()

 def get_soundpacks(self, *args, **kwargs):
  # This should redirect users of other languages to the right version of the TWBlue website.
  lang = languageHandler.curLang[:2]
  url = application.url
  final_url = "{0}/{1}/soundpacks".format(url, lang)
  try:
   response = requests.get(final_url)
  except:
   output.speak(_(u"An error happened while trying to connect to the server. Please try later."))
   return
  # There is no twblue.es/en, so if English is the language used this should be False anyway.
  if response.status_code == 200 and lang != "en":
   webbrowser.open_new_tab(final_url)
  else:
   webbrowser.open_new_tab(application.url+"/soundpacks")

 def visit_website(self, *args, **kwargs):
  # This should redirect users of other languages to the right version of the TWBlue website.
  lang = languageHandler.curLang[:2]
  url = application.url
  final_url = "{0}/{1}".format(url, lang)
  try:
   response = requests.get(final_url)
  except:
   output.speak(_(u"An error happened while trying to connect to the server. Please try later."))
   return
  # There is no twblue.es/en, so if English is the language used this should be False anyway.
  if response.status_code == 200 and lang != "en":
   webbrowser.open_new_tab(final_url)
  else:
   webbrowser.open_new_tab(application.url)

 def manage_accounts(self, *args, **kwargs):
  sm = sessionManager.sessionManagerController(started=True)
  sm.fill_list()
  sm.show()
  for i in sm.new_sessions:
   self.create_buffers(sessions.sessions[i])
   call_threaded(self.start_buffers, sessions.sessions[i])
  for i in sm.removed_sessions:
   if sessions.sessions[i].logged == True:
    self.logout_account(sessions.sessions[i].session_id)
   self.destroy_buffer(sessions.sessions[i].settings["twitter"]["user_name"], sessions.sessions[i].settings["twitter"]["user_name"])
   self.accounts.remove(sessions.sessions[i].settings["twitter"]["user_name"])
   sessions.sessions.pop(i)

 def update_profile(self, *args, **kwargs):
  r = user.profileController(self.get_best_buffer().session)

 def user_details(self, *args, **kwargs):
  buffer = self.get_current_buffer()
  if not hasattr(buffer, "session") or buffer.session == None: return
  if hasattr(buffer, "user_details"):
   buffer.user_details()

 def toggle_autoread(self, *args, **kwargs):
  buffer = self.get_current_buffer()
  if hasattr(buffer, "session") and buffer.session == None: return
  if buffer.name not in buffer.session.settings["other_buffers"]["autoread_buffers"]:
   buffer.session.settings["other_buffers"]["autoread_buffers"].append(buffer.name)
   output.speak(_(u"The auto-reading of new tweets is enabled for this buffer"), True)
  elif buffer.name in buffer.session.settings["other_buffers"]["autoread_buffers"]:
   buffer.session.settings["other_buffers"]["autoread_buffers"].remove(buffer.name)
   output.speak(_(u"The auto-reading of new tweets is disabled for this buffer"), True)
  buffer.session.settings.write()

 def toggle_session_mute(self, *args, **kwargs):
  buffer = self.get_best_buffer()
  if buffer.session.settings["sound"]["session_mute"] == False:
   buffer.session.settings["sound"]["session_mute"] = True
   output.speak(_(u"Session mute on"), True)
  elif buffer.session.settings["sound"]["session_mute"] == True:
   buffer.session.settings["sound"]["session_mute"] = False
   output.speak(_(u"Session mute off"), True)
  buffer.session.settings.write()

 def toggle_buffer_mute(self, *args, **kwargs):
  buffer = self.get_current_buffer()
  if hasattr(buffer, "session") and buffer.session == None: return
  if buffer.name not in buffer.session.settings["other_buffers"]["muted_buffers"]:
   buffer.session.settings["other_buffers"]["muted_buffers"].append(buffer.name)
   output.speak(_(u"Buffer mute on"), True)
  elif buffer.name in buffer.session.settings["other_buffers"]["muted_buffers"]:
   buffer.session.settings["other_buffers"]["muted_buffers"].remove(buffer.name)
   output.speak(_(u"Buffer mute off"), True)
  buffer.session.settings.write()

 def view_documentation(self, *args, **kwargs):
  lang = localization.get("documentation")
  os.chdir("documentation/%s" % (lang,))
  webbrowser.open("manual.html")
  os.chdir("../../")

 def view_changelog(self, *args, **kwargs):
  if application.snapshot == True:
   webbrowser.open("https://github.com/manuelcortez/twblue/blob/next-gen/doc/changelog.md")
  else:
   lang = localization.get("documentation")
   os.chdir("documentation/%s" % (lang,))
   webbrowser.open("changelog.html")
   os.chdir("../../")

 def insert_buffer(self, buffer, position):
  self.buffers.insert(position, buffer)

 def copy_to_clipboard(self, *args, **kwargs):
  output.copy(self.get_current_buffer().get_message())
  output.speak(_(u"Copied"))

 def repeat_item(self, *args, **kwargs):
  output.speak(self.get_current_buffer().get_message())

 def execute_action(self, action):
  if hasattr(self, action):
   getattr(self, action)()

 def update_buffers(self):
  for i in self.buffers[:]:
   if i.session != None and i.session.is_logged == True:
    try:
     i.start_stream(mandatory=True)
    except TwythonAuthError:
     buff = self.view.search(i.name, i.account)
     i.remove_buffer(force=True)
     commonMessageDialogs.blocked_timeline()
     if self.get_current_buffer() == i:
      self.right()
     self.view.delete_buffer(buff)
     self.buffers.remove(i)
     del i

 def update_buffer(self, *args, **kwargs):
  bf = self.get_current_buffer()
  if not hasattr(bf, "start_stream"):
   output.speak(_(u"Unable to update this buffer."))
   return
  else:
   output.speak(_(u"Updating buffer..."))
   n = bf.start_stream(mandatory=True, avoid_autoreading=True)
   if n != None:
    output.speak(_(u"{0} items retrieved").format(n,))

 def buffer_title_changed(self, buffer):
  if "-timeline" in buffer.name:
   title = _(u"Timeline for {}").format(buffer.username,)
  elif "-favorite" in buffer.name:
   title = _(u"Likes for {}").format(buffer.username,)
  elif "-followers" in buffer.name:
   title = _(u"Followers for {}").format(buffer.username,)
  elif "-friends" in buffer.name:
   title = _(u"Friends for {}").format(buffer.username,)
  buffer_index = self.view.search(buffer.name, buffer.account)
  self.view.set_page_title(buffer_index, title)

 def ocr_image(self, *args, **kwargs):
  buffer = self.get_current_buffer()
  if hasattr(buffer, "get_right_tweet") == False:
   output.speak(_(u"Invalid buffer"))
   return
  tweet = buffer.get_tweet()
  media_list = []
  if ("entities" in tweet) and ("media" in tweet["entities"]):
   [media_list.append(i) for i in tweet["entities"]["media"] if i not in media_list]
  elif "retweeted_status" in tweet and "media" in tweet["retweeted_status"]["entities"]:
   [media_list.append(i) for i in tweet["retweeted_status"]["entities"]["media"] if i not in media_list]
  elif "quoted_status" in tweet and "media" in tweet["quoted_status"]["entities"]:
   [media_list.append(i) for i in tweet["quoted_status"]["entities"]["media"] if i not in media_list]
  if len(media_list) > 1:
   image_list = [_(u"Picture {0}").format(i,) for i in range(0, len(media_list))]
   dialog = dialogs.urlList.urlList(title=_(u"Select the picture"))
   if dialog.get_response() == widgetUtils.OK:
    img = media_list[dialog.get_item()]
   else:
    return
  elif len(media_list) == 1:
   img = media_list[0]
  else:
   output.speak(_(u"Invalid buffer"))
   return
  if buffer.session.settings["mysc"]["ocr_language"] != "":
   ocr_lang = buffer.session.settings["mysc"]["ocr_language"]
  else:
   ocr_lang = ocr.OCRSpace.short_langs.index(tweet["lang"])
   ocr_lang = ocr.OCRSpace.OcrLangs[ocr_lang]
  api = ocr.OCRSpace.OCRSpaceAPI()
  try:
   text = api.OCR_URL(img["media_url"], lang=ocr_lang)
  except ocr.OCRSpace.APIError as er:
   output.speak(_(u"Unable to extract text"))
   return
  msg = messages.viewTweet(text["ParsedText"], [], False)

 def update_sent_dms(self, total, account):
  sent_dms = self.search_buffer("sent_direct_messages", account)
  if sent_dms != None:
   sent_dms.put_items_on_list(total)

 def more_dms(self, data, account):
  sent_dms = self.search_buffer("sent_direct_messages", account)
  if sent_dms != None:
   sent_dms.put_more_items(data)

 def save_data_in_db(self):
  for i in sessions.sessions:
   sessions.sessions[i].shelve()
