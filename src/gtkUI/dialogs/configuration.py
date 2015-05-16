# -*- coding: utf-8 -*-
import baseDialog
import wx
import logging as original_logger
import application
class general(wx.Panel, baseDialog.BaseWXDialog):
 def __init__(self, parent, languages):
  super(general, self).__init__(parent)
  sizer = wx.BoxSizer(wx.VERTICAL)
  language = wx.StaticText(self, -1, _(u"Language"))
  self.language = wx.ListBox(self, -1, choices=languages)
  self.language.SetSize(self.language.GetBestSize())
  langBox = wx.BoxSizer(wx.HORIZONTAL)
  langBox.Add(language, 0, wx.ALL, 5)
  langBox.Add(self.language, 0, wx.ALL, 5)
  sizer.Add(langBox, 0, wx.ALL, 5)
  self.ask_at_exit = wx.CheckBox(self, -1, _(U"ask before exiting " + application.name))
  sizer.Add(self.ask_at_exit, 0, wx.ALL, 5)
  self.use_invisible_shorcuts = wx.CheckBox(self, -1, _(u"Use invisible interface's keyboard shortcuts while GUI is visible"))
  sizer.Add(self.use_invisible_shorcuts, 0, wx.ALL, 5)
  self.disable_sapi5 = wx.CheckBox(self, -1, _(u"Activate Sapi5 when any other screen reader is not being run"))
  sizer.Add(self.disable_sapi5, 0, wx.ALL, 5)
  self.hide_gui = wx.CheckBox(self, -1, _(u"Hide GUI on launch"))
  sizer.Add(self.hide_gui, 0, wx.ALL, 5)
  self.SetSizer(sizer)

class generalAccount(wx.Panel, baseDialog.BaseWXDialog):
 def __init__(self, parent):
  super(generalAccount, self).__init__(parent)
  sizer = wx.BoxSizer(wx.VERTICAL)
  self.au = wx.Button(self, wx.NewId(), _(u"Set the autocomplete function"))
  sizer.Add(self.au, 0, wx.ALL, 5)
  self.relative_time = wx.CheckBox(self, wx.NewId(), _(U"Relative times"))
  sizer.Add(self.relative_time, 0, wx.ALL, 5)
  apiCallsBox = wx.BoxSizer(wx.HORIZONTAL)
  apiCallsBox.Add(wx.StaticText(self, -1, _(u"API calls when the stream is started (One API call equals to 200 tweetts, two API calls equals 400 tweets, etc):")), 0, wx.ALL, 5)
  self.apiCalls = wx.SpinCtrl(self, wx.NewId())
  self.apiCalls.SetRange(1, 10)
  self.apiCalls.SetSize(self.apiCalls.GetBestSize())
  apiCallsBox.Add(self.apiCalls, 0, wx.ALL, 5)
  sizer.Add(apiCallsBox, 0, wx.ALL, 5)
  tweetsPerCallBox = wx.BoxSizer(wx.HORIZONTAL)
  tweetsPerCallBox.Add(wx.StaticText(self, -1, _(u"Items on each API call")), 0, wx.ALL, 5)
  self.itemsPerApiCall = wx.SpinCtrl(self, wx.NewId())
  self.itemsPerApiCall.SetRange(0, 200)
  self.itemsPerApiCall.SetSize(self.itemsPerApiCall.GetBestSize())
  tweetsPerCallBox.Add(self.itemsPerApiCall, 0, wx.ALL, 5)
  sizer.Add(tweetsPerCallBox, 0, wx.ALL, 5)
  self.reverse_timelines = wx.CheckBox(self, wx.NewId(), _(u"Inverted buffers: The newest tweets will be shown at the beginning of the lists while the oldest at the end"))
  sizer.Add(self.reverse_timelines, 0, wx.ALL, 5)
  self.SetSizer(sizer)

class other_buffers(wx.Panel):
 def __init__(self, parent):
  super(other_buffers, self).__init__(parent)
  sizer = wx.BoxSizer(wx.VERTICAL)
  self.SetSizer(sizer)

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
  self.SetSizer(sizer)

 def get(self, control):
  return getattr(self, control).GetStringSelection()

class audioServicesPanel(wx.Panel):
 def __init__(self, parent):
  super(audioServicesPanel, self).__init__(parent)
  mainSizer = wx.BoxSizer(wx.VERTICAL)
  apiKeyLabel = wx.StaticText(self, -1, _(u"If you've got a SndUp account, enter your API Key here. Whether the API Key is wrong, the App will fail to upload anything to the server. Whether there's no API Key here, then the audio files will be uploaded anonimously"))
  self.apiKey = wx.TextCtrl(self, -1)
  dc = wx.WindowDC(self.apiKey)
  dc.SetFont(self.apiKey.GetFont())
  self.apiKey.SetSize(dc.GetTextExtent("0"*100))
  apiKeyBox = wx.BoxSizer(wx.HORIZONTAL)
  apiKeyBox.Add(apiKeyLabel, 0, wx.ALL, 5)
  apiKeyBox.Add(self.apiKey, 0, wx.ALL, 5)
  mainSizer.Add(apiKeyBox, 0, wx.ALL, 5)
  first_sizer = wx.BoxSizer(wx.HORIZONTAL)
  self.dropbox = wx.Button(self, -1)
  first_sizer.Add(self.dropbox, 0, wx.ALL, 5)
  mainSizer.Add(first_sizer, 0, wx.ALL, 5)
  self.SetSizer(mainSizer)

 def set_dropbox(self, active=True):
  if active == True:
   self.dropbox.SetLabel(_(u"Unlink your Dropbox account"))
  else:
   self.dropbox.SetLabel(_(u"Link your Dropbox account"))
   
 def show_dialog(self):
  wx.MessageDialog(self, _(u"The authorization request will be opened in your browser. Copy the code from Dropbox and paste it into the text box which will appear. You only need to do this once."), _(u"Authorization"), wx.OK).ShowModal()

 def get_response(self):
  dlg = wx.TextEntryDialog(self, _(u"Enter the code here."), _(u"Verification code"))
  if dlg.ShowModal() == wx.ID_CANCEL:
   return False
  return dlg.GetValue()

 def show_error(self):
  wx.MessageDialog(self, _(u"Error during authorisation. Try again later."), _(u"Error!"), wx.ICON_ERROR).ShowModal()

 def get_dropbox(self):
  return self.dropbox.GetLabel()

class configurationDialog(baseDialog.BaseWXDialog):

 def set_title(self, title):
  self.SetTitle(title)

 def __init__(self):
  super(configurationDialog, self).__init__(None, -1)
  self.panel = wx.Panel(self)
  self.SetTitle(_(u"TW Blue preferences"))
  self.sizer = wx.BoxSizer(wx.VERTICAL)
  self.notebook = wx.Notebook(self.panel)

 def create_general(self, languageList):
  self.general = general(self.notebook, languageList)
  self.notebook.AddPage(self.general, _(u"General"))
  self.general.SetFocus()

 def create_general_account(self):
  self.general = generalAccount(self.notebook)
  self.notebook.AddPage(self.general, _(u"General"))
  self.general.SetFocus()

 def create_other_buffers(self):
  self.buffers = other_buffers(self.notebook)
  self.notebook.AddPage(self.buffers, _(u"Show other buffers"))

 def create_ignored_clients(self, ignored_clients_list):
  self.ignored_clients = ignoredClients(self.notebook, ignored_clients_list)
  self.notebook.AddPage(self.ignored_clients, _(u"Ignored clients"))

 def create_sound(self, output_devices, input_devices, soundpacks):
  self.sound = sound(self.notebook, output_devices, input_devices, soundpacks)
  self.notebook.AddPage(self.sound, _(u"Sound"))
 def create_audio_services(self):
  self.services = audioServicesPanel(self.notebook)
  self.notebook.AddPage(self.services, _(u"Audio Services"))

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

