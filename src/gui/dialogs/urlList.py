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
import webbrowser
import url_shortener

class urlList(wx.Dialog):
 def __init__(self, urls):
  self.urls = urls
  super(urlList, self).__init__(parent=None, title=_(u"Select an URL"))
  panel = wx.Panel(self)
#  label = wx.StaticText(panel, -1, _(u"Select a URL"))
  self.lista = wx.ListBox(panel, -1)
  self.lista.SetFocus()
  self.populate_list()
  self.lista.SetSelection(0)
  self.lista.SetSize(self.lista.GetBestSize())
  sizer = wx.BoxSizer(wx.VERTICAL)
#  sizer.Add(label, 0, wx.ALL, 5)
  sizer.Add(self.lista, 0, wx.ALL, 5)
  goBtn = wx.Button(panel, wx.ID_OK)
  goBtn.SetDefault()
  goBtn.Bind(wx.EVT_BUTTON, self.onGo)
  cancelBtn = wx.Button(panel, wx.ID_CANCEL)
  btnSizer = wx.BoxSizer()
  btnSizer.Add(goBtn, 0, wx.ALL, 5)
  btnSizer.Add(cancelBtn, 0, wx.ALL, 5)
  sizer.Add(btnSizer, 0, wx.ALL, 5)
  panel.SetSizer(sizer)
  self.SetClientSize(sizer.CalcMin())

 def onGo(self, ev):
  webbrowser.open(self.lista.GetStringSelection())
  self.Destroy()

 def populate_list(self):
  for i in self.urls:
   self.lista.Append(i)

class shorten(urlList):
 def __init__(self, urls, parent):
  urlList.__init__(self, urls)
  self.parent = parent

 def onGo(self, ev):
  self.parent.text.SetValue(self.parent.text.GetValue().replace(self.lista.GetStringSelection(), url_shortener.shorten(self.lista.GetStringSelection())))
  self.Destroy()

class unshorten(shorten):
 def __init__(self, urls, parent):
  shorten.__init__(self, urls, parent)

 def onGo(self, ev):
  self.parent.text.SetValue(self.parent.text.GetValue().replace(self.lista.GetStringSelection(), url_shortener.unshorten(self.lista.GetStringSelection())))
  self.Destroy()