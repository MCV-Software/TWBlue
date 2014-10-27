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

ssmg = None
import gui
import paths
import config
import commandline
import platform
if platform.system() == "Windows":
 from logger import logger as logging
if platform.system() == "Darwin":
 import osx_prepare
 osx_prepare.setup()
from sessionmanager import manager
from sessionmanager import gui as smGUI
manager.setup()
import sys

if hasattr(sys, 'frozen'):
  sys.stderr = open(paths.logs_path("stderr.log"), 'w')
  sys.stdout = open(paths.logs_path("stdout.log"), 'w')

class app(wx.App):
 def __init__(self, *args, **kwargs):
  super(app, self).__init__(*args, **kwargs)
  if platform.system() != "Darwin":
   self.start()
  else:
   self.mac()

 def mac(self):
  self.hold_frame = wx.Frame(title="None", parent=None)
  self.hold_frame.Show()
  wx.CallLater(10, self.start)

 def start(self):
  ssmg = smGUI.sessionManagerWindow()
  if ssmg.ShowModal() == wx.ID_OK:
   frame = gui.main.mainFrame()
   frame.Show()
   frame.showing = True
   if config.main != None and config.main["general"]["hide_gui"] == True and platform.system() == "Windows":
    frame.show_hide()
    frame.Hide()
   self.SetTopWindow(frame)
   if hasattr(self, "frame"): self.hold_frame.Hide()
  # If the user press on cancel.
  else:
   self.Exit()

ap = app()
 ### I should uncomment this
#if platform.system() != "Windows":
# local = wx.Locale(wx.LANGUAGE_DEFAULT)
# local.AddCatalogLookupPathPrefix(paths.locale_path())
# local.AddCatalog("twblue")
#ap = app(redirect=True, useBestVisual=True, filename=paths.logs_path('tracebacks.log'))
#wx.CallLater(10, start)
ap.MainLoop()

