# -*- coding: utf-8 -*-
import wx
from multiplatform_widgets import widgets
from wxUI.dialogs import baseDialog

class keystrokeEditorDialog(baseDialog.BaseWXDialog):
 def __init__(self):
  super(keystrokeEditorDialog, self).__init__(parent=None, id=-1, title=_("Keystroke editor"))
  panel = wx.Panel(self)
  self.actions = []
  sizer = wx.BoxSizer(wx.VERTICAL)
  keysText = wx.StaticText(panel, -1, _("Select a keystroke to edit"))
  self.keys = widgets.list(self, _("Action"), _("Keystroke"), style=wx.LC_REPORT|wx.LC_SINGLE_SEL, size=(400, 450))
  self.keys.list.SetFocus()
  firstSizer = wx.BoxSizer(wx.HORIZONTAL)
  firstSizer.Add(keysText, 0, wx.ALL, 5)
  firstSizer.Add(self.keys.list, 0, wx.ALL, 5)
  self.edit = wx.Button(panel, -1, _("Edit"))
  self.edit.SetDefault()
  self.execute = wx.Button(panel, -1, _("Execute action"))
  close = wx.Button(panel, wx.ID_CANCEL, _("Close"))
  secondSizer = wx.BoxSizer(wx.HORIZONTAL)
  secondSizer.Add(self.edit, 0, wx.ALL, 5)
  secondSizer.Add(self.execute, 0, wx.ALL, 5)
  secondSizer.Add(close, 0, wx.ALL, 5)
  sizer.Add(firstSizer, 0, wx.ALL, 5)
  sizer.Add(secondSizer, 0, wx.ALL, 5)
  panel.SetSizer(sizer)
  self.SetClientSize(sizer.CalcMin())

 def put_keystrokes(self, actions, keystrokes):
  selection = self.keys.get_selected()
  self.keys.clear()
  for i in keystrokes:
   if (i in actions) == False:
    continue
   action = actions[i]
   self.actions.append(i)
   keystroke = keystrokes[i]
   self.keys.insert_item(False, *[action, keystroke])
  self.keys.select_item(selection)

 def get_action(self):
  return self.keys.get_selected()

class editKeystrokeDialog(baseDialog.BaseWXDialog):
 def __init__(self):
  super(editKeystrokeDialog, self).__init__(parent=None, id=-1, title=_("Editing keystroke"))
  panel = wx.Panel(self)
  sizer = wx.BoxSizer(wx.VERTICAL)
  self.control = wx.CheckBox(panel, -1, _("Control"))
  self.alt = wx.CheckBox(panel, -1, _("Alt"))
  self.shift = wx.CheckBox(panel, -1, _("Shift"))
  self.win = wx.CheckBox(panel, -1, _("Windows"))
  sizer1 = wx.BoxSizer(wx.HORIZONTAL)
  sizer1.Add(self.control)
  sizer1.Add(self.alt)
  sizer1.Add(self.shift)
  sizer1.Add(self.win)
  charLabel = wx.StaticText(panel, -1, _("Key"))
  self.key = wx.TextCtrl(panel, -1)
  sizer2 = wx.BoxSizer(wx.HORIZONTAL)
  sizer2.Add(charLabel)
  sizer2.Add(self.key)
  ok = wx.Button(panel, wx.ID_OK, _("OK"))
  ok.SetDefault()
  cancel = wx.Button(panel, wx.ID_CANCEL)
  sizer3 = wx.BoxSizer(wx.HORIZONTAL)
  sizer3.Add(ok)
  sizer3.Add(cancel)
  sizer.Add(sizer1)
  sizer.Add(sizer2)
  sizer.Add(sizer3)
  panel.SetSizerAndFit(sizer)


def no_win_message():
 return wx.MessageDialog(None, _("You need to use the Windows key"), _("Invalid keystroke"), wx.OK|wx.ICON_ERROR).ShowModal()

def no_key():
 return wx.MessageDialog(None, _("You must provide a character for the keystroke"), _("Invalid keystroke"), wx.ICON_ERROR).ShowModal()