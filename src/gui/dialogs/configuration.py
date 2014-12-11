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
#import gui
from gui import buffers
import sound as snd
import sound_lib
import languageHandler
import logging as original_logger
import os
import webbrowser
import paths
import platform
from mysc import restart
from extra.autocompletionUsers import settings
log = original_logger.getLogger("configuration")

system = platform.system()
class general(wx.Panel):
 def __init__(self, parent):
  wx.Panel.__init__(self, parent)
  sizer = wx.BoxSizer(wx.VERTICAL)
  language = wx.StaticText(self, -1, _(u"Language"))
  self.langs = languageHandler.getAvailableLanguages()
  langs = []
  [langs.append(i[1]) for i in self.langs]
  self.codes = []
  [self.codes.append(i[0]) for i in self.langs]
  self.language = wx.ListBox(self, -1, choices=langs)
  id = self.codes.index(config.main["general"]["language"])
  self.language.SetSelection(id)
  self.language.SetSize(self.language.GetBestSize())
  langBox = wx.BoxSizer(wx.HORIZONTAL)
  langBox.Add(language, 0, wx.ALL, 5)
  langBox.Add(self.language, 0, wx.ALL, 5)
  sizer.Add(langBox, 0, wx.ALL, 5)
  self.au = wx.Button(self, -1, _(u"Set the autocomplete function"))
  self.ask_at_exit = wx.CheckBox(self, -1, _(U"ask before exiting TwBlue?"))
  self.ask_at_exit.SetValue(config.main["general"]["ask_at_exit"])
  sizer.Add(self.ask_at_exit, 0, wx.ALL, 5)
  self.use_invisible_shorcuts = wx.CheckBox(self, -1, _(u"Use invisible interface's keyboard shorcuts on the GUI"))
  self.use_invisible_shorcuts.SetValue(config.main["general"]["use_invisible_keyboard_shorcuts"])
  sizer.Add(self.use_invisible_shorcuts, 0, wx.ALL, 5)
  self.relative_time = wx.CheckBox(self, -1, _(U"Relative times"))
  self.relative_time.SetValue(config.main["general"]["relative_times"])
  sizer.Add(self.relative_time, 0, wx.ALL, 5)
  if platform.system() == "Windows":
   self.disable_sapi5 = wx.CheckBox(self, -1, _(u"Activate Sapi5 when any other screen reader is not being run"))
   self.disable_sapi5.SetValue(config.main["general"]["voice_enabled"])
   sizer.Add(self.disable_sapi5, 0, wx.ALL, 5)
   self.show_gui = wx.CheckBox(self, -1, _(u"Activate the auto-start of the invisible interface"))
   self.show_gui.SetValue(config.main["general"]["hide_gui"])
   sizer.Add(self.show_gui, 0, wx.ALL, 5)
  apiCallsBox = wx.BoxSizer(wx.HORIZONTAL)
  apiCallsBox.Add(wx.StaticText(self, -1, _(u"API calls when the stream is started (One API call equals to 200 tweetts, two API calls equals 400 tweets, etc):")), 0, wx.ALL, 5)
  self.apiCalls = wx.SpinCtrl(self, -1)
  self.apiCalls.SetRange(1, 10)
  self.apiCalls.SetValue(config.main["general"]["max_api_calls"])
  self.apiCalls.SetSize(self.apiCalls.GetBestSize())
  apiCallsBox.Add(self.apiCalls, 0, wx.ALL, 5)
  sizer.Add(apiCallsBox, 0, wx.ALL, 5)
  tweetsPerCallBox = wx.BoxSizer(wx.HORIZONTAL)
  tweetsPerCallBox.Add(wx.StaticText(self, -1, _(u"Items on each API call")), 0, wx.ALL, 5)
  self.itemsPerApiCall = wx.SpinCtrl(self, -1)
  self.itemsPerApiCall.SetRange(0, 200)
  self.itemsPerApiCall.SetValue(config.main["general"]["max_tweets_per_call"])
  self.itemsPerApiCall.SetSize(self.itemsPerApiCall.GetBestSize())
  tweetsPerCallBox.Add(self.itemsPerApiCall, 0, wx.ALL, 5)
  sizer.Add(tweetsPerCallBox, 0, wx.ALL, 5)
  self.reverse_timelines = wx.CheckBox(self, -1, _(u"Inverted buffers: The newest tweets will be shown at the beginning of the lists while the oldest at the end"))
  self.reverse_timelines.SetValue(config.main["general"]["reverse_timelines"])
  sizer.Add(self.reverse_timelines, 0, wx.ALL, 5)
  self.SetSizer(sizer)

  
class other_buffers(wx.Panel):
 def __init__(self, parent):
  wx.Panel.__init__(self, parent)
  sizer = wx.BoxSizer(wx.VERTICAL)
  self.followers_value = config.main["other_buffers"]["show_followers"]
  self.friends_value = config.main["other_buffers"]["show_friends"]
  self.favs_value = config.main["other_buffers"]["show_favourites"]
  self.events_value = config.main["other_buffers"]["show_events"]
  self.blocks_value = config.main["other_buffers"]["show_blocks"]
  self.mutes_value = config.main["other_buffers"]["show_muted_users"]
  self.followers = wx.CheckBox(self, -1, _(u"Show followers"))
  self.followers.SetValue(config.main["other_buffers"]["show_followers"])
  sizer.Add(self.followers, 0, wx.ALL, 5)
  self.friends = wx.CheckBox(self, -1, _(u"Show friends"))
  self.friends.SetValue(config.main["other_buffers"]["show_friends"])
  sizer.Add(self.friends, 0, wx.ALL, 5)
  self.favs = wx.CheckBox(self, -1, _(u"Show favourites"))
  self.favs.SetValue(config.main["other_buffers"]["show_favourites"])
  sizer.Add(self.favs, 0, wx.ALL, 5)
  self.blocks = wx.CheckBox(self, -1, _(u"Show blocked users"))
  self.blocks.SetValue(config.main["other_buffers"]["show_blocks"])
  sizer.Add(self.blocks, 0, wx.ALL, 5)
  self.mutes = wx.CheckBox(self, -1, _(u"Show muted users"))
  self.mutes.SetValue(config.main["other_buffers"]["show_muted_users"])
  sizer.Add(self.mutes, 0, wx.ALL, 5)
  self.events = wx.CheckBox(self, -1, _(u"Show events"))
  self.events.SetValue(config.main["other_buffers"]["show_events"])
  sizer.Add(self.events, 0, wx.ALL, 5)
  self.SetSizer(sizer)

class ignoredClients(wx.Panel):
 def __init__(self, parent):
  super(ignoredClients, self).__init__(parent=parent)
  sizer = wx.BoxSizer(wx.VERTICAL)
  choices = config.main["twitter"]["ignored_clients"]
  label = wx.StaticText(self, -1, _(u"Ignored clients"))
  self.clients = wx.ListBox(self, -1, choices=choices)
  self.clients.SetSize(self.clients.GetBestSize())
  clientsBox = wx.BoxSizer(wx.HORIZONTAL)
  clientsBox.Add(label, 0, wx.ALL, 5)
  clientsBox.Add(self.clients, 0, wx.ALL, 5)
  add = wx.Button(self, -1, _(u"Add client"))
  remove = wx.Button(self, -1, _(u"Remove client"))
  self.Bind(wx.EVT_BUTTON, self.add, add)
  self.Bind(wx.EVT_BUTTON, self.remove, remove)
  btnBox = wx.BoxSizer(wx.HORIZONTAL)
  btnBox.Add(add, 0, wx.ALL, 5)
  btnBox.Add(remove, 0, wx.ALL, 5)
  sizer.Add(clientsBox, 0, wx.ALL, 5)
  sizer.Add(btnBox, 0, wx.ALL, 5)
  self.SetSizer(sizer)

 def add(self, ev):
  entry = wx.TextEntryDialog(self, _(u"Enter the name of the client here"), _(u"Add a new ignored client"))
  if entry.ShowModal() == wx.ID_OK:
   client = entry.GetValue()
   if client not in config.main["twitter"]["ignored_clients"]:
    config.main["twitter"]["ignored_clients"].append(client)
    self.clients.Append(client)

 def remove(self, ev):
  if self.clients.GetCount() == 0: return
  id = self.clients.GetSelection()
  config.main["twitter"]["ignored_clients"].pop(id)
  self.clients.Delete(id)

class sound(wx.Panel):
 def __init__(self, parent):
  wx.Panel.__init__(self, parent)
  sizer = wx.BoxSizer(wx.VERTICAL)
  volume = wx.StaticText(self, -1, _(u"Volume"))
  self.volumeCtrl = wx.Slider(self)
  self.volumeCtrl.SetRange(0, 100)
  self.volumeCtrl.SetValue(config.main["sound"]["volume"]*100)
  self.volumeCtrl.SetSize(self.volumeCtrl.GetBestSize())
  volumeBox = wx.BoxSizer(wx.HORIZONTAL)
  volumeBox.Add(volume, 0, wx.ALL, 5)
  volumeBox.Add(self.volumeCtrl, 0, wx.ALL, 5)
  sizer.Add(volumeBox, 0, wx.ALL, 5)
  self.global_mute = wx.CheckBox(self, -1, _(u"Global mute"))
  self.global_mute.SetValue(config.main["sound"]["global_mute"])
  sizer.Add(self.global_mute, 0, wx.ALL, 5)
  self.output_devices = sound_lib.output.Output.get_device_names()
  output_label = wx.StaticText(self, -1, _(u"Output device"))
  self.output = wx.ComboBox(self, -1, choices=self.output_devices, style=wx.CB_READONLY)
  self.output.SetValue(config.main["sound"]["output_device"])
  self.output.SetSize(self.output.GetBestSize())
  outputBox = wx.BoxSizer(wx.HORIZONTAL)
  outputBox.Add(output_label, 0, wx.ALL, 5)
  outputBox.Add(self.output, 0, wx.ALL, 5)
  sizer.Add(outputBox, 0, wx.ALL, 5)
  self.input_devices = sound_lib.input.Input.get_device_names()
  input_label = wx.StaticText(self, -1, _(u"Input device"))
  self.input = wx.ComboBox(self, -1, choices=self.input_devices, style=wx.CB_READONLY)
  self.input.SetValue(config.main["sound"]["input_device"])
  self.input.SetSize(self.input.GetBestSize())
  inputBox = wx.BoxSizer(wx.HORIZONTAL)
  inputBox.Add(input_label, 0, wx.ALL, 5)
  inputBox.Add(self.input, 0, wx.ALL, 5)
  sizer.Add(inputBox, 0, wx.ALL, 5)
  soundBox =  wx.BoxSizer(wx.VERTICAL)
  self.soundpacks = []
  [self.soundpacks.append(i) for i in os.listdir(paths.sound_path()) if os.path.isdir(paths.sound_path(i)) == True ]
  soundpack_label = wx.StaticText(self, -1, _(u"Sound pack"))
  self.soundpack = wx.ComboBox(self, -1, choices=self.soundpacks, style=wx.CB_READONLY)
  self.soundpack.SetValue(config.main["sound"]["current_soundpack"])
  self.soundpack.SetSize(self.soundpack.GetBestSize())
  soundBox.Add(soundpack_label, 0, wx.ALL, 5)
  soundBox.Add(self.soundpack, 0, wx.ALL, 5)
  sizer.Add(soundBox, 0, wx.ALL, 5)
  self.SetSizer(sizer)

class audioServicesPanel(wx.Panel):
 def __init__(self, parent):
  super(audioServicesPanel, self).__init__(parent)
  mainSizer = wx.BoxSizer(wx.VERTICAL)
  apiKeyLabel = wx.StaticText(self, -1, _(u"If you've got a SndUp account, enter your API Key here. Whether the API Key is wrong, the App will fail to upload anything to the server. Whether there's no API Key here, then the audio files will be uploaded anonimously"))
  self.apiKey = wx.TextCtrl(self, -1)
  self.apiKey.SetValue(config.main["sound"]["sndup_api_key"])
  dc = wx.WindowDC(self.apiKey)
  dc.SetFont(self.apiKey.GetFont())
  self.apiKey.SetSize(dc.GetTextExtent("0"*100))
  apiKeyBox = wx.BoxSizer(wx.HORIZONTAL)
  apiKeyBox.Add(apiKeyLabel, 0, wx.ALL, 5)
  apiKeyBox.Add(self.apiKey, 0, wx.ALL, 5)
  mainSizer.Add(apiKeyBox, 0, wx.ALL, 5)
  first_sizer = wx.BoxSizer(wx.HORIZONTAL)
  self.dropbox = wx.Button(self, -1)
  if len(config.main["services"]["dropbox_token"]) > 0:
   self.dropbox.SetLabel(_(u"Unlink your Dropbox account"))
  else:
   self.dropbox.SetLabel(_(u"Link your Dropbox account"))
  self.dropbox.Bind(wx.EVT_BUTTON, self.onLink_unlink)
  first_sizer.Add(self.dropbox, 0, wx.ALL, 5)
  mainSizer.Add(first_sizer, 0, wx.ALL, 5)
  self.SetSizer(mainSizer)

 def setup_dropbox(self):
  from extra.AudioUploader import dropbox_transfer
  auth = dropbox_transfer.dropboxLogin()
  url = auth.get_url()
  wx.MessageDialog(self, _(u"The authorisation request will be shown on your browser. Copy the code tat Dropbox will provide and, in the text box that will appear on TW Blue, paste it. This code is necessary to continue. You only need to do it once."), _(u"Authorisation"), wx.OK).ShowModal()
  webbrowser.open(url)
  dlg = wx.TextEntryDialog(self, _(u"Enter the code here."), _(u"Verification code"))
  if dlg.ShowModal() == wx.ID_CANCEL:
   return False
  resp = dlg.GetValue()
  if resp == "":
   self.dropbox.SetLabel(_(u"Link your Dropbox account"))
   return False
  else:
   try:
    auth.authorise(resp)
    self.dropbox.SetLabel(_(u"Unlink your Dropbox account"))
   except:
    wx.MessageDialog(self, _(u"Error during authorisation. Try again later."), _(u"Error!"), wx.ICON_ERROR).ShowModal()
    self.dropbox.SetLabel(_(u"Link your Dropbox account"))
    return False

 def onLink_unlink(self, ev):
  if self.dropbox.GetLabel() == _(u"Link your Dropbox account"):
   self.setup_dropbox()
  else:
   self.disconnect_dropbox()

 def disconnect_dropbox(self):
  config.main["services"]["dropbox_token"] = ""
  self.dropbox.SetLabel(_(u"Link your Dropbox account"))

class configurationDialog(wx.Dialog):
 def __init__(self, parent):
  self.parent = parent
  wx.Dialog.__init__(self, None, -1)
  panel = wx.Panel(self)
  self.SetTitle(_(u"TW Blue preferences"))
  sizer = wx.BoxSizer(wx.VERTICAL)
  notebook = wx.Notebook(panel)
  self.general = general(notebook)
  notebook.AddPage(self.general, _(u"General"))
  self.general.SetFocus()
  self.Bind(wx.EVT_BUTTON, self.autocompletion, self.general.au)
  self.buffers = other_buffers(notebook)
  notebook.AddPage(self.buffers, _(u"Show other buffers"))
  self.ignored_clients = ignoredClients(notebook)
  notebook.AddPage(self.ignored_clients, _(u"Ignored clients"))
  self.sound = sound(notebook)
  notebook.AddPage(self.sound, _(u"Sound"))
  self.services = audioServicesPanel(notebook)
  notebook.AddPage(self.services, _(u"Audio Services"))
  sizer.Add(notebook, 0, wx.ALL, 5)
  ok_cancel_box = wx.BoxSizer(wx.HORIZONTAL)
  ok = wx.Button(panel, wx.ID_OK, _(u"Save"))
  ok.Bind(wx.EVT_BUTTON, self.onSave)
  ok.SetDefault()
  cancel = wx.Button(panel, wx.ID_CANCEL, _(u"Close"))
  self.SetEscapeId(cancel.GetId())
  ok_cancel_box.Add(ok, 0, wx.ALL, 5)
  ok_cancel_box.Add(cancel, 0, wx.ALL, 5)
  sizer.Add(ok_cancel_box, 0, wx.ALL, 5)
  panel.SetSizer(sizer)
  self.SetClientSize(sizer.CalcMin())

 def autocompletion(self, ev):
  configuration = settings.autocompletionSettings(self.parent)

 def check_followers_change(self):
  if self.buffers.followers.GetValue() != self.buffers.followers_value:
   if self.buffers.followers.GetValue() == True:
    log.debug("Creating followers list...")
    followers = buffers.peoplePanel(self.parent.nb, self.parent, "followers", self.parent.twitter.twitter.get_followers_list, argumento=self.parent.db.settings["user_name"])
    self.parent.nb.InsertSubPage(self.parent.db.settings["buffers"].index(self.parent.db.settings["user_name"]), followers, _(u"Followers"))
    num = followers.start_streams()
    followers.put_items(num)
    self.parent.db.settings["buffers"].append("followers")
   elif self.buffers.followers.GetValue() == False:
    self.parent.nb.DeletePage(self.parent.db.settings["buffers"].index("followers"))
    self.parent.db.settings.pop("followers")
    self.parent.db.settings["buffers"].remove("followers")

 def check_friends_change(self):
  if self.buffers.friends.GetValue() != self.buffers.friends_value:
   if self.buffers.friends.GetValue() == True:
    log.debug("Creating friends list...")
    friends = buffers.peoplePanel(self.parent.nb, self.parent, "friends", self.parent.twitter.twitter.get_friends_list, argumento=self.parent.db.settings["user_name"])
    self.parent.nb.InsertSubPage(self.parent.db.settings["buffers"].index(self.parent.db.settings["user_name"]), friends, _(u"friends"))
    num = friends.start_streams()
    friends.put_items(num)
    self.parent.db.settings["buffers"].append("friends")
   elif self.buffers.friends.GetValue() == False:
    self.parent.nb.DeletePage(self.parent.db.settings["buffers"].index("friends"))
    self.parent.db.settings.pop("friends")
    self.parent.db.settings["buffers"].remove("friends")

 def check_favs_change(self):
  if self.buffers.favs.GetValue() != self.buffers.favs_value:
   if self.buffers.favs.GetValue() == True:
    log.debug("Creating favorites...")
    favs = buffers.basePanel(self.parent.nb, self.parent, "favs", self.parent.twitter.twitter.get_favorites)
    self.parent.nb.InsertSubPage(self.parent.db.settings["buffers"].index(self.parent.db.settings["user_name"]), favs, _(u"Favorites"))
    num = favs.start_streams()
    favs.put_items(num)
    self.parent.db.settings["buffers"].append("favs")
   elif self.buffers.favs.GetValue() == False:
    self.parent.nb.DeletePage(self.parent.db.settings["buffers"].index("favs"))
    self.parent.db.settings.pop("favs")
    self.parent.db.settings["buffers"].remove("favs")

 def check_events_change(self):
  if self.buffers.events.GetValue() != self.buffers.events_value:
   if self.buffers.events.GetValue() == True:
    log.debug("Creating events...")
    events = buffers.eventsPanel(self.parent.nb, self.parent)
    self.parent.nb.InsertSubPage(self.parent.db.settings["buffers"].index(self.parent.db.settings["user_name"]), events, _(u"Events"))
    self.parent.db.settings["buffers"].append("events")
   elif self.buffers.events.GetValue() == False:
    self.parent.nb.DeletePage(self.parent.db.settings["buffers"].index("events"))
    self.parent.db.settings["buffers"].remove("events")

 def check_blocks_change(self):
  if self.buffers.blocks.GetValue() != self.buffers.blocks_value:
   if self.buffers.blocks.GetValue() == True:
    log.debug("Creating blocked users list...")
    blocks = buffers.peoplePanel(self.parent.nb, self.parent, "blocks", self.parent.twitter.twitter.list_blocks)
    self.parent.nb.InsertSubPage(self.parent.db.settings["buffers"].index(self.parent.db.settings["user_name"]), blocks, _(u"Blocked users"))
    num = blocks.start_streams()
    blocks.put_items(num)
    self.parent.db.settings["buffers"].append("blocks")
   elif self.buffers.blocks.GetValue() == False:
    self.parent.nb.DeletePage(self.parent.db.settings["buffers"].index("blocks"))
    self.parent.db.settings.pop("blocks")
    self.parent.db.settings["buffers"].remove("blocks")

 def check_mutes_change(self):
  if self.buffers.mutes.GetValue() != self.buffers.mutes_value:
   if self.buffers.mutes.GetValue() == True:
    log.debug("Creating muted users list...")
    mutes = buffers.peoplePanel(self.parent.nb, self.parent, "muteds", self.parent.twitter.twitter.get_muted_users_list)
    self.parent.nb.InsertSubPage(self.parent.db.settings["buffers"].index(self.parent.db.settings["user_name"]), mutes, _(u"Muted users"))
    num = mutes.start_streams()
    mutes.put_items(num)
    self.parent.db.settings["buffers"].append("muteds")
   elif self.buffers.mutes.GetValue() == False:
    self.parent.nb.DeletePage(self.parent.db.settings["buffers"].index("muteds"))
    self.parent.db.settings.pop("muteds")
    self.parent.db.settings["buffers"].remove("muteds")

 def onSave(self, ev):
  need_restart = False
  # Check general settings
  if config.main["general"]["language"] != self.general.langs[self.general.language.GetSelection()][0]:
   if self.general.langs[self.general.language.GetSelection()][0] in self.general.codes: config.main["general"]["language"] = self.general.langs[self.general.language.GetSelection()][0]
   languageHandler.setLanguage(config.main["general"]["language"])
   need_restart = True
  if platform.system() == "Windows":
   config.main["general"]["voice_enabled"] = self.general.disable_sapi5.GetValue()
   config.main["general"]["ask_at_exit"] = self.general.ask_at_exit.GetValue()
   if (self.general.use_invisible_shorcuts.GetValue() == True and config.main["general"]["use_invisible_keyboard_shorcuts"] != True) and self.parent.showing == True:
    km = self.parent.create_invisible_keyboard_shorcuts()
    self.parent.register_invisible_keyboard_shorcuts(km)
   elif (self.general.use_invisible_shorcuts.GetValue() == False and config.main["general"]["use_invisible_keyboard_shorcuts"] != False) and self.parent.showing == True:
    km = self.parent.create_invisible_keyboard_shorcuts()
    self.parent.unregister_invisible_keyboard_shorcuts(km)
   config.main["general"]["use_invisible_keyboard_shorcuts"] = self.general.use_invisible_shorcuts.GetValue()
   config.main["general"]["hide_gui"] = self.general.show_gui.GetValue()
  config.main["general"]["max_api_calls"] = self.general.apiCalls.GetValue()
  config.main["general"]["max_tweets_per_call"] = self.general.itemsPerApiCall.GetValue()
  if config.main["general"]["relative_times"] != self.general.relative_time.GetValue():
   config.main["general"]["relative_times"] = self.general.relative_time.GetValue()
   need_restart = True
  if config.main["general"]["reverse_timelines"] != self.general.reverse_timelines.GetValue():
   config.main["general"]["reverse_timelines"] = self.general.reverse_timelines.GetValue()
   need_restart = True

  ## Check buffers settings
  config.main["other_buffers"]["show_followers"] = self.buffers.followers.GetValue()
  self.check_followers_change()
  config.main["other_buffers"]["show_friends"] = self.buffers.friends.GetValue()
  self.check_friends_change()
  config.main["other_buffers"]["show_favourites"] = self.buffers.favs.GetValue()
  self.check_favs_change()
  config.main["other_buffers"]["show_events"] = self.buffers.events.GetValue()
  self.check_events_change()
  config.main["other_buffers"]["show_blocks"] = self.buffers.blocks.GetValue()
  self.check_blocks_change()
  config.main["other_buffers"]["show_muted_users"] = self.buffers.mutes.GetValue()
  self.check_mutes_change()

  ## Check sound settings
  config.main["sound"]["volume"] = self.sound.volumeCtrl.GetValue()/100.0
  config.main["sound"]["global_mute"] = self.sound.global_mute.GetValue()
  if system == "Windows":
   config.main["sound"]["output_device"] = self.sound.output.GetStringSelection()
   config.main["sound"]["input_device"] = self.sound.input.GetValue()
   try:
    snd.player.input.set_device(snd.player.input.find_device_by_name(config.main["sound"]["input_device"]))
    snd.player.output.set_device(snd.player.output.find_device_by_name(config.main["sound"]["output_device"]))
   except:
    config.main["sound"]["output_device"] = "Default"
    config.main["sound"]["input_device"] = "Default"
  config.main["sound"]["sndup_api_key"] = self.services.apiKey.GetValue()
  config.main["sound"]["current_soundpack"] = self.sound.soundpack.GetStringSelection()
  snd.player.check_soundpack()
  if need_restart == True:
   config.main.write()
   wx.MessageDialog(None, _(u"The application requires to be restarted to save these changes. Press OK to do it now."), _("Restart TW Blue"), wx.OK).ShowModal()
   restart.restart_program()

  config.main.write()
  self.EndModal(wx.ID_OK)
