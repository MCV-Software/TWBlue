# -*- coding: utf-8 -*-
############################################################
#    Copyright (c) 2013, 2014 Manuel Eduardo Cortéz Vallejo <manuel@manuelcortez.net>
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
from . import baseDialog

class selectUserDialog(baseDialog.BaseWXDialog):
 def __init__(self, title, users):
  super(selectUserDialog, self).__init__(parent=None, id=wx.NewId(), title=title)
  panel = wx.Panel(self)
  userSizer = wx.BoxSizer()
  self.cb = wx.ComboBox(panel, -1, choices=users, value=users[0], size=wx.DefaultSize)
  self.cb.SetFocus()
  self.autocompletion = wx.Button(panel, -1, _("&Autocomplete users"))
  userSizer.Add(wx.StaticText(panel, -1, _("User")), 0, wx.ALL, 5)
  userSizer.Add(self.cb, 0, wx.ALL, 5)
  userSizer.Add(self.autocompletion, 0, wx.ALL, 5)
  sizer = wx.BoxSizer(wx.VERTICAL)
  ok = wx.Button(panel, wx.ID_OK, _("OK"))
  ok.SetDefault()
#  ok.Bind(wx.EVT_BUTTON, self.onok)
  cancel = wx.Button(panel, wx.ID_CANCEL, _("Close"))
  btnsizer = wx.BoxSizer()
  btnsizer.Add(ok, 0, wx.ALL, 5)
  btnsizer.Add(cancel, 0, wx.ALL, 5)
  sizer.Add(userSizer, 0, wx.ALL, 5)
  sizer.Add(btnsizer, 0, wx.ALL, 5)
  panel.SetSizer(sizer)
  self.SetClientSize(sizer.CalcMin())

 def get_user(self):
  return self.cb.GetValue()

