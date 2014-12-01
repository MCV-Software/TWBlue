# -*- coding: utf-8 -*-
############################################################
#    Copyright (c) 2013, 2014 Manuel Eduardo Cortéz Vallejo <manuel@manuelcortez.net>
#       
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
############################################################
import wx
import dialogs
import buffers
import config
import twitter
import db
import webbrowser
import sound
import updater
import application
import os
import logging as original_logger
import output
import platform
import urllib2
import sysTrayIcon
import switchModule
import languageHandler
import pygeocoder
from pygeolib import GeocoderError
from sessionmanager import manager
from mysc import event
from mysc.thread_utils import call_threaded
from twython import TwythonError
from urllib2 import URLError
from mysc.repeating_timer import RepeatingTimer
from mysc import localization
if platform.system() == "Windows" or platform.system() == "Linux":
 from keyboard_handler.wx_handler import WXKeyboardHandler
from extra import SoundsTutorial
from keystrokeEditor import gui as keystrokeEditorGUI
log = original_logger.getLogger("gui.main")

geocoder = pygeocoder.Geocoder()
class mainFrame(wx.Frame):
 """ Main class of the Frame. This is the Main Window."""

 ### MENU
 def makeMenus(self):
  """ Creates, bind and returns the menu bar for the application. Also in this function, the accel table is created."""
  menuBar = wx.MenuBar()

  # Application menu
  app = wx.Menu()
  switch_account = app.Append(wx.NewId(), _(u"S&witch account"))
  self.Bind(wx.EVT_MENU, self.switch_account, switch_account)
  updateProfile = app.Append(wx.NewId(), _(u"&Update profile"))
  self.Bind(wx.EVT_MENU, self.update_profile, updateProfile)
  show_hide = app.Append(wx.NewId(), _(u"&Hide window"))
  self.Bind(wx.EVT_MENU, self.show_hide, show_hide)
  search = app.Append(wx.NewId(), _(u"&Search"))
  self.Bind(wx.EVT_MENU, self.search, search)
  lists = app.Append(wx.NewId(), _(u"&Lists manager"))
  self.Bind(wx.EVT_MENU, self.list_manager, lists)
  sounds_tutorial = app.Append(wx.NewId(), _(u"Sounds &tutorial"))
  self.Bind(wx.EVT_MENU, self.learn_sounds, sounds_tutorial)
  keystroke_editor = app.Append(wx.NewId(), _(u"&Edit keystrokes"))
  self.Bind(wx.EVT_MENU, self.edit_keystrokes, keystroke_editor)
  prefs = app.Append(wx.ID_PREFERENCES, _(u"&Preferences"))
  self.Bind(wx.EVT_MENU, self.preferences, prefs)
  close = app.Append(wx.ID_EXIT, _(u"E&xit"))
  self.Bind(wx.EVT_MENU, self.close, close)

  # Tweet menu
  tweet = wx.Menu()
  compose = tweet.Append(wx.NewId(), _(u"&Tweet"))
  self.Bind(wx.EVT_MENU, self.compose, compose)
  response = tweet.Append(wx.NewId(), _(u"Re&ply"))
  self.Bind(wx.EVT_MENU, self.reply, response)
  retweet = tweet.Append(wx.NewId(), _(u"&Retweet"))
  self.Bind(wx.EVT_MENU, self.retweet, retweet)
  fav = tweet.Append(wx.NewId(), _(u"Add to &favourites"))
  self.Bind(wx.EVT_MENU, self.fav, fav)
  unfav = tweet.Append(wx.NewId(), _(u"Remove from favo&urites"))
  self.Bind(wx.EVT_MENU, self.unfav, unfav)
  view = tweet.Append(wx.NewId(), _(u"&Show tweet"))
  self.Bind(wx.EVT_MENU, self.view, view)
  view_coordinates = tweet.Append(wx.NewId(), _(u"View &address"))
  self.Bind(wx.EVT_MENU, self.reverse_geocode, view_coordinates)
  delete = tweet.Append(wx.NewId(), _(u"&Delete"))
  self.Bind(wx.EVT_MENU, self.delete, delete)

  # User menu
  user = wx.Menu()
  follow = user.Append(wx.NewId(), _(u"&Follow"))
  self.Bind(wx.EVT_MENU, self.onFollow, follow)
  unfollow = user.Append(wx.NewId(), _(u"&Unfollow"))
  self.Bind(wx.EVT_MENU, self.onUnfollow, unfollow)
  mute = user.Append(wx.NewId(), _(u"&Mute"))
  self.Bind(wx.EVT_MENU, self.onMute, mute)
  unmute = user.Append(wx.NewId(), _(u"U&nmute"))
  self.Bind(wx.EVT_MENU, self.onUnmute, unmute)
  report = user.Append(wx.NewId(), _(u"&Report as spam"))
  self.Bind(wx.EVT_MENU, self.onReport, report)
  block = user.Append(wx.NewId(), _(u"&Block"))
  self.Bind(wx.EVT_MENU, self.onBlock, block)
  unblock = user.Append(wx.NewId(), _(u"Unb&lock"))
  self.Bind(wx.EVT_MENU, self.onUnblock, unblock)
  dm = user.Append(wx.NewId(), _(u"Direct me&ssage"))
  self.Bind(wx.EVT_MENU, self.dm, dm)
  addToList = user.Append(wx.NewId(), _(u"&Add to list"))
  self.Bind(wx.EVT_MENU, self.add_to_list, addToList)
  removeFromList = user.Append(wx.NewId(), _(u"R&emove from list"))
  self.Bind(wx.EVT_MENU, self.remove_from_list, removeFromList)
  viewLists = user.Append(wx.NewId(), _(u"&View lists"))
  self.Bind(wx.EVT_MENU, self.view_user_lists, viewLists)
  details = user.Append(wx.NewId(), _(u"Show user &profile"))
  self.Bind(wx.EVT_MENU, self.details, details)
  timeline = user.Append(wx.NewId(), _(u"&Timeline"))
  self.Bind(wx.EVT_MENU, self.open_timeline, timeline)
  favs = user.Append(wx.NewId(), _(u"V&iew favourites"))
  self.Bind(wx.EVT_MENU, self.favs_timeline, favs)

  # buffer menu
  buffer = wx.Menu()
  load_previous_items = buffer.Append(wx.NewId(), _(u"&Load previous items"))
  self.Bind(wx.EVT_MENU, self.get_more_items, load_previous_items)
  mute = buffer.Append(wx.NewId(), _(u"&Mute"))
  self.Bind(wx.EVT_MENU, self.toggle_mute, mute)
  autoread = buffer.Append(wx.NewId(), _(u"&Autoread tweets for this buffer"))
  self.Bind(wx.EVT_MENU, self.toggle_autoread, autoread)
  clear = buffer.Append(wx.NewId(), _(u"&Clear buffer"))
  self.Bind(wx.EVT_MENU, self.clear_list, clear)
  deleteTl = buffer.Append(wx.NewId(), _(u"&Remove buffer"))
  self.Bind(wx.EVT_MENU, self.delete_buffer, deleteTl)

 # Help Menu
  help = wx.Menu()
  doc = help.Append(-1, _(u"&Documentation"))
  self.Bind(wx.EVT_MENU, self.onManual, doc)
  changelog = help.Append(wx.NewId(), _(u"&What's new in this version?"))
  self.Bind(wx.EVT_MENU, self.onChangelog, changelog)
  check_for_updates = help.Append(wx.NewId(), _(u"&Check for updates"))
  self.Bind(wx.EVT_MENU, self.onCheckForUpdates, check_for_updates)
  reportError = help.Append(wx.NewId(), _(u"&Report an error"))
  self.Bind(wx.EVT_MENU, self.onReportBug, reportError)
  visit_website = help.Append(-1, _(u"TW Blue &website"))
  self.Bind(wx.EVT_MENU, self.onVisit_website, visit_website)
  about = help.Append(-1, _(u"About &TW Blue"))
  self.Bind(wx.EVT_MENU, self.onAbout, about)

  # Add all to the menu Bar
  menuBar.Append(app, _(u"&Application"))
  menuBar.Append(tweet, _(u"&Tweet"))
  menuBar.Append(user, _(u"&User"))
  menuBar.Append(buffer, _(u"&Buffer"))
  menuBar.Append(help, _(u"&Help"))

  downID = wx.NewId()
  upID = wx.NewId()
  leftID = wx.NewId()
  rightID = wx.NewId()
  if platform.system() == "Darwin":
   self.Bind(wx.EVT_MENU, self.down, id=downID)
   self.Bind(wx.EVT_MENU, self.up, id=upID)
   self.Bind(wx.EVT_MENU, self.left, id=leftID)
   self.Bind(wx.EVT_MENU, self.right, id=rightID)

  # Creates the acceleration table.
  self.accel_tbl = wx.AcceleratorTable([
(wx.ACCEL_CTRL, ord('N'), compose.GetId()),
(wx.ACCEL_CTRL, ord('R'), response.GetId()),
(wx.ACCEL_CTRL|wx.ACCEL_SHIFT, ord('R'), retweet.GetId()),
(wx.ACCEL_CTRL, ord('F'), fav.GetId()),
(wx.ACCEL_CTRL|wx.ACCEL_SHIFT, ord('F'), unfav.GetId()),
(wx.ACCEL_CTRL|wx.ACCEL_SHIFT, ord('V'), view.GetId()),
(wx.ACCEL_CTRL, ord('D'), dm.GetId()),

(wx.ACCEL_CTRL, ord('Q'), close.GetId()),
(wx.ACCEL_CTRL, ord('S'), follow.GetId()),
(wx.ACCEL_CTRL|wx.ACCEL_SHIFT, ord('S'), unfollow.GetId()),
(wx.ACCEL_CTRL, ord('K'), block.GetId()),
(wx.ACCEL_CTRL|wx.ACCEL_SHIFT, ord('K'), report.GetId()),
(wx.ACCEL_CTRL, ord('I'), timeline.GetId()),
(wx.ACCEL_CTRL|wx.ACCEL_SHIFT, ord('I'), deleteTl.GetId()),
(wx.ACCEL_CTRL, ord('M'), show_hide.GetId()),
(wx.ACCEL_CTRL, ord('P'), updateProfile.GetId()),
(wx.ACCEL_CTRL, wx.WXK_DOWN, downID),
(wx.ACCEL_CTRL, wx.WXK_UP, upID),
(wx.ACCEL_CTRL, wx.WXK_LEFT, leftID),
(wx.ACCEL_CTRL, wx.WXK_RIGHT, rightID),
  ])

  self.SetAcceleratorTable(self.accel_tbl)
  return menuBar

 ### MAIN
 def __init__(self, authorised=True, user_key=None, user_secret=None):
  """ Main function of this class."""
  if authorised == False:
   self.user_key = user_key
   self.user_secret = user_secret
  else:
   self.user_key = self.user_secret = None
  log.debug("Loading temporal database...")
  self.db = db.db()
  # Gets the twitter object for future calls to the twitter Rest API.
  log.debug("Getting Twitter's Rest API...")
  self.twitter = twitter.twitter.twitter()
  super(mainFrame, self).__init__(None, -1, "TW Blue", size=(1600, 1600))
  self.Bind(wx.EVT_QUERY_END_SESSION, self.exit)
  self.Bind(wx.EVT_END_SESSION, self.exit)
  log.debug(u"Creating the system tray icon... ")
  self.sysTray=sysTrayIcon.SysTrayIcon(self)
  panel = wx.Panel(self)
  self.sizer = wx.BoxSizer(wx.VERTICAL)
  self.SetTitle("TW Blue")
  try:
   updater.update_manager.check_for_update()
  except:
   pass
  self.SetMenuBar(self.makeMenus())
  self.setup_twitter(panel)

 def logging_in_twblue(self, panel):
  log.debug("Retrieving username...")
  twitter.starting.start_user_info(config=self.db, twitter=self.twitter)
  config.main["twitter"]["user_name"] = self.db.settings["user_name"]
  self.SetTitle(u"@%s. - TW Blue" % (self.db.settings["user_name"]))
  self.nb = wx.Treebook(panel, -1)
  self.Bind(wx.EVT_CLOSE, self.close)
  self.nb.Bind(wx.EVT_TREEBOOK_PAGE_CHANGED, self.onPageChanged)
  # Gets the tabs for home, mentions, send and direct messages.
  log.debug("Creating buffers...")
  self.db.settings["buffers"] = []
  account = buffers.accountPanel(self.nb)
  self.nb.AddPage(account, self.db.settings["user_name"])
  self.db.settings["buffers"].append(self.db.settings["user_name"])
  account_index = self.db.settings["buffers"].index(self.db.settings["user_name"])
  home = buffers.basePanel(self.nb, self, "home_timeline", self.twitter.twitter.get_home_timeline, sound="tweet_received.ogg")
  self.nb.InsertSubPage(account_index, home, _(u"Home"))
  self.db.settings["buffers"].append("home_timeline")
  self.nb.SetSelection(1)
  self.nb.GetPage(1).list.list.SetFocus()
  mentionsP = buffers.basePanel(self.nb, self, "mentions", self.twitter.twitter.get_mentions_timeline, sound="mention_received.ogg")
  self.nb.InsertSubPage(account_index, mentionsP, _("Mentions"))
  self.db.settings["buffers"].append("mentions")
  dms = buffers.dmPanel(self.nb, self, "direct_messages", self.twitter.twitter.get_direct_messages, sound="dm_received.ogg")
  self.nb.InsertSubPage(account_index, dms, _(u"Direct messages"))
  self.db.settings["buffers"].append("direct_messages")
  sent = buffers.basePanel(self.nb, self, "sent", self.twitter.twitter.get_user_timeline, argumento=self.db.settings["user_name"])
  self.nb.InsertSubPage(account_index, sent, _(u"Sent"))
  self.db.settings["buffers"].append("sent")
# If the user has enabled favs from config.
  if config.main["other_buffers"]["show_favourites"] == True:
   log.debug("Getting Favorited tweets...")
   favs = buffers.basePanel(self.nb, self, "favs", self.twitter.twitter.get_favorites)
   self.nb.InsertSubPage(account_index, favs, _(u"Favourites"))
   self.db.settings["buffers"].append("favs")
# If followers are enabled from config.
  if config.main["other_buffers"]["show_followers"] == True:
   log.debug("Getting followers...")
   followers = buffers.peoplePanel(self.nb, self, "followers", self.twitter.twitter.get_followers_list, argumento=self.db.settings["user_name"], sound="update_followers.ogg")
   self.nb.InsertSubPage(account_index, followers, _(u"Followers"))
   self.db.settings["buffers"].append("followers")
  # Same here but for friends.
  if config.main["other_buffers"]["show_friends"] == True:
   log.debug("Getting friends...")
   friends = buffers.peoplePanel(self.nb, self, "friends", self.twitter.twitter.get_friends_list, argumento=self.db.settings["user_name"])
   self.nb.InsertSubPage(account_index, friends, _(u"Friends"))
   self.db.settings["buffers"].append("friends")
  if config.main["other_buffers"]["show_blocks"] == True:
   blocked = buffers.peoplePanel(self.nb, self, "blocks", self.twitter.twitter.list_blocks)
   self.nb.InsertSubPage(account_index, blocked, _(u"Blocked users"))
   self.db.settings["buffers"].append("blocks")
  if config.main["other_buffers"]["show_muted_users"] == True:
   muteds = buffers.peoplePanel(self.nb, self, "muteds", self.twitter.twitter.get_muted_users_list)
   self.nb.InsertSubPage(account_index, muteds, _(u"Muted users"))
   self.db.settings["buffers"].append("muteds")
  if config.main["other_buffers"]["show_events"] == True:
   evt = buffers.eventsPanel(self.nb, self, sound="new_event.ogg")
   self.nb.InsertSubPage(account_index, evt, _(u"Events"))
   self.db.settings["buffers"].append("events")
  searches = buffers.emptyPanel(self.nb)
  self.nb.InsertSubPage(account_index, searches, _(u"Searches"))
  self.db.settings["buffers"].append("searches")

  for i in config.main["other_buffers"]["tweet_searches"]:
   self.nb.InsertSubPage(self.db.settings["buffers"].index("searches"), buffers.searchPanel(self.nb, self, "%s-search" % (i,), q=i, count=100), _(u"Search for %s" % (i,)))
   self.db.settings["buffers"].append("%s-search" % (i,))
  timelines = buffers.emptyPanel(self.nb)
  self.nb.InsertSubPage(account_index, timelines, _(u"Timelines"))
  self.db.settings["buffers"].append("timelines")
  for i in config.main["other_buffers"]["timelines"]:
   self.nb.InsertSubPage(self.db.settings["buffers"].index("timelines"), buffers.basePanel(self.nb, self, i, self.twitter.twitter.get_user_timeline, argumento=i, timeline=True, sound="tweet_timeline.ogg"), _(u"Timeline for %s") % i)
   self.db.settings["buffers"].append(i)
  lists = buffers.emptyPanel(self.nb)
  self.nb.InsertSubPage(account_index, lists, _(u"Lists"))
  self.db.settings["buffers"].append("lists")
  for i in config.main["other_buffers"]["lists"]:
   self.nb.InsertSubPage(self.db.settings["buffers"].index("lists"), buffers.listPanel(self.nb, self, i+"-list", argumento=twitter.utils.find_list(i, self.db.settings["lists"])), _(u"List for %s") % i)
   self.db.settings["buffers"].append(i+"-list")

  ## favourites timelines
  favs_timelines = buffers.emptyPanel(self.nb)
  self.nb.InsertSubPage(account_index, favs_timelines, _(U"Favourites timelines"))
  self.db.settings["buffers"].append("favourites_timelines")
  for i in config.main["other_buffers"]["favourites_timelines"]:
   self.nb.InsertSubPage(self.db.settings["buffers"].index("favourites_timelines"), buffers.favsPanel(self.nb, self, i+"favs", argumento=i, sound="favourites_timeline_updated.ogg"), _(u"Favourites for %s") % i,)
   self.db.settings["buffers"].append(i+"favs")
  self.fav_stream = RepeatingTimer(180, self.get_fav_buffers)
  self.fav_stream.start()
  self.sizer.Add(self.nb, 0, wx.ALL, 5)
  panel.SetSizer(self.sizer)
  self.SetClientSize(self.sizer.CalcMin())
  self.Bind(event.MyEVT_STARTED, self.onInit)
  self.Bind(event.EVT_RESULT, self.onMemberAdded)
  call_threaded(self.init, run_streams=True)

 def init(self, run_streams=False):
  """ Calls the start_stream function for each stream tab."""
  deleted = 0
  for i in range(0, self.nb.GetPageCount()):
   if self.nb.GetPage(i).type == "account" or self.nb.GetPage(i).type == "empty": continue
   if i == self.nb.GetPageCount() and deleted > 0:
    i = i-1
    deleted = deleted-1
   log.debug("Starting stream for %s..." % self.nb.GetPage(i).name_buffer)
   info_event = event.infoEvent(event.EVT_STARTED, 1)
   try:
    if self.nb.GetPage(i).type == "search":
     self.nb.GetPage(i).timer = RepeatingTimer(180, self.nb.GetPage(i).load_search)
     self.nb.GetPage(i).timer.start()
    num = self.nb.GetPage(i).start_streams()
    info_event.SetItem(i, num)
    wx.PostEvent(self, info_event)
   except TwythonError as e:
    continue
   except UnicodeDecodeError: # This happens when there is a bad internet connection
    continue
  output.speak(_(u"Ready"))

  if run_streams == True:
   self.get_home()
   self.get_tls()
   self.check_streams = RepeatingTimer(config.main["general"]["time_to_check_streams"], self.check_stream_up)
   self.check_streams.start()
  # If all it's done, then play a nice sound saying that all it's OK.
  sound.player.play("ready.ogg")

 def remove_list(self, id):
  for i in range(0, self.nb.GetPageCount()):
   if self.nb.GetPage(i).type == "list":
    if self.nb.GetPage(i).argumento == id:
     pos = self.nb.GetCurrentPage().remove_invalid_buffer()
     if pos != None:
      self.nb.DeletePage(pos)
      self.onMemberAdded()

 def onMemberAdded(self, ev):
  self.stream2.disconnect()
  del self.stream2
  self.get_tls()

 def get_fav_buffers(self):
  for i in config.main["other_buffers"]["favourites_timelines"]:
   num = self.nb.GetPage(self.db.settings["buffers"].index(i+"favs")).start_streams()
   if num > 0: output.speak(_(u"%s favourites from %s") % (nun, i))

 def setup_twitter(self, panel):
  """ Setting up the connection for twitter, or authenticate if the config file has valid credentials."""
  try:
   self.twitter.login(self.user_key, self.user_secret)
   self.logging_in_twblue(panel)
   log.info("Authorized in Twitter.")
   del self.user_key; del self.user_secret
  except:
   dlg1 = wx.MessageDialog(panel, _(u"Connection error. Try again later."), _(u"Error!"), wx.ICON_ERROR)
   dlg1.ShowModal()
   self.Close(True)

 def get_home(self):
  """ Gets the home stream, that manages home timeline, mentions, direct messages and sent."""
  try:
   self.stream = twitter.buffers.stream.streamer(application.app_key, application.app_secret, config.main["twitter"]["user_key"], config.main["twitter"]["user_secret"], parent=self)
   call_threaded(self.stream.user)
  except:
   self.stream.disconnect()

 def start_lists(self):
  for i in range(0, self.nb.GetPageCount()):
   if self.nb.GetPage(i).type == "list": self.nb.GetPage(i).retrieve_ids()

 def get_tls(self):
  """ Setting the stream for individual user timelines."""
#  try:
  self.stream2 = twitter.buffers.indibidual.streamer(application.app_key, application.app_secret, config.main["twitter"]["user_key"], config.main["twitter"]["user_secret"], parent=self)
  # The self.ids contains all IDS for the follow argument of the stream.
  ids = ""
   # If we have more than 0 items on a list, then.
  for i in config.main["other_buffers"]["timelines"]:
   ids = ids+self.db.settings[i][0]["user"]["id_str"]+", "
  for i in range(0, self.nb.GetPageCount()):
   if self.nb.GetPage(i).type == "list":
    for z in self.nb.GetPage(i).users:
     ids+= str(z)+", "
  if ids != "":
 #   try:
   call_threaded(self.stream2.statuses.filter, follow=ids)
 #   except:
 #    pass
#  except:
#   self.stream2.disconnect()

 def check_stream_up(self):
  try:
   urllib2.urlopen("http://74.125.228.231", timeout=5)
  except urllib2.URLError:
   if self.stream.connected == True: self.stream.disconnect()
   if hasattr(self, "stream2") and self.stream2.connected: self.stream2.disconnect()
   if config.main["general"]["announce_stream_status"] == True: output.speak(_(u"Streams disconnected. TW Blue will try to reconnect in a minute."))
   return
  if self.stream.connected == False:
   del self.stream
   if config.main["general"]["announce_stream_status"] == True: output.speak(_(u"Reconnecting streams..."))
   call_threaded(self.init)
   self.get_home()
  if hasattr(self, "stream2") and self.stream2.connected == False:
   log.debug("Trying reconnects the timelines stream...")
   del self.stream2
   self.get_tls()

 ### Events

 def edit_keystrokes(self, ev=None):
  if hasattr(self, "keyboard_handler"):
   dlg = keystrokeEditorGUI.keystrokeEditor(parent=self, keyboard_handler=self.keyboard_handler)
  else:
   dlg = keystrokeEditorGUI.keystrokeEditor(parent=self)
  dlg.ShowModal()
  dlg.Destroy()

 def search(self, ev=None):
  dlg = dialogs.search.searchDialog()
  if dlg.ShowModal() == wx.ID_OK:
   term = dlg.term.GetValue()
   if dlg.tweets.GetValue() == True:
    search =buffers.searchPanel(self.nb, self, "%s-search" % (term,), q=term, count=100)
    self.nb.InsertSubPage(self.db.settings["buffers"].index("searches"), search, _(u"search for %s") % (term,))
    self.db.settings["buffers"].append("%s-search" % (term,))
    config.main["other_buffers"]["tweet_searches"].append(term)
   elif dlg.users.GetValue() == True:
    search =buffers.searchUsersPanel(self.nb, self, "%s_search" % (term,), q=term, count=20)
    self.nb.InsertSubPage(self.db.settings["buffers"].index("searches"), search, _(u"search users for %s") % (term,))
    self.db.settings["buffers"].append("%s_search" % (term,))
   timer = RepeatingTimer(180, search.load_search)
   timer.start()
   num = search.start_streams()
   search.put_items(num)
  dlg.Destroy()

 def learn_sounds(self, ev):
  SoundsTutorial.gui.soundsTutorial().ShowModal()

 def view_user_lists(self, ev=None):
  userDlg = dialogs.utils.selectUserDialog(parent=self, title=_(u"Select the user"))
  if userDlg.ShowModal() == wx.ID_OK:
   user = userDlg.cb.GetValue()
  else:
   return
  dlg = dialogs.lists.userListViewer(self, user)
  dlg.ShowModal()
  userDlg.Destroy()
  dlg.Destroy()

 def add_to_list(self, ev=None):
  userDlg = dialogs.utils.selectUserDialog(parent=self, title=_(u"Select the user"))
  if userDlg.ShowModal() == wx.ID_OK:
   user = userDlg.cb.GetValue()
  else:
   return
  dlg = dialogs.lists.addUserListDialog(self)
  if dlg.ShowModal() == wx.ID_OK:
   try:
    list = self.twitter.twitter.add_list_member(list_id=self.db.settings["lists"][dlg.lista.get_selected()]["id"], screen_name=user)
    older_list = twitter.utils.find_item(self.db.settings["lists"][dlg.lista.get_selected()]["id"], self.db.settings["lists"])
    if list["mode"] == "private":
     self.db.settings["lists"].pop(older_list)
     self.db.settings["lists"].append(list)
   except TwythonError as e:
    output.speak("error %s: %s" % (e.error_code, e.msg))
  userDlg.Destroy()
  dlg.Destroy()

 def remove_from_list(self, ev=None):
  userDlg = dialogs.utils.selectUserDialog(parent=self, title=_(u"Select the user"))
  if userDlg.ShowModal() == wx.ID_OK:
   user = userDlg.cb.GetValue()
  else:
   return
  dlg = dialogs.lists.removeUserListDialog(self)
  if dlg.ShowModal() == wx.ID_OK:
   try:
    list = self.twitter.twitter.delete_list_member(list_id=self.db.settings["lists"][dlg.lista.get_selected()]["id"], screen_name=user)
    older_list = twitter.utils.find_item(self.db.settings["lists"][dlg.get_selected()]["id"], self.db.settings["lists"])
    if list["mode"] == "private":
     self.db.settings["lists"].pop(older_list)
     self.db.settings["lists"].append(list)
   except TwythonError as e:
    output.speak("error %s: %s" % (e.error_code, e.msg))
  userDlg.Destroy()
  dlg.Destroy()

 def list_manager(self, ev):
  dlg = dialogs.lists.listViewer(self)
  dlg.ShowModal()
  self.stream2.disconnect()
  del self.stream2
  self.get_tls()
  dlg.Destroy()

 def onInit(self, ev):
  if self.nb.GetPage(ev.GetItem()[0]).type != "search" or self.nb.GetPage(ev.GetItem()[0]).type != "favourites_timeline": self.nb.GetPage(ev.GetItem()[0]).put_items(ev.GetItem()[1])

 def preferences(self, ev=None):
  dlg = dialogs.configuration.configurationDialog(self)
  dlg.ShowModal()
  dlg.Destroy()

 def update_profile(self, ev=None):
  dialogs.update_profile.updateProfile(self).ShowModal()

 def onManual(self, ev):
  lang = localization.get("documentation")
  os.chdir("documentation/%s" % (lang,))
  webbrowser.open("manual.html")
  os.chdir("../../")

 def onChangelog(self, ev):
  lang = localization.get("documentation")
  os.chdir("documentation/%s" % (lang,))
  webbrowser.open("changes.html")
  os.chdir("../../")

 def onVisit_website(self, ev):
  webbrowser.open("http://twblue.com.mx")

 def onReportBug(self, ev):
  webbrowser.open("https://github.com/manuelcortez/TWBlue/issues")
#  issueReporterGUI.reportBug(self.db.settings["user_name"]).ShowModal()

 def onCheckForUpdates(self, ev):
  updater.update_manager.check_for_update(msg=True)

 def details(self, ev=None):
  """ This function shows details for the selected user."""
  dlg = dialogs.utils.selectUserDialog(parent=self, title=_(u"User details"))
  if dlg.ShowModal() == wx.ID_OK:
   dialogs.show_user.showUserProfile(self.twitter, dlg.cb.GetValue()).ShowModal()
   dlg.Destroy()

 def delete(self, ev=None):
  """ Deleting a tweet or direct message."""
  if self.nb.GetCurrentPage().name_buffer != "followers" and self.nb.GetCurrentPage() != "friends" and self.nb.GetCurrentPage().name_buffer != "events":
   dlg = wx.MessageDialog(self, _(u"Do you really want to delete this message? It will be eliminated from Twitter as well."), _(u"Delete"), wx.ICON_QUESTION|wx.YES_NO)
   if dlg.ShowModal() == wx.ID_YES:
    self.nb.GetCurrentPage().destroy_status(wx.EVT_MENU)
   else:
    return

 def onPageChanged(self, ev):
  """ Announces the new title for the tab."""
  if platform.system() == "Darwin":
   output.speak(self.nb.GetPageText(self.nb.GetSelection())+",", True)

 def skip_blank_pages(self, forward=True):
  if self.nb.GetCurrentPage().type == "account" or self.nb.GetCurrentPage().type == "empty" and (self.showing == False or platform.system() == "Darwin"):
   self.nb.AdvanceSelection(forward)

 def close(self, ev=None):
  if config.main["general"]["ask_at_exit"] == True:
   dlg = wx.MessageDialog(self, _(u"Do you really want to close TW Blue?"), _(u"Exit"), wx.YES_NO|wx.ICON_QUESTION)
   if dlg.ShowModal() == wx.ID_YES:
    self.exit()
   dlg.Destroy()
  else:
   output.speak(_(u"Exiting..."))
   self.exit()

 def exit(self, event=None):
  config.main.write()
  log.debug("Exiting...")
  self.sysTray.RemoveIcon()
  try:
   self.check_streams.cancel()
  except AttributeError:
   pass
  sound.player.cleaner.cancel()
  try:
   self.stream.disconnect()
   log.debug("Stream disconnected.")
  except:
   pass
  try:
   self.stream2.disconnect()
   log.debug(u"Timelines stream disconnected.")
  except:
   pass
  wx.GetApp().ExitMainLoop()

 def onFollow(self, ev=None):
  """ Opens the follow dialog."""
  dialogs.follow.follow(self.nb.GetCurrentPage(), "follow").ShowModal()

 def onUnfollow(self, ev=None):
  """ Opens the unfollow dialog."""
  dialogs.follow.follow(self.nb.GetCurrentPage(), "unfollow").ShowModal()

 def onMute(self, ev=None):
  """ Opens the unfollow dialog."""
  dialogs.follow.follow(self.nb.GetCurrentPage(), "mute").ShowModal()

 def onUnmute(self, ev=None):
  """ Opens the unfollow dialog."""
  dialogs.follow.follow(self.nb.GetCurrentPage(), "unmute").ShowModal()

 def onReport(self, ev=None):
  """ Opens the report dialog, to report as spam to the specified user."""
  dialogs.follow.follow(self.nb.GetCurrentPage(), "report").ShowModal()

 def onBlock(self, ev=None):
  """ Opens the "block" dialog, to block the user that you want."""
  dialogs.follow.follow(self.nb.GetCurrentPage(), "block").ShowModal()

 def onUnblock(self, ev=None):
  """ Opens the "block" dialog, to block the user that you want."""
  dialogs.follow.follow(self.nb.GetCurrentPage(), "unblock").ShowModal()

 def action(self, ev=None):
  dialogs.follow.follow(self.nb.GetCurrentPage()).ShowModal()

 def compose(self, ev=None):
  """ Opens the new tweet dialog."""
  self.nb.GetCurrentPage().post_status(ev)

 def reply(self, ev=None):
  """ Opens the response dialog."""
  self.nb.GetCurrentPage().onResponse(ev)

 def dm(self, ev=None):
  """ Opens the DM Dialog."""
  # The direct_messages buffer has a method to post a diret messages while the other tabs does has not it. 
  if self.nb.GetCurrentPage().name_buffer == "direct_messages":
   self.nb.GetCurrentPage().onResponse(ev)
  elif self.nb.GetCurrentPage().name_buffer == "events": return
  else:
#   dialogs.message.dm(_(u"Direct message to %s ") % (self.db.settings[self.nb.GetCurrentPage().name_buffer][self.nb.GetCurrentPage().get_selected()]["user"]["screen_name"]), "", "", self.nb.GetCurrentPage()).ShowModal()
   self.nb.GetCurrentPage().onDm(ev)

 def retweet(self, ev=None):
  if self.nb.GetCurrentPage().name_buffer != "direct_messages" and self.nb.GetCurrentPage().name_buffer != "followers" and self.nb.GetCurrentPage().name_buffer != "friends" and self.nb.GetCurrentPage().name_buffer != "events":
   self.nb.GetCurrentPage().onRetweet(ev)

 def view(self, ev=None):
  tp = self.nb.GetCurrentPage().type
  if tp == "buffer" or tp == "timeline" or tp == "favourites_timeline" or tp == "list" or tp == "search":
   try:
    id = self.db.settings[self.nb.GetCurrentPage().name_buffer][self.nb.GetCurrentPage().list.get_selected()]["id"]
    tweet = self.twitter.twitter.show_status(id=id)
    dialogs.message.viewTweet(tweet).ShowModal()
   except TwythonError as e:
    non_tweet = self.nb.GetCurrentPage().get_message(dialog=True)
    dialogs.message.viewNonTweet(non_tweet).ShowModal()
  else:
   non_tweet = self.nb.GetCurrentPage().get_message(dialog=True)
   dialogs.message.viewNonTweet(non_tweet).ShowModal()

 def fav(self, ev=None):
  if self.nb.GetCurrentPage().name_buffer != "direct_messages" and self.nb.GetCurrentPage().name_buffer != "followers" and self.nb.GetCurrentPage().name_buffer != "friends":
   try:
    self.twitter.twitter.create_favorite(id=self.db.settings[self.nb.GetCurrentPage().name_buffer][self.nb.GetCurrentPage().list.get_selected()]["id"])
    sound.player.play("favourite.ogg")
   except TwythonError as e:
    output.speak(_(u"Error while adding to favourites."), True)
    sound.player.play("error.ogg")

 def unfav(self, ev=None):
  if self.nb.GetCurrentPage().name_buffer != "direct_messages" and self.nb.GetCurrentPage().name_buffer != "followers" and self.nb.GetCurrentPage().name_buffer != "friends":
   try:
    self.twitter.twitter.destroy_favorite(id=self.db.settings[self.nb.GetCurrentPage().name_buffer][self.nb.GetCurrentPage().list.get_selected()]["id"])
   except TwythonError as e:
    output.speak(_(u"Error while removing from favourites."), True)
    sound.player.play("error.ogg")

 def open_timeline(self, ev=None):
  dlg = dialogs.utils.selectUserDialog(self, _(u"Individual timeline"))
  if dlg.ShowModal() == wx.ID_OK:
   user = twitter.utils.if_user_exists(self.twitter.twitter, dlg.cb.GetValue())
   if user == None:
    wx.MessageDialog(None, _(u"The user does not exist"), _(u"Error"), wx.ICON_ERROR).ShowModal()
    dlg.Destroy()
    return
   if user not in config.main["other_buffers"]["timelines"]:
    config.main["other_buffers"]["timelines"].append(user)
   else:
    wx.MessageDialog(None, _(u"There's currently a timeline for this user. You are not able to open another"), _(u"Existing timeline"), wx.ICON_ERROR).ShowModal()
    dlg.Destroy()
    return
   sound.player.play("create_timeline.ogg")
   st = buffers.basePanel(self.nb, self, user, self.twitter.twitter.get_user_timeline, argumento=user, sound="ready.ogg", timeline=True)
   num = st.start_streams()
   self.db.settings["buffers"].append(user)
   if num == 0:
    wx.MessageDialog(None, _(u"This user has no tweets. You can't open a timeline for this user"), _(u"Error!"), wx.ICON_ERROR).ShowModal()
    self.db.settings.pop(user)
#    self.nb.DeletePage(self.db.settings["buffers"].index(user))
    self.db.settings["buffers"].remove(user)
   else:
    self.nb.InsertSubPage(self.db.settings["buffers"].index("timelines"), st, _(u"Timeline for %s") % (user))
    st.put_items(num)
    st.sound = "tweet_timeline.ogg"
   self.stream2.disconnect()
   del self.stream2
   self.get_tls()
  dlg.Destroy()

 def favs_timeline(self, ev=None):
  dlg = dialogs.utils.selectUserDialog(self, _(u"List of favourites"))
  if dlg.ShowModal() == wx.ID_OK:
   user = twitter.utils.if_user_exists(self.twitter.twitter, dlg.cb.GetValue())
   if user == None:
    wx.MessageDialog(None, _(u"The user does not exist"), _(u"Error"), wx.ICON_ERROR).ShowModal()
    dlg.Destroy()
    return
   if user not in config.main["other_buffers"]["favourites_timelines"]:
    config.main["other_buffers"]["favourites_timelines"].append(user)
   else:
    wx.MessageDialog(None, _(u"There's already a list of favourites for this user. You can't create another."), _(u"Existing list"), wx.ICON_ERROR).ShowModal()
    dlg.Destroy()
    return
   sound.player.play("create_timeline.ogg")
   st = buffers.favsPanel(self.nb, self, user+"-favs", argumento=user, sound="favourites_timeline_updated.ogg")
   self.nb.InsertSubPage(self.db.settings["buffers"].index("favourites_timelines"), st, _(u"Favourites for %s") % (user))
   num = st.start_streams()
   self.db.settings["buffers"].append(user+"-favs")
   if num == 0:
    wx.MessageDialog(None, _(u"This user has no favourites. You can't create a list of favourites for this user."), _(u"Error!"), wx.ICON_ERROR).ShowModal()
    self.db.settings.pop(user+"-favs")
    self.nb.DeletePage(self.db.settings["buffers"].index(user+"-favs"))
    self.db.settings["buffers"].remove(user+"-favs")
   st.put_items(num)
  dlg.Destroy()

 def onAbout(self, ev=None):
  info = wx.AboutDialogInfo()
  info.SetName(application.name)
  info.SetVersion(application.version)
  info.SetDescription(application.description)
  info.SetCopyright(application.copyright)
  info.SetTranslators(application.translators)
#  info.SetLicence(application.licence)
  info.AddDeveloper(application.author)
  wx.AboutBox(info)

 def delete_buffer(self, ev=None):
  pos = self.nb.GetCurrentPage().remove_buffer()
  if pos != None:
   self.stream2.disconnect()
   del self.stream2
   self.nb.DeletePage(self.nb.GetSelection())
   sound.player.play("delete_timeline.ogg")
   self.get_tls()

 def delete_invalid_timeline(self):
  pos = self.nb.GetCurrentPage().remove_invalid_buffer()
  if pos != None:
   self.nb.DeletePage(self.nb.GetSelection())

 ### Hidden Window
 def left(self, event=None):
  num = self.nb.GetSelection()
  if num == 0:
   self.nb.ChangeSelection(self.nb.GetPageCount()-1)
  else:
   self.nb.SetSelection(num-1)
  while self.nb.GetCurrentPage().type == "account" or self.nb.GetCurrentPage().type == "empty": self.skip_blank_pages(False)
  try:
   msg = _(u"%s, %s of %s") % (self.nb.GetPageText(self.nb.GetSelection()), self.nb.GetCurrentPage().list.get_selected()+1, self.nb.GetCurrentPage().list.get_count())
  except:
   msg = _(u"%s. Empty") % (self.nb.GetPageText(self.nb.GetSelection()))
  output.speak(msg, 1)

 def right(self, event=None):
  num = self.nb.GetSelection()
  if num+1 == self.nb.GetPageCount():
   self.nb.SetSelection(0)
  else:
   self.nb.SetSelection(num+1)
  while self.nb.GetCurrentPage().type == "account" or self.nb.GetCurrentPage().type == "empty": self.skip_blank_pages(True)
  try:
   msg = _(u"%s, %s of %s") % (self.nb.GetPageText(self.nb.GetSelection()), self.nb.GetCurrentPage().list.get_selected()+1, self.nb.GetCurrentPage().list.get_count())
  except:
   msg = _(u"%s. Empty") % (self.nb.GetPageText(self.nb.GetSelection()))
  output.speak(msg, 1)

 def show_hide(self, ev=None):
#  if platform.system() == "Linux" or platform.system() == "Darwin": return
  keymap = {}
  for i in config.main["keymap"]:
   if hasattr(self, i):
    keymap[config.main["keymap"][i]] = getattr(self, i)
  if self.showing == True:
   self.keyboard_handler = WXKeyboardHandler(self)
   self.keyboard_handler.register_keys(keymap)
   self.Hide()
   self.showing = False
  else:
   self.keyboard_handler.unregister_keys(keymap)
   del self.keyboard_handler
   self.Show()
   self.showing = True

 def toggle_global_mute(self, event=None):
  if config.main["sound"]["global_mute"] == False:
   config.main["sound"]["global_mute"] = True
   output.speak(_(u"Global mute on"))
  elif config.main["sound"]["global_mute"] == True:
   config.main["sound"]["global_mute"] = False
   output.speak(_(u"Global mute off"))

 def toggle_mute(self, event=None):
  buffer = self.nb.GetCurrentPage().name_buffer
  if buffer not in config.main["other_buffers"]["muted_buffers"]:
   config.main["other_buffers"]["muted_buffers"].append(buffer)
   output.speak(_(u"Buffer mute on"))
  elif buffer in config.main["other_buffers"]["muted_buffers"]:
   config.main["other_buffers"]["muted_buffers"].remove(buffer)
   output.speak(_(u"Buffer mute off"))

 def toggle_autoread(self, event=None):
  buffer = self.nb.GetCurrentPage().name_buffer
  if buffer not in config.main["other_buffers"]["autoread_buffers"]:
   config.main["other_buffers"]["autoread_buffers"].append(buffer)
   output.speak(_(u"The auto-reading of new tweets is enabled for this buffer"))
  elif buffer in config.main["other_buffers"]["autoread_buffers"]:
   config.main["other_buffers"]["autoread_buffers"].remove(buffer)
   output.speak(_(u"The auto-reading of new tweets is disabled for this buffer"))

 def repeat_item(self):
  output.speak(self.nb.GetCurrentPage().get_message(), 1)

 def copy_to_clipboard(self, event=None):
  output.Copy(self.nb.GetCurrentPage().get_message())
  output.speak(_(u"Copied"))

 def clear_list(self, event=None):
  self.nb.GetCurrentPage().interact("clear_list")

 def conversation_up(self, evt=None):
  if config.main["general"]["reverse_timelines"] == True and evt == None:
   self.conversation_down("down")
   return
  id = self.db.settings[self.nb.GetCurrentPage().name_buffer][self.nb.GetCurrentPage().list.get_selected()]["in_reply_to_status_id_str"]
  pos = twitter.utils.find_previous_reply(id, self.db.settings["home_timeline"])
  if pos != None:
   self.nb.ChangeSelection(1)
   self.nb.GetCurrentPage().list.select_item(pos)
   msg = _(u"%s") % (self.nb.GetCurrentPage().get_message())
   output.speak(msg)

 def conversation_down(self, evt=None):
  if config.main["general"]["reverse_timelines"] == True and evt == None:
   self.conversation_up("up")
   return
  id = self.db.settings[self.nb.GetCurrentPage().name_buffer][self.nb.GetCurrentPage().list.get_selected()]["id_str"]
#  pos = twitter.utils.find_next_reply(id, self.db.settings["home_timeline"])
  pos = twitter.utils.find_next_reply(id, self.db.settings["home_timeline"])
  if pos != None:
   self.nb.ChangeSelection(1)
   self.nb.GetCurrentPage().list.select_item(pos)
   msg = _(u"%s") % (self.nb.GetCurrentPage().get_message())
   output.speak(msg)

 def go_home(self):
  self.nb.GetCurrentPage().list.select_item(0)
  try:
   output.speak(self.nb.GetCurrentPage().get_message(), 1)
  except:
   pass

 def go_end(self):
  self.nb.GetCurrentPage().list.select_item(self.nb.GetCurrentPage().list.get_count()-1)
  try:
   output.speak(self.nb.GetCurrentPage().get_message(), 1)
  except:
   pass

 def go_page_up(self):
  if self.nb.GetCurrentPage().list.get_selected <= 20:
   index = 0
  else:
   index = self.nb.GetCurrentPage().list.get_selected() - 20
  self.nb.GetCurrentPage().list.select_item(index)
  try:
   output.speak(self.nb.GetCurrentPage().get_message(), 1)
  except:
   pass

 def go_page_down(self):
  if self.nb.GetCurrentPage().list.get_selected() >= self.nb.GetCurrentPage().list.get_count() - 20:
   index = self.nb.GetCurrentPage().list.get_count()-1
  else:
   index = self.nb.GetCurrentPage().list.get_selected() + 20
  self.nb.GetCurrentPage().list.select_item(index)
  try:
   output.speak(self.nb.GetCurrentPage().get_message(), 1)
  except:
   pass

 def volume_up(self):
  self.nb.GetCurrentPage().interact("volume_up")

 def volume_down(self):
  self.nb.GetCurrentPage().interact("volume_down")

 def url(self):
  self.nb.GetCurrentPage().interact("url")

 def audio(self):
  self.nb.GetCurrentPage().interact("audio")

 def up(self, event=None):
  pos = self.nb.GetCurrentPage().list.get_selected()
  index = self.nb.GetCurrentPage().list.get_selected()-1
  try:
   self.nb.GetCurrentPage().list.select_item(index)
  except:
   pass
  if pos == self.nb.GetCurrentPage().list.get_selected():
   sound.player.play("limit.ogg", False)
  try:
   output.speak(self.nb.GetCurrentPage().get_message(), 1)
  except:
   pass

 def down(self, event=None):
  index = self.nb.GetCurrentPage().list.get_selected()+1
  pos = self.nb.GetCurrentPage().list.get_selected()
  try:
   self.nb.GetCurrentPage().list.select_item(index)
  except:
   pass
  if pos == self.nb.GetCurrentPage().list.get_selected():
   sound.player.play("limit.ogg", False)
  try:
   output.speak(self.nb.GetCurrentPage().get_message(), 1)
  except:
   pass

 def get_more_items(self, event=None):
  self.nb.GetCurrentPage().get_more_items()

 def search_buffer(self, buffer_type=None, name_buffer=None):
  page = None
  for i in range(0, self.nb.GetPageCount()):
   page = self.nb.GetPage(i)
   if page.type != buffer_type:
    continue
   if page.name_buffer == name_buffer:
    return page
  return page

 def switch_account(self, ev):
  switchModule.switcher(self)

 def reverse_geocode(self, event=None):
  try:
   if self.db.settings[self.nb.GetCurrentPage().name_buffer][self.nb.GetCurrentPage().list.get_selected()]["coordinates"] != None:
    x = self.db.settings[self.nb.GetCurrentPage().name_buffer][self.nb.GetCurrentPage().list.get_selected()]["coordinates"]["coordinates"][0]
    y = self.db.settings[self.nb.GetCurrentPage().name_buffer][self.nb.GetCurrentPage().list.get_selected()]["coordinates"]["coordinates"][1]
    address = geocoder.reverse_geocode(y, x)
    if event == None: output.speak(address[0].__str__().decode("utf-8"))
    else: wx.MessageDialog(self, address[0].__str__().decode("utf-8"), _(u"Address"), wx.OK).ShowModal()
   else:
    output.speak(_(u"There are no coordinates in this tweet"))
  except GeocoderError:
   output.speak(_(u"There are no results for the coordinates in this tweet"))
  except ValueError:
   output.speak(_(u"Error decoding coordinates. Try again later."))
  except KeyError:
   pass

 def view_reverse_geocode(self, event=None):
  try:
   if self.db.settings[self.nb.GetCurrentPage().name_buffer][self.nb.GetCurrentPage().list.get_selected()]["coordinates"] != None:
    x = self.db.settings[self.nb.GetCurrentPage().name_buffer][self.nb.GetCurrentPage().list.get_selected()]["coordinates"]["coordinates"][0]
    y = self.db.settings[self.nb.GetCurrentPage().name_buffer][self.nb.GetCurrentPage().list.get_selected()]["coordinates"]["coordinates"][1]
    address = geocoder.reverse_geocode(y, x)
    dialogs.message.viewNonTweet(address[0].__str__().decode("utf-8")).ShowModal()
   else:
    output.speak(_(u"There are no coordinates in this tweet"))
  except GeocoderError:
   output.speak(_(u"There are no results for the coordinates in this tweet"))
  except ValueError:
   output.speak(_(u"Error decoding coordinates. Try again later."))
  except KeyError:
   pass

### Close App
 def Destroy(self):
  self.sysTray.Destroy()
  super(mainFrame, self).Destroy()
