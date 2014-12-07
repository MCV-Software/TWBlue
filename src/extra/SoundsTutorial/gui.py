# -*- coding: utf-8 -*-
import wx
import config
import os
import paths
import sound

class soundsTutorial(wx.Dialog):
 def __init__(self):
  self.actions = [
  _(u"The tweet may contain a playable audio"),
  _(u"A timeline has been created"),
    _(u"A timeline has been deleted"),
    _(u"You've received a direct message"),
    _(u"You've sent a direct message"),
    _(u"A bug has happened"),
  _(u"You've added a tweet to your favourites"),
  _(u"Someone's favourites have been updated"),
  _(u"The tweet has coordinates to determine its location"),
  _(u"There are no more tweets to read"),
    _(u"A list has a new tweet"),
    _(u"You can't add any more characters on the tweet"),
    _(u"You've been mentioned "),
  _(u"A new event has happened"),
  _(u"TW Blue is ready "),
    _(u"You've replied"),
    _(u"You've retweeted"),
    _(u"A search has been updated"),
    _(u"There's a new tweet in the main buffer"),
    _(u"You've sent a tweet"),
  _(u"There's a new tweet in a timeline"),
    _(u"You have a new follower"),
    _(u"You've turned the volume up or down")]
  self.files = os.listdir(paths.sound_path("default"))
  super(soundsTutorial, self).__init__(None, -1)
  if len(self.actions) > len(self.files):
   wx.MessageDialog(None, _(u"It seems as though the currently used sound pack needs an update. %i fails are still be required to use this function. Make sure to obtain the needed lacking sounds or to contact with the sound pack developer.") % (len(self.actions) - len(self.files)), _(u"Error"), wx.ICON_ERROR).ShowModal()
   self.Destroy()
  self.SetTitle(_(u"Sounds tutorial"))
  panel = wx.Panel(self)
  sizer = wx.BoxSizer(wx.VERTICAL)
  label = wx.StaticText(panel, -1, _(u"Press enter to listen to the sound for the selected event"))
  self.items = wx.ListBox(panel, 1, choices=self.actions, style=wx.LB_SINGLE)
  self.items.SetSelection(0)
  listBox = wx.BoxSizer(wx.HORIZONTAL)
  listBox.Add(label)
  listBox.Add(self.items)
  play = wx.Button(panel, 1, (u"Play"))
  play.SetDefault()
  self.Bind(wx.EVT_BUTTON, self.onPlay, play)
  close = wx.Button(panel, wx.ID_CANCEL)
  btnBox = wx.BoxSizer(wx.HORIZONTAL)
  btnBox.Add(play)
  btnBox.Add(close)
  sizer.Add(listBox)
  sizer.Add(btnBox)
  panel.SetSizer(sizer)

 def onPlay(self, ev):
  sound.player.play(self.files[self.items.GetSelection()])