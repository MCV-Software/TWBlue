# -*- coding: utf-8 -*-
import wx

class basePanelMenu(wx.Menu):
 def __init__(self):
  super(basePanelMenu, self).__init__()
  self.retweet = wx.MenuItem(self, wx.NewId(), _(u"&Retweet"))
  self.AppendItem(self.retweet)
  self.reply = wx.MenuItem(self, wx.NewId(), _(u"Re&ply"))
  self.AppendItem(self.reply)
  self.fav = wx.MenuItem(self, wx.NewId(), _(u"Add to &favourites"))
  self.AppendItem(self.fav)
  self.unfav = wx.MenuItem(self, wx.NewId(), _(u"Remove from favo&urites"))
  self.AppendItem(self.unfav)
  self.openUrl = wx.MenuItem(self, wx.NewId(), _(u"&Open URL"))
  self.AppendItem(self.openUrl)
  self.play = wx.MenuItem(self, wx.NewId(), _(u"&Play audio"))
  self.AppendItem(self.play)
  self.view = wx.MenuItem(self, wx.NewId(), _(u"&Show tweet"))
  self.AppendItem(self.view)
  self.copy = wx.MenuItem(self, wx.NewId(), _(u"&Copy to clipboard"))
  self.AppendItem(self.copy)
  self.remove = wx.MenuItem(self, wx.NewId(), _(u"&Delete"))
  self.AppendItem(self.remove)
  self.userActions = wx.MenuItem(self, wx.NewId(), _(u"&User actions..."))
  self.AppendItem(self.userActions)

class dmPanelMenu(wx.Menu):
 def __init__(self):
  super(dmPanelMenu, self).__init__()
  self.reply = wx.MenuItem(self, wx.NewId(), _(u"Re&ply"))
  self.AppendItem(self.reply)
  self.openUrl = wx.MenuItem(self, wx.NewId(), _(u"&Open URL"))
  self.AppendItem(self.openUrl)
  self.play = wx.MenuItem(self, wx.NewId(), _(u"&Play audio"))
  self.AppendItem(self.play)
  self.view = wx.MenuItem(self, wx.NewId(), _(u"&Show direct message"))
  self.AppendItem(self.view)
  self.copy = wx.MenuItem(self, wx.NewId(), _(u"&Copy to clipboard"))
  self.AppendItem(self.copy)
  self.remove = wx.MenuItem(self, wx.NewId(), _(u"&Delete"))
  self.AppendItem(self.remove)
  self.userActions = wx.MenuItem(self, wx.NewId(), _(u"&User actions..."))
  self.AppendItem(self.userActions)

class sentPanelMenu(wx.Menu):
 def __init__(self):
  super(sentPanelMenu, self).__init__()
  self.openUrl = wx.MenuItem(self, wx.NewId(), _(u"&Open URL"))
  self.AppendItem(self.openUrl)
  self.play = wx.MenuItem(self, wx.NewId(), _(u"&Play audio"))
  self.AppendItem(self.play)
  self.view = wx.MenuItem(self, wx.NewId(), _(u"&Show tweet"))
  self.AppendItem(self.view)
  self.copy = wx.MenuItem(self, wx.NewId(), _(u"&Copy to clipboard"))
  self.AppendItem(self.copy)
  self.remove = wx.MenuItem(self, wx.NewId(), _(u"&Delete"))
  self.AppendItem(self.remove)

class eventsPanelMenu(wx.Menu):
 def __init__(self):
  super(eventsPanelMenu, self).__init__()
  self.view = wx.MenuItem(self, wx.NewId(), _(u"&Show event"))
  self.AppendItem(self.view)
  self.copy = wx.MenuItem(self, wx.NewId(), _(u"&Copy to clipboard"))
  self.AppendItem(self.copy)
  self.remove = wx.MenuItem(self, wx.NewId(), _(u"&Delete"))
  self.AppendItem(self.remove)

class peoplePanelMenu(wx.Menu):
 def __init__(self):
  super(peoplePanelMenu, self).__init__()
  self.reply = wx.MenuItem(self, wx.NewId(), _(u"Direct &message"))
  self.AppendItem(self.reply)
  self.lists = wx.MenuItem(self, wx.NewId(), _(u"&View lists"))
  self.AppendItem(self.lists)
  self.lists.Enable(False)
  self.details = wx.MenuItem(self, wx.NewId(), _(u"Show user &profile"))
  self.AppendItem(self.details)
  self.view = wx.MenuItem(self, wx.NewId(), _(u"&Show user"))
  self.AppendItem(self.view)
  self.copy = wx.MenuItem(self, wx.NewId(), _(u"&Copy to clipboard"))
  self.AppendItem(self.copy)
  self.userActions = wx.MenuItem(self, wx.NewId(), _(u"&User actions..."))
  self.AppendItem(self.userActions)

class trendsPanelMenu(wx.Menu):
 def __init__(self):
  super(trendsPanelMenu, self).__init__()
  self.search_topic = wx.MenuItem(self, wx.NewId(), _(u"Search topic"))
  self.AppendItem(self.search_topic)
  self.tweetThisTrend = wx.MenuItem(self, wx.NewId(), _(u"&Tweet about this trend"))
  self.AppendItem(self.tweetThisTrend)
  self.view = wx.MenuItem(self, wx.NewId(), _(u"&Show item"))
  self.AppendItem(self.view)
  self.copy = wx.MenuItem(self, wx.NewId(), _(u"&Copy to clipboard"))
  self.AppendItem(self.copy)
