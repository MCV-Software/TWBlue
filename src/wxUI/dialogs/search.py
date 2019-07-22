# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals
import widgetUtils
from . import baseDialog
import wx
from extra import translator

class searchDialog(baseDialog.BaseWXDialog):
 def __init__(self, value=""):
  super(searchDialog, self).__init__(None, -1)
  panel = wx.Panel(self)
  sizer = wx.BoxSizer(wx.VERTICAL)
  self.SetTitle(_(u"Search on Twitter"))
  label = wx.StaticText(panel, -1, _(u"&Search"))
  self.term = wx.TextCtrl(panel, -1, value)
  dc = wx.WindowDC(self.term)
  dc.SetFont(self.term.GetFont())
  self.term.SetSize(dc.GetTextExtent("0"*40))
  sizer.Add(label, 0, wx.ALL, 5)
  sizer.Add(self.term, 0, wx.ALL, 5)
  self.tweets = wx.RadioButton(panel, -1, _(u"Tweets"), style=wx.RB_GROUP)
  self.users = wx.RadioButton(panel, -1, _(u"Users"))
  widgetUtils.connect_event(self.tweets, widgetUtils.RADIOBUTTON, self.show_advanced_search)
  widgetUtils.connect_event(self.users, widgetUtils.RADIOBUTTON, self.hide_advanced_search)
  radioSizer = wx.BoxSizer(wx.HORIZONTAL)
  radioSizer.Add(self.tweets, 0, wx.ALL, 5)
  radioSizer.Add(self.users, 0, wx.ALL, 5)
  sizer.Add(radioSizer, 0, wx.ALL, 5)
  lang = wx.StaticText(panel, -1, _(u"&Language for results: "))
  langs = [x for x in list(translator.translator.languages.values())]
  langs.insert(0, _(u"any"))
  self.lang = wx.ComboBox(panel, -1, choices=langs, value=langs[0], style = wx.CB_READONLY)
  langBox = wx.BoxSizer(wx.HORIZONTAL)
  langBox.Add(lang, 0, wx.ALL, 5)
  langBox.Add(self.lang, 0, wx.ALL, 5)
  sizer.Add(langBox, 0, wx.ALL, 5)
  resulttype = wx.StaticText(panel, -1, _(U"Results &type: "))
  self.resultstype = wx.ComboBox(panel, -1, choices=[_(u"Mixed"), _(u"Recent"), _(u"Popular")], value=_(u"Mixed"), style=wx.CB_READONLY)
  rBox = wx.BoxSizer(wx.HORIZONTAL)
  rBox.Add(resulttype, 0, wx.ALL, 5)
  rBox.Add(self.resultstype, 0, wx.ALL, 5)
  sizer.Add(rBox, 0, wx.ALL, 5)
  ok = wx.Button(panel, wx.ID_OK, _(u"&OK"))
  ok.SetDefault()
  cancel = wx.Button(panel, wx.ID_CANCEL, _(u"&Close"))
  btnsizer = wx.BoxSizer()
  btnsizer.Add(ok, 0, wx.ALL, 5)
  btnsizer.Add(cancel, 0, wx.ALL, 5)
  sizer.Add(btnsizer, 0, wx.ALL, 5)
  panel.SetSizer(sizer)
  self.SetClientSize(sizer.CalcMin())

 def get_language(self):
  l = self.lang.GetStringSelection()
  if l == _(u"any"):
   return ""
  for langcode, langname in translator.translator.languages.items():
   if langname == l:
    return langcode

 def get_result_type(self):
  r = self.resultstype.GetValue()
  if r == _(u"Mixed"): return "mixed"
  elif r == _(u"Recent"): return "recent"
  elif r == _(u"Popular"): return "popular"

 def hide_advanced_search(self, *args, **kwargs):
  self.lang.Hide()
  self.resultstype.Hide()

 def show_advanced_search(self, *args, **kwargs):
  self.lang.Show()
  self.resultstype.Show()
