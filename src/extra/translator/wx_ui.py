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
from . import translator
import wx
from wxUI.dialogs import baseDialog

class translateDialog(baseDialog.BaseWXDialog):
 def __init__(self):
  super(translateDialog, self).__init__(None, -1, title=_("Translate message"))
  panel = wx.Panel(self)
  sizer = wx.BoxSizer(wx.VERTICAL)
  staticSource = wx.StaticText(panel, -1, _("Source language"))
  self.source_lang = wx.ComboBox(panel, -1, choices=[x[1] for x in translator.available_languages()], style = wx.CB_READONLY)
  self.source_lang.SetFocus()
  staticDest = wx.StaticText(panel, -1, _("Target language"))
  self.source_lang.SetSelection(0)
  self.dest_lang = wx.ComboBox(panel, -1, choices=[x[1] for x in translator.available_languages()], style = wx.CB_READONLY)
  listSizer = wx.BoxSizer(wx.HORIZONTAL)
  listSizer.Add(staticSource)
  listSizer.Add(self.source_lang)
  listSizer.Add(staticDest)
  listSizer.Add(self.dest_lang)
  ok = wx.Button(panel, wx.ID_OK)
  ok.SetDefault()
  cancel = wx.Button(panel, wx.ID_CANCEL)
  self.SetEscapeId(wx.ID_CANCEL)

 def get(self, control):
  return getattr(self, control).GetSelection()