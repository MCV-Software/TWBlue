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

class spellCheckerDialog(wx.Dialog):
 def __init__(self):
  super(spellCheckerDialog, self).__init__(None, 1)
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
  self.ignore = wx.Button(panel, -1, _(u"Ignore"))
  self.ignoreAll = wx.Button(panel, -1, _(u"Ignore all"))
  self.replace = wx.Button(panel, -1, _(u"Replace"))
  self.replaceAll = wx.Button(panel, -1, _(u"Replace all"))
  close = wx.Button(panel, wx.ID_CANCEL)
  btnBox = wx.BoxSizer(wx.HORIZONTAL)
  btnBox.Add(self.ignore)
  btnBox.Add(self.ignoreAll)
  btnBox.Add(self.replace)
  btnBox.Add(self.replaceAll)
  btnBox.Add(close)
  sizer.Add(wordBox)
  sizer.Add(contextBox)
  sizer.Add(suggestionsBox)
  sizer.Add(btnBox)
  panel.SetSizerAndFit(sizer)


 def get_response(self):
  return self.ShowModal()

 def set_title(self, title):
  return self.SetTitle(title)

 def set_word_and_suggestions(self, word, context, suggestions):
  self.word.SetValue(word)
  self.context.ChangeValue(context)
  self.suggestions.Set(suggestions)
  self.suggestions.SetFocus()

 def get_selected_suggestion(self):
  return self.suggestions.GetStringSelection()

def dict_not_found_error():
 wx.MessageDialog(None, _(u"A bug has happened. There are no dictionaries available for the selected language in TW Blue"), _(u"Error"), wx.ICON_ERROR).ShowModal()

def finished():
 wx.MessageDialog(None, _(u"The spelling review has finished."), _("Finished"), style=wx.OK).ShowModal()
