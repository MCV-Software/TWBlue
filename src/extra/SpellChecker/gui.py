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
import output
import config
import languageHandler
from enchant.checker import SpellChecker
from enchant.errors import DictNotFoundError

class spellCheckerDialog(wx.Dialog):
 def __init__(self, text, dictionary):
  super(spellCheckerDialog, self).__init__(None, 1)
  try:
   if config.main["general"]["language"] == "system": self.checker = SpellChecker()
   else: self.checker = SpellChecker(languageHandler.getLanguage())
   self.checker.set_text(text)
  except DictNotFoundError:
   wx.MessageDialog(None, _(u"A bug has happened. There are no dictionaries available for the selected language in TW Blue"), _(u"Error"), wx.ICON_ERROR).ShowModal()
   self.Destroy()
  panel = wx.Panel(self)
  sizer = wx.BoxSizer(wx.VERTICAL)
  word = wx.StaticText(panel, -1, _(u"Mis-spelled word"))
  self.word = wx.TextCtrl(panel, -1)
  wordBox = wx.BoxSizer(wx.HORIZONTAL)
  wordBox.Add(word)
  wordBox.Add(self.word)
  context = wx.StaticText(panel, -1, _(u"Context"))
  self.context = wx.TextCtrl(panel, -1)
  contextBox = wx.BoxSizer(wx.HORIZONTAL)
  contextBox.Add(context)
  contextBox.Add(self.context)
  suggest = wx.StaticText(panel, -1, _(u"Suggestions"))
  self.suggestions = wx.ListBox(panel, -1, choices=[], style=wx.LB_SINGLE)
  suggestionsBox = wx.BoxSizer(wx.HORIZONTAL)
  suggestionsBox.Add(suggest)
  suggestionsBox.Add(self.suggestions)
  ignore = wx.Button(panel, -1, _(u"Ignore"))
  self.Bind(wx.EVT_BUTTON, self.onIgnore, ignore)
  ignoreAll = wx.Button(panel, -1, _(u"Ignore all"))
  self.Bind(wx.EVT_BUTTON, self.onIgnoreAll, ignoreAll)
  replace = wx.Button(panel, -1, _(u"Replace"))
  self.Bind(wx.EVT_BUTTON, self.onReplace, replace)
  replaceAll = wx.Button(panel, -1, _(u"Replace all"))
  self.Bind(wx.EVT_BUTTON, self.onReplaceAll, replaceAll)
  close = wx.Button(panel, wx.ID_CANCEL)
  btnBox = wx.BoxSizer(wx.HORIZONTAL)
  btnBox.Add(ignore)
  btnBox.Add(ignoreAll)
  btnBox.Add(replace)
  btnBox.Add(replaceAll)
  btnBox.Add(close)
  sizer.Add(wordBox)
  sizer.Add(contextBox)
  sizer.Add(suggestionsBox)
  sizer.Add(btnBox)
  panel.SetSizerAndFit(sizer)
  self.check()

 def check(self):
  try:
   self.checker.next()
   textToSay = _(u"Mis-spelled word: %s") % (self.checker.word,)
   context = u"... %s %s %s" % (self.checker.leading_context(10), self.checker.word, self.checker.trailing_context(10))
   self.SetTitle(textToSay)
   output.speak(textToSay)
   self.word.SetValue(self.checker.word)
   self.context.ChangeValue(context)
   self.suggestions.Set(self.checker.suggest())
   self.suggestions.SetFocus()
  except StopIteration:
   wx.MessageDialog(self, _(u"The spelling review has finished."), _("Finished"), style=wx.OK).ShowModal()
   self.EndModal(wx.ID_OK)
  except AttributeError:
   pass

 def onIgnore(self, ev):
  self.check()

 def onIgnoreAll(self, ev):
  self.checker.ignore_always(word=self.checker.word)
  self.check()

 def onReplace(self, ev):
  self.checker.replace(self.suggestions.GetStringSelection())
  self.check()

 def onReplaceAll(self, ev):
  self.checker.replace_always(self.suggestions.GetStringSelection())
  self.check()