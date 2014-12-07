# -*- coding: utf-8 -*-
""" TW Blue

A twitter accessible, easy of use and cross platform application."""
############################################################
#    Copyright(C)2013-2014 Manuel Eduardo Cortéz Vallejo <manuel@manuelcortez.net>
#       
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
############################################################
import wx
import os
ssmg = None
import gui
import paths
import config
import commandline
import platform
from logger import logger as logging
from sessionmanager import manager
from sessionmanager import gui as smGUI
manager.setup()
import sys
import config
import output
import sound
import languageHandler

if hasattr(sys, 'frozen'):
  sys.stderr = open(paths.logs_path("stderr.log"), 'w')
  sys.stdout = open(paths.logs_path("stdout.log"), 'w')

#app = wx.App()
app = wx.App(redirect=True, useBestVisual=True, filename=paths.logs_path('tracebacks.log'))
configured = False
configs = []
for i in os.listdir(paths.config_path()):
 if os.path.isdir(paths.config_path(i)): configs.append(i)
if len(configs) == 1:
 manager.manager.set_current_session(configs[0])
 config.MAINFILE = "%s/session.conf" % (manager.manager.get_current_session())
 config.setup()
 lang=config.main['general']['language']
 languageHandler.setLanguage(lang)
 sound.setup()
 output.setup()
 configured = True
else:
 ssmg = smGUI.sessionManagerWindow()
if configured == True or ssmg.ShowModal() == wx.ID_OK:
 frame = gui.main.mainFrame()
 frame.Show()
 frame.showing = True
 if config.main != None and config.main["general"]["hide_gui"] == True and platform.system() == "Windows":
  frame.show_hide()
  frame.Hide()
 app.SetTopWindow(frame)
else:
 app.Exit()
 ### I should uncomment this
#if platform.system() != "Windows":
# local = wx.Locale(wx.LANGUAGE_DEFAULT)
# local.AddCatalogLookupPathPrefix(paths.locale_path())
# local.AddCatalog("twblue")
#ap = app(redirect=True, useBestVisual=True, filename=paths.logs_path('tracebacks.log'))
#wx.CallLater(10, start)
app.MainLoop()

