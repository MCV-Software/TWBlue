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
import wx, twitter, gui.dialogs, sound, config
from mysc.repeating_timer import RepeatingTimer

class selectUserDialog(wx.Dialog):
 def __init__(self, parent, title):
  self.parent = parent
  wx.Dialog.__init__(self, None, -1)
  panel = wx.Panel(self)
  userSizer = wx.BoxSizer()
  self.SetTitle(title)
  if self.parent.nb.GetCurrentPage().name_buffer == "followers" or self.parent.nb.GetCurrentPage().name_buffer == "friends":
   list = [self.parent.db.settings[self.parent.nb.GetCurrentPage().name_buffer][self.parent.nb.GetCurrentPage().list.get_selected()]["screen_name"]]
  else:
   try: list =twitter.utils.get_all_users(self.parent.db.settings[self.parent.nb.GetCurrentPage().name_buffer][self.parent.nb.GetCurrentPage().list.get_selected()], self.parent.db)
   except KeyError: list = [self.parent.db.settings[self.parent.nb.GetCurrentPage().name_buffer][self.parent.nb.GetCurrentPage().list.get_selected()]["screen_name"]]
  self.cb = wx.ComboBox(panel, -1, choices=list, value=list[0], size=wx.DefaultSize)
  self.cb.SetFocus()
  userSizer.Add(wx.StaticText(panel, -1, _(u"User")), 0, wx.ALL, 5)
  userSizer.Add(self.cb)
  sizer = wx.BoxSizer(wx.VERTICAL)
  ok = wx.Button(panel, wx.ID_OK, _(u"OK"))
  ok.SetDefault()
#  ok.Bind(wx.EVT_BUTTON, self.onok)
  cancel = wx.Button(panel, wx.ID_CANCEL, _(u"Close"))
  btnsizer = wx.BoxSizer()
  btnsizer.Add(ok, 0, wx.ALL, 5)
  btnsizer.Add(cancel, 0, wx.ALL, 5)
  sizer.Add(userSizer, 0, wx.ALL, 5)
  sizer.Add(btnsizer, 0, wx.ALL, 5)
  panel.SetSizer(sizer)
  self.SetClientSize(sizer.CalcMin())