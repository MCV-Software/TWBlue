import win32api
import win32con

from main import KeyboardHandler

class WindowsKeyboardHandler(KeyboardHandler):

 def __init__ (self, *args, **kwargs):
  super(WindowsKeyboardHandler, self).__init__(*args, **kwargs)
  #Setup the replacement dictionaries.
  for i in dir(win32con):
   if i.startswith("VK_"):
    key = i[3:].lower()
    self.replacement_keys[key] = getattr(win32con, i)
   elif i.startswith("MOD_"):
    key = i[4:].lower()
    self.replacement_mods[key] = getattr(win32con, i)
  self.replacement_keys .update(dict(pageup=win32con.VK_PRIOR, pagedown=win32con.VK_NEXT))

 def parse_key (self, keystroke, separator="+"):
  keystroke = str(keystroke) #We don't want unicode
  keystroke = [self.keycode_from_key(i) for i in keystroke.split(separator)]
  mods = 0
  for i in keystroke[:-1]:
   mods = mods | i #or everything together
  return (mods, keystroke[-1])

 def keycode_from_key(self, key):
  if key in self.replacement_mods:
   return self.replacement_mods[key]
  if key in self.replacement_keys:
   return self.replacement_keys[key]
  if len(key) == 1:
   return win32api.VkKeyScanEx(key, win32api.GetKeyboardLayout())

 def is_key_pressed(self, key):
  """Returns if the given key was pressed.  Requires an active message loop or will simply give if the key was pressed recently."""
  key = self.keycode_from_key(key)
  return win32api.GetAsyncKeyState(key)

