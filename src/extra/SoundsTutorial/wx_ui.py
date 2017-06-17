# -*- coding: utf-8 -*-
import wx
import widgetUtils

class soundsTutorialDialog(widgetUtils.BaseDialog):
 def __init__(self, actions):
  super(soundsTutorialDialog, self).__init__(None, -1)
  self.SetTitle(_("Sounds tutorial"))
  panel = wx.Panel(self)
  sizer = wx.BoxSizer(wx.VERTICAL)
  label = wx.StaticText(panel, -1, _("Press enter to listen to the sound for the selected event"))
  self.items = wx.ListBox(panel, 1, choices=actions, style=wx.LB_SINGLE)
  self.items.SetSelection(0)
  listBox = wx.BoxSizer(wx.HORIZONTAL)
  listBox.Add(label)
  listBox.Add(self.items)
  self.play = wx.Button(panel, 1, ("Play"))
  self.play.SetDefault()
  close = wx.Button(panel, wx.ID_CANCEL)
  btnBox = wx.BoxSizer(wx.HORIZONTAL)
  btnBox.Add(self.play)
  btnBox.Add(close)
  sizer.Add(listBox)
  sizer.Add(btnBox)
  panel.SetSizer(sizer)
  self.SetClientSize(sizer.CalcMin())

 def get_selection(self):
  return self.items.GetSelection()