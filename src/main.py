# -*- coding: utf-8 -*-
import languageHandler
import wx
import paths
import commandline
import config
import sound
import output

def setup():
 config.setup()
 sound.setup()
 output.setup()
 languageHandler.setLanguage(config.app["app-settings"]["language"])
 from controller import mainController
 from sessionmanager import sessionManager
 app = wx.App()
 sm = sessionManager.sessionManagerController()
 sm.fill_list()
 if len(sm.sessions) == 0: sm.show()
 else:
  sm.do_ok()
 del sm
 r = mainController.Controller()
 r.view.Show()
 sound.player.play("ready.ogg")
 app.MainLoop()

setup()