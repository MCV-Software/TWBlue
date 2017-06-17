# -*- coding: utf-8 -*-
import wx
import widgetUtils
from multiplatform_widgets import widgets
import application
class autocompletionManageDialog(widgetUtils.BaseDialog):
 def __init__(self):
  super(autocompletionManageDialog, self).__init__(parent=None, id=-1, title=_("Manage Autocompletion database"))
  panel = wx.Panel(self)
  sizer = wx.BoxSizer(wx.VERTICAL)
  label = wx.StaticText(panel, -1, _("Editing {0} users database").format(application.name,))
  self.users = widgets.list(panel, _("Username"), _("Name"), style=wx.LC_REPORT)
  sizer.Add(label, 0, wx.ALL, 5)
  sizer.Add(self.users.list, 0, wx.ALL, 5)
  self.add = wx.Button(panel, -1, _("Add user"))
  self.remove = wx.Button(panel, -1, _("Remove user"))
  optionsBox = wx.BoxSizer(wx.HORIZONTAL)
  optionsBox.Add(self.add, 0, wx.ALL, 5)
  optionsBox.Add(self.remove, 0, wx.ALL, 5)
  sizer.Add(optionsBox, 0, wx.ALL, 5)
  ok = wx.Button(panel, wx.ID_OK)
  cancel = wx.Button(panel, wx.ID_CANCEL)
  sizerBtn = wx.BoxSizer(wx.HORIZONTAL)
  sizerBtn.Add(ok, 0, wx.ALL, 5)
  sizer.Add(cancel, 0, wx.ALL, 5)
  sizer.Add(sizerBtn, 0, wx.ALL, 5)
  panel.SetSizer(sizer)
  self.SetClientSize(sizer.CalcMin())

 def put_users(self, users):
  for i in users:
   j = [i[0], i[1]]
   self.users.insert_item(False, *j)

 def get_user(self):
  usr = False
  userDlg = wx.TextEntryDialog(None, _("Twitter username"), _("Add user to database"))
  if userDlg.ShowModal() == wx.ID_OK:
   usr = userDlg.GetValue()
  return usr

 def show_invalid_user_error(self):
  wx.MessageDialog(None, _("The user does not exist"), _("Error!"), wx.ICON_ERROR).ShowModal()