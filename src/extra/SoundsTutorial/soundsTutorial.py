# -*- coding: utf-8 -*-
import widgetUtils
import config
import os
import paths
import logging
log = logging.getLogger("extra.SoundsTutorial.soundsTutorial")
import sound
import wx_ui
import soundsTutorial_constants

class soundsTutorial(object):
 def __init__(self):
  log.debug("Creating sounds tutorial object...")
  super(soundsTutorial, self).__init__()
  self.actions = []
  log.debug("Loading actions for sounds tutorial...")
  [self.actions.append(i[1]) for i in soundsTutorial_constants.actions]
  self.files = []
  log.debug("Searching sound files...")
  [self.files.append(i[0]) for i in soundsTutorial_constants.actions]
  log.debug("Creating dialog...")
  self.dialog = wx_ui.soundsTutorialDialog(self.actions)
  widgetUtils.connect_event(self.dialog.play, widgetUtils.BUTTON_PRESSED, self.on_play)
  self.dialog.get_response()

 def on_play(self, *args, **kwargs):
  try:
   sound.player.play(self.files[self.dialog.items.GetSelection()]+".ogg")
  except:
   log.exception("Error playing the %s sound" % (self.files[self.dialog.items.GetSelection()],))