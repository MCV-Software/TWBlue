# -*- coding: utf-8 -*-
############################################################
#    Copyright (c) 2014 Manuel Eduardo Cortéz Vallejo <manuel@manuelcortez.net>
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

class trendingTopicsDialog(wx.Dialog):
 def __init__(self, information):
  super(trendingTopicsDialog, self).__init__(None, -1)
  self.countries = {}
  self.cities = {}
  self.information = information
  self.split_information()
  panel = wx.Panel(self)
  sizer = wx.BoxSizer(wx.VERTICAL)
  self.SetTitle(_(u"View trending topics"))
  label = wx.StaticText(panel, -1, _(u"Trending topics by"))
  sizer.Add(label, 0, wx.ALL, 5)
  self.country = wx.RadioButton(panel, -1, _(u"Country"), style=wx.RB_GROUP)
  self.city = wx.RadioButton(panel, -1, _(u"City"))
  self.Bind(wx.EVT_RADIOBUTTON, self.get_places, self.country)
  self.Bind(wx.EVT_RADIOBUTTON, self.get_places, self.city)

  radioSizer = wx.BoxSizer(wx.HORIZONTAL)
  radioSizer.Add(label, 0, wx.ALL, 5)
  radioSizer.Add(self.country, 0, wx.ALL, 5)
  radioSizer.Add(self.city, 0, wx.ALL, 5)
  sizer.Add(radioSizer, 0, wx.ALL, 5)
  label = wx.StaticText(panel, -1, _(u"Location"))
  self.location = wx.ListBox(panel, -1, choices=[], style=wx.CB_READONLY)
  self.get_places()
  locationBox = wx.BoxSizer(wx.HORIZONTAL)
  locationBox.Add(label, 0, wx.ALL, 5)
  locationBox.Add(self.location, 0, wx.ALL, 5)
  sizer.Add(locationBox, 0, wx.ALL, 5)
  ok = wx.Button(panel, wx.ID_OK, _(u"OK"))
  ok.SetDefault()
  cancel = wx.Button(panel, wx.ID_CANCEL, _(u"Close"))
  btnsizer = wx.BoxSizer()
  btnsizer.Add(ok, 0, wx.ALL, 5)
  btnsizer.Add(cancel, 0, wx.ALL, 5)
  sizer.Add(btnsizer, 0, wx.ALL, 5)
  panel.SetSizer(sizer)
  self.SetClientSize(sizer.CalcMin())

 def split_information(self):
  for i in self.information:
   if i["placeType"]["name"] == "Country":
    self.countries[i["name"]] = i["woeid"]
   else:
    self.cities[i["name"]] = i["woeid"]

 def get_places(self, event=None):
  values = []
  if self.country.GetValue() == True:
   for i in self.information:
    if i["placeType"]["name"] == "Country":
     values.append(i["name"])
  elif self.city.GetValue() == True:
   for i in self.information:
    if i["placeType"]["name"] != "Country":
     values.append(i["name"])
  self.location.Set(values)
   