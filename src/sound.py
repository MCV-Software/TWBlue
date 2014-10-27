# -*- coding: utf-8 -*-
""" Sound utilities."""
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
import sys
import url_shortener
import audio_services
import config
import os
import logging as original_logger 
log = original_logger.getLogger("sound")
import paths
import sound_lib
import subprocess
import platform
system = platform.system()
from mysc.repeating_timer import RepeatingTimer

player = None

def setup():
 global player
 if not player:
  player = soundSystem()

def recode_audio(filename, quality=4.5):
 global system
 if system == "Windows": subprocess.call(r'"%s" -q %r "%s"' % (paths.app_path('oggenc2.exe'), quality, filename))

def recording(filename):
# try:
 val = sound_lib.recording.WaveRecording(filename=filename)
# except sound_lib.main.BassError:
#  sound_lib.input.Input()
#  val = sound_lib.recording.WaveRecording(filename=filename)
 return val

class soundSystem(object):

 def check_soundpack(self):
  """ Checks if the folder where live the current soundpack exists."""
  self.soundpack_OK = False
  if os.path.exists(paths.sound_path(config.main["sound"]["current_soundpack"])):
   self.path = paths.sound_path(config.main["sound"]["current_soundpack"])
   self.soundpack_OK = True
  elif os.path.exists(paths.sound_path("default")):
   self.path = paths.sound_path("default")
   self.soundpack_OK = True
  else:
   self.soundpack_OK = False

 def __init__(self):
  """ Sound Player."""
  # Set the output and input default devices.
  self.output = sound_lib.output.Output()
  self.input = sound_lib.input.Input()
  # Try to use the selected device from the configuration. It can fail if the machine does not has a mic.
  try:
   self.output.set_device(self.output.find_device_by_name(config.main["sound"]["output_device"]))
   self.input.set_device(self.input.find_device_by_name(config.main["sound"]["input_device"]))
  except:
   config.main["sound"]["output_device"] = "Default"
   config.main["sound"]["input_device"] = "Default"

  self.files = []
  self.cleaner = RepeatingTimer(60, self.clear_list)
  self.cleaner.start()
  self.check_soundpack()

 def clear_list(self):
  log.debug("Cleaning sounds... Total sounds found: %i" % len(self.files))
  if self.files == []: return
  for i in xrange(0, len(self.files)):
   if self.files[i].is_playing == False:
    self.files[i].free()
    self.files.pop(i)
  log.debug("Files used now: %i" % len(self.files))

 def play(self, sound, argument=False):
  if self.soundpack_OK == False: return
  if config.main["sound"]["global_mute"] == True: return
  sound_object = sound_lib.stream.FileStream(file="%s/%s" % (self.path, sound))
  sound_object.volume = float(config.main["sound"]["volume"])
  self.files.append(sound_object)
  sound_object.play()

class urlStream(object):
 def __init__(self, url):
  self.url = url
  log.debug(u"URL: %s" % url)
  self.prepared = False

 def prepare(self):
  self.prepared = False
  url = url_shortener.unshorten(self.url)
  log.debug("url desacortada: "+str(url))
  if url != None:
   self.url = url
  transformer = audio_services.find_url_transformer(self.url)
  self.url = transformer(self.url)
  log.debug(u"Url transformada: %s" % self.url)
  prepare = True

 def play(self):
  self.stream = sound_lib.stream.URLStream(url=self.url)
  self.stream.volume = float(config.main["sound"]["volume"])
  self.stream.play()

 @staticmethod
 def delete_old_tempfiles():
  for f in glob(os.path.join(tempfile.gettempdir(), 'tmp*.wav')):
   try:
    os.remove(f)
   except:
    pass

