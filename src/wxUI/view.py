# -*- coding: utf-8 -*-
import wx

class mainFrame(wx.Frame):
 """ Main class of the Frame. This is the Main Window."""

 ### MENU
 def makeMenus(self):
  """ Creates, bind and returns the menu bar for the application. Also in this function, the accel table is created."""
  menuBar = wx.MenuBar()

  # Application menu
  app = wx.Menu()
  updateProfile = app.Append(wx.NewId(), _(u"&Update profile"))
#  self.Bind(wx.EVT_MENU, self.controller.update_profile, updateProfile)
  show_hide = app.Append(wx.NewId(), _(u"&Hide window"))
#  self.Bind(wx.EVT_MENU, self.controller.show_hide, show_hide)
  search = app.Append(wx.NewId(), _(u"&Search"))
  self.Bind(wx.EVT_MENU, self.controller.search, search)
  lists = app.Append(wx.NewId(), _(u"&Lists manager"))
#  self.view.Bind(wx.EVT_MENU, self.list_manager, lists)
  sounds_tutorial = app.Append(wx.NewId(), _(u"Sounds &tutorial"))
#  self.view.Bind(wx.EVT_MENU, self.learn_sounds, sounds_tutorial)
  keystroke_editor = app.Append(wx.NewId(), _(u"&Edit keystrokes"))
  self.Bind(wx.EVT_MENU, self.controller.edit_keystrokes, keystroke_editor)
  prefs = app.Append(wx.ID_PREFERENCES, _(u"&Preferences"))
#  self.view.Bind(wx.EVT_MENU, self.preferences, prefs)
  close = app.Append(wx.ID_EXIT, _(u"E&xit"))
#  self.view.Bind(wx.EVT_MENU, self.close, close)

  # Tweet menu
  tweet = wx.Menu()
  compose = tweet.Append(wx.NewId(), _(u"&Tweet"))
  self.Bind(wx.EVT_MENU, self.controller.post_tweet, compose)
  response = tweet.Append(wx.NewId(), _(u"Re&ply"))
#  self.view.Bind(wx.EVT_MENU, self.reply, response)
  retweet = tweet.Append(wx.NewId(), _(u"&Retweet"))
#  self.view.Bind(wx.EVT_MENU, self.retweet, retweet)
  fav = tweet.Append(wx.NewId(), _(u"Add to &favourites"))
#  self.view.Bind(wx.EVT_MENU, self.fav, fav)
  unfav = tweet.Append(wx.NewId(), _(u"Remove from favo&urites"))
#  self.view.Bind(wx.EVT_MENU, self.unfav, unfav)
  view = tweet.Append(wx.NewId(), _(u"&Show tweet"))
#  self.view.Bind(wx.EVT_MENU, self.view, view)
  delete = tweet.Append(wx.NewId(), _(u"&Delete"))
#  self.view.Bind(wx.EVT_MENU, self.delete, delete)

  # User menu
  user = wx.Menu()
  follow = user.Append(wx.NewId(), _(u"&Follow"))
#  self.view.Bind(wx.EVT_MENU, self.onFollow, follow)
  unfollow = user.Append(wx.NewId(), _(u"&Unfollow"))
#  self.view.Bind(wx.EVT_MENU, self.onUnfollow, unfollow)
  mute = user.Append(wx.NewId(), _(u"&Mute"))
#  self.view.Bind(wx.EVT_MENU, self.onMute, mute)
  unmute = user.Append(wx.NewId(), _(u"U&nmute"))
#  self.view.Bind(wx.EVT_MENU, self.onUnmute, unmute)
  report = user.Append(wx.NewId(), _(u"&Report as spam"))
#  self.view.Bind(wx.EVT_MENU, self.onReport, report)
  block = user.Append(wx.NewId(), _(u"&Block"))
#  self.view.Bind(wx.EVT_MENU, self.onBlock, block)
  unblock = user.Append(wx.NewId(), _(u"Unb&lock"))
#  self.view.Bind(wx.EVT_MENU, self.onUnblock, unblock)
  dm = user.Append(wx.NewId(), _(u"Direct me&ssage"))
#  self.view.Bind(wx.EVT_MENU, self.dm, dm)
  addToList = user.Append(wx.NewId(), _(u"&Add to list"))
#  self.view.Bind(wx.EVT_MENU, self.add_to_list, addToList)
  removeFromList = user.Append(wx.NewId(), _(u"R&emove from list"))
#  self.view.Bind(wx.EVT_MENU, self.remove_from_list, removeFromList)
  viewLists = user.Append(wx.NewId(), _(u"&View lists"))
#  self.view.Bind(wx.EVT_MENU, self.view_user_lists, viewLists)
  details = user.Append(wx.NewId(), _(u"Show user &profile"))
#  self.view.Bind(wx.EVT_MENU, self.details, details)
  timeline = user.Append(wx.NewId(), _(u"&Timeline"))
#  self.view.Bind(wx.EVT_MENU, self.open_timeline, timeline)
  favs = user.Append(wx.NewId(), _(u"V&iew favourites"))
#  self.view.Bind(wx.EVT_MENU, self.favs_timeline, favs)

  # buffer menu
  buffer = wx.Menu()
  mute = buffer.Append(wx.NewId(), _(u"&Mute"))
#  self.view.Bind(wx.EVT_MENU, self.toggle_mute, mute)
  autoread = buffer.Append(wx.NewId(), _(u"&Autoread tweets for this buffer"))
#  self.view.Bind(wx.EVT_MENU, self.toggle_autoread, autoread)
  clear = buffer.Append(wx.NewId(), _(u"&Clear buffer"))
#  self.view.Bind(wx.EVT_MENU, self.clear_list, clear)
  deleteTl = buffer.Append(wx.NewId(), _(u"&Remove buffer"))
#  self.view.Bind(wx.EVT_MENU, self.delete_buffer, deleteTl)

 # Help Menu
  help = wx.Menu()
  doc = help.Append(-1, _(u"&Documentation"))
#  self.view.Bind(wx.EVT_MENU, self.onManual, doc)
  changelog = help.Append(wx.NewId(), _(u"&What's new in this version?"))
#  self.view.Bind(wx.EVT_MENU, self.onChangelog, changelog)
  check_for_updates = help.Append(wx.NewId(), _(u"&Check for updates"))
#  self.view.Bind(wx.EVT_MENU, self.onCheckForUpdates, check_for_updates)
  reportError = help.Append(wx.NewId(), _(u"&Report an error"))
#  self.view.Bind(wx.EVT_MENU, self.onReportBug, reportError)
  visit_website = help.Append(-1, _(u"TW Blue &website"))
#  self.view.Bind(wx.EVT_MENU, self.onVisit_website, visit_website)
  about = help.Append(-1, _(u"About &TW Blue"))
#  self.view.Bind(wx.EVT_MENU, self.onAbout, about)

  # Add all to the menu Bar
  menuBar.Append(app, _(u"&Application"))
  menuBar.Append(tweet, _(u"&Tweet"))
  menuBar.Append(user, _(u"&User"))
  menuBar.Append(buffer, _(u"&Buffer"))
  menuBar.Append(help, _(u"&Help"))

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
  ])

  self.SetAcceleratorTable(self.accel_tbl)
  return menuBar

 ### MAIN
 def __init__(self, controller):
  """ Main function of this class."""
  super(mainFrame, self).__init__(None, -1, "TW Blue", size=(1600, 1600))
  self.controller = controller
  self.panel = wx.Panel(self)
  self.sizer = wx.BoxSizer(wx.VERTICAL)
  self.SetTitle("TW Blue")
  self.SetMenuBar(self.makeMenus())
  self.nb = wx.Treebook(self.panel, wx.NewId())
  self.buffers = {}
  self.SetMenuBar(self.makeMenus())

 def add_buffer(self, buffer, name):
  self.nb.AddPage(buffer, name)
  self.buffers[name] = buffer.GetId()

 def insert_buffer(self, buffer, name, pos):
  self.nb.InsertSubPage(pos, buffer, name)
  self.buffers[name] = buffer.GetId()
  
 def prepare(self):
  self.sizer.Add(self.nb, 0, wx.ALL, 5)
  self.panel.SetSizer(self.sizer)
  self.SetClientSize(self.sizer.CalcMin())

 def search(self, name_, account):
  for i in range(0, self.nb.GetPageCount()):
   if self.nb.GetPage(i).name == name_ and self.nb.GetPage(i).account == account: return i

 def get_current_buffer(self):
  return self.nb.GetCurrentPage()

 def get_buffer(self, pos):
  return self.GetPage(pos)

 def get_buffer_by_id(self, id):
  return self.nb.FindWindowById(id)

 def show(self):
  self.Show()