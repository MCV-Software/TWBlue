import os

from base import Output

class Dolphin (Output):
 """Supports dolphin products."""

 name = 'Dolphin'
 lib32 = 'dolapi.dll'

 def speak(self, text, interrupt=0):
  if interrupt:
   self.silence()
  #If we don't call this, the API won't let us speak.
  if self.is_active():
   self.lib.DolAccess_Command(unicode(text), (len(text)*2)+2, 1)

 def silence(self):
  self.lib.DolAccess_Action(141)

 def is_active(self):
  try:
   return self.lib.DolAccess_GetSystem() in (1, 4, 8)
  except:
   return False

output_class = Dolphin
