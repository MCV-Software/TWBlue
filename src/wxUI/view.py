# -*- coding: utf-8 -*-
import wx
import wx.adv
import application

class mainFrame(wx.Frame):
 """ Main class of the Frame. This is the Main Window."""

 ### MENU
 def makeMenus(self):
  """ Creates, bind and returns the menu bar for the application. Also in this function, the accel table is created."""
  menuBar = wx.MenuBar()

  # Application menu
  app = wx.Menu()
  self.manage_accounts = app.Append(wx.ID_ANY, _(u"&Manage accounts"))
  self.updateProfile = app.Append(wx.ID_ANY, _(u"&Update profile"))
  self.show_hide = app.Append(wx.ID_ANY, _(u"&Hide window"))
  self.menuitem_search = app.Append(wx.ID_ANY, _(u"&Search"))
  self.lists = app.Append(wx.ID_ANY, _(u"&Lists manager"))
  self.keystroke_editor = app.Append(wx.ID_ANY, _(u"&Edit keystrokes"))
  self.account_settings = app.Append(wx.ID_ANY, _(u"Account se&ttings"))
  self.prefs = app.Append(wx.ID_PREFERENCES, _(u"&Global settings"))
  self.close = app.Append(wx.ID_EXIT, _(u"E&xit"))

  # Tweet menu
  tweet = wx.Menu()
  self.compose = tweet.Append(wx.ID_ANY, _(u"&Tweet"))
  self.reply = tweet.Append(wx.ID_ANY, _(u"Re&ply"))
  self.retweet = tweet.Append(wx.ID_ANY, _(u"&Retweet"))
  self.fav = tweet.Append(wx.ID_ANY, _(u"&Like"))
  self.unfav = tweet.Append(wx.ID_ANY, _(u"&Unlike"))
  self.view = tweet.Append(wx.ID_ANY, _(u"&Show tweet"))
  self.view_coordinates = tweet.Append(wx.ID_ANY, _(u"View &address"))
  self.view_conversation = tweet.Append(wx.ID_ANY, _(u"View conversa&tion"))
  self.ocr = tweet.Append(wx.ID_ANY, _(u"Read text in picture"))
  self.delete = tweet.Append(wx.ID_ANY, _(u"&Delete"))

  # User menu
  user = wx.Menu()
  self.follow = user.Append(wx.ID_ANY, _(u"&Actions..."))
  self.timeline = user.Append(wx.ID_ANY, _(u"&View timeline..."))
  self.dm = user.Append(wx.ID_ANY, _(u"Direct me&ssage"))
  self.addToList = user.Append(wx.ID_ANY, _(u"&Add to list"))
  self.removeFromList = user.Append(wx.ID_ANY, _(u"R&emove from list"))
  self.viewLists = user.Append(wx.ID_ANY, _(u"&View lists"))
  self.details = user.Append(wx.ID_ANY, _(u"Show user &profile"))
  self.favs = user.Append(wx.ID_ANY, _(u"V&iew likes"))

  # buffer menu
  buffer = wx.Menu()
  self.update_buffer = buffer.Append(wx.ID_ANY, _(u"&Update buffer"))
  self.trends = buffer.Append(wx.ID_ANY, _(u"New &trending topics buffer..."))
  self.filter = buffer.Append(wx.ID_ANY, _(u"Create a &filter"))
  self.manage_filters = buffer.Append(wx.ID_ANY, _(u"&Manage filters"))
  self.find = buffer.Append(wx.ID_ANY, _(u"Find a string in the currently focused buffer..."))
  self.load_previous_items = buffer.Append(wx.ID_ANY, _(u"&Load previous items"))
  buffer.AppendSeparator()
  self.mute_buffer = buffer.AppendCheckItem(wx.ID_ANY, _(u"&Mute"))
  self.autoread = buffer.AppendCheckItem(wx.ID_ANY, _(u"&Autoread"))
  self.clear = buffer.Append(wx.ID_ANY, _(u"&Clear buffer"))
  self.deleteTl = buffer.Append(wx.ID_ANY, _(u"&Destroy"))

  # audio menu
  audio = wx.Menu()
  self.seekLeft = audio.Append(wx.ID_ANY, _(u"&Seek back 5 seconds"))
  self.seekRight = audio.Append(wx.ID_ANY, _(u"&Seek forward 5 seconds"))

 # Help Menu
  help = wx.Menu()
  self.doc = help.Append(-1, _(u"&Documentation"))
  self.sounds_tutorial = help.Append(wx.ID_ANY, _(u"Sounds &tutorial"))
  self.changelog = help.Append(wx.ID_ANY, _(u"&What's new in this version?"))
  self.check_for_updates = help.Append(wx.ID_ANY, _(u"&Check for updates"))
  self.reportError = help.Append(wx.ID_ANY, _(u"&Report an error"))
  self.visit_website = help.Append(-1, _(u"{0}'s &website").format(application.name,))
  self.get_soundpacks = help.Append(-1, _(u"Get soundpacks for TWBlue"))
  self.about = help.Append(-1, _(u"About &{0}").format(application.name,))

  # Add all to the menu Bar
  menuBar.Append(app, _(u"&Application"))
  menuBar.Append(tweet, _(u"&Tweet"))
  menuBar.Append(user, _(u"&User"))
  menuBar.Append(buffer, _(u"&Buffer"))
  menuBar.Append(audio, _(u"&Audio"))
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
(wx.ACCEL_CTRL, ord('I'), self.timeline.GetId()),
(wx.ACCEL_CTRL|wx.ACCEL_SHIFT, ord('I'), self.deleteTl.GetId()),
(wx.ACCEL_CTRL, ord('M'), self.show_hide.GetId()),
(wx.ACCEL_CTRL, wx.WXK_LEFT, self.seekLeft.GetId()),
(wx.ACCEL_CTRL, ord('P'), self.updateProfile.GetId()),
(wx.ACCEL_CTRL, wx.WXK_RIGHT, self.seekRight.GetId()),
(wx.ACCEL_CTRL, ord(' '), self.seekLeft.GetId()),
  ])

  self.SetAcceleratorTable(self.accel_tbl)
  return menuBar

 ### MAIN
 def __init__(self):
  """ Main function of this class."""
  super(mainFrame, self).__init__(None, -1, application.name, size=(1600, 1600))
  self.panel = wx.Panel(self)
  self.sizer = wx.BoxSizer(wx.VERTICAL)
  self.SetTitle(application.name)
  self.SetMenuBar(self.makeMenus())
  self.nb = wx.Treebook(self.panel, wx.ID_ANY)
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
#  self.Maximize()
  self.sizer.Layout()
  self.SetClientSize(self.sizer.CalcMin())
#  print self.GetSize()

 def get_buffers(self):
  return [self.nb.GetPage(i) for i in range(0, self.nb.GetPageCount())]

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

 def show_address(self, address):
  wx.MessageDialog(self, address, _(u"Address"), wx.OK).ShowModal()

 def delete_buffer(self, pos):
  self.nb.DeletePage(pos)

 def about_dialog(self):
  info = wx.adv.AboutDialogInfo()
  info.SetName(application.name)
  info.SetVersion(application.version)
  info.SetDescription(application.description)
  info.SetCopyright(application.copyright)
  info.SetTranslators(application.translators)
#  info.SetLicence(application.licence)
  for i in application.authors:
   info.AddDeveloper(i)
  wx.adv.AboutBox(info)

 def set_focus(self):
  self.SetFocus()

 def check_menuitem(self, menuitem, check=True):
  if hasattr(self, menuitem):
   getattr(self, menuitem).Check(check)

 def set_page_title(self, page, title):
  return self.nb.SetPageText(page, title)

 def get_page_title(self, page):
  return self.nb.GetPageText(page)

def no_update_available():
 wx.MessageDialog(None, _(u"Your {0} version is up to date").format(application.name,), _(u"Update"), style=wx.OK).ShowModal()
