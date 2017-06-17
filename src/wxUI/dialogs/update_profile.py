# -*- coding: utf-8 -*-

import wx
from . import baseDialog

class updateProfileDialog(baseDialog.BaseWXDialog):
 def __init__(self):
  super(updateProfileDialog, self).__init__(parent=None, id=-1)
  self.SetTitle(_("Update your profile"))
  panel = wx.Panel(self)
  labelName = wx.StaticText(panel, -1, _("&Name (20 characters maximum)"))
  self.name = wx.TextCtrl(panel, -1)
  self.name.SetFocus()
  dc = wx.WindowDC(self.name)
  dc.SetFont(self.name.GetFont())
  self.name.SetSize(dc.GetTextExtent("0"*20))
  labelLocation = wx.StaticText(panel, -1, _("&Location"))
  self.location = wx.TextCtrl(panel, -1)
  dc = wx.WindowDC(self.location)
  dc.SetFont(self.location.GetFont())
  self.location.SetSize(dc.GetTextExtent("0"*35))
  labelUrl = wx.StaticText(panel, -1, _("&Website"))
  self.url = wx.TextCtrl(panel, -1)
  dc = wx.WindowDC(self.url)
  dc.SetFont(self.url.GetFont())
  self.url.SetSize(dc.GetTextExtent("0"*22))
  labelDescription = wx.StaticText(panel, -1, _("&Bio (160 characters maximum)"))
  self.description = wx.TextCtrl(panel, -1, size=(400, 400))
  dc = wx.WindowDC(self.description)
  dc.SetFont(self.description.GetFont())
  self.description.SetSize(dc.GetTextExtent("0"*160))
  self.image = None
  self.upload_image = wx.Button(panel, -1, _("Upload a &picture"))
  self.ok = wx.Button(panel, wx.ID_OK, _("&Update profile"))
  self.ok.SetDefault()
  close = wx.Button(panel, wx.ID_CANCEL, _("&Close"))
  sizer = wx.BoxSizer(wx.VERTICAL)
  nameBox = wx.BoxSizer(wx.HORIZONTAL)
  nameBox.Add(labelName, 0, wx.ALL, 5)
  nameBox.Add(self.name, 0, wx.ALL, 5)
  sizer.Add(nameBox, 0, wx.ALL, 5)
  locationBox = wx.BoxSizer(wx.HORIZONTAL)
  locationBox.Add(labelLocation, 0, wx.ALL, 5)
  locationBox.Add(self.location, 0, wx.ALL, 5)
  sizer.Add(locationBox, 0, wx.ALL, 5)
  urlBox = wx.BoxSizer(wx.HORIZONTAL)
  urlBox.Add(labelUrl, 0, wx.ALL, 5)
  urlBox.Add(self.url, 0, wx.ALL, 5)
  sizer.Add(urlBox, 0, wx.ALL, 5)
  descriptionBox = wx.BoxSizer(wx.HORIZONTAL)
  descriptionBox.Add(labelDescription, 0, wx.ALL, 5)
  descriptionBox.Add(self.description, 0, wx.ALL, 5)
  sizer.Add(descriptionBox, 0, wx.ALL, 5)
  sizer.Add(self.upload_image, 5, wx.CENTER, 5)
  btnBox = wx.BoxSizer(wx.HORIZONTAL)
  btnBox.Add(self.ok, 0, wx.ALL, 5)
  btnBox.Add(close, 0, wx.ALL, 5)
  sizer.Add(btnBox, 0, wx.ALL, 5)
  panel.SetSizer(sizer)
  self.SetClientSize(sizer.CalcMin())

 def set_name(self, name):
  self.set("name", name)

 def set_description(self, description):
  self.set("description", description)

 def set_location(self, location):
  self.set("location", location)

 def set_url(self, url):
  self.set("url", url)

 def change_upload_button(self, uploaded=False):
  if uploaded == False:
   self.upload_image.SetLabel(_("Upload a picture"))
  else:
   self.upload_image.SetLabel(_("Discard image"))

 def upload_picture(self):
  openFileDialog = wx.FileDialog(self, _("Select the picture to be uploaded"), "", "", _("Image files (*.png, *.jpg, *.gif)|*.png; *.jpg; *.gif"), wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
  if openFileDialog.ShowModal() == wx.ID_CANCEL:
   return None
  return openFileDialog.GetPath()

 def hide_upload_button(self, hide):
  self.upload_image.Enable(hide)

 def set_readonly(self):
  self.name.style = wx.TE_READONLY
  self.name.Refresh()
  self.description.style = wx.TE_READONLY
  self.description.Refresh()
  self.location.style = wx.TE_READONLY
  self.location.Refresh()
  self.url.style = wx.TE_READONLY
  self.url.Refresh()
  self.hide_upload_button(False)
  self.ok.Enable(False)