# -*- coding: utf-8 -*-
import os
import webbrowser
import sound_lib
import paths
import widgetUtils
import config
import languageHandler
from wxUI.dialogs import configuration
from wxUI import commonMessageDialogs
from extra.autocompletionUsers import settings
from extra.AudioUploader import dropbox_transfer
from pubsub import pub
import logging
log = logging.getLogger("Settings")

class globalSettingsController(object):
 def __init__(self):
  super(globalSettingsController, self).__init__()
  self.dialog = configuration.configurationDialog()
  self.create_config()
  self.needs_restart = False

 def create_config(self):
  self.langs = languageHandler.getAvailableLanguages()
  langs = []
  [langs.append(i[1]) for i in self.langs]
  self.codes = []
  [self.codes.append(i[0]) for i in self.langs]
  id = self.codes.index(config.app["app-settings"]["language"])
  self.dialog.create_general(langs)
  self.dialog.general.language.SetSelection(id)
  self.dialog.set_value("general", "ask_at_exit", config.app["app-settings"]["ask_at_exit"])
  self.dialog.set_value("general", "use_invisible_shorcuts", config.app["app-settings"]["use_invisible_keyboard_shorcuts"])
  self.dialog.set_value("general", "disable_sapi5", config.app["app-settings"]["voice_enabled"])
  self.dialog.set_value("general", "hide_gui", config.app["app-settings"]["hide_gui"])  
  self.dialog.realize()
  self.response = self.dialog.get_response()

 def save_configuration(self):
  if self.codes[self.dialog.general.language.GetSelection()] != config.app["app-settings"]["language"]:
   config.app["app-settings"]["language"] = self.codes[self.dialog.general.language.GetSelection()]
   languageHandler.setLanguage(config.app["app-settings"]["language"])
   self.needs_restart = True
  if config.app["app-settings"]["use_invisible_keyboard_shorcuts"] != self.dialog.get_value("general", "use_invisible_shorcuts"):
   config.app["app-settings"]["use_invisible_keyboard_shorcuts"] = self.dialog.get_value("general", "use_invisible_shorcuts")
   pub.sendMessage("invisible-shorcuts-changed", registered=self.dialog.get_value("general", "use_invisible_shorcuts"))
  config.app["app-settings"]["voice_enabled"] = self.dialog.get_value("general", "disable_sapi5")
  config.app["app-settings"]["hide_gui"] = self.dialog.get_value("general", "hide_gui")
  config.app["app-settings"]["ask_at_exit"] = self.dialog.get_value("general", "ask_at_exit")
  config.app.write()

class accountSettingsController(globalSettingsController):
 def __init__(self, buffer, window):
  self.user = buffer.session.db["user_name"]
  self.buffer = buffer
  self.window = window
  self.config = buffer.session.settings
  super(accountSettingsController, self).__init__()

 def create_config(self):
  self.dialog.create_general_account()
  widgetUtils.connect_event(self.dialog.general.au, widgetUtils.BUTTON_PRESSED, self.manage_autocomplete)
  self.dialog.set_value("general", "relative_time", self.config["general"]["relative_times"])
  self.dialog.set_value("general", "apiCalls", self.config["general"]["max_api_calls"])
  self.dialog.set_value("general", "itemsPerApiCall", self.config["general"]["max_tweets_per_call"])
  self.dialog.set_value("general", "reverse_timelines", self.config["general"]["reverse_timelines"])
  self.dialog.create_other_buffers()
  self.dialog.set_value("buffers", "followers", self.config["other_buffers"]["show_followers"])
  self.dialog.set_value("buffers", "friends", self.config["other_buffers"]["show_friends"])
  self.dialog.set_value("buffers", "favs", self.config["other_buffers"]["show_favourites"])
  self.dialog.set_value("buffers", "blocks", self.config["other_buffers"]["show_blocks"])
  self.dialog.set_value("buffers", "mutes", self.config["other_buffers"]["show_muted_users"])
  self.dialog.set_value("buffers", "events", self.config["other_buffers"]["show_events"])
  self.dialog.create_ignored_clients(self.config["twitter"]["ignored_clients"])
  widgetUtils.connect_event(self.dialog.ignored_clients.add, widgetUtils.BUTTON_PRESSED, self.add_ignored_client)
  widgetUtils.connect_event(self.dialog.ignored_clients.remove, widgetUtils.BUTTON_PRESSED, self.remove_ignored_client)
  self.input_devices = sound_lib.input.Input.get_device_names()
  self.output_devices = sound_lib.output.Output.get_device_names()
  self.soundpacks = []
  [self.soundpacks.append(i) for i in os.listdir(paths.sound_path()) if os.path.isdir(paths.sound_path(i)) == True ]
  self.dialog.create_sound(self.input_devices, self.output_devices, self.soundpacks)
  self.dialog.set_value("sound", "volumeCtrl", self.config["sound"]["volume"]*100)
  self.dialog.set_value("sound", "input", self.config["sound"]["input_device"])
  self.dialog.set_value("sound", "output", self.config["sound"]["output_device"])
  self.dialog.set_value("sound", "session_mute", self.config["sound"]["session_mute"])
  self.dialog.set_value("sound", "soundpack", self.config["sound"]["current_soundpack"])
  self.dialog.create_audio_services()
  if self.config["services"]["dropbox_token"] == "":
   self.dialog.services.set_dropbox(False)
  else:
   self.dialog.services.set_dropbox(True)
  widgetUtils.connect_event(self.dialog.services.dropbox, widgetUtils.BUTTON_PRESSED, self.manage_dropbox)
  self.dialog.set_value("services", "apiKey", self.config["sound"]["sndup_api_key"])
  self.dialog.realize()
  self.dialog.set_title(_(u"Account settings for %s") % (self.user,))
  self.response = self.dialog.get_response()

 def save_configuration(self):
  if self.config["general"]["relative_times"] != self.dialog.get_value("general", "relative_time"):
   self.needs_restart = True
   self.config["general"]["relative_times"] = self.dialog.get_value("general", "relative_time")
  self.config["general"]["max_api_calls"] = self.dialog.get_value("general", "apiCalls")
  self.config["general"]["max_tweets_per_call"] = self.dialog.get_value("general", "itemsPerApiCall")
  if self.config["general"]["reverse_timelines"] != self.dialog.get_value("general", "reverse_timelines"):
   self.needs_restart = True
   self.config["general"]["reverse_timelines"] = self.dialog.get_value("general", "reverse_timelines")
  if self.config["other_buffers"]["show_followers"] != self.dialog.get_value("buffers", "followers"):
   self.config["other_buffers"]["show_followers"] = self.dialog.get_value("buffers", "followers")
   pub.sendMessage("create-new-buffer", buffer="followers", account=self.user, create=self.config["other_buffers"]["show_followers"])
  if self.config["other_buffers"]["show_friends"] != self.dialog.get_value("buffers", "friends"):
   self.config["other_buffers"]["show_friends"] = self.dialog.get_value("buffers", "friends")
   pub.sendMessage("create-new-buffer", buffer="friends", account=self.user, create=self.config["other_buffers"]["show_friends"])
  if self.config["other_buffers"]["show_favourites"] != self.dialog.get_value("buffers", "favs"):
   self.config["other_buffers"]["show_favourites"] = self.dialog.get_value("buffers", "favs")
   pub.sendMessage("create-new-buffer", buffer="favourites", account=self.user, create=self.config["other_buffers"]["show_favourites"])
  if self.config["other_buffers"]["show_blocks"] != self.dialog.get_value("buffers", "blocks"):
   self.config["other_buffers"]["show_blocks"] = self.dialog.get_value("buffers", "blocks")
   pub.sendMessage("create-new-buffer", buffer="blocked", account=self.user, create=self.config["other_buffers"]["show_blocks"])
  if self.config["other_buffers"]["show_muted_users"] != self.dialog.get_value("buffers", "mutes"):
   self.config["other_buffers"]["show_muted_users"] = self.dialog.get_value("buffers", "mutes")
   pub.sendMessage("create-new-buffer", buffer="muted", account=self.user, create=self.config["other_buffers"]["show_muted_users"])
  if self.config["other_buffers"]["show_events"] != self.dialog.get_value("buffers", "events"):
   self.config["other_buffers"]["show_events"] = self.dialog.get_value("buffers", "events")
   pub.sendMessage("create-new-buffer", buffer="events", account=self.user, create=self.config["other_buffers"]["show_events"])
  if self.config["sound"]["input_device"] != self.dialog.sound.get("input"):
   self.config["sound"]["input_device"] = self.dialog.sound.get("input")
   try:
    self.buffer.session.sound.input.set_device(self.buffer.session.sound.input.find_device_by_name(self.config["sound"]["input_device"]))
   except:
    self.config["sound"]["input_device"] = "default"
  if self.config["sound"]["output_device"] != self.dialog.sound.get("output"):
   self.config["sound"]["output_device"] = self.dialog.sound.get("output")
   try:
    self.buffer.session.sound.output.set_device(self.buffer.session.sound.output.find_device_by_name(self.config["sound"]["output_device"]))
   except:
    self.config["sound"]["output_device"] = "default"
  self.config["sound"]["volume"] = self.dialog.get_value("sound", "volumeCtrl")/100.0
  self.config["sound"]["session_mute"] = self.dialog.get_value("sound", "session_mute")
  self.config["sound"]["current_soundpack"] = self.dialog.sound.get("soundpack")
  self.buffer.session.sound.config = self.config["sound"]
  self.buffer.session.sound.check_soundpack()
  self.config["sound"]["sndup_api_key"] = self.dialog.get_value("services", "apiKey")


 def manage_autocomplete(self, *args, **kwargs):
  configuration = settings.autocompletionSettings(self.buffer.session.settings, self.buffer, self.window)

 def add_ignored_client(self, *args, **kwargs):
  client = commonMessageDialogs.get_ignored_client()
  if client == None: return
  if client not in self.config["twitter"]["ignored_clients"]:
   self.config["twitter"]["ignored_clients"].append(client)
   self.dialog.ignored_clients.append(client)

 def remove_ignored_client(self, *args, **kwargs):
  if self.dialog.ignored_clients.get_clients() == 0: return
  id = self.dialog.ignored_clients.get_client_id()
  self.config["twitter"]["ignored_clients"].pop(id)
  self.dialog.ignored_clients.remove_(id)

 def manage_dropbox(self, *args, **kwargs):
  if self.dialog.services.get_dropbox() == _(u"Link your Dropbox account"):
   self.connect_dropbox()
  else:
   self.disconnect_dropbox()

 def connect_dropbox(self):
  auth = dropbox_transfer.dropboxLogin(self.config)
  url = auth.get_url()
  self.dialog.services.show_dialog()
  webbrowser.open(url)
  resp = self.dialog.services.get_response()
  if resp == "":
   self.dialog.services.set_dropbox(False)
  else:
   try:
    auth.authorise(resp)
    self.dialog.services.set_dropbox()
   except:
    self.dialog.services.show_error()
    self.dialog.services.set_dropbox(False)

 def disconnect_dropbox(self):
  self.config["services"]["dropbox_token"] = ""
  self.dialog.services.set_dropbox(False)
