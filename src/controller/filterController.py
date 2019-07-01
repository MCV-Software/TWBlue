# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from builtins import object
import time
import widgetUtils
import application
from wxUI.dialogs import filterDialogs
from wxUI import commonMessageDialogs

class filter(object):
 def __init__(self, buffer, filter_title=None, if_word_exists=None, in_lang=None, regexp=None, word=None, in_buffer=None):
  self.buffer = buffer
  self.dialog = filterDialogs.filterDialog(languages=[i["name"] for i in application.supported_languages])
  if self.dialog.get_response()  == widgetUtils.OK:
   title = self.dialog.get("title")
   contains = self.dialog.get("contains")
   term = self.dialog.get("term")
   regexp = self.dialog.get("regexp")
   allow_rts = self.dialog.get("allow_rts")
   allow_quotes = self.dialog.get("allow_quotes")
   allow_replies = self.dialog.get("allow_replies")
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
   d = dict(in_buffer=self.buffer.name, word=term, regexp=regexp, in_lang=lang_option, languages=langcodes, if_word_exists=contains, allow_rts=allow_rts, allow_quotes=allow_quotes, allow_replies=allow_replies)
   if title in self.buffer.session.settings["filters"]:
    return commonMessageDialogs.existing_filter()
   self.buffer.session.settings["filters"][title] = d
   self.buffer.session.settings.write()

class filterManager(object):

 def __init__(self, session):
  self.session = session
  self.dialog = filterDialogs.filterManagerDialog()
  self.insert_filters(self.session.settings["filters"])
  if self.dialog.filters.get_count() == 0:
   self.dialog.edit.Enable(False)
   self.dialog.delete.Enable(False)
  else:
   widgetUtils.connect_event(self.dialog.edit, widgetUtils.BUTTON_PRESSED, self.edit_filter)
   widgetUtils.connect_event(self.dialog.delete, widgetUtils.BUTTON_PRESSED, self.delete_filter)
  response = self.dialog.get_response()

 def insert_filters(self, filters):
  self.dialog.filters.clear()
  for f in list(filters.keys()):
   filterName = f
   buffer = filters[f]["in_buffer"]
   if filters[f]["if_word_exists"] == "True" and filters[f]["word"] != "":
    filter_by_word = "True"
   else:
    filter_by_word = "False"
   filter_by_lang = ""
   if filters[f]["in_lang"] != "None":
    filter_by_lang = "True"
   b = [f, buffer, filter_by_word, filter_by_lang]
   self.dialog.filters.insert_item(False, *b)

 def edit_filter(self, *args, **kwargs):
  pass

 def delete_filter(self, *args, **kwargs):
  filter_title = self.dialog.filters.get_text_column(self.dialog.filters.get_selected(), 0)
  response = commonMessageDialogs.delete_filter()
  if response == widgetUtils.YES:
   self.session.settings["filters"].pop(filter_title)
   self.session.settings.write()
   self.insert_filters(self.session.settings["filters"])