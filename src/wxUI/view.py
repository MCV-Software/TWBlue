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
  self.updateProfile = app.Append(wx.NewId(), _(u"&Update profile"))
  self.show_hide = app.Append(wx.NewId(), _(u"&Hide window"))
  self.menuitem_search = app.Append(wx.NewId(), _(u"&Search"))
  self.lists = app.Append(wx.NewId(), _(u"&Lists manager"))
  self.sounds_tutorial = app.Append(wx.NewId(), _(u"Sounds &tutorial"))
  self.keystroke_editor = app.Append(wx.NewId(), _(u"&Edit keystrokes"))
  self.account_settings = app.Append(wx.NewId(), _(u"Account se&ttings"))
  self.prefs = app.Append(wx.ID_PREFERENCES, _(u"&Global settings"))
  self.close = app.Append(wx.ID_EXIT, _(u"E&xit"))

  # Tweet menu
  tweet = wx.Menu()
  self.compose = tweet.Append(wx.NewId(), _(u"&Tweet"))
  self.reply = tweet.Append(wx.NewId(), _(u"Re&ply"))
  self.retweet = tweet.Append(wx.NewId(), _(u"&Retweet"))
  self.fav = tweet.Append(wx.NewId(), _(u"Add to &favourites"))
  self.unfav = tweet.Append(wx.NewId(), _(u"Remove from favo&urites"))
  self.view = tweet.Append(wx.NewId(), _(u"&Show tweet"))
  self.delete = tweet.Append(wx.NewId(), _(u"&Delete"))

  # User menu
  user = wx.Menu()
  self.follow = user.Append(wx.NewId(), _(u"&Follow"))
  self.unfollow = user.Append(wx.NewId(), _(u"&Unfollow"))
  self.mute = user.Append(wx.NewId(), _(u"&Mute"))
  self.unmute = user.Append(wx.NewId(), _(u"U&nmute"))
  self.report = user.Append(wx.NewId(), _(u"&Report as spam"))
  self.block = user.Append(wx.NewId(), _(u"&Block"))
  self.unblock = user.Append(wx.NewId(), _(u"Unb&lock"))
  self.dm = user.Append(wx.NewId(), _(u"Direct me&ssage"))
  self.addToList = user.Append(wx.NewId(), _(u"&Add to list"))
  self.removeFromList = user.Append(wx.NewId(), _(u"R&emove from list"))
  self.viewLists = user.Append(wx.NewId(), _(u"&View lists"))
  self.details = user.Append(wx.NewId(), _(u"Show user &profile"))
  self.timeline = user.Append(wx.NewId(), _(u"&Timeline"))
  self.favs = user.Append(wx.NewId(), _(u"V&iew favourites"))

  # buffer menu
  buffer = wx.Menu()
  self.mute = buffer.Append(wx.NewId(), _(u"&Mute"))
  self.autoread = buffer.Append(wx.NewId(), _(u"&Autoread tweets for this buffer"))
  self.clear = buffer.Append(wx.NewId(), _(u"&Clear buffer"))
  self.deleteTl = buffer.Append(wx.NewId(), _(u"&Remove buffer"))

 # Help Menu
  help = wx.Menu()
  self.doc = help.Append(-1, _(u"&Documentation"))
  self.changelog = help.Append(wx.NewId(), _(u"&What's new in this version?"))
  self.check_for_updates = help.Append(wx.NewId(), _(u"&Check for updates"))
  self.reportError = help.Append(wx.NewId(), _(u"&Report an error"))
  self.visit_website = help.Append(-1, _(u"TW Blue &website"))
  self.about = help.Append(-1, _(u"About &TW Blue"))

  # Add all to the menu Bar
  menuBar.Append(app, _(u"&Application"))
  menuBar.Append(tweet, _(u"&Tweet"))
  menuBar.Append(user, _(u"&User"))
  menuBar.Append(buffer, _(u"&Buffer"))
  menuBar.Append(help, _(u"&Help"))

  self.accel_tbl = wx.AcceleratorTable([
(wx.ACCEL_CTRL, ord('N'), self.compose.GetId()),
(wx.ACCEL_CTRL, ord('R'), self.reply.GetId()),
(wx.ACCEL_CTRL|wx.ACCEL_SHIFT, ord('R'), self.retweet.GetId()),
(wx.ACCEL_CTRL, ord('F'), self.fav.GetId()),
(wx.ACCEL_CTRL|wx.ACCEL_SHIFT, ord('F'), self.unfav.GetId()),
(wx.ACCEL_CTRL|wx.ACCEL_SHIFT, ord('V'), self.view.GetId()),
(wx.ACCEL_CTRL, ord('D'), self.dm.GetId()),

(wx.ACCEL_CTRL, ord('Q'), self.close.GetId()),
(wx.ACCEL_CTRL, ord('S'), self.follow.GetId()),
(wx.ACCEL_CTRL|wx.ACCEL_SHIFT, ord('S'), self.unfollow.GetId()),
(wx.ACCEL_CTRL, ord('K'), self.block.GetId()),
(wx.ACCEL_CTRL|wx.ACCEL_SHIFT, ord('K'), self.report.GetId()),
(wx.ACCEL_CTRL, ord('I'), self.timeline.GetId()),
(wx.ACCEL_CTRL|wx.ACCEL_SHIFT, ord('I'), self.deleteTl.GetId()),
(wx.ACCEL_CTRL, ord('M'), self.show_hide.GetId()),
(wx.ACCEL_CTRL, ord('P'), self.updateProfile.GetId()),
  ])

  self.SetAcceleratorTable(self.accel_tbl)
  return menuBar

 ### MAIN
 def __init__(self):
  """ Main function of this class."""
  super(mainFrame, self).__init__(None, -1, "TW Blue", size=(1600, 1600))
  self.panel = wx.Panel(self)
  self.sizer = wx.BoxSizer(wx.VERTICAL)
  self.SetTitle("TW Blue")
  self.SetMenuBar(self.makeMenus())
  self.nb = wx.Treebook(self.panel, wx.NewId())
  self.buffers = {}

 def get_buffer_count(self):
  return self.nb.GetPageCount()

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

 def get_current_buffer_pos(self):
  return self.nb.GetSelection()

 def get_buffer(self, pos):
  return self.GetPage(pos)

 def change_buffer(self, position):
  self.nb.ChangeSelection(position)

 def get_buffer_text(self):
  return self.nb.GetPageText(self.nb.GetSelection())

 def get_buffer_by_id(self, id):
  return self.nb.FindWindowById(id)
 def advance_selection(self, forward):
  self.nb.AdvanceSelection(forward)

 def show(self):
  self.Show()

