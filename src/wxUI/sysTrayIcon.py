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
from wx import adv
import application
import paths
import os

class SysTrayIcon(adv.TaskBarIcon):

	def __init__(self):
		super(SysTrayIcon, self).__init__()
		icon=wx.Icon(os.path.join(paths.app_path(), "icon.ico"), wx.BITMAP_TYPE_ICO)
		self.SetIcon(icon, application.name)
		self.menu=wx.Menu()
		self.tweet = self.menu.Append(wx.ID_ANY, _("Tweet"))
		self.global_settings = self.menu.Append(wx.ID_ANY, _("&Global settings"))
		self.account_settings = self.menu.Append(wx.ID_ANY, _("Account se&ttings"))
		self.update_profile = self.menu.Append(wx.ID_ANY, _("Update &profile"))
		self.show_hide = self.menu.Append(wx.ID_ANY, _("&Show / hide"))
		self.doc = self.menu.Append(wx.ID_ANY, _("&Documentation"))
		self.check_for_updates = self.menu.Append(wx.ID_ANY, _("Check for &updates"))
		self.exit = self.menu.Append(wx.ID_ANY, _("&Exit"))

	def show_menu(self):
		self.PopupMenu(self.menu)

	def Destroy(self):
		self.menu.Destroy()
		super(SysTrayIcon, self).Destroy()