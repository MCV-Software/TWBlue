from __future__ import absolute_import
from .external.pybass import *
from .main import bass_call, bass_call_0, BassError, update_3d_system, FlagObject
from ctypes import pointer, c_float, c_long, c_ulong, c_buffer

class Channel (FlagObject):
 """A "channel" can be a sample playback channel (HCHANNEL), a sample stream (HSTREAM), a MOD music (HMUSIC), or a recording (HRECORD). Each "Channel" function can be used with one or more of these channel types."""

 def __init__ (self, handle):
  self.handle = handle
  self.attribute_mapping = {
   'eaxmix': BASS_ATTRIB_EAXMIX,
   'frequency': BASS_ATTRIB_FREQ,
   'pan': BASS_ATTRIB_PAN,
   'volume': BASS_ATTRIB_VOL
  }

 def add_attributes_to_mapping(self, **attrs):
  self.attribute_mapping.update(**attrs)

 def play (self, restart=False):
  """Starts (or resumes) playback of a sample, stream, MOD music, or recording."""
  return bass_call(BASS_ChannelPlay, self.handle, restart)

 def play_blocking(self, restart=False):
  self.play(restart=restart)
  while self.is_playing:
   pass

 def pause (self):
  return bass_call(BASS_ChannelPause, self.handle)

 def is_active (self):
  "Checks if a sample, stream, or MOD music is active (playing) or stalled. Can also check if a recording is in progress."""
  return bass_call_0(BASS_ChannelIsActive, self.handle)

 @property
 def is_playing(self):
  return self.is_active() == BASS_ACTIVE_PLAYING

 @property
 def is_paused(self):
  return self.is_active() == BASS_ACTIVE_PAUSED

 @property
 def is_stopped(self):
  return self.is_active() == BASS_ACTIVE_STOPPED

 @property
 def is_stalled(self):
  return self.is_active() == BASS_ACTIVE_STALLED

 def get_position (self, mode=BASS_POS_BYTE):
  """Retrieves the playback position of a sample, stream, or MOD music. Can also be used with a recording channel."""
  return bass_call_0(BASS_ChannelGetPosition, self.handle, mode)

 def set_position (self, pos, mode=BASS_POS_BYTE):
  """Sets the playback position of a sample, MOD music, or stream."""
  return bass_call(BASS_ChannelSetPosition, self.handle, pos, mode)

 position = property(get_position, set_position)

 def stop (self):
  """Stops a sample, stream, MOD music, or recording."""
  return bass_call(BASS_ChannelStop, self.handle)

 def update (self, length=0):
  """Updates the playback buffer of a stream or MOD music."""
  return bass_call(BASS_ChannelUpdate, self.handle, length)

 def get_length (self, mode=BASS_POS_BYTE):
  return bass_call_0(BASS_ChannelGetLength, self.handle, mode)

 __len__ = get_length

 def __bool__(self):
  return True

 def get_device(self):
  """Retrieves the device that a channel is using."""
  return bass_call_0( BASS_ChannelGetDevice, self.handle)

 def set_device (self, device):
  """Changes the device that a stream, MOD music or sample is using."""
  bass_call(BASS_ChannelSetDevice, self.handle, device)

 device = property(get_device, set_device)

 def set_fx(self, type, priority=0):
  """Sets an effect on a stream, MOD music, or recording channel."""
  return SoundEffect(bass_call(BASS_ChannelSetFX, type, priority))

 def bytes_to_seconds(self, position=None):
  """Translates a byte position into time (seconds), based on a channel's format."""
  position = position or self.position
  return bass_call_0(BASS_ChannelBytes2Seconds, self.handle, position)

 def length_in_seconds(self):
  return self.bytes_to_seconds(self.get_length())


 def seconds_to_bytes(self, position):
  """Translates a time (seconds) position into bytes, based on a channel's format."""
  return bass_call_0(BASS_ChannelSeconds2Bytes, self.handle, position)

 def get_attribute(self, attribute):
  """Retrieves the value of a channel's attribute."""
  value = pointer(c_float())
  if attribute in self.attribute_mapping:
   attribute = self.attribute_mapping[attribute]
  bass_call(BASS_ChannelGetAttribute, self.handle, attribute, value)
  return value.contents.value

 def set_attribute(self, attribute, value):
  """Sets the value of a channel's attribute."""
  if attribute in self.attribute_mapping:
   attribute = self.attribute_mapping[attribute]
  return bass_call(BASS_ChannelSetAttribute, self.handle, attribute, value)

 def slide_attribute(self, attribute, value, time):
  """Slides a channel's attribute from its current value to a new value."""
  if attribute in self.attribute_mapping:
   attribute = self.attribute_mapping[attribute]
  return bass_call(BASS_ChannelSlideAttribute, self.handle, attribute, value, time*1000)

 def is_sliding (self, attribute=None):
  """Checks if an attribute (or any attribute) of a sample, stream, or MOD music is sliding."""
  return bass_call_0(BASS_ChannelIsSliding, self.handle, attribute)

 def get_info(self):
  """Retrieves information on a channel."""
  value = pointer(BASS_CHANNELINFO())
  bass_call(BASS_ChannelGetInfo, self.handle, value)
  return value[0]

 def get_level(self):
  """Retrieves the level (peak amplitude) of a stream, MOD music or recording channel."""
  return bass_call_0(BASS_ChannelGetLevel, self.handle)

 def lock(self):
  """Locks a stream, MOD music or recording channel to the current thread."""
  return bass_call(BASS_ChannelLock, self.handle, True)

 def unlock(self):
  """Unlocks a stream, MOD music or recording channel from the current thread."""
  return bass_call(BASS_ChannelLock, self.handle, False)

 def get_3d_attributes(self):
  """Retrieves the 3D attributes of a sample, stream, or MOD music channel with 3D functionality."""
  answer = dict(mode=c_ulong(), min=c_float(), max=c_float(), iangle=c_ulong(), oangle=c_ulong(), outvol=c_float())
  bass_call(BASS_ChannelGet3DAttributes, self.handle, pointer(answer['mode']), pointer(answer['min']), pointer(answer['max']), pointer(answer['iangle']), pointer(answer['oangle']), pointer(answer['outvol']))
  for k in answer:
   answer[k] = answer[k].value()
  return answer

 @update_3d_system
 def set_3d_attributes(self, mode=-1, min=0.0, max=0.0, iangle=-1, oangle=-1, outvol=-1):
  """Sets the 3D attributes of a sample, stream, or MOD music channel with 3D functionality."""
  return bass_call(BASS_ChannelSet3DAttributes, self.handle, mode, min, max, iangle, oangle, outvol)

 def get_3d_position(self):
  """Retrieves the 3D position of a sample, stream, or MOD music channel with 3D functionality."""
  answer = dict(position=BASS_3DVECTOR(), orientation=BASS_3DVECTOR(), velocity=BASS_3DVECTOR())
  bass_call(BASS_ChannelGet3DPosition, self.handle, pointer(answer['position']), pointer(answer['orientation']), pointer(answer['velocity']))
  return answer

 @update_3d_system
 def set_3d_position(self, position=None, orientation=None, velocity=None):
  """Sets the 3D position of a sample, stream, or MOD music channel with 3D functionality."""
  if position:
   position = pointer(position)
  if orientation:
   orientation = pointer(orientation)
  if velocity:
   velocity = pointer(velocity)
  return bass_call(BASS_ChannelSet3DPosition, self.handle, position, orientation, velocity)

 def set_link(self, handle):
  """Links two MOD music or stream channels together."""
  bass_call(BASS_ChannelSetLink, self.handle, handle)

 def remove_link(self, handle):
  """Removes a link between two MOD music or stream channels."""
  return bass_call(BASS_ChannelRemoveLink, self.handle, handle)

 def __iadd__(self, other):
  """Convenience method to link this channel to another.  Calls set_link on the passed in item's handle"""
  self.set_link(other.handle)
  return self

 def __isub__(self, other):
  """Convenience method to unlink this channel from another.  Calls remove_link on the passed in item's handle"""
  self.remove_link(other.handle)
  return self

 def get_frequency(self):
  return self.get_attribute(BASS_ATTRIB_FREQ )

 def set_frequency(self, frequency):
  self.set_attribute(BASS_ATTRIB_FREQ, frequency)

 frequency = property(fget=get_frequency, fset=set_frequency)

 def get_pan(self):
  return self.get_attribute(BASS_ATTRIB_PAN)

 def set_pan(self, pan):
  return self.set_attribute(BASS_ATTRIB_PAN, pan)

 pan = property(fget=get_pan, fset=set_pan)

 def get_volume(self):
  return self.get_attribute(BASS_ATTRIB_VOL)

 def set_volume(self, volume):
  self.set_attribute(BASS_ATTRIB_VOL, volume)

 volume = property(fget=get_volume, fset=set_volume)

 def get_data(self, length=16384):
  buf = c_buffer(length)
  bass_call_0(BASS_ChannelGetData, self.handle, pointer(buf), length)
  return buf


#This is less and less of a one-to-one mapping,
#But I feel that it's better to be consistent with ourselves
#Than with the library.  We won't punish ourselves
#For their bad decisions

 def get_looping(self):
  return bass_call_0(BASS_ChannelFlags, self.handle, BASS_SAMPLE_LOOP, 0) == 20

 def set_looping(self, looping):
  if looping:
   return bass_call_0(BASS_ChannelFlags, self.handle, BASS_SAMPLE_LOOP, BASS_SAMPLE_LOOP)
  return bass_call_0(BASS_ChannelFlags, self.handle, 0, BASS_SAMPLE_LOOP)

 looping = property(fget=get_looping, fset=set_looping)

 def __del__(self):
  try:
   self.free()
  except:
   pass

 def get_x(self):
  return self.get_3d_position()['position'].x

 def set_x(self, val):
  pos = self.get_3d_position()
  pos['position'].x = val
  self.set_3d_position(**pos)

 x = property(fget=get_x, fset=set_x)

 def get_y(self):
  return self.get_3d_position()['position'].y

 def set_y(self, val):
  pos = self.get_3d_position()
  pos['position'].y = val
  self.set_3d_position(**pos)

 y = property(fget=get_y, fset=set_y)

 def get_z(self):
  return self.get_3d_position()['position'].z

 def set_z(self, val):
  pos = self.get_3d_position()
  pos['position'].z = val
  self.set_3d_position(**pos)

 z = property(fget=get_z, fset=set_z)

 def get_attributes(self):
  """Retrieves all values of all attributes from this object and displays them in a dictionary whose keys are determined by this object's attribute_mapping"""
  res = {}
  for k in self.attribute_mapping:
   try:
    res[k] = self.get_attribute(k)
   except BassError:
    pass
  return res
