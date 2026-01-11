# -*- coding: utf-8 -*-
import os
import logging
import paths
import config
import languageHandler
import application
from pubsub import pub
from wxUI.dialogs import configuration
from wxUI import commonMessageDialogs

log = logging.getLogger("Settings")

class globalSettingsController(object):
    def __init__(self):
        super(globalSettingsController, self).__init__()
        self.dialog = configuration.configurationDialog()
        self.create_config()
        self.needs_restart = False
        self.is_started = True

    def make_kmmap(self):
        res={}
        for i in os.listdir(os.path.join(paths.app_path(), 'keymaps')):
            if ".keymap" not in i:
                continue
            try:
                res[i[:-7]] =i
            except:
                log.exception("Exception while loading keymap " + i)
        return res

    def create_config(self):
        self.kmmap=self.make_kmmap()
        self.langs = languageHandler.getAvailableLanguages()
        langs = []
        [langs.append(i[1]) for i in self.langs]
        self.codes = []
        [self.codes.append(i[0]) for i in self.langs]
        id = self.codes.index(config.app["app-settings"]["language"])
        self.kmfriendlies=[]
        self.kmnames=[]
        for k,v in list(self.kmmap.items()):
            self.kmfriendlies.append(k)
            self.kmnames.append(v)
        self.kmid=self.kmnames.index(config.app['app-settings']['load_keymap'])
        self.dialog.create_general(langs,self.kmfriendlies)
        self.dialog.general.language.SetSelection(id)
        self.dialog.general.km.SetSelection(self.kmid)
        self.dialog.set_value("general", "ask_at_exit", config.app["app-settings"]["ask_at_exit"])
        self.dialog.set_value("general", "no_streaming", config.app["app-settings"]["no_streaming"])
        self.dialog.set_value("general", "play_ready_sound", config.app["app-settings"]["play_ready_sound"])
        self.dialog.set_value("general", "speak_ready_msg", config.app["app-settings"]["speak_ready_msg"])
        self.dialog.set_value("general", "read_long_posts_in_gui", config.app["app-settings"]["read_long_posts_in_gui"])
        self.dialog.set_value("general", "use_invisible_shorcuts", config.app["app-settings"]["use_invisible_keyboard_shorcuts"])
        self.dialog.set_value("general", "disable_sapi5", config.app["app-settings"]["voice_enabled"])
        self.dialog.set_value("general", "hide_gui", config.app["app-settings"]["hide_gui"])  
        self.dialog.set_value("general", "update_period", config.app["app-settings"]["update_period"])
        self.dialog.set_value("general", "check_for_updates", config.app["app-settings"]["check_for_updates"])
        proxyTypes = [_("System default"), _("HTTP"), _("SOCKS v4"), _("SOCKS v4 with DNS support"), _("SOCKS v5"), _("SOCKS v5 with DNS support")]
        self.dialog.create_proxy(proxyTypes)
        try:
            self.dialog.proxy.type.SetSelection(config.app["proxy"]["type"])
        except:
            self.dialog.proxy.type.SetSelection(0)
        self.dialog.set_value("proxy", "server", config.app["proxy"]["server"])
        self.dialog.set_value("proxy", "port", config.app["proxy"]["port"])
        self.dialog.set_value("proxy", "user", config.app["proxy"]["user"])
        self.dialog.set_value("proxy", "password", config.app["proxy"]["password"])
        self.dialog.create_translator_panel()
        self.dialog.set_value("translator_panel", "libre_api_url", config.app["translator"]["lt_api_url"])
        self.dialog.set_value("translator_panel", "libre_api_key", config.app["translator"]["lt_api_key"])
        self.dialog.set_value("translator_panel", "deepL_api_key", config.app["translator"]["deepl_api_key"])
        self.dialog.realize()
        self.response = self.dialog.get_response()

    def save_configuration(self):
        if self.codes[self.dialog.general.language.GetSelection()] != config.app["app-settings"]["language"]:
            config.app["app-settings"]["language"] = self.codes[self.dialog.general.language.GetSelection()]
            languageHandler.setLanguage(config.app["app-settings"]["language"])
            self.needs_restart = True
            log.debug("Triggered app restart due to interface language changes.")
        if self.kmnames[self.dialog.general.km.GetSelection()] != config.app["app-settings"]["load_keymap"]:
            config.app["app-settings"]["load_keymap"] =self.kmnames[self.dialog.general.km.GetSelection()]
            kmFile = open(os.path.join(paths.config_path(), "keymap.keymap"), "w")
            kmFile.close()
            log.debug("Triggered app restart due to a keymap change.")
            self.needs_restart = True
        if config.app["app-settings"]["use_invisible_keyboard_shorcuts"] != self.dialog.get_value("general", "use_invisible_shorcuts"):
            config.app["app-settings"]["use_invisible_keyboard_shorcuts"] = self.dialog.get_value("general", "use_invisible_shorcuts")
            pub.sendMessage("invisible-shorcuts-changed", registered=self.dialog.get_value("general", "use_invisible_shorcuts"))
        if config.app["app-settings"]["no_streaming"] != self.dialog.get_value("general", "no_streaming"):
            config.app["app-settings"]["no_streaming"] = self.dialog.get_value("general", "no_streaming")
            self.needs_restart = True
            log.debug("Triggered app restart due to change in streaming availability.")
        if config.app["app-settings"]["update_period"] != self.dialog.get_value("general", "update_period"):
            config.app["app-settings"]["update_period"] = self.dialog.get_value("general", "update_period")
            self.needs_restart = True
            log.debug("Triggered app restart due to changes in update period.")
        config.app["app-settings"]["voice_enabled"] = self.dialog.get_value("general", "disable_sapi5")
        config.app["app-settings"]["hide_gui"] = self.dialog.get_value("general", "hide_gui")
        config.app["app-settings"]["ask_at_exit"] = self.dialog.get_value("general", "ask_at_exit")
        config.app["app-settings"]["read_long_posts_in_gui"] = self.dialog.get_value("general", "read_long_posts_in_gui")
        config.app["app-settings"]["play_ready_sound"] = self.dialog.get_value("general", "play_ready_sound")
        config.app["app-settings"]["speak_ready_msg"] = self.dialog.get_value("general", "speak_ready_msg")
        config.app["app-settings"]["check_for_updates"] = self.dialog.get_value("general", "check_for_updates")
        if config.app["proxy"]["type"]!=self.dialog.get_value("proxy", "type") or config.app["proxy"]["server"] != self.dialog.get_value("proxy", "server") or config.app["proxy"]["port"] != self.dialog.get_value("proxy", "port") or config.app["proxy"]["user"] != self.dialog.get_value("proxy", "user") or config.app["proxy"]["password"] != self.dialog.get_value("proxy", "password"):
            if self.is_started == True:
                self.needs_restart = True
                log.debug("Triggered app restart due to change in proxy settings.")
            config.app["proxy"]["type"] = self.dialog.proxy.type.Selection
            config.app["proxy"]["server"] = self.dialog.get_value("proxy", "server")
            config.app["proxy"]["port"] = self.dialog.get_value("proxy", "port")
            config.app["proxy"]["user"] = self.dialog.get_value("proxy", "user")
            config.app["proxy"]["password"] = self.dialog.get_value("proxy", "password")
        config.app["translator"]["lt_api_url"] = self.dialog.get_value("translator_panel", "libre_api_url")
        config.app["translator"]["lt_api_key"] = self.dialog.get_value("translator_panel", "libre_api_key")
        config.app["translator"]["deepl_api_key"] = self.dialog.get_value("translator_panel", "deepL_api_key")
        config.app.write()
