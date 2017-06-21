# -*- coding: utf-8 -*-
import wx
import widgetUtils
import application

class autocompletionSettingsDialog(widgetUtils.BaseDialog):
 def __init__(self):
  super(autocompletionSettingsDialog, self).__init__(parent=None, id=-1, title=_("Autocomplete users' settings"))
  panel = wx.Panel(self)
  sizer = wx.BoxSizer(wx.VERTICAL)
  self.followers_buffer = wx.CheckBox(panel, -1, _("Add users from followers buffer"))
  self.friends_buffer = wx.CheckBox(panel, -1, _("Add users from friends buffer"))
  sizer.Add(self.followers_buffer, 0, wx.ALL, 5)
  sizer.Add(self.friends_buffer, 0, wx.ALL, 5)
  self.viewList = wx.Button(panel, -1, _("Manage database..."))
  sizer.Add(self.viewList, 0, wx.ALL, 5)
  ok = wx.Button(panel, wx.ID_OK)
  cancel = wx.Button(panel, wx.ID_CANCEL)
  sizerBtn = wx.BoxSizer(wx.HORIZONTAL)
  sizerBtn.Add(ok, 0, wx.ALL, 5)
  sizer.Add(cancel, 0, wx.ALL, 5)
  sizer.Add(sizerBtn, 0, wx.ALL, 5)
  panel.SetSizer(sizer)
  self.SetClientSize(sizer.CalcMin())

def show_success_dialog():
 wx.MessageDialog(None, _("{0}'s database of users has been updated.").format(application.name,), _("Done"), wx.OK).ShowModal()