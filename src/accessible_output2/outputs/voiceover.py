from base import Output, OutputError

class VoiceOver (Output):
 """Supports the VoiceOver screenreader on the Mac.

 Note that this will also output as a message to the braille display if VoiceOver is used with braille.
 Calling this module could cause VoiceOver to be started.
 """
 name = 'VoiceOver'

 def __init__(self, *args, **kwargs):
  super(VoiceOver, self).__init__(*args, **kwargs)
  try:
   from appscript import app
   self.app = app('VoiceOver')
  except ImportError:
   raise OutputError

 def speak(self, text, interupt=False):
  self.app.output(text)

 def is_active(self):
  return True
