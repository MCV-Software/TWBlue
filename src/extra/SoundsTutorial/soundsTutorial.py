# -*- coding: utf-8 -*-
import widgetUtils
import config
import os
import paths
import sound
import wx_ui
import soundsTutorial_constants

class soundsTutorial(object):
 def __init__(self):
  super(soundsTutorial, self).__init__()
  self.actions = []
  [self.actions.append(i[1]) for i in soundsTutorial_constants.actions]
  self.files = []
  [self.files.append(i[0]) for i in soundsTutorial_constants.actions]
  self.dialog = wx_ui.soundsTutorialDialog(self.actions)
  widgetUtils.connect_event(self.dialog.play, widgetUtils.BUTTON_PRESSED, self.on_play)
  self.dialog.get_response()

 def on_play(self, *args, **kwargs):
  sound.player.play(self.files[self.dialog.items.GetSelection()]+".ogg")