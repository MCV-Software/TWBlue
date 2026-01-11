# -*- coding: utf-8 -*-
import config
from deepl import Translator

def translate(text: str, target_language: str) -> str:
    key = config.app["translator"]["deepl_api_key"]
    t = Translator(key)
    return t.translate_text(text, target_lang=target_language).text

def languages():
    key = config.app["translator"]["deepl_api_key"]
    t = Translator(key)
    langs = t.get_target_languages()
    return langs