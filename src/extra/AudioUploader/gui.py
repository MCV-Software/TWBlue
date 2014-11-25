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
import tempfile
import sound
import os
import config
from mysc.thread_utils import call_threaded
import sound_lib

class audioDialog(wx.Dialog):
 def __init__(self, parent):
  self.parent = parent
  wx.Dialog.__init__(self, None, -1, _(u"Attach audio"))
  self.file = None
  self.recorded = False
  self.recording = None
  self.playing = None
  panel = wx.Panel(self)
  sizer = wx.BoxSizer(wx.VERTICAL)
  self.play = wx.Button(panel, -1, _(u"Play"))
  self.play.Bind(wx.EVT_BUTTON, self.onPlay)
  self.play.Disable()
  self.pause = wx.Button(panel, -1, _(u"Pause"))
  self.pause.Bind(wx.EVT_BUTTON, self.onPause)
  self.pause.Disable()
  self.record = wx.Button(panel, -1, _(u"Record"))
  self.record.Bind(wx.EVT_BUTTON, self.onRecord)
  self.record.SetFocus()
  self.attach_exists = wx.Button(panel, -1, _(u"Add an existing file"))
  self.attach_exists.Bind(wx.EVT_BUTTON, self.onAttach)
  self.discard = wx.Button(panel, -1, _(u"Discard"))
  self.discard.Bind(wx.EVT_BUTTON, self.onDiscard)
  self.discard.Disable()
  label = wx.StaticText(panel, -1, _(u"Upload to"))
  self.services = wx.ComboBox(panel, -1, choices=self.get_available_services(), value=self.get_available_services()[0], style=wx.CB_READONLY)
  servicesBox = wx.BoxSizer(wx.HORIZONTAL)
  servicesBox.Add(label)
  servicesBox.Add(self.services)
  self.attach = wx.Button(panel, wx.ID_OK, _(u"Attach"))
  self.attach.Disable()
  cancel = wx.Button(panel, wx.ID_CANCEL, _(u"Cancel"))
  sizer.Add(self.play)
  sizer.Add(self.pause)
  sizer.Add(self.record)
  sizer.Add(self.attach_exists)
  sizer.Add(self.discard)
  sizer.Add(self.attach)

 def get_available_services(self):
  services = []
  if config.main["services"]["dropbox_token"] != "":
   services.append("Dropbox")
   service.append("TwUp")
   services.append("SNDUp")
  return services

 def onPause(self, ev):
  if self.pause.GetLabel() == _(u"Pause"):
   self.recording.pause()
   self.pause.SetLabel(_(u"Resume"))
  elif self.pause.GetLabel() == _(u"Resume"):
   self.recording.play()
   self.pause.SetLabel(_(U"Pause"))

 def onRecord(self, ev):
  if self.recording != None:
   self.stop_recording()
   self.pause.Disable()
  else:
   self.start_recording()
   self.pause.Enable()

 def start_recording(self):
  self.attach_exists.Disable()
  self.file = tempfile.mktemp(suffix='.wav')
  self.recording = sound.recording(self.file)
  self.recording.play()
  self.record.SetLabel(_(u"Stop recording"))
  output.speak(_(u"Recording"))

 def stop_recording(self):
  self.recording.stop()
  self.recording.free()
  output.speak(_(u"Stopped"))
  self.recorded = True
  self.record.SetLabel(_(u"Record"))
  self.file_attached()

 def file_attached(self):
  self.pause.SetLabel(_(u"Pause"))
  self.record.Disable()
  self.play.Enable()
  self.discard.Enable()
  self.attach_exists.Disable()
  self.attach.Enable()
  self.play.SetFocus()

 def onDiscard(self, evt):
  evt.Skip()
  if self.playing:
   self._stop()
  if self.recording != None:
   self.attach.Disable()
   self.play.Disable()
  self.file = None
  self.record.Enable()
  self.attach_exists.Enable()
  self.record.SetFocus()
  self.discard.Disable()
  self.recording = None
  output.speak(_(u"Discarded"))

 def onPlay(self, evt):
  evt.Skip()
  if not self.playing:
   call_threaded(self._play)
  else:
   self._stop()

 def _play(self):
  output.speak(_(u"Playing..."))
#  try:
  self.playing = sound_lib.stream.FileStream(file=unicode(self.file), flags=sound_lib.stream.BASS_UNICODE)
  self.playing.play()
  self.play.SetLabel(_(u"Stop"))
  try:
   while self.playing.is_playing:
    pass
   self.play.SetLabel(_(u"Play"))
   self.playing.free()
   self.playing = None
  except:
   pass

 def _stop(self):
  output.speak(_(u"Stopped"))
  self.playing.stop()
  self.playing.free()
  self.play.SetLabel(_(u"Play"))
  self.playing = None

 def postprocess(self):
  if self.file.lower().endswith('.wav'):
   output.speak(_(u"Recoding audio..."))
   sound.recode_audio(self.file)
   self.wav_file = self.file
   self.file = '%s.ogg' % self.file[:-4]

 def cleanup(self):
  if self.playing and self.playing.is_playing:
   self.playing.stop()
  if self.recording != None:
   if self.recording.is_playing:
    self.recording.stop()
   try:
    self.recording.free()
   except:
    pass
   os.remove(self.file)
   if hasattr(self, 'wav_file'):
    os.remove(self.wav_file)
    del(self.wav_file)
  if hasattr(self, 'wav_file') and os.path.exists(self.file):
   os.remove(self.file)


 def onAttach(self, ev):
  openFileDialog = wx.FileDialog(self, _(u"Select the audio file to be uploaded"), "", "", _("Audio Files (*.mp3, *.ogg, *.wav)|*.mp3; *.ogg; *.wav"), wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
  if openFileDialog.ShowModal() == wx.ID_CANCEL:
   return
  self.file = openFileDialog.GetPath()
  self.file_attached()
  ev.Skip()
