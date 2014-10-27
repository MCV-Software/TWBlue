from main import KeyboardHandler
import threading
import thread
import pyatspi
def parse(s):
 """parse a string like control+f into (modifier, key).
Unknown modifiers will return ValueError."""
 m = 0
 lst = s.split('+')
 if not len(lst): return (0, s)
#Are these right?
 d = {
 "shift": 1<<pyatspi.MODIFIER_SHIFT,
 "control": 1<<pyatspi.MODIFIER_CONTROL,
 "alt": 1<<pyatspi.MODIFIER_ALT,
"win":1<<pyatspi.MODIFIER_META3,
 }
 for item in lst:
  if item in d:
   m|=d[item]
   lst.remove(item)
#end if
 if len(lst) > 1: #more than one key, parse error
  raise ValueError, 'unknown modifier %s' % lst[0]
 return (m, lst[0].lower())
class AtspiThread(threading.Thread):
 def run(self):
  pyatspi.Registry.registerKeystrokeListener(handler, kind=(pyatspi.KEY_PRESSED_EVENT,),
  mask=pyatspi.allModifiers())
  pyatspi.Registry.start()
#the keys we registered
keys = {}
def handler(e):
 m,k = e.modifiers,e.event_string.lower()
#not sure why we can't catch control+f. Try to fix it.
 if (not e.is_text) and e.id >= 97 <= 126:
  k = chr(e.id)
 if (m,k) not in keys: return False
 thread.start_new(keys[(m,k)], ())
 return True #don't pass it on
class LinuxKeyboardHandler(KeyboardHandler):
 def __init__(self, *args, **kwargs):
  KeyboardHandler.__init__(self, *args, **kwargs)
  t = AtspiThread()
  t.start()
 def register_key(self, key, function):
  """key will be a string, such as control+shift+f.
We need to convert that, using parse_key,
into modifier and key to put into our dictionary."""
#register key so we know if we have it on event receive.
  t = parse(key)
  keys[t] = function
#if we got this far, the key is valid.
  KeyboardHandler.register_key(self, key, function)

 def unregister_key (self, key, function):
  KeyboardHandler.unregister_key(self, key, function)
  del keys[parse(key)]
