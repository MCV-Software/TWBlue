from accessible_output2 import load_library
import platform

class OutputError(Exception):
 pass

class Output(object):
 name = "Unnamed Output" #The name of this output
 lib32 = None #name of 32-bit lib
 lib64 = None #name of 64-bit lib
 priority = 100 #Where to sort in the list of available outputs for automaticly speaking

 def __init__(self):
  is_32bit = platform.architecture()[0] == "32bit"
  if self.lib32 and is_32bit:
   self.lib = load_library(self.lib32)
  elif self.lib64:
   self.lib = load_library(self.lib64)

 def output(self, text, **options):
  output = False
  if hasattr(self, 'speak') and callable(self.speak):
   self.speak(text, **options)
   output = True
  if hasattr(self, 'braille') and callable(self.braille):
   self.braille(text, **options)
   output = True
  if not output:
   raise RuntimeError("Output %r does not have any method defined to output" % self)


