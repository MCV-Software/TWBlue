# -*- coding: utf-8 -*-
import application
import widgetUtils
from gi.repository import Gtk, Gdk

class mainFrame(Gtk.Window):
 """ Main class of the Frame. This is the Main Window."""

 def append_to_menu(self, menu, *elements):
  for i in elements:
   menu.append(i)

 ### MENU
 def makeMenus(self):
  """ Creates, bind and returns the menu bar for the application. Also in this function, the accel table is created."""
  menuBar = Gtk.MenuBar()

  # Application menu
  app = Gtk.Menu()

  self.manage_accounts = Gtk.MenuItem(label=_(u"Manage accounts"))
  self.updateProfile = Gtk.MenuItem(label="Update profile")
  self.updateProfile.add_accelerator("activate", self.accel_group, ord("U"), Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
  # As in Gtk is not possible to bind keyboard  shorcuts to the system, we don't have support for an invisible interface.
  self.show_hide = None
  self.menuitem_search = Gtk.MenuItem(label="Search")
  self.trends = Gtk.MenuItem(label="View trending topics")
  self.trends.add_accelerator("activate", self.accel_group, ord("T"), Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
  self.lists = Gtk.MenuItem(label="Lists manager")
  self.keystrokes_editor = None
  self.account_settings = Gtk.MenuItem(label="Account settings")
  self.prefs = Gtk.MenuItem(label="Global settings")
  self.close = Gtk.MenuItem(label="Close")
  self.close.add_accelerator("activate", self.accel_group, ord("Q"), Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
  self.append_to_menu(app, self.manage_accounts, self.updateProfile, self.menuitem_search, self.trends, self.lists, self.account_settings, self.prefs, self.close)

  app_menu = Gtk.MenuItem(label="Application")
  app_menu.add_accelerator("activate", self.accel_group, ord("a"), Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
  app_menu.set_submenu(app)
  menuBar.append(app_menu)

  # Tweet menu
  tweet = Gtk.Menu()
  self.compose = Gtk.MenuItem(label="Tweet")
  self.compose.add_accelerator("activate", self.accel_group, ord("N"), Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
  self.reply = Gtk.MenuItem(label="Reply")
  self.reply.add_accelerator("activate", self.accel_group, ord("R"), Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
  self.retweet = Gtk.MenuItem(label="Retweet")
  self.retweet.add_accelerator("activate", self.accel_group, ord("T"), Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
  self.fav = Gtk.MenuItem(label="Add to favourites")
  self.fav.add_accelerator("activate", self.accel_group, ord("F"), Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
  self.unfav = Gtk.MenuItem(label="Remove from favourites")
  self.view = Gtk.MenuItem(label="Show tweet")
  self.view_coordinates = Gtk.MenuItem(label="View address")
  self.view_conversation = Gtk.MenuItem(label="View conversation")
  self.delete = Gtk.MenuItem(label="Delete")
  self.append_to_menu(tweet, self.compose, self.reply, self.retweet, self.fav, self.unfav, self.view, self.view_coordinates, self.view_conversation, self.delete)
  tweet_menu = Gtk.MenuItem(label="Tweet")
  tweet_menu.set_submenu(tweet)
  menuBar.append(tweet_menu)

  # User menu
  user = Gtk.Menu()
  self.follow = Gtk.MenuItem(label="Follow")
  self.unfollow = Gtk.MenuItem(label="Unfollow")
  self.mute = Gtk.MenuItem(label="Mute")
  self.unmute = Gtk.MenuItem(label="Unmute")
  self.report = Gtk.MenuItem(label="Report as spam")
  self.block = Gtk.MenuItem(label="Block")
  self.unblock = Gtk.MenuItem(label="Unblock")
  self.dm = Gtk.MenuItem(label="Direct message")
  self.addToList = Gtk.MenuItem(label="Add to list")
  self.removeFromList = Gtk.MenuItem(label="Remove from list")
  self.viewLists = Gtk.MenuItem(label="View lists")
  self.details = Gtk.MenuItem(label="Show user profile")
  self.favs = Gtk.MenuItem(label="View favourites")
  self.append_to_menu(user, self.follow, self.unfollow, self.mute, self.unmute, self.report, self.block, self.unblock, self.dm, self.addToList, self.removeFromList, self.viewLists, self.details, self.favs)
  user_menu = Gtk.MenuItem(label="User")
  user_menu.set_submenu(user)
  menuBar.append(user_menu)

  # buffer menu
  buffer = Gtk.Menu()
  self.timeline = Gtk.MenuItem(label="New buffer...")
  self.load_previous_items = Gtk.MenuItem(label="Load previous items")
  self.mute_buffer = Gtk.MenuItem(label="Mute")
  self.autoread = Gtk.MenuItem(label="Autoread")
  self.clear = Gtk.MenuItem(label="Clear buffer")
  self.deleteTl = Gtk.MenuItem(label="Destroy")
  self.append_to_menu(buffer, self.timeline, self.load_previous_items, self.mute_buffer, self.autoread, self.clear, self.deleteTl)
  buffer_menu = Gtk.MenuItem(label="Buffer")
  buffer_menu.set_submenu(buffer)
  menuBar.append(buffer_menu)

 # Help Menu
  help = Gtk.Menu()
  self.doc = Gtk.MenuItem(label="Documentation")
  self.sounds_tutorial = Gtk.MenuItem(label="Sounds tutorial")
  self.changelog = Gtk.MenuItem(label="What's new in this version?")
  self.check_for_updates = Gtk.MenuItem(label="Check for updates")
  self.reportError = Gtk.MenuItem(label="Report an error")
  self.visit_website = Gtk.MenuItem(label=application.name+"'s website")
  self.about = Gtk.MenuItem(label="ABout "+application.name)
  self.append_to_menu(help, self.doc, self.sounds_tutorial, self.changelog, self.check_for_updates, self.reportError, self.visit_website, self.about)
  help_menu = Gtk.MenuItem(label="Help")
  help_menu.set_submenu(help)
  menuBar.append(help_menu)
  self.box.pack_start(menuBar, False, False, 0)

 ### MAIN
 def __init__(self):
  """ Main function of this class."""
  super(mainFrame, self).__init__(title=application.name)
  self.accel_group = Gtk.AccelGroup()
  self.add_accel_group(self.accel_group)
  self.box =  Gtk.VBox()
  self.makeMenus()
  self.nb = widgetUtils.notebook()
  self.w = None
  self.notebookBox = Gtk.Box(spacing=5)
  self.notebookBox.add(self.nb.view)
  self.box.add(self.notebookBox)
  self.add(self.box)
  select = self.nb.view.get_selection()
  select.connect("changed", self.load)

 def show(self):
  self.show_all()

 def get_buffer_count(self):
  return self.nb.get_count()

 def add_buffer(self, buffer, name):
  buff = widgetUtils.buffer(buffer)
  buff.name = name
  self.nb.store.append(None, (buff,))

 def insert_buffer(self, buffer, name, pos):
  iter = self.nb.store.get_iter(pos)
  buff = widgetUtils.buffer(buffer)
  buff.name = name
  self.nb.store.insert(iter, -1, (buff,))

 def prepare(self):
  pass

 def search(self, name_, account):
  (path, iter) = self.nb.search(self.nb.store, name_, account)
  if path != None:
   return path

 def get_current_buffer(self):
  return self.nb.get_current_page()

 def get_current_buffer_pos(self):
  return self.nb.get_current_page_path()

 def get_buffer(self, pos):
  return self.get_page(pos)

 def load(self, selection):
  model, treeiter = selection.get_selected()
  if treeiter != None:
   if self.w != None:
    self.notebookBox.remove(self.w)
   self.w = self.nb.store[treeiter][0].buffer
   self.notebookBox.add(self.w)
   self.show_all()

 def change_buffer(self, position):
  self.nb.ChangeSelection(position)

 def get_buffer_text(self):
  return self.nb.GetPageText(self.nb.GetSelection())

 def get_buffer_by_id(self, id):
  return self.nb.FindWindowById(id)
 def advance_selection(self, forward):
  self.nb.AdvanceSelection(forward)


 def show_address(self, address):
  wx.MessageDialog(self, address, _(u"Address"), wx.OK).ShowModal()

 def delete_buffer(self, pos):
  self.nb.DeletePage(pos)

 def about_dialog(self):
  info = wx.AboutDialogInfo()
  info.SetName(application.name)
  info.SetVersion(application.version)
  info.SetDescription(application.description)
  info.SetCopyright(application.copyright)
  info.SetTranslators(application.translators)
#  info.SetLicence(application.licence)
  info.AddDeveloper(application.author)
  wx.AboutBox(info)
 def set_focus(self):
  self.SetFocus()

 def check_menuitem(self, menuitem, check=True):
  if hasattr(self, menuitem):
   getattr(self, menuitem).Check(check)

def no_update_available():
 wx.MessageDialog(None, _(u"Your " + application.name + " version is up to date"), _(u"Update"), style=wx.OK).ShowModal()
