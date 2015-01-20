# -*- coding: utf-8 -*-
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