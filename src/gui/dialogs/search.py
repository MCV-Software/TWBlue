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

class searchDialog(wx.Dialog):
 def __init__(self):
  super(searchDialog, self).__init__(None, -1)
  panel = wx.Panel(self)
  sizer = wx.BoxSizer(wx.VERTICAL)
  self.SetTitle(_(u"Search on Twitter"))
  label = wx.StaticText(panel, -1, _(u"Search"))
  self.term = wx.TextCtrl(panel, -1,)
  dc = wx.WindowDC(self.term)
  dc.SetFont(self.term.GetFont())
  self.term.SetSize(dc.GetTextExtent("0"*40))
  sizer.Add(label, 0, wx.ALL, 5)
  sizer.Add(self.term, 0, wx.ALL, 5)
  self.tweets = wx.RadioButton(panel, -1, _(u"Tweets"), style=wx.RB_GROUP)
  self.users = wx.RadioButton(panel, -1, _(u"Users"))
  radioSizer = wx.BoxSizer(wx.HORIZONTAL)
  radioSizer.Add(self.tweets, 0, wx.ALL, 5)
  radioSizer.Add(self.users, 0, wx.ALL, 5)
  sizer.Add(radioSizer, 0, wx.ALL, 5)
  ok = wx.Button(panel, wx.ID_OK, _(u"OK"))
  ok.SetDefault()
  cancel = wx.Button(panel, wx.ID_CANCEL, _(u"Close"))
  btnsizer = wx.BoxSizer()
  btnsizer.Add(ok, 0, wx.ALL, 5)
  btnsizer.Add(cancel, 0, wx.ALL, 5)
  sizer.Add(btnsizer, 0, wx.ALL, 5)
  panel.SetSizer(sizer)
  self.SetClientSize(sizer.CalcMin())
