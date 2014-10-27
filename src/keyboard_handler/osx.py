from AppKit import *
from PyObjCTools import AppHelper
from Carbon.CarbonEvt import RegisterEventHotKey, GetApplicationEventTarget
from Carbon.Events import cmdKey, controlKey
import struct
from threading import Thread

from main import KeyboardHandler

kEventHotKeyPressedSubtype = 6
kEventHotKeyReleasedSubtype = 9

class OSXKeyboardHandler(KeyboardHandler):

 def __init__(self):
  super(OSXKeyboardHandler, self).__init__()
  self.replacement_keys = dict()
  self.app = KeyboardCapturingNSApplication.alloc().init()
  self._event_thread = Thread(target=AppHelper.runEventLoop)
  self._event_thread.start()

 def register_key (self, key, function):
  super(OSXKeyboardHandler, self).register_key(key, function)
  k, m = self.parse_key(key)
  key_id = RegisterEventHotKey(k, m, (0, 0), GetApplicationEventTarget(), 0)
  self.key_ids[key] = key_id

 def unregister_key (self, key, function):
  super(OSXKeyboardHandler, self).unregister_key(key, function)
  key_id = self.key_ids[key]
  raise NotImplementedError

 def parse_key (self, key):
  key=key.split("+")
 #replacements
 #Modifier keys:
  for index, item in enumerate(key[0:-1]):
   if self.replacement_mods.has_key(item):
    key[index] = self.replacement_mods[item]
  if self.replacement_keys.has_key(key[-1]):
   key[-1] = self.replacement_keys[key[-1]]
  elif len(key[-1])==1:
   key[-1] = ord(str(key[-1]))-36
  mods = 0
  for i in key[:-1]:
   mods = mods|i
  return [key[-1], mods]

class KeyboardCapturingNSApplication(NSApplication):

 def sendEvent_(self, theEvent):
  if theEvent.type() == NSSystemDefined and theEvent.subtype() == kEventHotKeyPressedSubtype:
   self.activateIgnoringOtherApps_(True)
   NSRunAlertPanel(u'Hot Key Pressed', u'Hot Key Pressed', None, None, None)
   super(NSApplication, self).sendEvent_(theEvent)

