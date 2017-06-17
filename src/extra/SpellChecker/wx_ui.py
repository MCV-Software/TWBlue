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
import application
class spellCheckerDialog(wx.Dialog):
 def __init__(self):
  super(spellCheckerDialog, self).__init__(None, 1)
  panel = wx.Panel(self)
  sizer = wx.BoxSizer(wx.VERTICAL)
  word = wx.StaticText(panel, -1, _("Misspelled word"))
  self.word = wx.TextCtrl(panel, -1)
  wordBox = wx.BoxSizer(wx.HORIZONTAL)
  wordBox.Add(word, 0, wx.ALL, 5)
  wordBox.Add(self.word, 0, wx.ALL, 5)
  context = wx.StaticText(panel, -1, _("Context"))
  self.context = wx.TextCtrl(panel, -1)
  contextBox = wx.BoxSizer(wx.HORIZONTAL)
  contextBox.Add(context, 0, wx.ALL, 5)
  contextBox.Add(self.context, 0, wx.ALL, 5)
  suggest = wx.StaticText(panel, -1, _("Suggestions"))
  self.suggestions = wx.ListBox(panel, -1, choices=[], style=wx.LB_SINGLE)
  suggestionsBox = wx.BoxSizer(wx.HORIZONTAL)
  suggestionsBox.Add(suggest, 0, wx.ALL, 5)
  suggestionsBox.Add(self.suggestions, 0, wx.ALL, 5)
  self.ignore = wx.Button(panel, -1, _("Ignore"))
  self.ignoreAll = wx.Button(panel, -1, _("Ignore all"))
  self.replace = wx.Button(panel, -1, _("Replace"))
  self.replaceAll = wx.Button(panel, -1, _("Replace all"))
  close = wx.Button(panel, wx.ID_CANCEL)
  btnBox = wx.BoxSizer(wx.HORIZONTAL)
  btnBox.Add(self.ignore, 0, wx.ALL, 5)
  btnBox.Add(self.ignoreAll, 0, wx.ALL, 5)
  btnBox.Add(self.replace, 0, wx.ALL, 5)
  btnBox.Add(self.replaceAll, 0, wx.ALL, 5)
  btnBox.Add(close, 0, wx.ALL, 5)
  sizer.Add(wordBox, 0, wx.ALL, 5)
  sizer.Add(contextBox, 0, wx.ALL, 5)
  sizer.Add(suggestionsBox, 0, wx.ALL, 5)
  sizer.Add(btnBox, 0, wx.ALL, 5)
  panel.SetSizer(sizer)
  self.SetClientSize(sizer.CalcMin())


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
 wx.MessageDialog(None, _("An error has occurred. There are no dictionaries available for the selected language in {0}").format(application.name,), _("Error"), wx.ICON_ERROR).ShowModal()

def finished():
 wx.MessageDialog(None, _("Spell check complete."), application.name, style=wx.OK).ShowModal()
