from base import Output, OutputError
import atexit
import application
class SpeechDispatcher(Output):
 """Supports speech dispatcher on Linux.
 Note that this module will use the configuration of speech dispatcher, the user will need to configure the voice, language, punctuation and rate before using this module.
 """
 name = 'SpeechDispatcher'

 def __init__(self, *args, **kwargs):
  super(SpeechDispatcher, self).__init__(*args, **kwargs)
  try:
   import speechd
   self.spd = speechd.SSIPClient(application.name)
  except ImportError:
   raise OutputError
  atexit.register(self.on_exit_event)

 def speak(self, text, interupt=False):
  if interupt == True:
   self.spd.cancel()
  self.spd.speak(text)

 def is_active(self):
  return True

 def on_exit_event(self):
  self.spd.close()
  del self.spd
