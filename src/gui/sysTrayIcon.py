# -*- coding: utf-8 -*-
""" A systray for TW Blue """
############################################################
#    Copyright (c) 2014 José Manuel Delicado Alcolea <jmdaweb@gmail.com>
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
import application
import paths
import os

class SysTrayIcon(wx.TaskBarIcon):

	def __init__(self, frame):
		super(SysTrayIcon, self).__init__()
		self.frame=frame
		icon=wx.Icon(os.path.join(paths.app_path(), "icon.ico"), wx.BITMAP_TYPE_ICO)
		self.SetIcon(icon, application.name)
		self.menu=wx.Menu()
		item=self.menu.Append(wx.ID_ANY, _(u"Tweet"))
		self.Bind(wx.EVT_MENU, frame.compose, item)
		item=self.menu.Append(wx.ID_ANY, _(u"Preferences"))
		self.Bind(wx.EVT_MENU, frame.preferences, item)
		item=self.menu.Append(wx.ID_ANY, _(u"Update profile"))
		self.Bind(wx.EVT_MENU, frame.update_profile, item)
		item=self.menu.Append(wx.ID_ANY, _(u"Show / hide"))
		self.Bind(wx.EVT_MENU, frame.show_hide, item)
		item=self.menu.Append(wx.ID_ANY, _(u"Documentation"))
		self.Bind(wx.EVT_MENU, frame.onManual, item)
		item=self.menu.Append(wx.ID_ANY, _(u"Check for updates"))
		self.Bind(wx.EVT_MENU, frame.onCheckForUpdates, item)
		item=self.menu.Append(wx.ID_ANY, _(u"Exit"))
		self.Bind(wx.EVT_MENU, frame.close, item)
		self.Bind(wx.EVT_TASKBAR_RIGHT_DOWN, self.onRightClick)
		self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.onLeftClick)

	def onRightClick(self, evt):
		self.PopupMenu(self.menu)

	def onLeftClick(self, evt):
		if (self.frame.showing):
			self.frame.SetFocus()
		else:
			self.frame.show_hide()

	def Destroy(self):
		self.menu.Destroy()
		super(SysTrayIcon, self).Destroy()
