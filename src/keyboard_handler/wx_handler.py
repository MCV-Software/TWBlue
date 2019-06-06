from __future__ import absolute_import
import functools
import logging
logger = logging.getLogger("keyboard_handler")
import wx

from .main import KeyboardHandler, KeyboardHandlerError
from . import key_constants

__all__ = ['WXKeyboardHandler', 'WXControlKeyboardHandler']

def call_after(func):
 def wrapper(*args, **kwargs):
  wx.CallAfter(func, *args, **kwargs)
 functools.update_wrapper(wrapper, func)
 return wrapper


class BaseWXKeyboardHandler(KeyboardHandler):

 def __init__(self, *args, **kwargs):
  super(BaseWXKeyboardHandler, self).__init__(*args, **kwargs)
  #Setup the replacement dictionaries.
  for i in dir(wx):
   if i.startswith('WXK_'):
    key = i[4:].lower()
    self.replacement_keys[key] = getattr(wx, i)
   elif i.startswith('MOD_'):
    key = i[4:].lower()
    self.replacement_mods[key] = getattr(wx, i)

 def parse_key (self, keystroke, separator="+"):
  keystroke = [self.keycode_from_key(i) for i in keystroke.split(separator)]
  mods = 0
  for i in keystroke[:-1]:
   mods = mods | i #or everything together
  return (mods, keystroke[-1])

 def keycode_from_key(self, key):
  result = None
  if key in self.replacement_mods:
   result = self.replacement_mods[key]
  elif key in self.replacement_keys:
   result = self.replacement_keys[key]
   if result >= 277:
    result -= 277
  elif len(key) == 1:
   result = ord(key.upper()) 
  if result is None:
   raise KeyboardHandlerError("Could not translate key %r into a valid keycode." % key)
  return result


 
class WXKeyboardHandler(BaseWXKeyboardHandler):

 def __init__ (self, parent, *args, **kwargs):
  super(WXKeyboardHandler, self).__init__(*args, **kwargs)
  self.parent = parent
  self.key_ids = {}
  self.replacement_keys = key_constants.keys
  self.replacement_mods = key_constants.modifiers

 @call_after
 def register_key(self, key, function):
  super(WXKeyboardHandler, self).register_key(key, function)
  key_id = wx.NewId()
  parsed = self.parse_key(key)
  res = self.parent.RegisterHotKey(key_id, *parsed)
  if not res:
   logger.warn("Failed to register hotkey: %s for function %r", key, function)
  self.parent.Bind(wx.EVT_HOTKEY, lambda evt: self.process_key(evt, key_id), id=key_id)
  self.key_ids[key] = key_id
  return res

 def parse_key (self, keystroke, separator="+"):
  keystroke = str(keystroke) #We don't want unicode
  keystroke = [self.keycode_from_key(i) for i in keystroke.split(separator)]
  mods = 0
  for i in keystroke[:-1]:
   mods = mods | i #or everything together
  return (mods, keystroke[-1])

 @call_after
 def unregister_key (self, key, function):
  super(WXKeyboardHandler, self).unregister_key(key, function)
  if key not in self.key_ids:
   return #there's nothing we can do.
  key_id = self.key_ids[key]
  self.parent.UnregisterHotKey(key_id)
  self.parent.Unbind( wx.EVT_HOTKEY, id=key_id)
  self.key_ids.pop(key)

 def process_key (self, evt, id):
  evt.Skip()
  key_ids = self.key_ids.keys()
  for i in key_ids:
   if self.key_ids.get(i) == id:
    self.handle_key(i)

class WXControlKeyboardHandler(wx.StaticText, KeyboardHandler):

 def __init__(self, parent=None, *a, **k):
  wx.StaticText.__init__(self, parent=parent)
  KeyboardHandler.__init__(self, *a, **k)
  self.wx_replacements = {}
  for i in [d for d in dir(wx) if d.startswith('WXK_')]:
   self.wx_replacements[getattr(wx, i)] = i[4:].lower()
  self.Bind(wx.EVT_KEY_DOWN, self.process_key, self)
  self.SetFocus()

 def process_key(self, evt):
  keycode = evt.GetKeyCode()
  keyname = self.wx_replacements.get(keycode, None)
  modifiers = ""
  replacements = (   (evt.ControlDown(), 'control+'),
   (evt.AltDown(),     'alt+'),
   (evt.ShiftDown(),   'shift+'),
   (evt.MetaDown(),    'win+')
  )
  for mod, ch in (replacements):
   if mod:
    modifiers += ch
  if keyname is None:
   if 27 < keycode < 256:
    keyname = chr(keycode).lower()
   else:
    keyname = "(%s)unknown" % keycode
  key = modifiers + keyname
  self.handle_key(key)
