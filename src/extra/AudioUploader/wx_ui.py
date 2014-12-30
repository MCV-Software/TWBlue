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
import widgetUtils
import output

class audioDialog(widgetUtils.BaseDialog):
 def __init__(self, services):
  super(audioDialog, self).__init__(None, -1, _(u"Attach audio"))
  panel = wx.Panel(self)
  sizer = wx.BoxSizer(wx.VERTICAL)
  self.play = wx.Button(panel, -1, _(u"Play"))
  self.play.Disable()
  self.pause = wx.Button(panel, -1, _(u"Pause"))
  self.pause.Disable()
  self.record = wx.Button(panel, -1, _(u"Record"))
  self.record.SetFocus()
  self.attach_exists = wx.Button(panel, -1, _(u"Add an existing file"))
  self.discard = wx.Button(panel, -1, _(u"Discard"))
  self.discard.Disable()
  label = wx.StaticText(panel, -1, _(u"Upload to"))
  self.services = wx.ComboBox(panel, -1, choices=services, value=services[0], style=wx.CB_READONLY)
  servicesBox = wx.BoxSizer(wx.HORIZONTAL)
  servicesBox.Add(label)
  servicesBox.Add(self.services)
  self.attach = wx.Button(panel, wx.ID_OK, _(u"Attach"))
  self.attach.Disable()
  cancel = wx.Button(panel, wx.ID_CANCEL, _(u"Cancel"))
  sizer.Add(self.play)
  sizer.Add(self.pause)
  sizer.Add(self.record)
  sizer.Add(self.attach_exists)
  sizer.Add(self.discard)
  sizer.Add(self.attach)

 def enable_control(self, control):
  if hasattr(self, control):
   getattr(self, control).Enable()

 def disable_control(self, control):
  if hasattr(self, control):
   getattr(self, control).Disable()

 def get_file(self):
  openFileDialog = wx.FileDialog(self, _(u"Select the audio file to be uploaded"), "", "", _("Audio Files (*.mp3, *.ogg, *.wav)|*.mp3; *.ogg; *.wav"), wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
  if openFileDialog.ShowModal() == wx.ID_CANCEL:
   return False
  return openFileDialog.GetPath()
