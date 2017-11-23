# -*- coding: utf-8 -*-
import baseDialog
import wx
import widgetUtils

class filterDialog(baseDialog.BaseWXDialog):
 def __init__(self, value="", languages=[]):
  super(filterDialog, self).__init__(None, -1)
  self.langs_list = languages
  panel = wx.Panel(self)
  sizer = wx.BoxSizer(wx.VERTICAL)
  self.SetTitle(_(u"Create a filter  for this buffer"))
  staticbox = wx.StaticBox(panel, label=_(u"Filter by word"))
  self.contains = wx.RadioButton(panel, -1, _(u"Ignore tweets wich contain the following word"), style=wx.RB_GROUP)
  self.doesnt_contain = wx.RadioButton(panel, -1, _(u"Ignore tweets without the following word"))
  radioSizer1 = wx.StaticBoxSizer(staticbox, wx.HORIZONTAL)
  radioSizer1.Add(self.contains, 0, wx.ALL, 5)
  radioSizer1.Add(self.doesnt_contain, 0, wx.ALL, 5)
  sizer.Add(radioSizer1, 0, wx.ALL, 5)
  label = wx.StaticText(panel, -1, _(u"word"))
  self.term = wx.TextCtrl(panel, -1, value)
  dc = wx.WindowDC(self.term)
  dc.SetFont(self.term.GetFont())
  self.term.SetSize(dc.GetTextExtent("0"*40))
  bsizer = wx.BoxSizer(wx.HORIZONTAL)
  bsizer.Add(label, 0, wx.ALL, 5)
  bsizer.Add(self.term, 0, wx.ALL, 5)
  sizer.Add(bsizer, 0, wx.ALL, 5)
  self.regexp = wx.CheckBox(panel, wx.NewId(), _(u"Use this term as a regular expression"))
  sizer.Add(self.regexp, 0, wx.ALL, 5)
  staticbox = wx.StaticBox(panel, label=_(u"Filter by language"))
  self.load_language = wx.RadioButton(panel, -1, _(u"Load tweets in the following languages"), style=wx.RB_GROUP)
  self.ignore_language = wx.RadioButton(panel, -1, _(u"Ignore tweets in the following languages"))
  self.skip_language_filtering = wx.RadioButton(panel, -1, _(u"Don't filter by language"))
  self.skip_language_filtering.SetValue(True)
  widgetUtils.connect_event(self.load_language, widgetUtils.RADIOBUTTON, self.show_language_options)
  widgetUtils.connect_event(self.ignore_language, widgetUtils.RADIOBUTTON, self.show_language_options)
  widgetUtils.connect_event(self.skip_language_filtering, widgetUtils.RADIOBUTTON, self.hide_language_options)
  radioSizer2 = wx.StaticBoxSizer(staticbox, wx.HORIZONTAL)
  radioSizer2.Add(self.load_language, 0, wx.ALL, 5)
  radioSizer2.Add(self.ignore_language, 0, wx.ALL, 5)
  radioSizer2.Add(self.skip_language_filtering, 0, wx.ALL, 5)
  sizer.Add(radioSizer2, 0, wx.ALL, 5)
  self.indexes = []
  langsLabel = wx.StaticText(panel, -1, _(u"Supported languages"))
  self.cb = wx.ComboBox(panel, -1, choices=languages, value=languages[0])
  langsSizer = wx.BoxSizer()
  langsSizer.Add(langsLabel, 0, wx.ALL, 5)
  langsSizer.Add(self.cb, 0, wx.ALL, 5)
  self.add = wx.Button(panel, wx.NewId(), _(u"Add selected language to filter"))
  self.add.Bind(wx.EVT_BUTTON, self.add_lang)
  langsSizer.Add(self.add, 0, wx.ALL, 5)
  sizer.Add(langsSizer, 0, wx.ALL, 5)
  lbl = wx.StaticText(panel, wx.NewId(), _(u"Selected languages"))
  self.langs = wx.ListBox(panel, -1)
  self.remove = wx.Button(panel, wx.NewId(), _(u"Remove"))
  self.remove.Bind(wx.EVT_BUTTON, self.remove_lang)
  selectionSizer = wx.BoxSizer(wx.HORIZONTAL)
  selectionSizer.Add(lbl, 0, wx.ALL, 5)
  selectionSizer.Add(self.langs, 0, wx.ALL, 5)
  selectionSizer.Add(self.remove, 0, wx.ALL, 5)
  sizer.Add(selectionSizer, 0, wx.ALL, 5)
  ok = wx.Button(panel, wx.ID_OK, _(u"OK"))
  ok.SetDefault()
  cancel = wx.Button(panel, wx.ID_CANCEL, _(u"Cancel"))
  btnsizer = wx.BoxSizer()
  btnsizer.Add(ok, 0, wx.ALL, 5)
  btnsizer.Add(cancel, 0, wx.ALL, 5)
  sizer.Add(btnsizer, 0, wx.ALL, 5)
  panel.SetSizer(sizer)
  self.hide_language_options()
  self.SetClientSize(sizer.CalcMin())

 def get_lang(self):
  return self.cb.GetValue()

 def add_lang(self, *args, **kwargs):
  selection = self.get_lang()
  if selection in self.langs_list:
   self.langs.Append(selection)
   self.indexes.append(selection)

 def remove_lang(self, *args, **kwargs):
  n = self.langs.GetSelection()
  v = self.langs.GetStringSelection()
  self.langs.Delete(n)
  self.indexes.remove(v)

 def get_selected_langs(self):
  return self.indexes

 def hide_language_options(self, *args, **kwargs):
  for i in [self.cb, self.add, self.langs, self.remove]:
   i.Hide()

 def show_language_options(self, *args, **kwargs):
  for i in [self.cb, self.add, self.langs, self.remove]:
   i.Show()
