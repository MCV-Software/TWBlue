# -*- coding: utf-8 -*-
import wx

class basePanelMenu(wx.Menu):
 def __init__(self):
  super(basePanelMenu, self).__init__()
  self.retweet = wx.MenuItem(self, wx.NewId(), _("&Retweet"))
  self.Append(self.retweet)
  self.reply = wx.MenuItem(self, wx.NewId(), _("Re&ply"))
  self.Append(self.reply)
  self.fav = wx.MenuItem(self, wx.NewId(), _("&Like"))
  self.Append(self.fav)
  self.unfav = wx.MenuItem(self, wx.NewId(), _("&Unlike"))
  self.Append(self.unfav)
  self.openUrl = wx.MenuItem(self, wx.NewId(), _("&Open URL"))
  self.Append(self.openUrl)
  self.play = wx.MenuItem(self, wx.NewId(), _("&Play audio"))
  self.Append(self.play)
  self.view = wx.MenuItem(self, wx.NewId(), _("&Show tweet"))
  self.Append(self.view)
  self.copy = wx.MenuItem(self, wx.NewId(), _("&Copy to clipboard"))
  self.Append(self.copy)
  self.remove = wx.MenuItem(self, wx.NewId(), _("&Delete"))
  self.Append(self.remove)
  self.userActions = wx.MenuItem(self, wx.NewId(), _("&User actions..."))
  self.Append(self.userActions)

class dmPanelMenu(wx.Menu):
 def __init__(self):
  super(dmPanelMenu, self).__init__()
  self.reply = wx.MenuItem(self, wx.NewId(), _("Re&ply"))
  self.Append(self.reply)
  self.openUrl = wx.MenuItem(self, wx.NewId(), _("&Open URL"))
  self.Append(self.openUrl)
  self.play = wx.MenuItem(self, wx.NewId(), _("&Play audio"))
  self.Append(self.play)
  self.view = wx.MenuItem(self, wx.NewId(), _("&Show direct message"))
  self.Append(self.view)
  self.copy = wx.MenuItem(self, wx.NewId(), _("&Copy to clipboard"))
  self.Append(self.copy)
  self.remove = wx.MenuItem(self, wx.NewId(), _("&Delete"))
  self.Append(self.remove)
  self.userActions = wx.MenuItem(self, wx.NewId(), _("&User actions..."))
  self.Append(self.userActions)

class sentPanelMenu(wx.Menu):
 def __init__(self):
  super(sentPanelMenu, self).__init__()
  self.openUrl = wx.MenuItem(self, wx.NewId(), _("&Open URL"))
  self.Append(self.openUrl)
  self.play = wx.MenuItem(self, wx.NewId(), _("&Play audio"))
  self.Append(self.play)
  self.view = wx.MenuItem(self, wx.NewId(), _("&Show tweet"))
  self.Append(self.view)
  self.copy = wx.MenuItem(self, wx.NewId(), _("&Copy to clipboard"))
  self.Append(self.copy)
  self.remove = wx.MenuItem(self, wx.NewId(), _("&Delete"))
  self.Append(self.remove)

class eventsPanelMenu(wx.Menu):
 def __init__(self):
  super(eventsPanelMenu, self).__init__()
  self.view = wx.MenuItem(self, wx.NewId(), _("&Show event"))
  self.Append(self.view)
  self.copy = wx.MenuItem(self, wx.NewId(), _("&Copy to clipboard"))
  self.Append(self.copy)
  self.remove = wx.MenuItem(self, wx.NewId(), _("&Delete"))
  self.Append(self.remove)

class peoplePanelMenu(wx.Menu):
 def __init__(self):
  super(peoplePanelMenu, self).__init__()
  self.reply = wx.MenuItem(self, wx.NewId(), _("Direct &message"))
  self.Append(self.reply)
  self.lists = wx.MenuItem(self, wx.NewId(), _("&View lists"))
  self.Append(self.lists)
  self.lists.Enable(False)
  self.details = wx.MenuItem(self, wx.NewId(), _("Show user &profile"))
  self.Append(self.details)
  self.view = wx.MenuItem(self, wx.NewId(), _("&Show user"))
  self.Append(self.view)
  self.copy = wx.MenuItem(self, wx.NewId(), _("&Copy to clipboard"))
  self.Append(self.copy)
  self.userActions = wx.MenuItem(self, wx.NewId(), _("&User actions..."))
  self.Append(self.userActions)

class trendsPanelMenu(wx.Menu):
 def __init__(self):
  super(trendsPanelMenu, self).__init__()
  self.search_topic = wx.MenuItem(self, wx.NewId(), _("Search topic"))
  self.Append(self.search_topic)
  self.tweetThisTrend = wx.MenuItem(self, wx.NewId(), _("&Tweet about this trend"))
  self.Append(self.tweetThisTrend)
  self.view = wx.MenuItem(self, wx.NewId(), _("&Show item"))
  self.Append(self.view)
  self.copy = wx.MenuItem(self, wx.NewId(), _("&Copy to clipboard"))
  self.Append(self.copy)
