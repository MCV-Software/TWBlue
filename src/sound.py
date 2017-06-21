# -*- coding: utf-8 -*-
from builtins import range
from builtins import object
import sys
import url_shortener
import audio_services
import os
import logging as original_logger 
log = original_logger.getLogger("sound")
import paths
from sound_lib.output import Output
from sound_lib.input import Input
from sound_lib.recording import WaveRecording
from sound_lib.stream import FileStream
from sound_lib.stream import URLStream as SoundlibURLStream
import subprocess
import platform
import output
system = platform.system()
from mysc.repeating_timer import RepeatingTimer
from mysc.thread_utils import call_threaded
import application
import tempfile
import glob
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
 val = WaveRecording(filename=filename)
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
   self.output = Output()
   self.input = Input()
  except IOError:
   pass
  # Try to use the selected device from the configuration. It can fail if the machine does not has a mic.
  try:
   log.debug("Setting input and output devices...")
   self.output.set_device(self.output.find_device_by_name(self.config["output_device"]))
   self.input.set_device(self.input.find_device_by_name(self.config["input_device"]))
  except:
   log.exception("Error in input or output devices, using defaults...")
   self.config["output_device"] = "Default"
   self.config["input_device"] = "Default"

  self.files = []
  self.cleaner = RepeatingTimer(60, self.clear_list)
  self.cleaner.start()
  self.check_soundpack()

 def clear_list(self):
  if len(self.files) == 0: return
  try:
   for i in range(0, len(self.files)):
    if self.files[i].is_playing == False:
     self.files[i].free()
     self.files.pop(i)
  except IndexError:
   pass

 def play(self, sound, argument=False):
  if self.soundpack_OK == False: return
  if self.config["session_mute"] == True: return
  sound_object = FileStream(file="%s/%s" % (self.path, sound))
  sound_object.volume = float(self.config["volume"])
  self.files.append(sound_object)
  sound_object.play()

class URLStream(object):
 def __init__(self,url=None):
  self.url = url
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


 def seek(self,step):
  pos=self.stream.get_position()
  pos=self.stream.bytes_to_seconds(pos)
  pos+=step
  pos=self.stream.seconds_to_bytes(pos)
  if pos<0:
   pos=0
  self.stream.set_position(pos)

 def playpause(self):
  if self.stream.is_playing==True:
   self.stream.pause()
  else:
   self.stream.play()

 def play(self, url=None, volume=1.0, stream=None,announce=True):
  if announce:
   output.speak(_("Playing..."))
  log.debug("Attempting to play an URL...")
  if url != None:
   self.prepare(url)
  elif stream != None:
   self.stream=stream
  if self.prepared == True:
   self.stream = SoundlibURLStream(url=bytes(self.url,'utf-8'))
  if hasattr(self,'stream'):
   self.stream.volume = float(volume)
   self.stream.play()
   log.debug("played")
#   call_threaded(self.delete_when_done)

 def stop_audio(self,delete=False):
  if hasattr(self, "stream"):
   output.speak(_("Stopped."), True)
   try:
    self.stream.stop()
    log.debug("Stopped audio stream.")
   except:
    log.exception("Exception while stopping stream.")
   if delete:
    del self.stream
    log.debug("Deleted audio stream.")
   return True
  else:
   return False

 @staticmethod
 def delete_old_tempfiles():
  for f in glob(os.path.join(tempfile.gettempdir(), 'tmp*.wav')):
   try:
    os.remove(f)
   except:
    pass

