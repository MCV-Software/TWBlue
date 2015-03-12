# -*- coding: utf-8 -*-
import application
from wxUI import (view, dialogs, commonMessageDialogs, sysTrayIcon)
from twitter import utils
from sessionmanager import manager, sessionManager

from update import updater
import buffersController
import messages
import settings
from sessionmanager import session as session_
from pubsub import pub
import sound
import output
from twython import TwythonError
from mysc.thread_utils import call_threaded
from mysc.repeating_timer import RepeatingTimer
from mysc import restart
import config
import widgetUtils
import pygeocoder
from pygeolib import GeocoderError
import platform
from extra import SoundsTutorial
import logging
if platform.system() == "Windows":
 import keystrokeEditor
 from keyboard_handler.wx_handler import WXKeyboardHandler
import userActionsController
import trendingTopics
import user
import webbrowser

log = logging.getLogger("mainController")

geocoder = pygeocoder.Geocoder()

class Controller(object):

 """ Main Controller for TWBlue. It manages the main window and sessions."""

 def search_buffer(self, name_, user):

  """ Searches a buffer.
 name_ str: The name for the buffer
 user str: The account for the buffer.
 for example you may want to search the home_timeline buffer for the tw_blue2 user.
  returns buffersController.buffer object with the result if there is one."""
  for i in self.buffers:
   if i.name == name_ and i.account == user: return i

 def get_current_buffer(self):
  """ Get the current bufferObject"""
  buffer = self.view.get_current_buffer()
  if hasattr(buffer, "account"):
   buffer = self.search_buffer(buffer.name, buffer.account)
   return buffer

 def get_best_buffer(self):
  """ Gets the best buffer for doing  something using the session object.
  This function is useful when you need to open a timeline or post a tweet, and the user is in a buffer without a session, for example the events buffer.
  This returns a bufferObject."""
  # Gets the parent buffer to know what account is doing an action
  view_buffer = self.view.get_current_buffer()
  # If the account has no session attached, we will need to search the home_timeline for that account to use its session.
  if view_buffer.type == "account" or view_buffer.type == "empty":
   buffer = self.search_buffer("home_timeline", view_buffer.account)
  else:
   buffer = self.search_buffer(view_buffer.name, view_buffer.account)
  return buffer

 def get_first_buffer(self, account):
  """ Gets the first valid buffer for an account.
  account str: A twitter username.
  The first valid buffer is the home timeline."""
  for i in self.buffers:
   if i.account == account and i.invisible == True:
    buff = i
    break
  return self.view.search(buff.name, buff.account)

 def get_last_buffer(self, account):
  """ Gets the last valid buffer for an account.
  account str: A twitter username.
  The last valid buffer is the last buffer that contains a session object assigned."""
  results = []
  [results.append(i) for i in self.buffers if i.account == account and i.invisible == True]
  return self.view.search(results[-1].name, results[-1].account)

 def bind_stream_events(self):
  """ Binds all the streaming events with their functions."""
  log.debug("Binding events for the Twitter stream API...")
  pub.subscribe(self.manage_home_timelines, "item-in-home")
  pub.subscribe(self.manage_mentions, "mention")
  pub.subscribe(self.manage_direct_messages, "direct-message")
  pub.subscribe(self.manage_sent_dm, "sent-dm")
  pub.subscribe(self.manage_sent_tweets, "sent-tweet")
  pub.subscribe(self.manage_events, "event")
  pub.subscribe(self.manage_followers, "follower")
  pub.subscribe(self.manage_friend, "friend")
  pub.subscribe(self.manage_unfollowing, "unfollowing")
  pub.subscribe(self.manage_favourite, "favourite")
  pub.subscribe(self.manage_unfavourite, "unfavourite")
  pub.subscribe(self.manage_blocked_user, "blocked-user")
  pub.subscribe(self.manage_unblocked_user, "unblocked-user")
  pub.subscribe(self.manage_item_in_timeline, "item-in-timeline")
  widgetUtils.connect_event(self.view, widgetUtils.CLOSE_EVENT, self.exit_)

 def bind_other_events(self):
  """ Binds the local application events with their functions."""
  log.debug("Binding other application events...")
  pub.subscribe(self.logout_account, "logout")
  pub.subscribe(self.login_account, "login")
  pub.subscribe(self.invisible_shorcuts_changed, "invisible-shorcuts-changed")
  pub.subscribe(self.manage_stream_errors, "stream-error")
  pub.subscribe(self.create_new_buffer, "create-new-buffer")
  pub.subscribe(self.restart_streams, "restart-streams")
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.show_hide, menuitem=self.view.show_hide)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.search, menuitem=self.view.menuitem_search)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.get_trending_topics, menuitem=self.view.trends)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.learn_sounds, menuitem=self.view.sounds_tutorial)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.accountConfiguration, menuitem=self.view.account_settings)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.configuration, menuitem=self.view.prefs)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.exit, menuitem=self.view.close)
  widgetUtils.connect_event(self.view, widgetUtils.CLOSE_EVENT, self.exit)
  if widgetUtils.toolkit == "wx":
   log.debug("Binding the exit function...")
   widgetUtils.connectExitFunction(self.exit_)
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
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.unfollow, menuitem=self.view.unfollow)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.mute, menuitem=self.view.mute)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.unmute, menuitem=self.view.unmute)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.report, menuitem=self.view.report)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.block, menuitem=self.view.block)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.unblock, menuitem=self.view.unblock)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.get_more_items, menuitem=self.view.load_previous_items)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.clear_buffer, menuitem=self.view.clear)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.remove_buffer, self.view.deleteTl)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.check_for_updates, self.view.check_for_updates)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.about, menuitem=self.view.about)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.visit_website, menuitem=self.view.visit_website)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.edit_keystrokes, menuitem=self.view.keystroke_editor)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.manage_accounts, self.view.manage_accounts)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.update_profile, menuitem=self.view.updateProfile)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.user_details, menuitem=self.view.details)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.toggle_autoread, menuitem=self.view.autoread)
  widgetUtils.connect_event(self.view, widgetUtils.MENU, self.toggle_buffer_mute, self.view.mute_buffer)
  widgetUtils.connect_event(self.view.nb, widgetUtils.NOTEBOOK_PAGE_CHANGED, self.buffer_changed)

 def set_systray_icon(self):
  self.systrayIcon = sysTrayIcon.SysTrayIcon()
  widgetUtils.connect_event(self.systrayIcon, widgetUtils.MENU, self.post_tweet, menuitem=self.systrayIcon.tweet)
  widgetUtils.connect_event(self.systrayIcon, widgetUtils.MENU, self.configuration, menuitem=self.systrayIcon.global_settings)
  widgetUtils.connect_event(self.systrayIcon, widgetUtils.MENU, self.accountConfiguration, menuitem=self.systrayIcon.account_settings)
  widgetUtils.connect_event(self.systrayIcon, widgetUtils.MENU, self.update_profile, menuitem=self.systrayIcon.update_profile)
  widgetUtils.connect_event(self.systrayIcon, widgetUtils.MENU, self.show_hide, menuitem=self.systrayIcon.show_hide)
  widgetUtils.connect_event(self.systrayIcon, widgetUtils.MENU, self.check_for_updates, menuitem=self.systrayIcon.check_for_updates)
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
  # accounts list.
  self.accounts = []
  # a dict for saving the current buffer position for each account (future)
  self.buffer_positions = {}
  # This saves the current account (important in invisible mode)
  self.current_account = ""
  self.view.prepare()
  self.bind_stream_events()
  self.bind_other_events()
  self.set_systray_icon()

 def check_invisible_at_startup(self):
  # Visibility check
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
  for i in session_.sessions:
   log.debug("Working on session %s" % (i,))
   if session_.sessions[i].is_logged == False:
    self.create_ignored_session_buffer(session_.sessions[i])
    continue
   self.create_buffers(session_.sessions[i])
  # Connection checker executed each minute.
  self.checker_function = RepeatingTimer(60, self.check_connection)
  self.checker_function.start()

 def start(self):
  """ Starts all buffer objects. Loads their items."""
  for i in session_.sessions:
   if session_.sessions[i].is_logged == False: continue
   self.start_buffers(session_.sessions[i])
  session_.sessions[session_.sessions.keys()[0]].sound.play("ready.ogg")
  output.speak(_(u"Ready"))

 def create_ignored_session_buffer(self, session):
  self.accounts.append(session.settings["twitter"]["user_name"])
  account = buffersController.accountPanel(self.view.nb, session.settings["twitter"]["user_name"], session.settings["twitter"]["user_name"], session.session_id)
  account.logged = False
  account.setup_account()
  self.buffers.append(account)
  self.view.add_buffer(account.buffer , name=session.settings["twitter"]["user_name"])
  self.buffer_positions[session.settings["twitter"]["user_name"]] = 1

 def login_account(self, session_id):
  for i in session_.sessions:
   if session_.sessions[i].session_id == session_id: session = session_.sessions[i]
  session.login()
  self.create_buffers(session, False)
  self.start_buffers(session)

 def create_buffers(self, session, createAccounts=True):
  """ Generates buffer objects for an user account.
  session SessionObject: a sessionmanager.session.Session Object"""
  session.get_user_info()
  if createAccounts == True:
   self.accounts.append(session.db["user_name"])
   self.buffer_positions[session.db["user_name"]] = 1
   account = buffersController.accountPanel(self.view.nb, session.db["user_name"], session.db["user_name"], session.session_id)
   account.setup_account()
   self.buffers.append(account)
   self.view.add_buffer(account.buffer , name=session.db["user_name"])
  home = buffersController.baseBufferController(self.view.nb, "get_home_timeline", "home_timeline", session, session.db["user_name"])
  self.buffers.append(home)
  self.view.insert_buffer(home.buffer, name=_(u"Home"), pos=self.view.search(session.db["user_name"], session.db["user_name"]))
  mentions = buffersController.baseBufferController(self.view.nb, "get_mentions_timeline", "mentions", session, session.db["user_name"], sound="mention_received.ogg")
  self.buffers.append(mentions)
  self.view.insert_buffer(mentions.buffer, name=_(u"Mentions"), pos=self.view.search(session.db["user_name"], session.db["user_name"]))
  dm = buffersController.baseBufferController(self.view.nb, "get_direct_messages", "direct_messages", session, session.db["user_name"], bufferType="dmPanel", sound="dm_received.ogg")
  self.buffers.append(dm)
  self.view.insert_buffer(dm.buffer, name=_(u"Direct messages"), pos=self.view.search(session.db["user_name"], session.db["user_name"]))
  sent_dm = buffersController.baseBufferController(self.view.nb, "get_sent_messages", "sent_direct_messages", session, session.db["user_name"], bufferType="dmPanel")
  self.buffers.append(sent_dm)
  self.view.insert_buffer(sent_dm.buffer, name=_(u"Sent direct messages"), pos=self.view.search(session.db["user_name"], session.db["user_name"]))
  sent_tweets = buffersController.baseBufferController(self.view.nb, "get_user_timeline", "sent_tweets", session, session.db["user_name"], bufferType="dmPanel", screen_name=session.db["user_name"])
  self.buffers.append(sent_tweets)
  self.view.insert_buffer(sent_tweets.buffer, name=_(u"Sent tweets"), pos=self.view.search(session.db["user_name"], session.db["user_name"]))
  if session.settings["other_buffers"]["show_favourites"] == True:
   favourites = buffersController.baseBufferController(self.view.nb, "get_favorites", "favourites", session, session.db["user_name"])
   self.buffers.append(favourites)

   self.view.insert_buffer(favourites.buffer, name=_(u"Favourites"), pos=self.view.search(session.db["user_name"], session.db["user_name"]))
  if session.settings["other_buffers"]["show_followers"] == True:
   followers = buffersController.peopleBufferController(self.view.nb, "get_followers_list", "followers", session, session.db["user_name"], screen_name=session.db["user_name"])
   self.buffers.append(followers)
   self.view.insert_buffer(followers.buffer, name=_(u"Followers"), pos=self.view.search(session.db["user_name"], session.db["user_name"]))
  if session.settings["other_buffers"]["show_friends"] == True:
   friends = buffersController.peopleBufferController(self.view.nb, "get_friends_list", "friends", session, session.db["user_name"], screen_name=session.db["user_name"])
   self.buffers.append(friends)
   self.view.insert_buffer(friends.buffer, name=_(u"Friends"), pos=self.view.search(session.db["user_name"], session.db["user_name"]))
  if session.settings["other_buffers"]["show_blocks"] == True:
   blocks = buffersController.peopleBufferController(self.view.nb, "list_blocks", "blocked", session, session.db["user_name"])
   self.buffers.append(blocks)
   self.view.insert_buffer(blocks.buffer, name=_(u"Blocked users"), pos=self.view.search(session.db["user_name"], session.db["user_name"]))
  if session.settings["other_buffers"]["show_muted_users"] == True:
   muted = buffersController.peopleBufferController(self.view.nb, "get_muted_users_list", "muted", session, session.db["user_name"])
   self.buffers.append(muted)
   self.view.insert_buffer(muted.buffer, name=_(u"Muted users"), pos=self.view.search(session.db["user_name"], session.db["user_name"]))
  if session.settings["other_buffers"]["show_events"] == True:
   events = buffersController.eventsBufferController(self.view.nb, "events", session, session.db["user_name"], bufferType="dmPanel", screen_name=session.db["user_name"])
   self.buffers.append(events)
   self.view.insert_buffer(events.buffer, name=_(u"Events"), pos=self.view.search(session.db["user_name"], session.db["user_name"]))
  timelines = buffersController.emptyPanel(self.view.nb, "timelines", session.db["user_name"])
  self.buffers.append(timelines)
  self.view.insert_buffer(timelines.buffer , name=_(u"Timelines"), pos=self.view.search(session.db["user_name"], session.db["user_name"]))
  for i in session.settings["other_buffers"]["timelines"]:
   tl = buffersController.baseBufferController(self.view.nb, "get_user_timeline", "%s-timeline" % (i,), session, session.db["user_name"], bufferType=None, screen_name=i)
   self.buffers.append(tl)
   self.view.insert_buffer(tl.buffer, name=_(u"Timeline for {}".format(i)), pos=self.view.search("timelines", session.db["user_name"]))
  searches = buffersController.emptyPanel(self.view.nb, "searches", session.db["user_name"])
  self.buffers.append(searches)
  self.view.insert_buffer(searches.buffer , name=_(u"Searches"), pos=self.view.search(session.db["user_name"], session.db["user_name"]))
  for i in session.settings["other_buffers"]["tweet_searches"]:
   tl = buffersController.searchBufferController(self.view.nb, "search", "%s-searchterm" % (i,), session, session.db["user_name"], bufferType="searchPanel", q=i)
   self.buffers.append(tl)
   self.view.insert_buffer(tl.buffer, name=_(u"Search for {}".format(i)), pos=self.view.search("searches", session.db["user_name"]))
   tl.timer = RepeatingTimer(180, tl.start_stream)
   tl.timer.start()
  for i in session.settings["other_buffers"]["trending_topic_buffers"]:
   buffer = buffersController.trendsBufferController(self.view.nb, "%s_tt" % (i,), session, session.db["user_name"], i)
   buffer.start_stream()
   self.buffers.append(buffer)
   self.view.insert_buffer(buffer.buffer, name=_(u"Trending topics for %s") % (buffer.name_), pos=self.view.search(session.db["user_name"], session.db["user_name"]))
   buffer.timer = RepeatingTimer(300, buffer.start_stream)
   buffer.timer.start()

 def logout_account(self, session_id):
  for i in session_.sessions:
   if session_.sessions[i].session_id == session_id: session = session_.sessions[i]
  user = session.db["user_name"]
  self.destroy_buffer("home_timeline", user)
  self.destroy_buffer("mentions", user)
  self.destroy_buffer("direct_messages", user)
  self.destroy_buffer("sent_direct_messages", user)
  self.destroy_buffer("sent_tweets", user)
  self.destroy_buffer("favourites", user)
  self.destroy_buffer("followers", user)
  self.destroy_buffer("friends", user)
  self.destroy_buffer("blocked", user)
  self.destroy_buffer("muted", user)
  self.destroy_buffer("events", user)
  self.destroy_buffer("timelines", user)
  for i in session.settings["other_buffers"]["timelines"]:
   self.destroy_buffer("%s-timeline" % (i,), user)
  self.destroy_buffer("searches", user)
  for i in session.settings["other_buffers"]["tweet_searches"]:
   self.destroy_buffer("%s-searchterm" % (i,), user)
  for i in session.settings["other_buffers"]["trending_topic_buffers"]:
   self.destroy_buffer("%s_tt" % (i,), user)
  
 def destroy_buffer(self, buffer_name, account):
  buffer = self.search_buffer(buffer_name, account)
  if buffer == None: return
  buff = self.view.search(buffer.name, buffer.account)
  if buff == None: return
  self.view.delete_buffer(buff)
  self.buffers.remove(buffer)
  del buffer

 def search(self, *args, **kwargs):
  """ Searches words or users in twitter. This creates a new buffer containing the search results."""
  log.debug("Creating a new search...")
  dlg = dialogs.search.searchDialog()
  if dlg.get_response() == widgetUtils.OK:
   term = dlg.get("term")
   buffer = self.get_best_buffer()
   if dlg.get("tweets") == True:
    if term not in buffer.session.settings["other_buffers"]["tweet_searches"]:
     buffer.session.settings["other_buffers"]["tweet_searches"].append(term)
     search = buffersController.searchBufferController(self.view.nb, "search", "%s-searchterm" % (term,), buffer.session, buffer.session.db["user_name"], bufferType="searchPanel", q=term)
    else:
     log.error("A buffer for the %s search term is already created. You can't create a duplicate buffer." % (term,))
     return
   elif dlg.get("users") == True:
    search = buffersController.searchPeopleBufferController(self.view.nb, "search_users", "%s-searchUser" % (term,), buffer.session, buffer.session.db["user_name"], bufferType=None, q=term)
   self.buffers.append(search)
   search.start_stream()
   self.view.insert_buffer(search.buffer, name=_(u"Search for {}".format(term)), pos=self.view.search("searches", buffer.session.db["user_name"]))
   search.timer = RepeatingTimer(180, search.start_stream)
   search.timer.start()
  dlg.Destroy()

 def edit_keystrokes(self, *args, **kwargs):
  editor = keystrokeEditor.KeystrokeEditor()
  if editor.changed == True:
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

 def view_user_lists(self, users):
  pass

 def add_to_list(self, user):
  pass

 def remove_from_list(self, user):
  pass

 def lists_manager(self):
  pass

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

 def report_error(self):
  pass

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
   answer = commonMessageDialogs.exit_dialog()
   if answer == widgetUtils.YES:
    self.exit_()
  else:
   self.exit_()

 def exit_(self, *args, **kwargs):
  log.debug("Exiting...")
  log.debug("Saving global configuration...")
  config.app.write()
  for item in session_.sessions:
   if session_.sessions[item].logged == False: continue
   log.debug("Saving config for %s session" % (session_.sessions[item].session_id,))
   session_.sessions[item].settings.write()
   log.debug("Disconnecting streams for %s session" % (session_.sessions[item].session_id,))
   session_.sessions[item].main_stream.disconnect()
   session_.sessions[item].timelinesStream.disconnect()
   session_.sessions[item].sound.cleaner.cancel()
  self.systrayIcon.Destroy()
  widgetUtils.exit_application()

 def follow(self, *args, **kwargs):
  buff = self.get_current_buffer()
  if not hasattr(buff, "get_right_tweet"): return
  tweet = buff.get_right_tweet()
  if buff.type != "people":
   users = utils.get_all_users(tweet, buff.session.db)
  else:
   users = [tweet["screen_name"]]
  u = userActionsController.userActionsController(buff, users)

 def unfollow(self, *args, **kwargs):
  buff = self.get_current_buffer()
  if not hasattr(buff, "get_right_tweet"): return
  tweet = buff.get_right_tweet()
  if buff.type != "people":
   users = utils.get_all_users(tweet, buff.session.db)
  else:
   users = [tweet["screen_name"]]
  u = userActionsController.userActionsController(buff, users, "unfollow")

 def mute(self, *args, **kwargs):
  buff = self.get_current_buffer()
  if not hasattr(buff, "get_right_tweet"): return
  tweet = buff.get_right_tweet()
  if buff.type != "people":
   users = utils.get_all_users(tweet, buff.session.db)
  else:
   users = [tweet["screen_name"]]
  u = userActionsController.userActionsController(buff, users, "mute")

 def unmute(self, *args, **kwargs):
  buff = self.get_current_buffer()
  if not hasattr(buff, "get_right_tweet"): return
  tweet = buff.get_right_tweet()
  if buff.type != "people":
   users = utils.get_all_users(tweet, buff.session.db)
  else:
   users = [tweet["screen_name"]]
  u = userActionsController.userActionsController(buff, users, "unmute")

 def block(self, *args, **kwargs):
  buff = self.get_current_buffer()
  if not hasattr(buff, "get_right_tweet"): return
  tweet = buff.get_right_tweet()
  if buff.type != "people":
   users = utils.get_all_users(tweet, buff.session.db)
  else:
   users = [tweet["screen_name"]]
  u = userActionsController.userActionsController(buff, users, "block")

 def unblock(self, *args, **kwargs):
  buff = self.get_current_buffer()
  if not hasattr(buff, "get_right_tweet"): return
  tweet = buff.get_right_tweet()
  if buff.type != "people":
   users = utils.get_all_users(tweet, buff.session.db)
  else:
   users = [tweet["screen_name"]]
  u = userActionsController.userActionsController(buff, users, "unblock")

 def report(self, *args, **kwargs):
  buff = self.get_current_buffer()
  if not hasattr(buff, "get_right_tweet"): return
  tweet = buff.get_right_tweet()
  if buff.type != "people":
   users = utils.get_all_users(tweet, buff.session.db)
  else:
   users = [tweet["screen_name"]]
  u = userActionsController.userActionsController(buff, users, "report")

 def post_tweet(self, event=None):
  buffer = self.get_best_buffer()
  buffer.post_tweet()

 def post_reply(self, *args, **kwargs):
  buffer = self.get_current_buffer()
  if buffer.name == "sent_direct_messages" or buffer.name == "sent-tweets": return
  elif buffer.name == "direct_messages":
   buffer.direct_message()
  else:
   buffer.reply()

 def send_dm(self, *args, **kwargs):
  buffer = self.get_current_buffer()
  if buffer.name == "sent_direct_messages" or buffer.name == "sent-tweets": return
  else:
   buffer.direct_message()

 def post_retweet(self, *args, **kwargs):
  buffer = self.get_current_buffer()
  if buffer.type == "dm" or buffer.type == "people" or buffer.type == "events":
   return
  else:
   buffer.retweet()

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

 def view_item(self, *args, **kwargs):
  buffer = self.get_current_buffer()
  if buffer.type == "baseBuffer" or buffer.type == "favourites_timeline" or buffer.type == "list" or buffer.type == "search":
   try:
    tweet_id = buffer.get_right_tweet()["id"]
    tweet = buffer.session.twitter.twitter.show_status(id=tweet_id)
    msg = messages.viewTweet(tweet, )
   except TwythonError:
    non_tweet = buffer.get_formatted_message()
    msg = messages.viewTweet(non_tweet, False)
  elif buffer.type == "account" or buffer.type == "empty":
   return
  else:
   non_tweet = buffer.get_formatted_message()
   msg = messages.viewTweet(non_tweet, False)

 def open_timeline(self, *args, **kwargs):
  buff = self.get_best_buffer()
  if not hasattr(buff, "get_right_tweet"): return
  tweet = buff.get_right_tweet()
  if buff.type != "people":
   users = utils.get_all_users(tweet, buff.session.db)
  else:
   users = [tweet["screen_name"]]
  dlg = dialogs.userSelection.selectUserDialog(users=users)
  if dlg.get_response() == widgetUtils.OK:
   buffer = self.get_best_buffer()
   if utils.if_user_exists(buffer.session.twitter.twitter, dlg.get_user()) != None:
    if dlg.get_action() == "tweets":
     if dlg.get_user() in buffer.session.settings["other_buffers"]["timelines"]:
      commonMessageDialogs.timeline_exist()
      return
     tl = buffersController.baseBufferController(self.view.nb, "get_user_timeline", "%s-timeline" % (dlg.get_user(),), buffer.session, buffer.session.db["user_name"], bufferType=None, screen_name=dlg.get_user())
     tl.start_stream()
     self.buffers.append(tl)
     self.view.insert_buffer(tl.buffer, name=_(u"Timeline for {}".format(dlg.get_user())), pos=self.view.search("timelines", buffer.session.db["user_name"]))
     buffer.session.settings["other_buffers"]["timelines"].append(dlg.get_user())
     pub.sendMessage("restart-streams", streams=["timelinesStream"], session=buffer.session)
     buffer.session.sound.play("create_timeline.ogg")
   else:
    commonMessageDialogs.user_not_exist()

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

 def toggle_global_mute(self):
  pass

 def toggle_mute(self):
  pass

 def toggle_autoread(self):
  pass

 def get_trending_topics(self, *args, **kwargs):
  buff = self.get_best_buffer()
  trends = trendingTopics.trendingTopicsController(buff.session)
  if trends.dialog.get_response() == widgetUtils.OK:
   woeid = trends.get_woeid()
   if woeid in buff.session.settings["other_buffers"]["trending_topic_buffers"]: return
   buffer = buffersController.trendsBufferController(self.view.nb, "%s_tt" % (woeid,), buff.session, buff.account, woeid)
   self.buffers.append(buffer)
   self.view.insert_buffer(buffer.buffer, name=_(u"Trending topics for %s") % (trends.get_string()), pos=self.view.search(buff.session.db["user_name"], buff.session.db["user_name"]))
   buffer.start_stream()
   timer = RepeatingTimer(300, buffer.start_stream)
   timer.start()
   buffer.session.settings["other_buffers"]["trending_topic_buffers"].append(woeid)

 def reverse_geocode(self, event=None):
  try:
   tweet = self.get_current_buffer().get_tweet()
   if tweet["coordinates"] != None:
    x = tweet["coordinates"]["coordinates"][0]
    y = tweet["coordinates"]["coordinates"][1]
    address = geocoder.reverse_geocode(y, x)
    if event == None: output.speak(address[0].__str__().decode("utf-8"))
    else: self.view.show_address(address[0].__str__().decode("utf-8"))
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
    address = geocoder.reverse_geocode(y, x)
    dlg = messages.viewTweet(address[0].__str__(), False)
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
  for i in self.accounts:
   buffer = self.view.search("home_timeline", i)
   if buffer != None: break
  self.view.change_buffer(buffer)

 def up(self, *args, **kwargs):
  page = self.get_current_buffer()
  if not hasattr(page.buffer, "list"):
   output.speak(_(u"This account is not logged in twitter."))
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
   output.speak(page.get_message())
  except:
   pass

 def down(self, *args, **kwargs):
  page = self.get_current_buffer()
  if not hasattr(page.buffer, "list"):
   output.speak(_(u"This account is not logged in twitter."))
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
   output.speak(page.get_message())
  except:
   pass

 def left(self, *args, **kwargs):
  buff = self.view.get_current_buffer_pos()
  buffer = self.get_current_buffer()
  if not hasattr(buffer.buffer, "list"):
   output.speak(_(u"This account is not logged in twitter."))
   return
  if buff == self.get_first_buffer(buffer.account) or buff == 0:
   self.view.change_buffer(self.get_last_buffer(buffer.account))
  else:
   self.view.change_buffer(buff-1)
  while self.get_current_buffer().invisible == False: self.skip_buffer(False)
  buffer = self.get_current_buffer()
  try:
   msg = _(u"%s, %s of %s") % (self.view.get_buffer_text(), buffer.buffer.list.get_selected()+1, buffer.buffer.list.get_count())
  except:
   msg = _(u"%s. Empty") % (self.view.get_buffer_text(),)
  output.speak(msg)

 def right(self, *args, **kwargs):
  buff = self.view.get_current_buffer_pos()
  buffer = self.get_current_buffer()
  if not hasattr(buffer.buffer, "list"):
   output.speak(_(u"This account is not logged in twitter."))
   return
  if buff == self.get_last_buffer(buffer.account) or buff+1 == self.view.get_buffer_count():
   self.view.change_buffer(self.get_first_buffer(buffer.account))
  else:
   self.view.change_buffer(buff+1)
  while self.get_current_buffer().invisible == False: self.skip_buffer(True)
  buffer = self.get_current_buffer()
  try:
   msg = _(u"%s, %s of %s") % (self.view.get_buffer_text(), buffer.buffer.list.get_selected()+1, buffer.buffer.list.get_count())
  except:
   msg = _(u"%s. Empty") % (self.view.get_buffer_text(),)
  output.speak(msg)

 def next_account(self, *args, **kwargs):
  index = self.accounts.index(self.current_account)
  if index+1 == len(self.accounts):
   index = 0
  else:
   index = index+1
  account = self.accounts[index]
  self.current_account = account
  buff = self.view.search("home_timeline", account)
  if buff == None:
   output.speak(_(u"{0}: This account is not logged in twitter.").format(account))
   return
  self.view.change_buffer(buff)
  buffer = self.get_current_buffer()
  try:
   msg = _(u"%s. %s, %s of %s") % (buffer.account, self.view.get_buffer_text(), buffer.buffer.list.get_selected()+1, buffer.buffer.list.get_count())
  except:
   msg = _(u"%s. Empty") % (self.view.get_buffer_text(),)
  output.speak(msg)

 def previous_account(self, *args, **kwargs):
  index = self.accounts.index(self.current_account)
  if index-1 < 0:
   index = len(self.accounts)-1
  else:
   index = index-1
  account = self.accounts[index]
  self.current_account = account
  buff = self.view.search("home_timeline", account)
  if buff == None:
   output.speak(_(u"{0}: This account is not logged in twitter.").format(account))
   return
  self.view.change_buffer(buff)
  buffer = self.get_current_buffer()
  try:
   msg = _(u"%s. %s, %s of %s") % (buffer.account, self.view.get_buffer_text(), buffer.buffer.list.get_selected()+1, buffer.buffer.list.get_count())
  except:
   msg = _(u"%s. Empty") % (self.view.get_buffer_text(),)
  output.speak(msg)

 def go_home(self):
  buffer = self.get_current_buffer()
  buffer.buffer.list.select_item(0)
  try:
   output.speak(buffer.get_message())
  except:
   pass

 def go_end(self):
  buffer = self.get_current_buffer()
  buffer.buffer.list.select_item(buffer.buffer.list.get_count()-1)
  try:
   output.speak(buffer.get_message())
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
   output.speak(buffer.get_message())
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
   output.speak(buffer.get_message())
  except:
   pass

 def url(self, *args, **kwargs):
  self.get_current_buffer().url()

 def audio(self, *args, **kwargs):
  self.get_current_buffer().audio()

 def volume_down(self, *args, **kwargs):
  self.get_current_buffer().volume_down()

 def volume_up(self, *args, **kwargs):
  self.get_current_buffer().volume_up()

 def create_invisible_keyboard_shorcuts(self):
  keymap = {}
  for i in config.app["keymap"]:
   if hasattr(self, i):
    keymap[config.app["keymap"][i]] = getattr(self, i)
  return keymap

 def register_invisible_keyboard_shorcuts(self, keymap):
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
   output.speak(message)

 def manage_home_timelines(self, data, user):
  buffer = self.search_buffer("home_timeline", user)
  play_sound = "tweet_received.ogg"
  if "home_timeline" not in buffer.session.settings["other_buffers"]["muted_buffers"]:
   self.notify(buffer.session, play_sound=play_sound)
  buffer.add_new_item(data)

 def manage_mentions(self, data, user):
  buffer = self.search_buffer("mentions", user)
  play_sound = "mention_received.ogg"
  message = _(u"New mention")
  if "mentions"  not in buffer.session.settings["other_buffers"]["muted_buffers"]:
   self.notify(buffer.session, play_sound=play_sound, message=message)
  buffer.add_new_item(data)

 def manage_direct_messages(self, data, user):
  buffer = self.search_buffer("direct_messages", user)
  play_sound = "dm_received.ogg"
  message = _(u"New direct message")
  if "direct_messages"  not in buffer.session.settings["other_buffers"]["muted_buffers"]:
   self.notify(buffer.session, play_sound=play_sound, message=message)
  buffer.add_new_item(data)

 def manage_sent_dm(self, data, user):
  buffer = self.search_buffer("sent_direct_messages", user)
  play_sound = "dm_sent.ogg"
  if "sent_direct_messages" not in buffer.session.settings["other_buffers"]["muted_buffers"]:
   self.notify(buffer.session, play_sound=play_sound)
  buffer.add_new_item(data)

 def manage_sent_tweets(self, data, user):
  buffer = self.search_buffer("sent_tweets", user)
  play_sound = "tweet_send.ogg"
  if "sent_tweets" not in buffer.session.settings["other_buffers"]["muted_buffers"]:
   self.notify(buffer.session, play_sound=play_sound)
  buffer.add_new_item(data)

 def manage_events(self, data, user):
  buffer = self.search_buffer("events", user)
  play_sound = "new_event.ogg"
  if "events" not in buffer.session.settings["other_buffers"]["muted_buffers"]:
   self.notify(buffer.session, play_sound=play_sound)
  buffer.add_new_item(data)

 def manage_followers(self, data, user):
  buffer = self.search_buffer("followers", user)
  play_sound = "update_followers.ogg"
  if "followers" not in buffer.session.settings["other_buffers"]["muted_buffers"]:
   self.notify(buffer.session, play_sound=play_sound)
  buffer.add_new_item(data)
  pub.sendMessage("restart-streams", streams=["main_stream"], session=buffer.session)

 def manage_friend(self, data, user):
  buffer = self.search_buffer("friends", user)
  buffer.add_new_item(data)

 def manage_unfollowing(self, item, user):
  buffer = self.search_buffer("friends", user)
  buffer.remove_item(item)

 def manage_favourite(self, data, user):
  buffer = self.search_buffer("favourites", user)
  play_sound = "favourite.ogg"
  if "favourites" not in buffer.session.settings["other_buffers"]["muted_buffers"]:
   self.notify(buffer.session, play_sound=play_sound)
  buffer.add_new_item(data)

 def manage_unfavourite(self, item, user):
  buffer = self.search_buffer("favourites", user)
  buffer.remove_item(item)

 def manage_blocked_user(self, data, user):
  buffer = self.search_buffer("blocked", user)
  buffer.add_new_item(data)

 def manage_unblocked_user(self, item, user):
  buffer = self.search_buffer("blocked", user)
  buffer.remove_item(item)

 def manage_item_in_timeline(self, data, user, who):
  buffer = self.search_buffer("%s-timeline" % (who,), user)
  play_sound = "tweet_timeline.ogg"
  if "%s-timeline" % (who,) not in buffer.session.settings["other_buffers"]["muted_buffers"]:
   self.notify(buffer.session, play_sound=play_sound)
  buffer.add_new_item(data)

 def start_buffers(self, session):
  log.debug("starting buffers... Session %s" % (session.session_id,))
  for i in self.buffers:
   if i.session == session and i.needs_init == True:
    i.start_stream()
  log.debug("Starting the streaming endpoint")
  session.start_streaming()

 def manage_stream_errors(self, session):
  log.error("An error ocurred with the stream for the %s session. It will be destroyed" % (session,))
  s = session_.sessions[session]
  s.listen_stream_error()

 def check_connection(self):
  for i in session_.sessions:
   if session_.sessions[i].is_logged == False: continue
   session_.sessions[i].check_connection()

 def create_new_buffer(self, buffer, account, create):
  buff = self.search_buffer("home_timeline", account)
  if create == True:
   if buffer == "favourites":
    favourites = buffersController.baseBufferController(self.view.nb, "get_favorites", "favourites", buff.session, buff.session.db["user_name"])
    self.buffers.append(favourites)
    self.view.insert_buffer(favourites.buffer, name=_(u"Favourites"), pos=self.view.search(buff.session.db["user_name"], buff.session.db["user_name"]))
    favourites.start_stream()
   if buffer == "followers":
    followers = buffersController.peopleBufferController(self.view.nb, "get_followers_list", "followers", buff.session, buff.session.db["user_name"], screen_name=buff.session.db["user_name"])
    self.buffers.append(followers)
    self.view.insert_buffer(followers.buffer, name=_(u"Followers"), pos=self.view.search(buff.session.db["user_name"], buff.session.db["user_name"]))
    followers.start_stream()
   elif buffer == "friends":
    friends = buffersController.peopleBufferController(self.view.nb, "get_friends_list", "friends", buff.session, buff.session.db["user_name"], screen_name=buff.session.db["user_name"])
    self.buffers.append(friends)
    self.view.insert_buffer(friends.buffer, name=_(u"Friends"), pos=self.view.search(buff.session.db["user_name"], buff.session.db["user_name"]))
    friends.start_stream()
   elif buffer == "blocked":
    blocks = buffersController.peopleBufferController(self.view.nb, "list_blocks", "blocked", buff.session, buff.session.db["user_name"])
    self.buffers.append(blocks)
    self.view.insert_buffer(blocks.buffer, name=_(u"Blocked users"), pos=self.view.search(buff.session.db["user_name"], buff.session.db["user_name"]))
    blocks.start_stream()
   elif buffer == "muted":
    muted = buffersController.peopleBufferController(self.view.nb, "get_muted_users_list", "muted", buff.session, buff.session.db["user_name"])
    self.buffers.append(muted)
    self.view.insert_buffer(muted.buffer, name=_(u"Muted users"), pos=self.view.search(buff.session.db["user_name"], buff.session.db["user_name"]))
    muted.start_stream()
   elif buffer == "events":
    events = buffersController.eventsBufferController(self.view.nb, "events", buff.session, buff.session.db["user_name"], bufferType="dmPanel", screen_name=buff.session.db["user_name"])
    self.buffers.append(events)
    self.view.insert_buffer(events.buffer, name=_(u"Events"), pos=self.view.search(buff.session.db["user_name"], buff.session.db["user_name"]))
  elif create == False:
   self.destroy_buffer(buffer, buff.session.db["user_name"])

 def restart_streams(self, streams=[], session=None):
  for i in streams:
   log.debug("Restarting the %s stream" % (i,))
   session.remove_stream(i)
  session.check_connection()

 def invisible_shorcuts_changed(self, registered):
  if registered == True:
   km = self.create_invisible_keyboard_shorcuts()
   self.register_invisible_keyboard_shorcuts(km)
  elif registered == False:
   km = self.create_invisible_keyboard_shorcuts()
   self.unregister_invisible_keyboard_shorcuts(km)

 def about(self, *args, **kwargs):
  self.view.about_dialog()

 def visit_website(self, *args, **kwargs):
  webbrowser.open(application.url)

 def manage_accounts(self, *args, **kwargs):
  sm = sessionManager.sessionManagerController()
  sm.fill_list()
  sm.show()
  for i in sm.new_sessions:
   self.create_buffers(session_.sessions[i])
   call_threaded(self.start_buffers, session_.sessions[i])
  for i in sm.removed_sessions:
   if session_.sessions[i].logged == True:
    self.logout_account(session_.sessions[i].session_id)
   self.destroy_buffer(session_.sessions[i].settings["twitter"]["user_name"], session_.sessions[i].settings["twitter"]["user_name"])
   self.accounts.remove(session_.sessions[i].settings["twitter"]["user_name"])
   session_.sessions.pop(i)

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
   output.speak(_(u"The auto-reading of new tweets is enabled for this buffer"))
  elif buffer.name in buffer.session.settings["other_buffers"]["autoread_buffers"]:
   buffer.session.settings["other_buffers"]["autoread_buffers"].remove(buffer.name)
   output.speak(_(u"The auto-reading of new tweets is disabled for this buffer"))

 def toggle_session_mute(self, *args, **kwargs):
  buffer = self.get_best_buffer()
  if buffer.session.settings["sound"]["session_mute"] == False:
   buffer.session.settings["sound"]["session_mute"] = True
   output.speak(_(u"Session mute on"))
  elif buffer.session.settings["sound"]["session_mute"] == True:
   buffer.session.settings["sound"]["session_mute"] = False
   output.speak(_(u"Global mute off"))

 def toggle_buffer_mute(self, *args, **kwargs):
  buffer = self.get_current_buffer()
  if hasattr(buffer, "session") and buffer.session == None: return
  if buffer.name not in buffer.session.settings["other_buffers"]["muted_buffers"]:
   buffer.session.settings["other_buffers"]["muted_buffers"].append(buffer.name)
   output.speak(_(u"Buffer mute on"))
  elif buffer.name in buffer.session.settings["other_buffers"]["muted_buffers"]:
   buffer.session.settings["other_buffers"]["muted_buffers"].remove(buffer.name)
   output.speak(_(u"Buffer mute off"))

 def __del__(self):
  config.app.write()