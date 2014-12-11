# -*- coding: utf-8 -*-
import wx

class basePanelMenu(wx.Menu):
 def __init__(self, parent):
  super(basePanelMenu, self).__init__()
  self.window = parent
  retweet = wx.MenuItem(self, wx.NewId(), _(u"&Retweet"))
  self.Bind(wx.EVT_MENU, self.window.onRetweet, retweet)
  self.AppendItem(retweet)
  reply = wx.MenuItem(self, wx.NewId(), _(u"Re&ply"))
  self.Bind(wx.EVT_MENU, self.window.onResponse, reply)
  self.AppendItem(reply)
  fav = wx.MenuItem(self, wx.NewId(), _(u"Add to &favourites"))
  self.Bind(wx.EVT_MENU, self.window.parent.fav, fav)
  self.AppendItem(fav)
  unfav = wx.MenuItem(self, wx.NewId(), _(u"Remove from favo&urites"))
  self.Bind(wx.EVT_MENU, self.window.parent.unfav, unfav)
  self.AppendItem(unfav)
  openUrl = wx.MenuItem(self, wx.NewId(), _(u"&Open URL"))
  self.Bind(wx.EVT_MENU, self.window.parent.url, openUrl)
  self.AppendItem(openUrl)
  play = wx.MenuItem(self, wx.NewId(), _(u"&Play audio"))
  self.Bind(wx.EVT_MENU, self.window.parent.audio, play)
  self.AppendItem(play)
  view = wx.MenuItem(self, wx.NewId(), _(u"&Show tweet"))
  self.Bind(wx.EVT_MENU, self.window.parent.view, view)
  self.AppendItem(view)
  copy = wx.MenuItem(self, wx.NewId(), _(u"&Copy to clipboard"))
  self.Bind(wx.EVT_MENU, self.window.parent.copy_to_clipboard, copy)
  self.AppendItem(copy)
  remove = wx.MenuItem(self, wx.NewId(), _(u"&Delete"))
  self.Bind(wx.EVT_MENU, self.window.parent.delete, remove)
  self.AppendItem(remove)
  userActions = wx.MenuItem(self, wx.NewId(), _(u"&User actions..."))
  self.Bind(wx.EVT_MENU, self.window.parent.onFollow, userActions)
  self.AppendItem(userActions)

class dmPanelMenu(wx.Menu):
 def __init__(self, parent):
  super(dmPanelMenu, self).__init__()
  self.window = parent
  reply = wx.MenuItem(self, wx.NewId(), _(u"Re&ply"))
  self.Bind(wx.EVT_MENU, self.window.onResponse, reply)
  self.AppendItem(reply)
  openUrl = wx.MenuItem(self, wx.NewId(), _(u"&Open URL"))
  self.Bind(wx.EVT_MENU, self.window.parent.url, openUrl)
  self.AppendItem(openUrl)
  play = wx.MenuItem(self, wx.NewId(), _(u"&Play audio"))
  self.Bind(wx.EVT_MENU, self.window.parent.audio, play)
  self.AppendItem(play)
  view = wx.MenuItem(self, wx.NewId(), _(u"&Show direct message"))
  self.Bind(wx.EVT_MENU, self.window.parent.view, view)
  self.AppendItem(view)
  copy = wx.MenuItem(self, wx.NewId(), _(u"&Copy to clipboard"))
  self.Bind(wx.EVT_MENU, self.window.parent.copy_to_clipboard, copy)
  self.AppendItem(copy)
  remove = wx.MenuItem(self, wx.NewId(), _(u"&Delete"))
  self.Bind(wx.EVT_MENU, self.window.parent.delete, remove)
  self.AppendItem(remove)
  userActions = wx.MenuItem(self, wx.NewId(), _(u"&User actions..."))
  self.Bind(wx.EVT_MENU, self.window.parent.onFollow, userActions)
  self.AppendItem(userActions)

class sentPanelMenu(wx.Menu):
 def __init__(self, parent):
  super(sentPanelMenu, self).__init__()
  self.window = parent
  openUrl = wx.MenuItem(self, wx.NewId(), _(u"&Open URL"))
  self.Bind(wx.EVT_MENU, self.window.parent.url, openUrl)
  self.AppendItem(openUrl)
  play = wx.MenuItem(self, wx.NewId(), _(u"&Play audio"))
  self.Bind(wx.EVT_MENU, self.window.parent.audio, play)
  self.AppendItem(play)
  view = wx.MenuItem(self, wx.NewId(), _(u"&Show tweet"))
  self.Bind(wx.EVT_MENU, self.window.parent.view, view)
  self.AppendItem(view)
  copy = wx.MenuItem(self, wx.NewId(), _(u"&Copy to clipboard"))
  self.Bind(wx.EVT_MENU, self.window.parent.copy_to_clipboard, copy)
  self.AppendItem(copy)
  remove = wx.MenuItem(self, wx.NewId(), _(u"&Delete"))
  self.Bind(wx.EVT_MENU, self.window.parent.delete, remove)
  self.AppendItem(remove)

class eventsPanelMenu(wx.Menu):
 def __init__(self, parent):
  super(eventsPanelMenu, self).__init__()
  self.window = parent
  view = wx.MenuItem(self, wx.NewId(), _(u"&Show event"))
  self.Bind(wx.EVT_MENU, self.window.parent.view, view)
  self.AppendItem(view)
  copy = wx.MenuItem(self, wx.NewId(), _(u"&Copy to clipboard"))
  self.Bind(wx.EVT_MENU, self.window.parent.copy_to_clipboard, copy)
  self.AppendItem(copy)
  remove = wx.MenuItem(self, wx.NewId(), _(u"&Delete"))
  self.Bind(wx.EVT_MENU, self.window.parent.delete, remove)
  self.AppendItem(remove)

class peoplePanelMenu(wx.Menu):
 def __init__(self, parent):
  super(peoplePanelMenu, self).__init__()
  self.window = parent
  reply = wx.MenuItem(self, wx.NewId(), _(u"&Mention"))
  self.Bind(wx.EVT_MENU, self.window.onResponse, reply)
  self.AppendItem(reply)
  lists = wx.MenuItem(self, wx.NewId(), _(u"&View lists"))
  self.Bind(wx.EVT_MENU, self.window.parent.view_user_lists, lists)
  self.AppendItem(lists)
  details = wx.MenuItem(self, wx.NewId(), _(u"Show user &profile"))
  self.Bind(wx.EVT_MENU, self.window.parent.details, details)
  self.AppendItem(details)
  view = wx.MenuItem(self, wx.NewId(), _(u"&Show user"))
  self.Bind(wx.EVT_MENU, self.window.parent.view, view)
  self.AppendItem(view)
  copy = wx.MenuItem(self, wx.NewId(), _(u"&Copy to clipboard"))
  self.Bind(wx.EVT_MENU, self.window.parent.copy_to_clipboard, copy)
  self.AppendItem(copy)
  userActions = wx.MenuItem(self, wx.NewId(), _(u"&User actions..."))
  self.Bind(wx.EVT_MENU, self.window.parent.onFollow, userActions)
  self.AppendItem(userActions)

class trendsPanelMenu(wx.Menu):
 def __init__(self, parent):
  super(trendsPanelMenu, self).__init__()
  self.window = parent
  tweetThisTrend = wx.MenuItem(self, wx.NewId(), _(u"&Tweet about this trend"))
  self.Bind(wx.EVT_MENU, self.window.onResponse, tweetThisTrend)
  self.AppendItem(tweetThisTrend)
  view = wx.MenuItem(self, wx.NewId(), _(u"&Show item"))
  self.Bind(wx.EVT_MENU, self.window.parent.view, view)
  self.AppendItem(view)
  copy = wx.MenuItem(self, wx.NewId(), _(u"&Copy to clipboard"))
  self.Bind(wx.EVT_MENU, self.window.parent.copy_to_clipboard, copy)
  self.AppendItem(copy)
