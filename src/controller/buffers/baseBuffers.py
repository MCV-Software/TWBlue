# -*- coding: utf-8 -*-
import wx
import output
import config
import sound
import widgetUtils
import logging
from pubsub import pub
from wxUI import buffers

log = logging.getLogger("controller.buffers")

def _items_exist(function):
 """ A decorator to execute a function only if the selected buffer contains at least one item."""
 def function_(self, *args, **kwargs):
  if self.buffer.list.get_count() > 0:
   function(self, *args, **kwargs)
 return function_

class buffer(object):
 """ A basic buffer object. This should be the base class for all other derived buffers."""

 def __init__(self, parent=None, function=None, session=None, *args, **kwargs):
  """Inits the main controller for this buffer:
    @ parent wx.Treebook object: Container where we will put this buffer.
    @ function str or None: function to be called periodically and update items on this buffer.
    @ session sessionmanager.session object or None: Session handler for settings, database and Twitter access.
  """
  super(buffer, self).__init__()
  self.function = function
  # Compose_function will be used to render an object on this buffer. Normally, signature is as follows:
  # compose_function(item, db, relative_times, show_screen_names=False, session=None)
  # Compose functions will be defined in every buffer if items are different than tweets.
  # Read more about compose functions in twitter/compose.py.
  self.compose_function = None
  self.args = args
  self.kwargs = kwargs
  # This will be used as a reference to the wx.Panel object wich stores the buffer GUI.
  self.buffer = None
  # This should countains the account associated to this buffer.
  self.account = ""
  # This controls wether the start_stream function should be called when starting the program.
  self.needs_init = True
  # if this is set to False, the buffer will be ignored on the invisible interface.
  self.invisible = False
  # Control variable, used to track time of execution for calls to start_stream.
  self.execution_time = 0

 def clear_list(self):
  pass

 def get_event(self, ev):
  """ Catches key presses in the WX interface and generate the corresponding event names."""
  if ev.GetKeyCode() == wx.WXK_RETURN and ev.ControlDown(): event = "audio"
  elif ev.GetKeyCode() == wx.WXK_RETURN: event = "url"
  elif ev.GetKeyCode() == wx.WXK_F5: event = "volume_down"
  elif ev.GetKeyCode() == wx.WXK_F6: event = "volume_up"
  elif ev.GetKeyCode() == wx.WXK_DELETE and ev.ShiftDown(): event = "clear_list"
  elif ev.GetKeyCode() == wx.WXK_DELETE: event = "destroy_status"
  else:
   event = None
   ev.Skip()
  if event != None:
   try:
    getattr(self, event)()
   except AttributeError:
    pass
 
 def volume_down(self):
  if self.session.settings["sound"]["volume"] > 0.0:
   if self.session.settings["sound"]["volume"] <= 0.05:
    self.session.settings["sound"]["volume"] = 0.0
   else:
    self.session.settings["sound"]["volume"] -=0.05
  sound.URLPlayer.player.audio_set_volume(int(self.session.settings["sound"]["volume"]*100.0))
  self.session.sound.play("volume_changed.ogg")
  self.session.settings.write()

 def volume_up(self):
  if self.session.settings["sound"]["volume"] < 1.0:
   if self.session.settings["sound"]["volume"] >= 0.95:
    self.session.settings["sound"]["volume"] = 1.0
   else:
    self.session.settings["sound"]["volume"] +=0.05
  sound.URLPlayer.player.audio_set_volume(int(self.session.settings["sound"]["volume"]*100))
  self.session.sound.play("volume_changed.ogg")
  self.session.settings.write()

 def start_stream(self, mandatory=False, play_sound=True):
  pass

 def get_more_items(self):
  output.speak(_(u"This action is not supported for this buffer"), True)

 def put_items_on_list(self, items):
  pass

 def remove_buffer(self):
  return False

 def remove_item(self, item):
  f = self.buffer.list.get_selected()
  self.buffer.list.remove_item(item)
  self.buffer.list.select_item(f)

 def bind_events(self):
  pass

 def get_object(self):
  return self.buffer

 def get_message(self):
  pass

 def set_list_position(self, reversed=False):
  if reversed == False:
   self.buffer.list.select_item(-1)
  else:
   self.buffer.list.select_item(0)

 def reply(self):
  pass

 def send_message(self):
  pass

 def share_item(self):
  pass

 def destroy_status(self):
  pass

 def post_status(self, *args, **kwargs):
  pass

 def save_positions(self):
  try:
   self.session.db[self.name+"_pos"]=self.buffer.list.get_selected()
  except AttributeError:
   pass

class accountPanel(buffer):
 def __init__(self, parent, name, account, account_id):
  super(accountPanel, self).__init__(parent, None, name)
  log.debug("Initializing buffer %s, account %s" % (name, account,))
  self.buffer = buffers.accountPanel(parent, name)
  self.type = self.buffer.type
  self.compose_function = None
  self.session = None
  self.needs_init = False
  self.account = account
  self.buffer.account = account
  self.name = name
  self.account_id = account_id

 def setup_account(self):
  widgetUtils.connect_event(self.buffer, widgetUtils.CHECKBOX, self.autostart, menuitem=self.buffer.autostart_account)
  if self.account_id in config.app["sessions"]["ignored_sessions"]:
   self.buffer.change_autostart(False)
  else:
   self.buffer.change_autostart(True)
  if not hasattr(self, "logged"):
   self.buffer.change_login(login=False)
   widgetUtils.connect_event(self.buffer.login, widgetUtils.BUTTON_PRESSED, self.logout)
  else:
   self.buffer.change_login(login=True)
   widgetUtils.connect_event(self.buffer.login, widgetUtils.BUTTON_PRESSED, self.login)

 def login(self, *args, **kwargs):
  del self.logged
  self.setup_account()
  pub.sendMessage("login", session_id=self.account_id)

 def logout(self, *args, **kwargs):
  self.logged = False
  self.setup_account()
  pub.sendMessage("logout", session_id=self.account_id)

 def autostart(self, *args, **kwargs):
  if self.account_id in config.app["sessions"]["ignored_sessions"]:
   self.buffer.change_autostart(True)
   config.app["sessions"]["ignored_sessions"].remove(self.account_id)
  else:
   self.buffer.change_autostart(False)
   config.app["sessions"]["ignored_sessions"].append(self.account_id)
  config.app.write()

class emptyPanel(buffer):
 def __init__(self, parent, name, account):
  super(emptyPanel, self).__init__(parent=parent)
  log.debug("Initializing buffer %s, account %s" % (name, account,))
  self.buffer = buffers.emptyPanel(parent, name)
  self.type = self.buffer.type
  self.compose_function = None
  self.account = account
  self.buffer.account = account
  self.name = name
  self.session = None
  self.needs_init = True
