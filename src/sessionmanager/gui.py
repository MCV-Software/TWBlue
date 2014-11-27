# -*- coding: utf-8 -*-
import shutil
import time
import wx
import manager
import session_exceptions
import paths
import config
import sound
import languageHandler
import output
import os
import twitter
import webbrowser
from multiplatform_widgets import widgets
from config_utils import Configuration

class sessionManagerWindow(wx.Dialog):
 def __init__(self):
  super(sessionManagerWindow, self).__init__(parent=None, title=_(u"Session manager"), size=wx.DefaultSize)
#  panelSizer = wx.BoxSizer(wx.VERTICAL)
  panel = wx.Panel(self)
  sizer = wx.BoxSizer(wx.VERTICAL)
  label = wx.StaticText(panel, -1, _(u"Select a twitter account to start TW Blue"), size=wx.DefaultSize)
  listSizer = wx.BoxSizer(wx.HORIZONTAL)
  self.list = widgets.list(panel, _(u"Account"), style=wx.LC_SINGLE_SEL|wx.LC_REPORT)
  listSizer.Add(label, 0, wx.ALL, 5)
  listSizer.Add(self.list.list, 0, wx.ALL, 5)
  sizer.Add(listSizer, 0, wx.ALL, 5)
  new = wx.Button(panel, -1, _(u"New account"), size=wx.DefaultSize)
  new.Bind(wx.EVT_BUTTON, self.new_account)
  self.removeSession = wx.Button(panel, -1, _(u"Remove session"))
  self.removeSession.Disable()
  self.removeSession.Bind(wx.EVT_BUTTON, self.remove)
  ok = wx.Button(panel, wx.ID_OK, size=wx.DefaultSize)
  ok.SetDefault()
  ok.Bind(wx.EVT_BUTTON, self.ok)
  cancel = wx.Button(panel, wx.ID_CANCEL, size=wx.DefaultSize)
  buttons = wx.BoxSizer(wx.HORIZONTAL)
  buttons.Add(new, 0, wx.ALL, 5)
  buttons.Add(self.removeSession, 0, wx.ALL, 5)
  buttons.Add(ok, 0, wx.ALL, 5)
  buttons.Add(cancel, 0, wx.ALL, 5)
  sizer.Add(buttons, 0, wx.ALL, 5)
  panel.SetSizer(sizer)
  self.fill_list()
  min = sizer.CalcMin()
  self.SetClientSize(min)

 def fill_list(self):
  self.sessions = []
  for i in os.listdir(paths.config_path()):
   if os.path.isdir(paths.config_path(i)):
    strconfig = "%s/session.conf" % (paths.config_path(i))
    config_test = Configuration(strconfig)
    name = config_test["twitter"]["user_name"]
    if name != "" or (config_test["twitter"]["user_key"] != "" and config_test["twitter"]["user_secret"] != ""):
     self.list.insert_item(False, name)
     self.sessions.append(i)
    else:
     del config_test
     shutil.rmtree(path=paths.config_path(i), ignore_errors=True)
  if self.list.get_count() > 0:
   self.list.select_item(0)
  self.list.list.SetSize(self.list.list.GetBestSize())
  self.removeSession.Enable()

 def ok(self, ev):
  if self.list.get_count() == 0:
   wx.MessageDialog(None, _(u"You need to configure an account."), _(u"Account Error"), wx.ICON_ERROR).ShowModal()
   return
  current_session = self.sessions[self.list.get_selected()]
  manager.manager.set_current_session(current_session)
  config.MAINFILE = "%s/session.conf" % (manager.manager.get_current_session())
  config.setup()
  lang=config.main['general']['language']
  languageHandler.setLanguage(lang)
  sound.setup()
  output.setup()
  self.EndModal(wx.ID_OK)

 def new_account(self, ev):
  twitter_object = twitter.twitter.twitter()
  dlg = wx.MessageDialog(self, _(u"The request for the required Twitter authorization to continue will be opened on your browser. You only need to do it once. Would you like to autorhise a new account now?"), _(u"Authorisation"), wx.YES_NO)
  if dlg.ShowModal() == wx.ID_NO:
   return
  else:
   location = (str(time.time())[:12])
   manager.manager.add_session(location)
   config.MAINFILE = "%s/session.conf" % (location,)
   config.setup()
   try:
    twitter_object.authorise()
   except:
    wx.MessageDialog(None, _(u"Your access token is invalid or the authorisation has failed. Please try again."), _(u"Invalid user token"), wx.ICON_ERROR).ShowModal()
    return
   total = self.list.get_count()
   name = _(u"Authorised account %d") % (total+1)
   self.list.insert_item(False, name)
   if self.list.get_count() == 1:
    self.list.select_item(0)
   self.sessions.append(location)

 def remove(self, ev):
  selected_item = self.list.get_selected()
  selected_session = self.sessions[selected_item]
  ask = wx.MessageDialog(self, _(u"Do you really want delete this account?"), _(u"Remove account"), wx.YES_NO)
  if ask.ShowModal() == wx.ID_YES:
   self.sessions.remove(selected_session)
   shutil.rmtree(path=paths.config_path(selected_session), ignore_errors=True)
   self.list.remove_item(selected_item)