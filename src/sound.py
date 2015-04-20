# -*- coding: utf-8 -*-
import sys
import url_shortener
import audio_services
import os
import logging as original_logger 
log = original_logger.getLogger("sound")
import paths
import sound_lib
import subprocess
import platform
import output
system = platform.system()
from mysc.repeating_timer import RepeatingTimer
import application
URLPlayer = None

def setup():
 global URLPlayer
 if not URLPlayer:
  log.debug("creating stream URL player...")
  URLPlayer = URLStream()

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
  if os.path.exists(paths.sound_path(self.config["current_soundpack"])):
   self.path = paths.sound_path(self.config["current_soundpack"])
   self.soundpack_OK = True
  elif os.path.exists(paths.sound_path("default")):
   log.error("The soundpack does not exist, using default...")
   self.path = paths.sound_path("default")
   self.soundpack_OK = True
  else:
   log.error("The current soundpack could not be found and the default soundpack has been deleted, " + application.name + " will not play sounds.")
   self.soundpack_OK = False

 def __init__(self, soundConfig):
  """ Sound Player."""
  self.config = soundConfig
  # Set the output and input default devices.
  try:
   self.output = sound_lib.output.Output()
   self.input = sound_lib.input.Input()
  except:
   pass
   # Try to use the selected device from the configuration. It can fail if the machine does not has a mic.
  try:
   log.debug("Setting input and output devices...")
   self.output.set_device(self.output.find_device_by_name(self.config["output_device"]))
   self.input.set_device(self.input.find_device_by_name(self.config["input_device"]))
  except:
   log.error("Error in input or output devices, using defaults...")
   self.config["output_device"] = "Default"
   self.config["input_device"] = "Default"

  self.files = []
  self.cleaner = RepeatingTimer(60, self.clear_list)
  self.cleaner.start()
  self.check_soundpack()

 def clear_list(self):
  log.debug("Cleaning sounds... Total sounds found: %i" % len(self.files))
  if len(self.files) == 0: return
  try:
   for i in range(0, len(self.files)):
    if self.files[i].is_playing == False:
     self.files[i].free()
     self.files.pop(i)
  except IndexError:
   pass
  log.debug("Files used now: %i" % len(self.files))

 def play(self, sound, argument=False):
  if self.soundpack_OK == False: return
  if self.config["session_mute"] == True: return
  sound_object = sound_lib.stream.FileStream(file="%s/%s" % (self.path, sound))
  sound_object.volume = float(self.config["volume"])
  self.files.append(sound_object)
  sound_object.play()

class URLStream(object):
 def __init__(self):
  self.url = None
  self.prepared = False
  log.debug("URL Player initialized")

 def prepare(self, url):
  log.debug("Preparing URL: %s" % (url,))
  self.prepared = False
  self.url = url_shortener.unshorten(url)
  log.debug("Expanded URL: %s" % (self.url,))
  if self.url != None:
   transformer = audio_services.find_url_transformer(self.url)
   self.url = transformer(self.url)
   log.debug("Transformed URL: %s. Prepared" % (self.url,))
   self.prepared = True
  else:
   self.url = url
   log.debug("Transformed URL: %s. Prepared" % (self.url,))
   self.prepared = True

 def play(self, url, volume=1.0):
  if hasattr(self, "stream") and self.stream.is_playing:
   output.speak(_(u"Stopped"))
   self.stream.stop()
   del self.stream
   log.debug("Stream stopped")
  else:
   output.speak(_(u"Playing..."))
   log.debug("Attempting to play an URL...")
   self.prepare(url)
   if self.prepared == True:
    self.stream = sound_lib.stream.URLStream(url=self.url)
    self.stream.volume = float(volume)
    self.stream.play()
    log.debug("played")

 def stop_audio(self):
  if hasattr(self, "stream") and self.stream.is_playing == True:
   self.stream.stop()

 @staticmethod
 def delete_old_tempfiles():
  for f in glob(os.path.join(tempfile.gettempdir(), 'tmp*.wav')):
   try:
    os.remove(f)
   except:
    pass

