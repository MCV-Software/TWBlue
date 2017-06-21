# -*- coding: utf-8 -*-

import widgetUtils
from . import baseDialog
import wx
from extra import translator

class searchDialog(baseDialog.BaseWXDialog):
 def __init__(self, value=""):
  super(searchDialog, self).__init__(None, -1)
  panel = wx.Panel(self)
  sizer = wx.BoxSizer(wx.VERTICAL)
  self.SetTitle(_("Search on Twitter"))
  label = wx.StaticText(panel, -1, _("&Search"))
  self.term = wx.TextCtrl(panel, -1, value)
  dc = wx.WindowDC(self.term)
  dc.SetFont(self.term.GetFont())
  self.term.SetSize(dc.GetTextExtent("0"*40))
  sizer.Add(label, 0, wx.ALL, 5)
  sizer.Add(self.term, 0, wx.ALL, 5)
  self.tweets = wx.RadioButton(panel, -1, _("Tweets"), style=wx.RB_GROUP)
  self.users = wx.RadioButton(panel, -1, _("Users"))
  widgetUtils.connect_event(self.tweets, widgetUtils.RADIOBUTTON, self.show_advanced_search)
  widgetUtils.connect_event(self.users, widgetUtils.RADIOBUTTON, self.hide_advanced_search)
  radioSizer = wx.BoxSizer(wx.HORIZONTAL)
  radioSizer.Add(self.tweets, 0, wx.ALL, 5)
  radioSizer.Add(self.users, 0, wx.ALL, 5)
  sizer.Add(radioSizer, 0, wx.ALL, 5)
  lang = wx.StaticText(panel, -1, _("&Language for results: "))
  langs = [x[1] for x in translator.translator.available_languages()]
  langs[:] = langs[1:]
  langs.insert(0, _("any"))
  self.lang = wx.ComboBox(panel, -1, choices=langs, value=langs[0], style = wx.CB_READONLY)
  langBox = wx.BoxSizer(wx.HORIZONTAL)
  langBox.Add(lang, 0, wx.ALL, 5)
  langBox.Add(self.lang, 0, wx.ALL, 5)
  sizer.Add(langBox, 0, wx.ALL, 5)
  resulttype = wx.StaticText(panel, -1, _("Results &type: "))
  self.resultstype = wx.ComboBox(panel, -1, choices=[_("Mixed"), _("Recent"), _("Popular")], value=_("Mixed"), style=wx.CB_READONLY)
  rBox = wx.BoxSizer(wx.HORIZONTAL)
  rBox.Add(resulttype, 0, wx.ALL, 5)
  rBox.Add(self.resultstype, 0, wx.ALL, 5)
  sizer.Add(rBox, 0, wx.ALL, 5)
  ok = wx.Button(panel, wx.ID_OK, _("&OK"))
  ok.SetDefault()
  cancel = wx.Button(panel, wx.ID_CANCEL, _("&Close"))
  btnsizer = wx.BoxSizer()
  btnsizer.Add(ok, 0, wx.ALL, 5)
  btnsizer.Add(cancel, 0, wx.ALL, 5)
  sizer.Add(btnsizer, 0, wx.ALL, 5)
  panel.SetSizer(sizer)
  self.SetClientSize(sizer.CalcMin())

 def get_language(self):
   return [x[0] for x in translator.translator.available_languages()][self.lang.GetSelection()]

 def get_result_type(self):
  r = self.resultstype.GetValue()
  if r == _("Mixed"): return "mixed"
  elif r == _("Recent"): return "recent"
  elif r == _("Popular"): return "popular"

 def hide_advanced_search(self, *args, **kwargs):
  self.lang.Hide()
  self.resultstype.Hide()

 def show_advanced_search(self, *args, **kwargs):
  self.lang.Show()
  self.resultstype.Show()
