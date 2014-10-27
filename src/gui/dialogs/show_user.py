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
import wx, twitter, config, gui.dialogs, sound, webbrowser

class showUserProfile(wx.Dialog):
 def __init__(self, twitter, screen_name):
  self.twitter = twitter
  self.screen_name = screen_name
  wx.Dialog.__init__(self, None, -1)
  self.SetTitle(_(u"Information for %s") % (screen_name))
  panel = wx.Panel(self)
  sizer = wx.BoxSizer(wx.VERTICAL)
  self.get_data()
  static = wx.StaticText(panel, -1, _(u"Details"))
  sizer.Add(static, 0, wx.ALL, 5)
  text = wx.TextCtrl(panel, -1, style=wx.TE_MULTILINE|wx.TE_READONLY)
#  dc = wx.WindowDC(text)
#  dc.SetFont(text.GetFont())
#  (x, y, z) = dc.GetMultiLineTextExtent("0"*10000)
#  text.SetSize((x, y))
  text.SetFocus()
  sizer.Add(text, 0, wx.ALL|wx.EXPAND, 5)
  self.url = wx.Button(panel, -1, _(u"Go to URL"), size=wx.DefaultSize)
  self.url.Bind(wx.EVT_BUTTON, self.onUrl)
  self.url.Disable()
  close = wx.Button(panel, wx.ID_CANCEL, _(u"Close"))
  close.Bind(wx.EVT_BUTTON, self.onClose)
  btnSizer = wx.BoxSizer(wx.HORIZONTAL)
  btnSizer.Add(self.url, 0, wx.ALL, 5)
  btnSizer.Add(close, 0, wx.ALL, 5)
  sizer.Add(btnSizer, 0, wx.ALL, 5)
  text.ChangeValue(self.compose_string())
  text.SetSize(text.GetBestSize())
  panel.SetSizer(sizer)
  self.SetClientSize(sizer.CalcMin())

 def onUrl(self, ev):
  webbrowser.open(self.data["url"])

 def onClose(self, ev):
  self.Destroy()

 def get_data(self):
  try:
   self.data = self.twitter.twitter.show_user(screen_name=self.screen_name)
  except:
   wx.MessageDialog(self, _(u"This user does not exist on Twitter"), _(u"Error"), wx.ICON_ERROR).ShowModal()
   self.EndModal()

 def compose_string(self):
  string = u""
  string = string + _(u"Username: @%s\n") % (self.data["screen_name"])
  string = string + _(u"Name: %s\n") % (self.data["name"])
  if self.data["location"] != "":
   string = string + _(u"Location: %s\n") % (self.data["location"])
  if self.data["url"] != None:
   string = string+ _(u"URL: %s\n") % (self.data["url"])
   self.url.Enable()
  if self.data["description"] != "":
   string = string+ _(u"Bio: %s\n") % (self.data["description"])
  if self.data["protected"] == True: protected = _(u"Yes")
  else: protected = _(u"No")
  string = string+ _(u"Protected: %s\n") % (protected)
  string = string+_(u"Followers: %s\n Friends: %s\n") % (self.data["followers_count"], self.data["friends_count"])
  string = string+ _(u"Tweets: %s\n") % (self.data["statuses_count"])
  string = string+ _(u"Favourites: %s") % (self.data["favourites_count"])
  return string