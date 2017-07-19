from __future__ import absolute_import
from .channel import Channel
from .external.pybass import *
from ctypes import string_at
import wave
from .main import bass_call, bass_call_0

class Recording(Channel):

 def __init__(self, frequency=44100, channels=2, flags=BASS_RECORD_PAUSE, proc=None, user=None):
  if not proc:
   proc = lambda: True
  self.callback = RECORDPROC(proc)
  self._frequency = frequency
  self._channels = channels
  self._flags = flags
  handle = bass_call(BASS_RecordStart, frequency, channels, flags, self.callback, user)
  super(Recording, self).__init__(handle)

 def free(self):
  pass


class WaveRecording(Recording):

 def __init__(self, filename=None, proc=None, *args, **kwargs):
  callback = proc or self.recording_callback
  super(WaveRecording, self).__init__(proc=callback, *args, **kwargs)
  self.filename = filename

 def recording_callback(self, handle, buffer, length, user):
  buf = string_at(buffer, length)
  self.file.writeframes(buf)
  return True

 def setup_file(self):
  self.file = wave.open(self.filename, 'w')
  self.file.setnchannels(self._channels)
  self.file.setsampwidth(2)
  self.file.setframerate(self._frequency)

 def play(self, *args, **kwargs):
  if not self.is_playing:
   self.setup_file()
  super(WaveRecording, self).play(*args, **kwargs)

 def stop(self, *args, **kwargs):
  super(WaveRecording, self).stop(*args, **kwargs)
  self.file.close()
