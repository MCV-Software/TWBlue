# -*- coding: utf-8 -*-
import config
import wx
import constants
from multiplatform_widgets import widgets
from constants import actions
from pubsub import pub

class keystrokeEditor(wx.Dialog):
 def __init__(self):
  super(keystrokeEditor, self).__init__(parent=None, id=-1, title=_(u"Keystroke editor"))
  panel = wx.Panel(self)
  self.actions = []
  sizer = wx.BoxSizer(wx.VERTICAL)
  keysText = wx.StaticText(panel, -1, _(u"Select a keystroke to edit"))
  self.keys = widgets.list(self, _(u"Action"), _(u"Keystroke"), style=wx.LC_REPORT|wx.LC_SINGLE_SEL, size=(400, 450))
  self.keys.list.SetFocus()
  firstSizer = wx.BoxSizer(wx.HORIZONTAL)
  firstSizer.Add(keysText)
  firstSizer.Add(self.keys.list)
  edit = wx.Button(panel, -1, _(u"Edit"))
  self.Bind(wx.EVT_BUTTON, self.edit, edit)
  edit.SetDefault()

  close = wx.Button(panel, wx.ID_CANCEL, _(u"Close"))
  secondSizer = wx.BoxSizer(wx.HORIZONTAL)
  secondSizer.Add(edit)
  secondSizer.Add(close)
  sizer.Add(firstSizer)
  sizer.Add(secondSizer)
  panel.SetSizerAndFit(sizer)

 def put_keystrokes(self, **keystrokes):
  for i in keystrokes:
   action = actions[i]
   self.actions.append(i)
   keystroke = keystrokes[i]
   self.keys.insert_item(False, *[action, keystroke])

 def edit(self, ev):
  action = self.actions[self.keys.get_selected()]
  pub.sendMessage("editing_keystroke", action=action, parentDialog=self)

class editKeystroke(wx.Dialog):
 def __init__(self, action, keystroke, keyboard_handler):
  super(editKeystroke, self).__init__(parent=None, id=-1, title=_(u"Editing keystroke"))
  self.parent = parent
  self.keyboard_handler = keyboard_handler
  self.action = action
  self.keystroke = keystroke
  panel = wx.Panel(self)
  sizer = wx.BoxSizer(wx.VERTICAL)
  self.control = wx.CheckBox(panel, -1, _(u"Control"))
  self.alt = wx.CheckBox(panel, -1, _(u"Alt"))
  self.shift = wx.CheckBox(panel, -1, _(u"Shift"))
  self.win = wx.CheckBox(panel, -1, _(u"Windows"))
  sizer1 = wx.BoxSizer(wx.HORIZONTAL)
  sizer1.Add(self.control)
  sizer1.Add(self.alt)
  sizer1.Add(self.shift)
  sizer1.Add(self.win)
  charLabel = wx.StaticText(panel, -1, _(u"Key"))
  self.key = wx.TextCtrl(panel, -1)
#  self.key.SetMaxLength(1)
  sizer2 = wx.BoxSizer(wx.HORIZONTAL)
  sizer2.Add(charLabel)
  sizer2.Add(self.key)
  ok = wx.Button(panel, wx.ID_OK, _(u"OK"))
  ok.SetDefault()
  self.Bind(wx.EVT_BUTTON, self.ok, ok)
  cancel = wx.Button(panel, wx.ID_CANCEL)
  sizer3 = wx.BoxSizer(wx.HORIZONTAL)
  sizer3.Add(ok)
  sizer3.Add(cancel)
  sizer.Add(sizer1)
  sizer.Add(sizer2)
  sizer.Add(sizer3)
  panel.SetSizerAndFit(sizer)
  self.set_default()

 def set_default(self):
  for i in self.keystroke.split("+"):
   if hasattr(self, i):
    key = getattr(self, i)
    key.SetValue(True)
  self.key.SetValue(self.keystroke.split("+")[-1])
  
 def ok(self, ev):
  keys = []
  if self.win.GetValue() == False:
   wx.MessageDialog(self, _(u"You need to use the Windows key"), _(u"Invalid keystroke"), wx.OK|wx.ICON_ERROR).ShowModal()
   return
  if self.control.GetValue() == True:
   keys.append("control")
  if self.win.GetValue() == True:
   keys.append("win")
  if self.alt.GetValue() == True:
   keys.append("alt")
  if self.shift.GetValue() == True:
   keys.append("shift")
  if self.key.GetValue() != "":
   keys.append(self.key.GetValue())
  else:
   wx.MessageDialog(self, _(u"You must provide a character for the keystroke"), _(u"Invalid keystroke"), wx.ICON_ERROR).ShowModal()
   return
  config.main["keymap"][self.action] = "+".join(keys)
  if self.keyboard_handler != None:
   self.keyboard_handler.unregister_key(self.keystroke, getattr(self.parent, self.action))
  self.keyboard_handler.register_key(config.main["keymap"][self.action], getattr(self.parent, self.action))
   
  self.EndModal(wx.ID_OK)