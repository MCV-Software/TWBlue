# -*- coding: utf-8 -*-
import os
import sound_lib
import paths
import widgetUtils
import config
import languageHandler
from wxUI.dialogs import configuration
from pubsub import pub
import logging
log = logging.getLogger("Settings")

class globalSettingsController(object):
 def __init__(self):
  super(globalSettingsController, self).__init__()
  self.dialog = configuration.configurationDialog()
  self.create_config()

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
  self.needs_restart = False
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
  config.app.write()

class accountSettingsController(globalSettingsController):
 def __init__(self, config, user_name):
  self.config = config
  self.user = user_name
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
  self.input_devices = sound_lib.input.Input.get_device_names()
  self.output_devices = sound_lib.output.Output.get_device_names()
  self.soundpacks = []
  [self.soundpacks.append(i) for i in os.listdir(paths.sound_path()) if os.path.isdir(paths.sound_path(i)) == True ]
  self.dialog.create_sound(self.input_devices, self.output_devices, self.soundpacks)
  self.dialog.set_value("sound", "volumeCtrl", self.config["sound"]["volume"])
  self.dialog.set_value("sound", "input", self.config["sound"]["input_device"])
  self.dialog.set_value("sound", "output", self.config["sound"]["output_device"])
  self.dialog.set_value("sound", "global_mute", self.config["sound"]["global_mute"])
  self.dialog.set_value("sound", "soundpack", self.config["sound"]["current_soundpack"])
  self.dialog.create_audio_services()
  self.dialog.realize()
  self.dialog.set_title(_(u"Account settings for %s") % (self.user,))
  self.response = self.dialog.get_response()

 def save_config(self): pass
 def manage_autocomplete(self, *args, **kwargs): pass