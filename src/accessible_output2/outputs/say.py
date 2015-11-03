from __future__ import absolute_import
import os
from .base import Output

class AppleSay(Output):
 """Speech output supporting the Apple Say subsystem."""
 name = 'Apple Say'
 def __init__(self, voice = 'Alex', rate = '300'):
  self.voice = voice
  self.rate = rate
  super(AppleSay, self).__init__()
 def is_active(self):
  return not os.system('which say')
 def speak(self, text, interrupt = 0):
  if interrupt:
   self.silence()
  os.system('say -v %s -r %s "%s" &' % (self.voice, self.rate, text))
 def silence(self):
  os.system('killall say')

output_class = AppleSay