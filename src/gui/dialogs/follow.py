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
import config
from mysc import event
import twitter
from twitter import utils
from twython import TwythonError
import output
import re

class follow(wx.Dialog):
 def __init__(self, parent, default="follow"):
  self.parent = parent
  wx.Dialog.__init__(self, None, -1)
  panel = wx.Panel(self)
  userSizer = wx.BoxSizer()
  self.SetTitle(_(u"Action"))
  if self.parent.name_buffer == "followers" or self.parent.name_buffer == "friends":
   list = [self.parent.db.settings[self.parent.name_buffer][self.parent.list.get_selected()]["screen_name"]]
  else:
   try: list =twitter.utils.get_all_users(self.parent.db.settings[self.parent.name_buffer][self.parent.list.get_selected()], self.parent.db)
   except KeyError: list = [self.parent.db.settings[self.parent.name_buffer][self.parent.list.get_selected()]["screen_name"]]
  self.cb = wx.ComboBox(panel, -1, choices=list, value=list[0])
  self.cb.SetFocus()
  userSizer.Add(self.cb)
  actionSizer = wx.BoxSizer(wx.VERTICAL)
  label2 = wx.StaticText(panel, -1, _(u"Action"))
  self.follow = wx.RadioButton(panel, -1, _(u"Follow"), style=wx.RB_GROUP)
  self.unfollow = wx.RadioButton(panel, -1, _(u"Unfollow"))
  self.mute = wx.RadioButton(panel, -1, _(u"Mute"))
  self.unmute = wx.RadioButton(panel, -1, _(u"Unmute"))
  self.block = wx.RadioButton(panel, -1, _(u"Block"))
  self.unblock = wx.RadioButton(panel, -1, _(u"Unblock"))
  self.reportSpam = wx.RadioButton(panel, -1, _(u"Report as spam"))
  self.ignore_client = wx.RadioButton(panel, -1, _(u"Ignore tweets from this client"))
  self.setup_default(default)
  actionSizer.Add(label2)
  actionSizer.Add(self.follow)
  actionSizer.Add(self.unfollow)
  actionSizer.Add(self.mute)
  actionSizer.Add(self.unmute)
  actionSizer.Add(self.block)
  actionSizer.Add(self.unblock)
  actionSizer.Add(self.reportSpam)
  actionSizer.Add(self.ignore_client)
  sizer = wx.BoxSizer(wx.VERTICAL)
  ok = wx.Button(panel, wx.ID_OK, _(u"OK"))
  ok.Bind(wx.EVT_BUTTON, self.onok)
  ok.SetDefault()
  cancel = wx.Button(panel, wx.ID_CANCEL, _(u"Close"))
  btnsizer = wx.BoxSizer()
  btnsizer.Add(ok)
  btnsizer.Add(cancel)
  sizer.Add(userSizer)
  sizer.Add(actionSizer)
  sizer.Add(btnsizer)
  panel.SetSizer(sizer)
  self.Bind(wx.EVT_CHAR_HOOK, self.onEscape, self.cb)

 def onEscape(self, ev):
  if ev.GetKeyCode() == wx.WXK_RETURN:
   self.onok(wx.EVT_BUTTON)
  ev.Skip()

 def onok(self, ev):
  if self.follow.GetValue() == True:
   try:
    self.parent.twitter.twitter.create_friendship(screen_name=self.cb.GetValue())
    self.Destroy()
   except TwythonError as err:
    output.speak("Error %s: %s" % (err.error_code, err.msg), True)
  elif self.unfollow.GetValue() == True:
   try:
    id = self.parent.twitter.twitter.destroy_friendship(screen_name=self.cb.GetValue())
    self.Destroy()
   except TwythonError as err:
    output.speak("Error %s: %s" % (err.error_code, err.msg), True)
  elif self.mute.GetValue() == True:
   try:
    id = self.parent.twitter.twitter.create_mute(screen_name=self.cb.GetValue())
    if config.main["other_buffers"]["show_muted_users"] == True:
     tweet_event = event.event(event.EVT_OBJECT, 1)
     tweet_event.SetItem(id)
     wx.PostEvent(self.parent.parent.nb.GetPage(self.parent.db.settings["buffers"].index("muteds")), tweet_event)
    self.parent.db.settings["muted_users"].append(id["id"])
    self.Destroy()
    output.speak(_(u"You've muted to %s") % (id["screen_name"]))
   except TwythonError as err:
    output.speak("Error %s: %s" % (err.error_code, err.msg), True)
  elif self.unmute.GetValue() == True:
   try:
    id = self.parent.twitter.twitter.destroy_mute(screen_name=self.cb.GetValue())
    if config.main["other_buffers"]["show_muted_users"] == True:
     item = utils.find_item(id, self.parent.db.settings["muteds"])
     if item > 0:
      deleted_event = event.event(event.EVT_DELETED, 1)
      deleted_event.SetItem(item)
      wx.PostEvent(self.parent.parent.nb.GetPage(self.parent.db.settings["buffers"].index("muteds")), deleted_event)
    if id["id"] in self.parent.db.settings["muted_users"]: self.parent.db.settings["muted_users"].remove(id["id"])
    self.Destroy()
    output.speak(_(u"You've unmuted to %s") % (id["screen_name"]))
   except TwythonError as err:
    output.speak("Error %s: %s" % (err.error_code, err.msg), True)
  elif self.reportSpam.GetValue() == True:
   try:
    self.parent.twitter.twitter.report_spam(screen_name=self.cb.GetValue())
    self.Destroy()
   except TwythonError as err:
    output.speak("Error %s: %s" % (err.error_code, err.msg), True)
  elif self.block.GetValue() == True:
   try:
    self.parent.twitter.twitter.create_block(screen_name=self.cb.GetValue())
    self.Destroy()
   except TwythonError as err:
    output.speak("Error %s: %s" % (err.error_code, err.msg), True)
  elif self.unblock.GetValue() == True:
   try:
    self.parent.twitter.twitter.destroy_block(screen_name=self.cb.GetValue())
    self.Destroy()
   except TwythonError as err:
    output.speak("Error %s: %s" % (err.error_code, err.msg), True)
  elif self.ignore_client.GetValue() == True:
   tweet = self.parent.get_tweet()
   if tweet.has_key("sender"):
    output.speak(_(u"You can't ignore direct messages"))
    return
   else:
    client = re.sub(r"(?s)<.*?>", "", tweet["source"])
   if client not in config.main["twitter"]["ignored_clients"]:
    config.main["twitter"]["ignored_clients"].append(client)
   self.Destroy()

 def setup_default(self, default):
  if default == "follow":
   self.follow.SetValue(True)
  elif default == "unfollow":
   self.unfollow.SetValue(True)
  elif default == "mute":
   self.mute.SetValue(True)
  elif default == "unmute":
   self.unmute.SetValue(True)
  elif default == "report":
   self.reportSpam.SetValue(True)
  elif default == "block":
   self.block.SetValue(True)
  elif default == "unblock":
   self.unblock.SetValue(True)