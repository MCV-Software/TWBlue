# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
from . import baseDialog
import wx

class trendingTopicsDialog(baseDialog.BaseWXDialog):
 def __init__(self):
  super(trendingTopicsDialog, self).__init__(None, -1)
  panel = wx.Panel(self)
  sizer = wx.BoxSizer(wx.VERTICAL)
  self.SetTitle(_("View trending topics"))
  label = wx.StaticText(panel, -1, _("Trending topics by"))
  sizer.Add(label, 0, wx.ALL, 5)
  self.country = wx.RadioButton(panel, -1, _("Country"), style=wx.RB_GROUP)
  self.city = wx.RadioButton(panel, -1, _("City"))
  radioSizer = wx.BoxSizer(wx.HORIZONTAL)
  radioSizer.Add(label, 0, wx.ALL, 5)
  radioSizer.Add(self.country, 0, wx.ALL, 5)
  radioSizer.Add(self.city, 0, wx.ALL, 5)
  sizer.Add(radioSizer, 0, wx.ALL, 5)
  label = wx.StaticText(panel, -1, _("&Location"))
  self.location = wx.ListBox(panel, -1, choices=[], style=wx.CB_READONLY)
  locationBox = wx.BoxSizer(wx.HORIZONTAL)
  locationBox.Add(label, 0, wx.ALL, 5)
  locationBox.Add(self.location, 0, wx.ALL, 5)
  sizer.Add(locationBox, 0, wx.ALL, 5)
  ok = wx.Button(panel, wx.ID_OK, _("&OK"))
  ok.SetDefault()
  cancel = wx.Button(panel, wx.ID_CANCEL, _("&Close"))
  btnsizer = wx.BoxSizer()
  btnsizer.Add(ok, 0, wx.ALL, 5)
  btnsizer.Add(cancel, 0, wx.ALL, 5)
  sizer.Add(btnsizer, 0, wx.ALL, 5)
  panel.SetSizer(sizer)
  self.SetClientSize(sizer.CalcMin())

 def get_active(self):
  if self.country.GetValue() == True:
   return "country"
  else:
   return "city"

 def get_item(self):
  return self.location.GetStringSelection()

 def set(self, values):
  self.location.Set(values)