# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import logging
from . import wx_ui
import widgetUtils
import output
import config
import languageHandler
import enchant
import paths
from . import twitterFilter
from enchant.checker import SpellChecker
from enchant.errors import DictNotFoundError
from enchant import tokenize
log = logging.getLogger("extra.SpellChecker.spellChecker")

class spellChecker(object):
 def __init__(self, text, dictionary):
  super(spellChecker, self).__init__()
  # Set Dictionary path if not set in a previous call to this method.
  # Dictionary path will be located in user config, see https://github.com/manuelcortez/twblue/issues/208
  dict_path = enchant.get_param("enchant.myspell.dictionary.path")
  if dict_path == None:
   enchant.set_param("enchant.myspell.dictionary.path", os.path.join(paths.config_path(), "dicts"))
   log.debug("Dictionary path set to %s" % (os.path.join(paths.config_path(), "dicts"),))
  log.debug("Creating the SpellChecker object. Dictionary: %s" % (dictionary,))
  self.active = True
  try:
   if config.app["app-settings"]["language"] == "system":
    log.debug("Using the system language")
    self.dict = enchant.DictWithPWL(languageHandler.curLang[:2], paths.config_path("wordlist.dict"))
   else:
    log.debug("Using language: %s" % (languageHandler.getLanguage(),))
    self.dict = enchant.DictWithPWL(languageHandler.getLanguage()[:2], paths.config_path("wordlist.dict"))
  except DictNotFoundError:
   log.exception("Dictionary for language %s not found." % (dictionary,))
   wx_ui.dict_not_found_error()
   self.active = False
  self.checker = SpellChecker(self.dict, filters=[twitterFilter.TwitterFilter, tokenize.EmailFilter, tokenize.URLFilter])
  self.checker.set_text(text)
  if self.active == True:
   log.debug("Creating dialog...")
   self.dialog = wx_ui.spellCheckerDialog()
   widgetUtils.connect_event(self.dialog.ignore, widgetUtils.BUTTON_PRESSED, self.ignore)
   widgetUtils.connect_event(self.dialog.ignoreAll, widgetUtils.BUTTON_PRESSED, self.ignoreAll)
   widgetUtils.connect_event(self.dialog.replace, widgetUtils.BUTTON_PRESSED, self.replace)
   widgetUtils.connect_event(self.dialog.replaceAll, widgetUtils.BUTTON_PRESSED, self.replaceAll)
   widgetUtils.connect_event(self.dialog.add, widgetUtils.BUTTON_PRESSED, self.add)
   self.check()
   self.dialog.get_response()
   self.fixed_text = self.checker.get_text()

 def check(self):
  try:
   next(self.checker)
   textToSay = _(u"Misspelled word: %s") % (self.checker.word,)
   context = u"... %s %s %s" % (self.checker.leading_context(10), self.checker.word, self.checker.trailing_context(10))
   self.dialog.set_title(textToSay)
   output.speak(textToSay)
   self.dialog.set_word_and_suggestions(word=self.checker.word, context=context, suggestions=self.checker.suggest())
  except StopIteration:
   log.debug("Process finished.")
   wx_ui.finished()
   self.dialog.Destroy()

 def ignore(self, ev):
  self.check()

 def ignoreAll(self, ev):
  self.checker.ignore_always(word=self.checker.word)
  self.check()

 def replace(self, ev):
  self.checker.replace(self.dialog.get_selected_suggestion())
  self.check()

 def replaceAll(self, ev):
  self.checker.replace_always(self.dialog.get_selected_suggestion())
  self.check()

 def add(self, ev):
  self.checker.add()
  self.check()
