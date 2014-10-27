from __future__ import absolute_import
from future.builtins import object
from ctypes import string_at
import wave

from .external.pybass import *
from . import config
from .main import bass_call, bass_call_0, BassError

class Input (object):

 def __init__ (self, device=-1):
  try:
   bass_call(BASS_RecordInit, device)
  except BassError:
   pass
  self._device = device
  self.config = config.BassConfig()

 def free(self):
  """Frees all resources used by the recording device."""
  return bass_call(BASS_RecordFree)

 def get_device(self):
    return bass_call_0(BASS_RecordGetDevice)

 def set_device(self, device):
  if device == self._device:
   return
  self.free()
  self.__init__(device=device)

 device = property(fget=get_device, fset=set_device)

 @staticmethod
 def get_device_names():
  """Convenience method that returns a list of device names that are considered
 valid by bass.
	
  Parameters: none.
  returns: list of devices, 0-indexed.
  """
  result = ['Default']
  info = BASS_DEVICEINFO()
  count = 0
  while BASS_RecordGetDeviceInfo(count, ctypes.byref(info)):
   if info.flags & BASS_DEVICE_ENABLED:
    retrieved = info.name
    if platform.system() == 'Windows':
     retrieved = retrieved.decode('mbcs')
    retrieved = retrieved.replace('(', '').replace(')', '').strip()
    result.append(retrieved)
   count += 1
  return result

 def find_device_by_name(self, name):
  return self.get_device_names().index(name) - 1

 def find_default_device(self):
  return -1

 def find_user_provided_device(self, device_name):
  try:
   return self.find_device_by_name(device_name)
  except ValueError:
   return self.find_default_device()
