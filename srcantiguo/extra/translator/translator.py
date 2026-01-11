# -*- coding: utf-8 -*-
import logging
import threading
import wx
import config
from pubsub import pub
from . engines import libre_translate, deep_l
from .wx_ui import translateDialog

log = logging.getLogger("extras.translator")

class TranslatorController(object):
    def __init__(self, text):
        super(TranslatorController, self).__init__()
        self.text = text
        self.languages = []
        self.response = False
        self.dialog = translateDialog()
        pub.subscribe(self.on_engine_changed, "translator.engine_changed")
        if config.app["translator"]["engine"] == "LibreTranslate":
            self.dialog.engine_select.SetSelection(0)
        elif config.app["translator"]["engine"] == "DeepL":
            self.dialog.engine_select.SetSelection(1)
        threading.Thread(target=self.load_languages).start()
        if self.dialog.ShowModal() == wx.ID_OK:
            self.response = True
            for k in self.language_dict:
                if self.language_dict[k] == self.dialog.dest_lang.GetStringSelection():
                    self.target_language= k
        pub.unsubscribe(self.on_engine_changed, "translator.engine_changed")

    def load_languages(self):
        self.language_dict = self.get_languages()
        self.languages = [self.language_dict[k] for k in self.language_dict]
        self.dialog.set_languages(self.languages)

    def on_engine_changed(self, engine):
        config.app["translator"]["engine"] = engine
        config.app.write()
        threading.Thread(target=self.load_languages).start()

    def translate(self):
        log.debug("Received translation request for language %s, text=%s" % (self.target_language, self.text))
        if config.app["translator"].get("engine") == "LibreTranslate":
            translator = libre_translate.CustomLibreTranslateAPI(config.app["translator"]["lt_api_url"], config.app["translator"]["lt_api_key"])
            vars = dict(q=self.text, target=self.target_language)
            return translator.translate(**vars)
        elif config.app["translator"]["engine"] == "DeepL" and config.app["translator"]["deepl_api_key"] != "":
            return deep_l.translate(text=self.text, target_language=self.target_language)

    def get_languages(self):
        languages = {}
        if config.app["translator"].get("engine") == "LibreTranslate":
            translator = libre_translate.CustomLibreTranslateAPI(config.app["translator"]["lt_api_url"], config.app["translator"]["lt_api_key"])
            languages = {l.get("code"): l.get("name") for l in translator.languages()}
        elif config.app["translator"]["engine"] == "DeepL" and config.app["translator"]["deepl_api_key"] != "":
            languages = {language.code: language.name for language in deep_l.languages()}
        return dict(sorted(languages.items(), key=lambda x: x[1]))
