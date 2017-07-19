from __future__ import absolute_import
import platform
import sys
from .channel import Channel
from .main import bass_call, bass_call_0
from .external.pybass import *

convert_to_unicode = str

class BaseStream(Channel):

 def _callback(*args):
  #Stub it out as otherwise it'll crash, hard.  Used for stubbing download procs
  return 0
 
 def free(self):
  return bass_call(BASS_StreamFree, self.handle)

 def get_file_position(self, mode):
  return bass_call_0(BASS_StreamGetFilePosition, self.handle, mode)

class Stream(BaseStream):

 def __init__(self, freq=44100, chans=2, flags=0, proc=None, user=None, three_d=False, autofree=False, decode=False):
  self.proc = STREAMPROC(proc)
  self.setup_flag_mapping()
  flags = flags | self.flags_for(three_d=three_d, autofree=autofree, decode=decode)
  handle = bass_call(BASS_StreamCreate, freq, chans, flags, self.proc, user)
  super(Stream, self).__init__(handle)

class FileStream(BaseStream):

 def __init__(self, mem=False, file=None, offset=0, length=0, flags=0, three_d=False, mono=False, autofree=False, decode=False, unicode=True):
  """Creates a sample stream from an MP3, MP2, MP1, OGG, WAV, AIFF or plugin supported file."""
  if platform.system() == 'Darwin' or platform.system() == "Linux":
   unicode = False
   file = file.encode(sys.getfilesystemencoding())
  self.setup_flag_mapping()
  flags = flags | self.flags_for(three_d=three_d, autofree=autofree, mono=mono, decode=decode, unicode=unicode)
  if unicode and isinstance(file, str):
   file = convert_to_unicode(file)
  self.file = file
  handle = bass_call(BASS_StreamCreateFile, mem, file, offset, length, flags)
  super(FileStream, self).__init__(handle)

 def setup_flag_mapping(self):
  super(FileStream, self).setup_flag_mapping()
  self.flag_mapping.update({
   'unicode': BASS_UNICODE
  })

class URLStream(BaseStream):

 def __init__(self, url="", offset=0, flags=0, downloadproc=None, user=None, three_d=False, autofree=False, decode=False):
  self._downloadproc = downloadproc or self._callback #we *must hold on to this
  self.downloadproc = DOWNLOADPROC(self._downloadproc)
  self.url = url
  self.setup_flag_mapping()
  flags = flags | self.flags_for(three_d=three_d, autofree=autofree, decode=decode)
  handle = bass_call(BASS_StreamCreateURL, url, offset, flags, self.downloadproc, user)
  super(URLStream, self).__init__(handle)
