# -*- coding: utf-8 -*-
import wx

class UserActionsDialog(wx.Dialog):
 def __init__(self, users=[], default="follow", *args, **kwargs):
  super(UserActionsDialog, self).__init__(parent=None, *args, **kwargs)
  panel = wx.Panel(self)
  userSizer = wx.BoxSizer()
  self.SetTitle(_(u"Action"))
  self.cb = wx.ComboBox(panel, -1, choices=users, value=users[0])
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
  ok.SetDefault()
  cancel = wx.Button(panel, wx.ID_CANCEL, _(u"Close"))
  btnsizer = wx.BoxSizer()
  btnsizer.Add(ok)
  btnsizer.Add(cancel)
  sizer.Add(userSizer)
  sizer.Add(actionSizer)
  sizer.Add(btnsizer)
  panel.SetSizer(sizer)

 def get_action(self):
  if self.follow.GetValue() == True: return "follow"
  elif self.unfollow.GetValue() == True: return "unfollow"
  elif self.mute.GetValue() == True: return "mute"
  elif self.unmute.GetValue() == True: return "unmute"
  elif self.reportSpam.GetValue() == True: return "report"
  elif self.block.GetValue() == True: return "block"
  elif self.unblock.GetValue() == True: return "unblock"
  elif self.ignore_client.GetValue() == True: return "ignore_client"

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
  elif default == "ignore_client":
   self.ignore_client.SetValue(True)

 def get_response(self):
  return self.ShowModal()

 def get_user(self):
  return self.cb.GetValue()