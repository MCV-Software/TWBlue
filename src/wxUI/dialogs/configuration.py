# -*- coding: utf-8 -*-
import logging as original_logger
import wx
import application
import output
import config
import baseDialog
from multiplatform_widgets import widgets

class general(wx.Panel, baseDialog.BaseWXDialog):
 def __init__(self, parent, languages,keymaps):
  super(general, self).__init__(parent)
  sizer = wx.BoxSizer(wx.VERTICAL)
  language = wx.StaticText(self, -1, _(u"Language"))
  self.language = wx.ListBox(self, -1, choices=languages)
  self.language.SetSize(self.language.GetBestSize())
  langBox = wx.BoxSizer(wx.HORIZONTAL)
  langBox.Add(language, 0, wx.ALL, 5)
  langBox.Add(self.language, 0, wx.ALL, 5)
  sizer.Add(langBox, 0, wx.ALL, 5)
  self.autostart = wx.CheckBox(self, -1, _(u"Run {0} at Windows startup").format(application.name,))
  self.ask_at_exit = wx.CheckBox(self, -1, _(U"ask before exiting {0}").format(application.name,))
  sizer.Add(self.autostart, 0, wx.ALL, 5)
  sizer.Add(self.ask_at_exit, 0, wx.ALL, 5)
  self.no_streaming = wx.CheckBox(self, -1, _(U"Disable Streaming functions"))
  sizer.Add(self.no_streaming, 0, wx.ALL, 5)
  updatePeriodBox = wx.BoxSizer(wx.HORIZONTAL)
  updatePeriodBox.Add(wx.StaticText(self, -1, _(u"Buffer update interval, in minutes")), 0, wx.ALL, 5)
  self.update_period = wx.SpinCtrl(self, wx.ID_ANY)
  self.update_period.SetRange(1, 30)
  self.update_period.SetSize(self.update_period.GetBestSize())
  updatePeriodBox.Add(self.update_period, 0, wx.ALL, 5)
  sizer.Add(updatePeriodBox, 0, wx.ALL, 5)
  self.play_ready_sound = wx.CheckBox(self, -1, _(U"Play a sound when {0} launches").format(application.name,))
  sizer.Add(self.play_ready_sound, 0, wx.ALL, 5)
  self.speak_ready_msg = wx.CheckBox(self, -1, _(U"Speak a message when {0} launches").format(application.name,))
  sizer.Add(self.speak_ready_msg, 0, wx.ALL, 5)
  self.use_invisible_shorcuts = wx.CheckBox(self, -1, _(u"Use invisible interface's keyboard shortcuts while GUI is visible"))
  sizer.Add(self.use_invisible_shorcuts, 0, wx.ALL, 5)
  self.disable_sapi5 = wx.CheckBox(self, -1, _(u"Activate Sapi5 when any other screen reader is not being run"))
  sizer.Add(self.disable_sapi5, 0, wx.ALL, 5)
  self.hide_gui = wx.CheckBox(self, -1, _(u"Hide GUI on launch"))
  sizer.Add(self.hide_gui, 0, wx.ALL, 5)
  self.handle_longtweets = wx.CheckBox(self, wx.ID_ANY, _(u"Use Codeofdusk's longtweet handlers (may decrease client performance)"))
  sizer.Add(self.handle_longtweets, 0, wx.ALL, 5)
  self.remember_mention_and_longtweet = wx.CheckBox(self, -1, _(u"Remember state for mention all and long tweet"))
  sizer.Add(self.remember_mention_and_longtweet, 0, wx.ALL, 5)
  kmbox =  wx.BoxSizer(wx.VERTICAL)
  km_label = wx.StaticText(self, -1, _(u"Keymap"))
  self.km = wx.ComboBox(self, -1, choices=keymaps, style=wx.CB_READONLY)
  self.km.SetSize(self.km.GetBestSize())
  kmbox.Add(km_label, 0, wx.ALL, 5)
  kmbox.Add(self.km, 0, wx.ALL, 5)
  self.check_for_updates = wx.CheckBox(self, -1, _(U"Check for updates when {0} launches").format(application.name,))
  sizer.Add(self.check_for_updates, 0, wx.ALL, 5)
  sizer.Add(kmbox, 0, wx.ALL, 5)
  self.SetSizer(sizer)

class proxy(wx.Panel, baseDialog.BaseWXDialog):

 def __init__(self, parent, proxyTypes):
  super(proxy, self).__init__(parent)
  sizer = wx.BoxSizer(wx.VERTICAL)
  type=wx.StaticText(self, wx.ID_ANY, _(u"Proxy type: "))
  self.type=wx.ComboBox(self, -1, choices=proxyTypes, style=wx.CB_READONLY)
  self.type.SetSize(self.type.GetBestSize())
  typeBox = wx.BoxSizer(wx.HORIZONTAL)
  typeBox.Add(type, 0, wx.ALL, 5)
  typeBox.Add(self.type, 0, wx.ALL, 5)
  sizer.Add(typeBox, 0, wx.ALL, 5)
  lbl = wx.StaticText(self, wx.ID_ANY, _(u"Proxy server: "))
  self.server = wx.TextCtrl(self, -1)
  serverBox = wx.BoxSizer(wx.HORIZONTAL)
  serverBox.Add(lbl, 0, wx.ALL, 5)
  serverBox.Add(self.server, 0, wx.ALL, 5)
  sizer.Add(serverBox, 0, wx.ALL, 5)
  lbl = wx.StaticText(self, wx.ID_ANY, _(u"Port: "))
  self.port = wx.TextCtrl(self, wx.ID_ANY)
  portBox = wx.BoxSizer(wx.HORIZONTAL)
  portBox.Add(lbl, 0, wx.ALL, 5)
  portBox.Add(self.port, 0, wx.ALL, 5)
  sizer.Add(portBox, 0, wx.ALL, 5)
  lbl = wx.StaticText(self, wx.ID_ANY, _(u"User: "))
  self.user = wx.TextCtrl(self, wx.ID_ANY)
  userBox = wx.BoxSizer(wx.HORIZONTAL)
  userBox.Add(lbl, 0, wx.ALL, 5)
  userBox.Add(self.user, 0, wx.ALL, 5)
  sizer.Add(userBox, 0, wx.ALL, 5)
  lbl = wx.StaticText(self, wx.ID_ANY, _(u"Password: "))
  self.password = wx.TextCtrl(self, wx.ID_ANY, style=wx.TE_PASSWORD)
  passwordBox = wx.BoxSizer(wx.HORIZONTAL)
  passwordBox.Add(lbl, 0, wx.ALL, 5)
  passwordBox.Add(self.password, 0, wx.ALL, 5)
  sizer.Add(serverBox, 0, wx.ALL, 5)
  self.SetSizer(sizer)

class generalAccount(wx.Panel, baseDialog.BaseWXDialog):
 def __init__(self, parent):
  super(generalAccount, self).__init__(parent)
  sizer = wx.BoxSizer(wx.VERTICAL)
  self.au = wx.Button(self, wx.ID_ANY, _(u"Autocompletion settings..."))
  sizer.Add(self.au, 0, wx.ALL, 5)
  self.relative_time = wx.CheckBox(self, wx.ID_ANY, _(U"Relative timestamps"))
  sizer.Add(self.relative_time, 0, wx.ALL, 5)
  if application.streaming_lives():
   apiCallsBox = wx.BoxSizer(wx.HORIZONTAL)
   apiCallsBox.Add(wx.StaticText(self, -1, _(u"API calls (One API call = 200 tweets, two API calls = 400 tweets, etc):")), 0, wx.ALL, 5)
   self.apiCalls = wx.SpinCtrl(self, wx.ID_ANY)
   self.apiCalls.SetRange(1, 10)
   self.apiCalls.SetSize(self.apiCalls.GetBestSize())
   apiCallsBox.Add(self.apiCalls, 0, wx.ALL, 5)
   sizer.Add(apiCallsBox, 0, wx.ALL, 5)
  tweetsPerCallBox = wx.BoxSizer(wx.HORIZONTAL)
  tweetsPerCallBox.Add(wx.StaticText(self, -1, _(u"Items on each API call")), 0, wx.ALL, 5)
  self.itemsPerApiCall = wx.SpinCtrl(self, wx.ID_ANY)
  self.itemsPerApiCall.SetRange(0, 200)
  self.itemsPerApiCall.SetSize(self.itemsPerApiCall.GetBestSize())
  tweetsPerCallBox.Add(self.itemsPerApiCall, 0, wx.ALL, 5)
  sizer.Add(tweetsPerCallBox, 0, wx.ALL, 5)
  self.reverse_timelines = wx.CheckBox(self, wx.ID_ANY, _(u"Inverted buffers: The newest tweets will be shown at the beginning while the oldest at the end"))
  sizer.Add(self.reverse_timelines, 0, wx.ALL, 5)
  lbl = wx.StaticText(self, wx.ID_ANY, _(u"Retweet mode"))
  self.retweet_mode = wx.ComboBox(self, wx.ID_ANY, choices=[_(u"Ask"), _(u"Retweet without comments"), _(u"Retweet with comments")], style=wx.CB_READONLY)
  rMode = wx.BoxSizer(wx.HORIZONTAL)
  rMode.Add(lbl, 0, wx.ALL, 5)
  rMode.Add(self.retweet_mode, 0, wx.ALL, 5)
  sizer.Add(rMode, 0, wx.ALL, 5)
  self.show_screen_names = wx.CheckBox(self, wx.ID_ANY, _(U"Show screen names instead of full names"))
  sizer.Add(self.show_screen_names, 0, wx.ALL, 5)
  PersistSizeLabel = wx.StaticText(self, -1, _(u"Number of items per buffer to cache in database (0 to disable caching, blank for unlimited)"))
  self.persist_size = wx.TextCtrl(self, -1)
  sizer.Add(PersistSizeLabel, 0, wx.ALL, 5)
  sizer.Add(self.persist_size, 0, wx.ALL, 5)
  self.SetSizer(sizer)

class reporting(wx.Panel, baseDialog.BaseWXDialog):
 def __init__(self, parent):
  super(reporting, self).__init__(parent)
  sizer = wx.BoxSizer(wx.VERTICAL)
  self.speech_reporting = wx.CheckBox(self, wx.ID_ANY, _(U"Enable automatic speech feedback"))
  sizer.Add(self.speech_reporting, 0, wx.ALL, 5)
  self.braille_reporting = wx.CheckBox(self, wx.ID_ANY, _(U"Enable automatic Braille feedback"))
  sizer.Add(self.braille_reporting, 0, wx.ALL, 5)
  self.SetSizer(sizer)

class other_buffers(wx.Panel):
 def __init__(self, parent):
  super(other_buffers, self).__init__(parent)
  sizer = wx.BoxSizer(wx.VERTICAL)
  self.buffers = widgets.list(self, _(u"Buffer"), _(u"Name"), _(u"Status"), style=wx.LC_SINGLE_SEL|wx.LC_REPORT)
  sizer.Add(self.buffers.list, 0, wx.ALL, 5)
  btnSizer = wx.BoxSizer(wx.HORIZONTAL)
  self.toggle_state = wx.Button(self, -1, _(u"Show/hide"))
  self.up = wx.Button(self, -1, _(u"Move up"))
  self.down = wx.Button(self, -1, _(u"Move down"))
  btnSizer.Add(self.toggle_state, 0, wx.ALL, 5)
  btnSizer.Add(self.up, 0, wx.ALL, 5)
  btnSizer.Add(self.down, 0, wx.ALL, 5)
  sizer.Add(btnSizer, 0, wx.ALL, 5)
  self.SetSizer(sizer)

 def insert_buffers(self, buffers):
  for i in buffers:
   if i[2] == True:
    self.buffers.insert_item(False, *[i[0], i[1], _(u"Show")])
   else:
    self.buffers.insert_item(False, *[i[0], i[1], _(u"Hide")])

 def connect_hook_func(self, func):
  self.buffers.list.Bind(wx.EVT_CHAR_HOOK, func)

 def move_up(self, *args, **kwargs):
  current = self.buffers.get_selected()
  if current == -1:
   output.speak(_(u"Select a buffer first."), True)
   return False
  if self.buffers.get_text_column(current, 2) == _(u"Hide"):
   output.speak(_(u"The buffer is hidden, show it first."), True)
   return False
  if current <= 0:
   output.speak(_(u"The buffer is already at the top of the list."), True)
   return False
  current_text = self.buffers.get_text_column(self.buffers.get_selected(), 0)
  current_name = self.buffers.get_text_column(self.buffers.get_selected(), 1)
  current_text_state = self.buffers.get_text_column(self.buffers.get_selected(), 2)
  text_above = self.buffers.get_text_column(self.buffers.get_selected()-1, 0)
  name_above = self.buffers.get_text_column(self.buffers.get_selected()-1, 1)
  text_above_state = self.buffers.get_text_column(self.buffers.get_selected()-1, 2)
  self.buffers.set_text_column(self.buffers.get_selected()-1, 0, current_text)
  self.buffers.set_text_column(self.buffers.get_selected()-1, 1, current_name)
  self.buffers.set_text_column(self.buffers.get_selected()-1, 2, current_text_state)
  self.buffers.set_text_column(self.buffers.get_selected(), 0, text_above)
  self.buffers.set_text_column(self.buffers.get_selected(), 1, name_above)
  self.buffers.set_text_column(self.buffers.get_selected(), 2, text_above_state)

 def move_down(self, *args, **kwargs):
  current = self.buffers.get_selected()
  if current == -1:
   output.speak(_(u"Select a buffer first."), True)
   return False
  if self.buffers.get_text_column(current, 2) == _(u"Hide"):
   output.speak(_(u"The buffer is hidden, show it first."), True)
   return False
  if current+1 >= self.buffers.get_count():
   output.speak(_(u"The buffer is already at the bottom of the list."), True)
   return False
  current_text = self.buffers.get_text_column(self.buffers.get_selected(), 0)
  current_name = self.buffers.get_text_column(self.buffers.get_selected(), 1)
  current_text_state = self.buffers.get_text_column(self.buffers.get_selected(), 2)
  text_below = self.buffers.get_text_column(self.buffers.get_selected()+1, 0)
  name_below = self.buffers.get_text_column(self.buffers.get_selected()+1, 1)
  text_below_state = self.buffers.get_text_column(self.buffers.get_selected()+1, 2)
  self.buffers.set_text_column(self.buffers.get_selected()+1, 0, current_text)
  self.buffers.set_text_column(self.buffers.get_selected()+1, 1, current_name)
  self.buffers.set_text_column(self.buffers.get_selected()+1, 2, current_text_state)
  self.buffers.set_text_column(self.buffers.get_selected(), 0, text_below)
  self.buffers.set_text_column(self.buffers.get_selected(), 1, name_below)
  self.buffers.set_text_column(self.buffers.get_selected(), 2, text_below_state)

 def get_event(self, ev):
  if ev.GetKeyCode() == wx.WXK_SPACE:
   return True
  else:
   ev.Skip()
   return False

 def change_selected_item(self):
  current = self.buffers.get_selected()
  text = self.buffers.get_text_column(current, 2)
  if text == _(u"Show"):
   self.buffers.set_text_column(current, 2, _(u"Hide"))
  else:
   self.buffers.set_text_column(current, 2, _(u"Show"))
  output.speak(self.buffers.get_text_column(current, 2),True)
 def get_list(self):
  buffers_list = []
  for i in xrange(0, self.buffers.get_count()):
   if self.buffers.get_text_column(i, 2) == _(u"Show"):
    buffers_list.append(self.buffers.get_text_column(i, 0))
  return buffers_list

class ignoredClients(wx.Panel):
 def __init__(self, parent, choices):
  super(ignoredClients, self).__init__(parent=parent)
  sizer = wx.BoxSizer(wx.VERTICAL)
  label = wx.StaticText(self, -1, _(u"Ignored clients"))
  self.clients = wx.ListBox(self, -1, choices=choices)
  self.clients.SetSize(self.clients.GetBestSize())
  clientsBox = wx.BoxSizer(wx.HORIZONTAL)
  clientsBox.Add(label, 0, wx.ALL, 5)
  clientsBox.Add(self.clients, 0, wx.ALL, 5)
  self.add = wx.Button(self, -1, _(u"Add client"))
  self.remove = wx.Button(self, -1, _(u"Remove client"))
  btnBox = wx.BoxSizer(wx.HORIZONTAL)
  btnBox.Add(self.add, 0, wx.ALL, 5)
  btnBox.Add(self.remove, 0, wx.ALL, 5)
  sizer.Add(clientsBox, 0, wx.ALL, 5)
  sizer.Add(btnBox, 0, wx.ALL, 5)
  self.SetSizer(sizer)

 def append(self, client):
  self.clients.Append(client)

 def get_clients(self):
  return self.clients.GetCount()

 def get_client_id(self):
  return self.clients.GetSelection()

 def remove_(self, id):
  self.clients.Delete(id)

class sound(wx.Panel):
 def __init__(self, parent, input_devices, output_devices, soundpacks):
  wx.Panel.__init__(self, parent)
  sizer = wx.BoxSizer(wx.VERTICAL)
  volume = wx.StaticText(self, -1, _(u"Volume"))
  self.volumeCtrl = wx.Slider(self)
  self.volumeCtrl.SetRange(0, 100)
  self.volumeCtrl.SetSize(self.volumeCtrl.GetBestSize())
  volumeBox = wx.BoxSizer(wx.HORIZONTAL)
  volumeBox.Add(volume, 0, wx.ALL, 5)
  volumeBox.Add(self.volumeCtrl, 0, wx.ALL, 5)
  sizer.Add(volumeBox, 0, wx.ALL, 5)
  self.session_mute = wx.CheckBox(self, -1, _(u"Session mute"))
  sizer.Add(self.session_mute, 0, wx.ALL, 5)
  output_label = wx.StaticText(self, -1, _(u"Output device"))
  self.output = wx.ComboBox(self, -1, choices=output_devices, style=wx.CB_READONLY)
  self.output.SetSize(self.output.GetBestSize())
  outputBox = wx.BoxSizer(wx.HORIZONTAL)
  outputBox.Add(output_label, 0, wx.ALL, 5)
  outputBox.Add(self.output, 0, wx.ALL, 5)
  sizer.Add(outputBox, 0, wx.ALL, 5)
  input_label = wx.StaticText(self, -1, _(u"Input device"))
  self.input = wx.ComboBox(self, -1, choices=input_devices, style=wx.CB_READONLY)
  self.input.SetSize(self.input.GetBestSize())
  inputBox = wx.BoxSizer(wx.HORIZONTAL)
  inputBox.Add(input_label, 0, wx.ALL, 5)
  inputBox.Add(self.input, 0, wx.ALL, 5)
  sizer.Add(inputBox, 0, wx.ALL, 5)
  soundBox =  wx.BoxSizer(wx.VERTICAL)
  soundpack_label = wx.StaticText(self, -1, _(u"Sound pack"))
  self.soundpack = wx.ComboBox(self, -1, choices=soundpacks, style=wx.CB_READONLY)
  self.soundpack.SetSize(self.soundpack.GetBestSize())
  soundBox.Add(soundpack_label, 0, wx.ALL, 5)
  soundBox.Add(self.soundpack, 0, wx.ALL, 5)
  sizer.Add(soundBox, 0, wx.ALL, 5)
  self.indicate_audio = wx.CheckBox(self, -1, _(u"Indicate audio tweets with sound"))
  sizer.Add(self.indicate_audio, 0, wx.ALL, 5)
  self.indicate_geo = wx.CheckBox(self, -1, _(u"Indicate geotweets with sound"))
  sizer.Add(self.indicate_geo, 0, wx.ALL, 5)
  self.indicate_img = wx.CheckBox(self, -1, _(u"Indicate tweets containing images with sound"))
  sizer.Add(self.indicate_img, 0, wx.ALL, 5)
  self.SetSizer(sizer)

 def get(self, control):
  return getattr(self, control).GetStringSelection()

class extrasPanel(wx.Panel):
 def __init__(self, parent, ocr_languages=[], translation_languages=[]):
  super(extrasPanel, self).__init__(parent)
  mainSizer = wx.BoxSizer(wx.VERTICAL)
  OCRBox = wx.StaticBox(self, label=_(u"Language for OCR"))
  self.ocr_lang = wx.ListBox(self, -1, choices=ocr_languages)
  self.ocr_lang.SetSize(self.ocr_lang.GetBestSize())
  ocrLanguageSizer = wx.StaticBoxSizer(OCRBox, wx.HORIZONTAL)
  ocrLanguageSizer.Add(self.ocr_lang, 0, wx.ALL, 5)
  mainSizer.Add(ocrLanguageSizer, 0, wx.ALL, 5)
  lbl = wx.StaticText(self, wx.ID_ANY, _(u"API Key for SndUp"))
  self.sndup_apiKey = wx.TextCtrl(self, -1)
  sndupBox = wx.BoxSizer(wx.HORIZONTAL)
  sndupBox.Add(lbl, 0, wx.ALL, 5)
  sndupBox.Add(self.sndup_apiKey, 0, wx.ALL, 5)
  mainSizer.Add(sndupBox, 0, wx.ALL, 5)
  self.SetSizer(mainSizer)

class configurationDialog(baseDialog.BaseWXDialog):
 def set_title(self, title):
  self.SetTitle(title)

 def __init__(self):
  super(configurationDialog, self).__init__(None, -1)
  self.panel = wx.Panel(self)
  self.SetTitle(_(u"{0} preferences").format(application.name,))
  self.sizer = wx.BoxSizer(wx.VERTICAL)
  self.notebook = wx.Notebook(self.panel)

 def create_general(self, languageList,keymaps):
  self.general = general(self.notebook, languageList,keymaps)
  self.notebook.AddPage(self.general, _(u"General"))
  self.general.SetFocus()

 def create_proxy(self, proxyTypes):
  self.proxy = proxy(self.notebook, proxyTypes)
  self.notebook.AddPage(self.proxy, _(u"Proxy"))

 def create_general_account(self):
  self.general = generalAccount(self.notebook)
  self.notebook.AddPage(self.general, _(u"General"))
  self.general.SetFocus()

 def create_reporting(self):
  self.reporting = reporting(self.notebook)
  self.notebook.AddPage(self.reporting, _(u"Feedback"))

 def create_other_buffers(self):
  self.buffers = other_buffers(self.notebook)
  self.notebook.AddPage(self.buffers, _(u"Buffers"))

 def create_ignored_clients(self, ignored_clients_list):
  self.ignored_clients = ignoredClients(self.notebook, ignored_clients_list)
  self.notebook.AddPage(self.ignored_clients, _(u"Ignored clients"))

 def create_sound(self, output_devices, input_devices, soundpacks):
  self.sound = sound(self.notebook, output_devices, input_devices, soundpacks)
  self.notebook.AddPage(self.sound, _(u"Sound"))

 def create_extras(self, ocr_languages=[], translator_languages=[]):
  self.extras = extrasPanel(self.notebook, ocr_languages, translator_languages)
  self.notebook.AddPage(self.extras, _(u"Extras"))

 def realize(self):
  self.sizer.Add(self.notebook, 0, wx.ALL, 5)
  ok_cancel_box = wx.BoxSizer(wx.HORIZONTAL)
  ok = wx.Button(self.panel, wx.ID_OK, _(u"Save"))
  ok.SetDefault()
  cancel = wx.Button(self.panel, wx.ID_CANCEL, _(u"Close"))
  self.SetEscapeId(cancel.GetId())
  ok_cancel_box.Add(ok, 0, wx.ALL, 5)
  ok_cancel_box.Add(cancel, 0, wx.ALL, 5)
  self.sizer.Add(ok_cancel_box, 0, wx.ALL, 5)
  self.panel.SetSizer(self.sizer)
  self.SetClientSize(self.sizer.CalcMin())

 def get_value(self, panel, key):
  p = getattr(self, panel)
  return getattr(p, key).GetValue()

 def set_value(self, panel, key, value):
  p = getattr(self, panel)
  control = getattr(p, key)
  getattr(control, "SetValue")(value)

