# -*- coding: utf-8 -*-
import wx
import baseDialog

class textLimited(baseDialog.BaseWXDialog):
 def __init__(self, *args, **kwargs):
  super(textLimited, self).__init__(parent=None, *args, **kwargs)

 def createTextArea(self, message="", text=""):
  self.panel = wx.Panel(self)
  self.label = wx.StaticText(self.panel, -1, message)
  self.SetTitle(str(len(text)))
  self.text = wx.TextCtrl(self.panel, -1, text)
  font = self.text.GetFont()
  dc = wx.WindowDC(self.text)
  dc.SetFont(font)
  x, y = dc.GetTextExtent("00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000")
  self.text.SetSize((x, y))
  self.text.SetFocus()
  self.textBox = wx.BoxSizer(wx.HORIZONTAL)
  self.textBox.Add(self.label, 0, wx.ALL, 5)
  self.textBox.Add(self.text, 0, wx.ALL, 5)

 def get_text(self):
  return self.text.GetValue()

 def set_text(self, text):
  return self.text.ChangeValue(text)

 def onSelect(self, ev):
  self.text.SelectAll()

class tweet(textLimited):
 def createControls(self, message, title, text):
  self.mainBox = wx.BoxSizer(wx.VERTICAL)
  self.createTextArea(message, text)
  self.mainBox.Add(self.textBox, 0, wx.ALL, 5)
  self.upload_image = wx.Button(self.panel, -1, _(u"Upload a picture"), size=wx.DefaultSize)
  self.spellcheck = wx.Button(self.panel, -1, _("Spelling correction"), size=wx.DefaultSize)
  self.attach = wx.Button(self.panel, -1, _(u"Attach audio"), size=wx.DefaultSize)
  self.shortenButton = wx.Button(self.panel, -1, _(u"Shorten URL"), size=wx.DefaultSize)
  self.unshortenButton = wx.Button(self.panel, -1, _(u"Expand URL"), size=wx.DefaultSize)
  self.shortenButton.Disable()
  self.unshortenButton.Disable()
  self.translateButton = wx.Button(self.panel, -1, _(u"Translate message"), size=wx.DefaultSize)
  self.okButton = wx.Button(self.panel, wx.ID_OK, _(u"Send"), size=wx.DefaultSize)
  self.okButton.SetDefault()
  cancelButton = wx.Button(self.panel, wx.ID_CANCEL, _(u"Close"), size=wx.DefaultSize)
  self.buttonsBox1 = wx.BoxSizer(wx.HORIZONTAL)
  self.buttonsBox1.Add(self.upload_image, 0, wx.ALL, 5)
  self.buttonsBox1.Add(self.spellcheck, 0, wx.ALL, 5)
  self.buttonsBox1.Add(self.attach, 0, wx.ALL, 5)
  self.mainBox.Add(self.buttonsBox1, 0, wx.ALL, 5)
  self.buttonsBox2 = wx.BoxSizer(wx.HORIZONTAL)
  self.buttonsBox2.Add(self.shortenButton, 0, wx.ALL, 5)
  self.buttonsBox2.Add(self.unshortenButton, 0, wx.ALL, 5)
  self.buttonsBox2.Add(self.translateButton, 0, wx.ALL, 5)
  self.mainBox.Add(self.buttonsBox2, 0, wx.ALL, 5)
  self.ok_cancelSizer = wx.BoxSizer(wx.HORIZONTAL)
  self.ok_cancelSizer.Add(self.okButton, 0, wx.ALL, 5)
  self.ok_cancelSizer.Add(cancelButton, 0, wx.ALL, 5)
  self.mainBox.Add(self.ok_cancelSizer)
  selectId = wx.NewId()
  self.Bind(wx.EVT_MENU, self.onSelect, id=selectId)
  self.accel_tbl = wx.AcceleratorTable([
(wx.ACCEL_CTRL, ord('A'), selectId),
])
  self.SetAcceleratorTable(self.accel_tbl)
  self.panel.SetSizer(self.mainBox)

 def __init__(self, message, title, text):
  super(tweet, self).__init__()
  self.createControls(message, title, text)
#  self.onTimer(wx.EVT_CHAR_HOOK)
  self.SetClientSize(self.mainBox.CalcMin())

class dm(textLimited):
 def createControls(self, message, title, users):
  self.panel = wx.Panel(self)
  self.mainBox = wx.BoxSizer(wx.VERTICAL)
  label = wx.StaticText(self.panel, -1, _(u"Recipient"))
  self.cb = wx.ComboBox(self.panel, -1, choices=users, value=users[0], size=wx.DefaultSize)
  self.createTextArea(message, text="")
  self.mainBox.Add(self.cb, 0, wx.ALL, 5)
  self.mainBox.Add(self.textBox, 0, wx.ALL, 5)
  self.spellcheck = wx.Button(self.panel, -1, _("Spelling correction"), size=wx.DefaultSize)
  self.attach = wx.Button(self.panel, -1, _(u"Attach audio"), size=wx.DefaultSize)
  self.shortenButton = wx.Button(self.panel, -1, _(u"Shorten URL"), size=wx.DefaultSize)
  self.unshortenButton = wx.Button(self.panel, -1, _(u"Expand URL"), size=wx.DefaultSize)
  self.shortenButton.Disable()
  self.unshortenButton.Disable()
  self.translateButton = wx.Button(self.panel, -1, _(u"Translate message"), size=wx.DefaultSize)
  self.okButton = wx.Button(self.panel, wx.ID_OK, _(u"Send"), size=wx.DefaultSize)
  self.okButton.SetDefault()
  cancelButton = wx.Button(self.panel, wx.ID_CANCEL, _(u"Close"), size=wx.DefaultSize)
  self.buttonsBox = wx.BoxSizer(wx.HORIZONTAL)
  self.buttonsBox.Add(self.spellcheck, 0, wx.ALL, 5)
  self.buttonsBox.Add(self.attach, 0, wx.ALL, 5)
  self.mainBox.Add(self.buttonsBox, 0, wx.ALL, 5)
  self.buttonsBox1 = wx.BoxSizer(wx.HORIZONTAL)
  self.buttonsBox1.Add(self.shortenButton, 0, wx.ALL, 5)
  self.buttonsBox1.Add(self.unshortenButton, 0, wx.ALL, 5)
  self.buttonsBox1.Add(self.translateButton, 0, wx.ALL, 5)
  self.mainBox.Add(self.buttonsBox1, 0, wx.ALL, 5)
  self.buttonsBox3 = wx.BoxSizer(wx.HORIZONTAL)
  self.buttonsBox3.Add(self.okButton, 0, wx.ALL, 5)
  self.buttonsBox3.Add(cancelButton, 0, wx.ALL, 5)
  self.mainBox.Add(self.buttonsBox3, 0, wx.ALL, 5)
  self.panel.SetSizer(self.mainBox)
  
 def __init__(self, message, title, users):
  super(dm, self).__init__()
  self.createControls(message, title, users)
#  self.onTimer(wx.EVT_CHAR_HOOK)
  self.SetClientSize(self.mainBox.CalcMin())
  
class reply(tweet):
 def __init__(self, message, title, text):
  super(reply, self).__init__(message, title, text)
  self.text.SetInsertionPoint(len(self.text.GetValue()))
  self.mentionAll = wx.Button(self, -1, _(u"Mention to all"), size=wx.DefaultSize)
  self.mentionAll.Disable()
  self.buttonsBox1.Add(self.mentionAll, 0, wx.ALL, 5)
  self.buttonsBox1.Layout()
  self.mainBox.Layout()
  self.SetClientSize(self.mainBox.CalcMin())

class viewTweet(wx.Dialog):
 def __init__(self, tweet):
  super(viewTweet, self).__init__(None, size=(850,850))
  self.SetTitle(_(u"Tweet - %i characters ") % (len(tweet)))
  panel = wx.Panel(self)
  label = wx.StaticText(panel, -1, _(u"Tweet"))
  self.text = wx.TextCtrl(panel, -1, tweet, style=wx.TE_READONLY|wx.TE_MULTILINE, size=(250, 180))
  dc = wx.WindowDC(self.text)
  dc.SetFont(self.text.GetFont())
  (x, y, z) = dc.GetMultiLineTextExtent("0"*140)
  self.text.SetSize((x, y))
  self.text.SetFocus()
  textBox = wx.BoxSizer(wx.HORIZONTAL)
  textBox.Add(label, 0, wx.ALL, 5)
  textBox.Add(self.text, 1, wx.EXPAND, 5)
  mainBox = wx.BoxSizer(wx.VERTICAL)
  mainBox.Add(textBox, 0, wx.ALL, 5)
  spellcheck = wx.Button(panel, -1, _("Spelling correction"), size=wx.DefaultSize)
  self.unshortenButton = wx.Button(panel, -1, _(u"Expand URL"), size=wx.DefaultSize)
  self.unshortenButton.Disable()
  translateButton = wx.Button(panel, -1, _(u"Translate message"), size=wx.DefaultSize)
  cancelButton = wx.Button(panel, wx.ID_CANCEL, _(u"Close"), size=wx.DefaultSize)
  buttonsBox = wx.BoxSizer(wx.HORIZONTAL)
  buttonsBox.Add(spellcheck, 0, wx.ALL, 5)
  buttonsBox.Add(self.unshortenButton, 0, wx.ALL, 5)
  buttonsBox.Add(translateButton, 0, wx.ALL, 5)
  buttonsBox.Add(cancelButton, 0, wx.ALL, 5)
  mainBox.Add(buttonsBox, 0, wx.ALL, 5)
  selectId = wx.NewId()
  self.Bind(wx.EVT_MENU, self.onSelect, id=selectId)
  self.accel_tbl = wx.AcceleratorTable([
(wx.ACCEL_CTRL, ord('A'), selectId),
])
  self.SetAcceleratorTable(self.accel_tbl)
  panel.SetSizer(mainBox)
  self.SetClientSize(mainBox.CalcMin())

 def onSelect(self, ev):
  self.text.SelectAll()