# -*- coding: utf-8 -*-
import time
import widgetUtils
import application
from wxUI.dialogs import filterDialogs

class filter(object):
 def __init__(self, buffer):
  self.buffer = buffer
  self.dialog = filterDialogs.filterDialog(languages=[i["name"] for i in application.supported_languages])
  if self.dialog.get_response()  == widgetUtils.OK:
   contains = self.dialog.get("contains")
   term = self.dialog.get("term")
   regexp = self.dialog.get("regexp")
   load_language = self.dialog.get("load_language")
   ignore_language = self.dialog.get("ignore_language")
   lang_option = None
   if ignore_language:
    lang_option = False
   elif load_language:
    lang_option = True
   langs = self.dialog.get_selected_langs()
   langcodes = []
   for i in application.supported_languages:
    if i["name"] in langs:
     langcodes.append(i["code"])
   d = dict(in_buffer=self.buffer.name, word=term, regexp=regexp, in_lang=lang_option, languages=langcodes, if_word_exists=contains)
   filter_title = "filter_{0}".format(str(time.time()))
   self.buffer.session.settings["filters"][filter_title] = d
   self.buffer.session.settings.write()