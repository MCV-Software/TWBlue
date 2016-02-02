from __future__ import absolute_import
from .external import pybass
from .channel import Channel

class Music(Channel):

 def __init__(self, mem=False, file=None, offset=0, length=0, flags=0, freq=0):
  handle = pybass.BASS_MusicLoad(mem, file, offset, length, flags, freq)
  super(Music, self).__init__(handle)
  self.add_attributes_to_mapping(
   music_amplify=pybass.BASS_ATTRIB_MUSIC_AMPLIFY,
   music_bpm = pybass.BASS_ATTRIB_MUSIC_BPM,
   music_pansep=pybass.BASS_ATTRIB_MUSIC_PANSEP,
   music_speed=pybass.BASS_ATTRIB_MUSIC_SPEED,
   music_vol_chan=pybass.BASS_ATTRIB_MUSIC_VOL_CHAN,
   music_vol_global=pybass.BASS_ATTRIB_MUSIC_VOL_GLOBAL,
   music_vol_inst=pybass.BASS_ATTRIB_MUSIC_VOL_INST,
  )
