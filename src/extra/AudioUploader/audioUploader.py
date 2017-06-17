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

from builtins import str
from builtins import object
import widgetUtils
from . import wx_ui
from . import wx_transfer_dialogs
from . import transfer
import output
import tempfile
import sound
import os
import config
from pubsub import pub
from mysc.thread_utils import call_threaded
import sound_lib
import logging

log = logging.getLogger("extra.AudioUploader.audioUploader")

class audioUploader(object):
 def __init__(self, configFile, completed_callback):
  self.config = configFile
  super(audioUploader, self).__init__()
  self.dialog = wx_ui.audioDialog(services=self.get_available_services())
  self.file = None
  self.recorded = False
  self.recording = None
  self.playing = None
  widgetUtils.connect_event(self.dialog.play, widgetUtils.BUTTON_PRESSED, self.on_play)
  widgetUtils.connect_event(self.dialog.pause, widgetUtils.BUTTON_PRESSED, self.on_pause)
  widgetUtils.connect_event(self.dialog.record, widgetUtils.BUTTON_PRESSED, self.on_record)
  widgetUtils.connect_event(self.dialog.attach_exists, widgetUtils.BUTTON_PRESSED, self.on_attach_exists)
  widgetUtils.connect_event(self.dialog.discard, widgetUtils.BUTTON_PRESSED, self.on_discard)
  if self.dialog.get_response() == widgetUtils.OK:
   self.postprocess()
   log.debug("Uploading file %s to %s..." % (self.file, self.dialog.get("services")))
   self.uploaderDialog = wx_transfer_dialogs.UploadDialog(self.file)
   output.speak(_("Attaching..."))
   if self.dialog.get("services") == "SNDUp":
    base_url = "http://sndup.net/post.php"
    if len(self.config["sound"]["sndup_api_key"]) > 0:
     url = base_url + '?apikey=' + self.config['sound']['sndup_api_key']
    else:
     url = base_url
   self.uploaderFunction = transfer.Upload(obj=self, field='file', url=url, filename=self.file, completed_callback=completed_callback)
   pub.subscribe(self.uploaderDialog.update, "uploading")
   self.uploaderDialog.get_response(self.uploaderFunction.perform_threaded)

 def get_available_services(self):
  services = []
  services.append("SNDUp")
  return services

 def on_pause(self, *args, **kwargs):
  if self.dialog.get("pause") == _("Pause"):
   self.recording.pause()
   self.dialog.set("pause", _("&Resume"))
  elif self.dialog.get("pause") == _("Resume"):
   self.recording.play()
   self.dialog.set("pause", _("&Pause"))

 def on_record(self, *args, **kwargs):
  if self.recording != None:
   self.stop_recording()
   self.dialog.disable_control("pause")
  else:
   self.start_recording()
   self.dialog.enable_control("pause")

 def start_recording(self):
  self.dialog.disable_control("attach_exists")
  self.file = tempfile.mktemp(suffix='.wav')
  self.recording = sound.recording(self.file)
  self.recording.play()
  self.dialog.set("record", _("&Stop"))
  output.speak(_("Recording"))

 def stop_recording(self):
  self.recording.stop()
  self.recording.free()
  output.speak(_("Stopped"))
  self.recorded = True
  self.dialog.set("record", _("&Record"))
  self.file_attached()

 def file_attached(self):
  self.dialog.set("pause", _("&Pause"))
  self.dialog.disable_control("record")
  self.dialog.enable_control("play")
  self.dialog.enable_control("discard")
  self.dialog.disable_control("attach_exists")
  self.dialog.enable_control("attach")
  self.dialog.play.SetFocus()

 def on_discard(self, *args, **kwargs):
  if self.playing:
   self._stop()
  if self.recording != None:
   self.cleanup()
  self.dialog.disable_control("attach")
  self.dialog.disable_control("play")
  self.file = None
  self.dialog.enable_control("record")
  self.dialog.enable_control("attach_exists")
  self.dialog.record.SetFocus()
  self.dialog.disable_control("discard")
  self.recording = None
  output.speak(_("Discarded"))

 def on_play(self, *args, **kwargs):
  if not self.playing:
   call_threaded(self._play)
  else:
   self._stop()

 def _play(self):
  output.speak(_("Playing..."))
#  try:
  self.playing = sound_lib.stream.FileStream(file=str(self.file), flags=sound_lib.stream.BASS_UNICODE)
  self.playing.play()
  self.dialog.set("play", _("&Stop"))
  try:
   while self.playing.is_playing:
    pass
   self.dialog.set("play", _("&Play"))
   self.playing.free()
   self.playing = None
  except:
   pass

 def _stop(self):
  output.speak(_("Stopped"))
  self.playing.stop()
  self.playing.free()
  self.dialog.set("play", _("&Play"))
  self.playing = None

 def postprocess(self):
  if self.file.lower().endswith('.wav'):
   output.speak(_("Recoding audio..."))
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

 def on_attach_exists(self, *args, **kwargs):
  self.file = self.dialog.get_file()
  if self.file != False:
   self.file_attached()

