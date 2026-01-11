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
from pubsub import pub
from wxUI.dialogs import baseDialog

class translateDialog(baseDialog.BaseWXDialog):
    def __init__(self):
        super(translateDialog, self).__init__(None, -1, title=_(u"Translate message"))
        self.engines = ["LibreTranslate", "DeepL"]
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        staticEngine = wx.StaticText(panel, -1, _(u"Translation engine"))
        self.engine_select = wx.ComboBox(panel, -1, choices=self.engines, style=wx.CB_READONLY)
        self.engine_select.Bind(wx.EVT_COMBOBOX, lambda event: pub.sendMessage("translator.engine_changed", engine=self.engine_select.GetValue()))
        staticDest = wx.StaticText(panel, -1, _(u"Target language"))
        self.dest_lang = wx.ComboBox(panel, -1, style = wx.CB_READONLY)
        self.dest_lang.SetFocus()
        self.dest_lang.SetSelection(0)
        engineSizer = wx.BoxSizer(wx.HORIZONTAL)
        engineSizer.Add(staticEngine)
        engineSizer.Add(self.engine_select)
        listSizer = wx.BoxSizer(wx.HORIZONTAL)
        listSizer.Add(staticDest)
        listSizer.Add(self.dest_lang)
        ok = wx.Button(panel, wx.ID_OK)
        ok.SetDefault()
        cancel = wx.Button(panel, wx.ID_CANCEL)
        self.SetEscapeId(wx.ID_CANCEL)
        sizer.Add(engineSizer, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(listSizer, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(ok, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        sizer.Add(cancel, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        panel.SetSizer(sizer)

    def set_languages(self, languages):
        wx.CallAfter(self.dest_lang.SetItems, languages)

    def get(self, control):
        return getattr(self, control).GetSelection()
