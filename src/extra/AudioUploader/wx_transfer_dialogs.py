# -*- coding: utf-8 -*-

import wx
from .utils import *
import widgetUtils

class UploadDialog(widgetUtils.BaseDialog):

 def __init__(self, filename, *args, **kwargs):
  super(UploadDialog, self).__init__(parent=None, id=wx.NewId(), *args, **kwargs)
  self.pane = wx.Panel(self)
  self.progress_bar = wx.Gauge(parent=self.pane)
  fileBox = wx.BoxSizer(wx.HORIZONTAL)
  fileLabel = wx.StaticText(self.pane, -1, _("File"))
  self.file = wx.TextCtrl(self.pane, -1, value=filename, style=wx.TE_READONLY|wx.TE_MULTILINE, size=(200, 100))
  self.file.SetFocus()
  fileBox.Add(fileLabel)
  fileBox.Add(self.file)
  currentAmountBox = wx.BoxSizer(wx.HORIZONTAL)
  current_amount_label = wx.StaticText(self.pane, -1, _("Transferred"))
  self.current_amount = wx.TextCtrl(self.pane, -1, value='0', style=wx.TE_READONLY|wx.TE_MULTILINE)
  currentAmountBox.Add(current_amount_label)
  currentAmountBox.Add(self.current_amount)
  totalSizeBox = wx.BoxSizer(wx.HORIZONTAL)
  total_size_label = wx.StaticText(self.pane, -1, _("Total file size"))
  self.total_size = wx.TextCtrl(self.pane, -1, value='0', style=wx.TE_READONLY|wx.TE_MULTILINE)
  totalSizeBox.Add(total_size_label)
  totalSizeBox.Add(self.total_size)
  speedBox = wx.BoxSizer(wx.HORIZONTAL)
  speedLabel = wx.StaticText(self.pane, -1, _("Transfer rate"))
  self.speed = wx.TextCtrl(self.pane, -1, style=wx.TE_READONLY|wx.TE_MULTILINE, value="0 Kb/s")
  speedBox.Add(speedLabel)
  speedBox.Add(self.speed)
  etaBox = wx.BoxSizer(wx.HORIZONTAL)
  etaLabel = wx.StaticText(self.pane, -1, _("Time left"))
  self.eta = wx.TextCtrl(self.pane, -1, style=wx.TE_READONLY|wx.TE_MULTILINE, value="Unknown", size=(200, 100))
  etaBox.Add(etaLabel)
  etaBox.Add(self.eta)
  self.create_buttons()
  sizer = wx.BoxSizer(wx.VERTICAL)
  sizer.Add(fileBox)
  sizer.Add(currentAmountBox)
  sizer.Add(totalSizeBox)
  sizer.Add(speedBox)
  sizer.Add(etaBox)
  sizer.Add(self.progress_bar)
  self.pane.SetSizerAndFit(sizer)

 def update(self, data):
  wx.CallAfter(self.progress_bar.SetValue, data["percent"])
  wx.CallAfter(self.current_amount.SetValue, '%s (%d%%)' % (convert_bytes(data["current"]), data["percent"]))
  wx.CallAfter(self.total_size.SetValue, convert_bytes(data["total"]))
  wx.CallAfter(self.speed.SetValue, data["speed"])
  if data["eta"]:
   wx.CallAfter(self.eta.SetValue, seconds_to_string(data["eta"]))

 def create_buttons(self):
  self.cancel_button = wx.Button(parent=self.pane, id=wx.ID_CANCEL)

 def get_response(self, fn):
  wx.CallAfter(fn, 0.01)
  self.ShowModal()
