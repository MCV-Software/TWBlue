# -*- coding: utf-8 -*-
import wx

class basePanelMenu(wx.Menu):
 def __init__(self):
  super(basePanelMenu, self).__init__()
  self.retweet = wx.MenuItem(self, wx.NewId(), _(u"&Retweet"))
  self.Append(self.retweet)
  self.reply = wx.MenuItem(self, wx.NewId(), _(u"Re&ply"))
  self.Append(self.reply)
  self.fav = wx.MenuItem(self, wx.NewId(), _(u"&Like"))
  self.Append(self.fav)
  self.unfav = wx.MenuItem(self, wx.NewId(), _(u"&Unlike"))
  self.Append(self.unfav)
  self.openUrl = wx.MenuItem(self, wx.NewId(), _(u"&Open URL"))
  self.Append(self.openUrl)
  self.play = wx.MenuItem(self, wx.NewId(), _(u"&Play audio"))
  self.Append(self.play)
  self.view = wx.MenuItem(self, wx.NewId(), _(u"&Show tweet"))
  self.Append(self.view)
  self.copy = wx.MenuItem(self, wx.NewId(), _(u"&Copy to clipboard"))
  self.Append(self.copy)
  self.remove = wx.MenuItem(self, wx.NewId(), _(u"&Delete"))
  self.Append(self.remove)
  self.userActions = wx.MenuItem(self, wx.NewId(), _(u"&User actions..."))
  self.Append(self.userActions)

class dmPanelMenu(wx.Menu):
 def __init__(self):
  super(dmPanelMenu, self).__init__()
  self.reply = wx.MenuItem(self, wx.NewId(), _(u"Re&ply"))
  self.append(self.reply)
  self.openUrl = wx.MenuItem(self, wx.NewId(), _(u"&Open URL"))
  self.append(self.openUrl)
  self.play = wx.MenuItem(self, wx.NewId(), _(u"&Play audio"))
  self.append(self.play)
  self.view = wx.MenuItem(self, wx.NewId(), _(u"&Show direct message"))
  self.append(self.view)
  self.copy = wx.MenuItem(self, wx.NewId(), _(u"&Copy to clipboard"))
  self.append(self.copy)
  self.remove = wx.MenuItem(self, wx.NewId(), _(u"&Delete"))
  self.append(self.remove)
  self.userActions = wx.MenuItem(self, wx.NewId(), _(u"&User actions..."))
  self.append(self.userActions)

class sentPanelMenu(wx.Menu):
 def __init__(self):
  super(sentPanelMenu, self).__init__()
  self.openUrl = wx.MenuItem(self, wx.NewId(), _(u"&Open URL"))
  self.append(self.openUrl)
  self.play = wx.MenuItem(self, wx.NewId(), _(u"&Play audio"))
  self.append(self.play)
  self.view = wx.MenuItem(self, wx.NewId(), _(u"&Show tweet"))
  self.append(self.view)
  self.copy = wx.MenuItem(self, wx.NewId(), _(u"&Copy to clipboard"))
  self.append(self.copy)
  self.remove = wx.MenuItem(self, wx.NewId(), _(u"&Delete"))
  self.append(self.remove)

class eventsPanelMenu(wx.Menu):
 def __init__(self):
  super(eventsPanelMenu, self).__init__()
  self.view = wx.MenuItem(self, wx.NewId(), _(u"&Show event"))
  self.append(self.view)
  self.copy = wx.MenuItem(self, wx.NewId(), _(u"&Copy to clipboard"))
  self.append(self.copy)
  self.remove = wx.MenuItem(self, wx.NewId(), _(u"&Delete"))
  self.append(self.remove)

class peoplePanelMenu(wx.Menu):
 def __init__(self):
  super(peoplePanelMenu, self).__init__()
  self.reply = wx.MenuItem(self, wx.NewId(), _(u"Direct &message"))
  self.append(self.reply)
  self.lists = wx.MenuItem(self, wx.NewId(), _(u"&View lists"))
  self.append(self.lists)
  self.lists.Enable(False)
  self.details = wx.MenuItem(self, wx.NewId(), _(u"Show user &profile"))
  self.append(self.details)
  self.view = wx.MenuItem(self, wx.NewId(), _(u"&Show user"))
  self.append(self.view)
  self.copy = wx.MenuItem(self, wx.NewId(), _(u"&Copy to clipboard"))
  self.append(self.copy)
  self.userActions = wx.MenuItem(self, wx.NewId(), _(u"&User actions..."))
  self.append(self.userActions)

class trendsPanelMenu(wx.Menu):
 def __init__(self):
  super(trendsPanelMenu, self).__init__()
  self.search_topic = wx.MenuItem(self, wx.NewId(), _(u"Search topic"))
  self.append(self.search_topic)
  self.tweetThisTrend = wx.MenuItem(self, wx.NewId(), _(u"&Tweet about this trend"))
  self.append(self.tweetThisTrend)
  self.view = wx.MenuItem(self, wx.NewId(), _(u"&Show item"))
  self.append(self.view)
  self.copy = wx.MenuItem(self, wx.NewId(), _(u"&Copy to clipboard"))
  self.append(self.copy)
