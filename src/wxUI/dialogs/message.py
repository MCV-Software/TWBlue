# -*- coding: utf-8 -*-
import wx
import widgetUtils

class textLimited(widgetUtils.BaseDialog):
 def __init__(self, *args, **kwargs):
  super(textLimited, self).__init__(parent=None, *args, **kwargs)
  self.shift=False
 def createTextArea(self, message="", text=""):
  self.panel = wx.Panel(self)
  self.label = wx.StaticText(self.panel, -1, message)
  self.SetTitle(str(len(text)))
  self.text = wx.TextCtrl(self.panel, -1, text, size=(439, -1),style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)
#  font = self.text.GetFont()
#  dc = wx.WindowDC(self.text)
#  dc.SetFont(font)
#  x, y = dc.GetTextExtent("00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000")
#  self.text.SetSize((x, y))
  self.Bind(wx.EVT_TEXT_ENTER, self.on_enter)
  self.Bind(wx.EVT_CHAR_HOOK, self.handle_keys)
  self.text.SetFocus()
  self.textBox = wx.BoxSizer(wx.HORIZONTAL)
  self.textBox.Add(self.label, 0, wx.ALL, 5)
  self.textBox.Add(self.text, 0, wx.ALL, 5)

 def text_focus(self):
  self.text.SetFocus()

 def get_text(self):
  return self.text.GetValue()

 def set_text(self, text):
  return self.text.ChangeValue(text)

 def set_title(self, new_title):
  return self.SetTitle(new_title)

 def enable_button(self, buttonName):
  if getattr(self, buttonName):
   return getattr(self, buttonName).Enable()

 def disable_button(self, buttonName):
  if getattr(self, buttonName):
   return getattr(self, buttonName).Disable()

 def onSelect(self, ev):
  self.text.SelectAll()

 def on_enter(self,event):
  if self.shift==False and hasattr(self,'okButton'):
   return wx.PostEvent(self.okButton.GetEventHandler(),wx.PyCommandEvent(wx.EVT_BUTTON.typeId,wx.ID_OK))
  else:
   return self.text.WriteText('\n')

 def handle_keys(self,event):
  self.shift=event.ShiftDown()
  event.Skip()

 def set_cursor_at_end(self):
  self.text.SetInsertionPoint(len(self.text.GetValue()))

 def set_cursor_at_position(self, position):
  self.text.SetInsertionPoint(position)

 def get_position(self):
  return self.text.GetInsertionPoint()

 def popup_menu(self, menu):
  self.PopupMenu(menu, self.text.GetPosition())

class tweet(textLimited):
 def createControls(self, title, message,  text):
  self.mainBox = wx.BoxSizer(wx.VERTICAL)
  self.createTextArea(message, text)
  self.mainBox.Add(self.textBox, 0, wx.ALL, 5)
  self.upload_image = wx.Button(self.panel, -1, _(u"Upload image..."), size=wx.DefaultSize)
  self.spellcheck = wx.Button(self.panel, -1, _("Check spelling..."), size=wx.DefaultSize)
  self.attach = wx.Button(self.panel, -1, _(u"Attach audio..."), size=wx.DefaultSize)
  self.shortenButton = wx.Button(self.panel, -1, _(u"Shorten URL"), size=wx.DefaultSize)
  self.unshortenButton = wx.Button(self.panel, -1, _(u"Expand URL"), size=wx.DefaultSize)
  self.shortenButton.Disable()
  self.unshortenButton.Disable()
  self.translateButton = wx.Button(self.panel, -1, _(u"Translate..."), size=wx.DefaultSize)
  self.autocompletionButton = wx.Button(self.panel, -1, _(u"&Autocomplete users"))
  self.okButton = wx.Button(self.panel, wx.ID_OK, _(u"Send"), size=wx.DefaultSize)
  self.okButton.SetDefault()
  cancelButton = wx.Button(self.panel, wx.ID_CANCEL, _(u"Close"), size=wx.DefaultSize)
  self.buttonsBox1 = wx.BoxSizer(wx.HORIZONTAL)
  self.buttonsBox1.Add(self.upload_image, 0, wx.ALL, 10)
  self.buttonsBox1.Add(self.spellcheck, 0, wx.ALL, 10)
  self.buttonsBox1.Add(self.attach, 0, wx.ALL, 10)
  self.mainBox.Add(self.buttonsBox1, 0, wx.ALL, 10)
  self.buttonsBox2 = wx.BoxSizer(wx.HORIZONTAL)
  self.buttonsBox2.Add(self.shortenButton, 0, wx.ALL, 10)
  self.buttonsBox2.Add(self.unshortenButton, 0, wx.ALL, 10)
  self.buttonsBox2.Add(self.translateButton, 0, wx.ALL, 10)
  self.mainBox.Add(self.buttonsBox2, 0, wx.ALL, 10)
  self.ok_cancelSizer = wx.BoxSizer(wx.HORIZONTAL)
  self.ok_cancelSizer.Add(self.autocompletionButton, 0, wx.ALL, 10)
  self.ok_cancelSizer.Add(self.okButton, 0, wx.ALL, 10)
  self.ok_cancelSizer.Add(cancelButton, 0, wx.ALL, 10)
  self.mainBox.Add(self.ok_cancelSizer)
  selectId = wx.NewId()
  self.Bind(wx.EVT_MENU, self.onSelect, id=selectId)
  self.accel_tbl = wx.AcceleratorTable([
(wx.ACCEL_CTRL, ord('A'), selectId),
])
  self.SetAcceleratorTable(self.accel_tbl)
  self.panel.SetSizer(self.mainBox)

 def __init__(self, title, message, text):
  super(tweet, self).__init__()
  self.shift=False
  self.createControls(message, title, text)
#  self.onTimer(wx.EVT_CHAR_HOOK)
  self.SetClientSize(self.mainBox.CalcMin())

 def get_image(self):
  openFileDialog = wx.FileDialog(self, _(u"Select the picture to be uploaded"), "", "", _("Image files (*.png, *.jpg, *.gif)|*.png; *.jpg; *.gif"), wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
  if openFileDialog.ShowModal() == wx.ID_CANCEL:
   return None
  return open(openFileDialog.GetPath(), "rb")
 

class retweet(tweet):
 def createControls(self, title, message,  text):
  self.mainBox = wx.BoxSizer(wx.VERTICAL)
  self.createTextArea(message, "")
  label = wx.StaticText(self.panel, -1, _(u"Retweet"))
  self.text2 = wx.TextCtrl(self.panel, -1, text, size=(439, -1), style=wx.TE_MULTILINE|wx.TE_READONLY)
  self.retweetBox = wx.BoxSizer(wx.HORIZONTAL)
  self.retweetBox.Add(label, 0, wx.ALL, 5)
  self.retweetBox.Add(self.text2, 0, wx.ALL, 5)
  self.mainBox.Add(self.textBox, 0, wx.ALL, 5)
  self.mainBox.Add(self.retweetBox, 0, wx.ALL, 5)
  self.upload_image = wx.Button(self.panel, -1, _(u"Upload a picture"), size=wx.DefaultSize)
  self.spellcheck = wx.Button(self.panel, -1, _("Spelling correction"), size=wx.DefaultSize)
  self.attach = wx.Button(self.panel, -1, _(u"Attach audio"), size=wx.DefaultSize)
  self.shortenButton = wx.Button(self.panel, -1, _(u"Shorten URL"), size=wx.DefaultSize)
  self.unshortenButton = wx.Button(self.panel, -1, _(u"Expand URL"), size=wx.DefaultSize)
  self.shortenButton.Disable()
  self.unshortenButton.Disable()
  self.translateButton = wx.Button(self.panel, -1, _(u"Translate message"), size=wx.DefaultSize)
  self.autocompletionButton = wx.Button(self.panel, -1, _(u"&Autocomplete users"))
  self.okButton = wx.Button(self.panel, wx.ID_OK, _(u"Send"), size=wx.DefaultSize)
  self.okButton.SetDefault()
  cancelButton = wx.Button(self.panel, wx.ID_CANCEL, _(u"Close"), size=wx.DefaultSize)
  self.buttonsBox1 = wx.BoxSizer(wx.HORIZONTAL)
  self.buttonsBox1.Add(self.upload_image, 0, wx.ALL, 10)
  self.buttonsBox1.Add(self.spellcheck, 0, wx.ALL, 10)
  self.buttonsBox1.Add(self.attach, 0, wx.ALL, 10)
  self.mainBox.Add(self.buttonsBox1, 0, wx.ALL, 10)
  self.buttonsBox2 = wx.BoxSizer(wx.HORIZONTAL)
  self.buttonsBox2.Add(self.shortenButton, 0, wx.ALL, 10)
  self.buttonsBox2.Add(self.unshortenButton, 0, wx.ALL, 10)
  self.buttonsBox2.Add(self.translateButton, 0, wx.ALL, 10)
  self.mainBox.Add(self.buttonsBox2, 0, wx.ALL, 10)
  self.ok_cancelSizer = wx.BoxSizer(wx.HORIZONTAL)
  self.ok_cancelSizer.Add(self.autocompletionButton, 0, wx.ALL, 10)
  self.ok_cancelSizer.Add(self.okButton, 0, wx.ALL, 10)
  self.ok_cancelSizer.Add(cancelButton, 0, wx.ALL, 10)
  self.mainBox.Add(self.ok_cancelSizer)
  selectId = wx.NewId()
  self.Bind(wx.EVT_MENU, self.onSelect, id=selectId)
  self.accel_tbl = wx.AcceleratorTable([
(wx.ACCEL_CTRL, ord('A'), selectId),
])
  self.SetAcceleratorTable(self.accel_tbl)
  self.panel.SetSizer(self.mainBox)

 def __init__(self, title, message, text):
  super(tweet, self).__init__()
  self.createControls(message, title, text)
#  self.onTimer(wx.EVT_CHAR_HOOK)
  self.SetClientSize(self.mainBox.CalcMin())

 def get_image(self):
  openFileDialog = wx.FileDialog(self, _(u"Select the picture to be uploaded"), "", "", _("Image files (*.png, *.jpg, *.gif)|*.png; *.jpg; *.gif"), wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
  if openFileDialog.ShowModal() == wx.ID_CANCEL:
   return None
  return open(openFileDialog.GetPath(), "rb")

class dm(textLimited):
 def createControls(self, title, message,  users):
  self.panel = wx.Panel(self)
  self.mainBox = wx.BoxSizer(wx.VERTICAL)
  label = wx.StaticText(self.panel, -1, _(u"Recipient"))
  self.cb = wx.ComboBox(self.panel, -1, choices=users, value=users[0], size=wx.DefaultSize)
  self.autocompletionButton = wx.Button(self.panel, -1, _(u"&Autocomplete users"))
  self.createTextArea(message, text="")
  userBox = wx.BoxSizer(wx.HORIZONTAL)
  userBox.Add(label, 0, wx.ALL, 5)
  userBox.Add(self.cb, 0, wx.ALL, 5)
  userBox.Add(self.autocompletionButton, 0, wx.ALL, 5)
  self.mainBox.Add(userBox, 0, wx.ALL, 5)
#  self.mainBox.Add(self.cb, 0, wx.ALL, 5)
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
  
 def __init__(self, title, message,  users):
  super(dm, self).__init__()
  self.createControls(message, title, users)
#  self.onTimer(wx.EVT_CHAR_HOOK)
  self.SetClientSize(self.mainBox.CalcMin())

 def get_user(self):
  return self.cb.GetValue()

 def set_user(self, user):
  return self.cb.SetValue(user)

class reply(tweet):
 def __init__(self, title, message,  text):
  super(reply, self).__init__(message, title, text)
  self.text.SetInsertionPoint(len(self.text.GetValue()))
  self.mentionAll = wx.Button(self, -1, _(u"Men&tion to all"), size=wx.DefaultSize)
  self.mentionAll.Disable()
  self.buttonsBox1.Add(self.mentionAll, 0, wx.ALL, 5)
  self.buttonsBox1.Layout()
  self.mainBox.Layout()
  self.SetClientSize(self.mainBox.CalcMin())

class viewTweet(widgetUtils.BaseDialog):
 def set_title(self, lenght):
  self.SetTitle(_(u"Tweet - %i characters ") % (lenght,))

 def __init__(self, text, rt_count, favs_count):
  super(viewTweet, self).__init__(None, size=(850,850))
  panel = wx.Panel(self)
  label = wx.StaticText(panel, -1, _(u"Tweet"))
  self.text = wx.TextCtrl(panel, -1, text, style=wx.TE_READONLY|wx.TE_MULTILINE, size=(250, 180))
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
  rtCountLabel = wx.StaticText(panel, -1, _(u"Retweets: "))
  rtCount = wx.TextCtrl(panel, -1, rt_count, size=wx.DefaultSize, style=wx.TE_READONLY|wx.TE_MULTILINE)
  rtBox = wx.BoxSizer(wx.HORIZONTAL)
  rtBox.Add(rtCountLabel, 0, wx.ALL, 5)
  rtBox.Add(rtCount, 0, wx.ALL, 5)
  favsCountLabel = wx.StaticText(panel, -1, _(u"Favourites: "))
  favsCount = wx.TextCtrl(panel, -1, favs_count, size=wx.DefaultSize, style=wx.TE_READONLY|wx.TE_MULTILINE)
  favsBox = wx.BoxSizer(wx.HORIZONTAL)
  favsBox.Add(favsCountLabel, 0, wx.ALL, 5)
  favsBox.Add(favsCount, 0, wx.ALL, 5)
  infoBox = wx.BoxSizer(wx.HORIZONTAL)
  infoBox.Add(rtBox, 0, wx.ALL, 5)
  infoBox.Add(favsBox, 0, wx.ALL, 5)
  mainBox.Add(infoBox, 0, wx.ALL, 5)
  self.spellcheck = wx.Button(panel, -1, _("Spelling correction"), size=wx.DefaultSize)
  self.unshortenButton = wx.Button(panel, -1, _(u"Expand URL"), size=wx.DefaultSize)
  self.unshortenButton.Disable()
  self.translateButton = wx.Button(panel, -1, _(u"Translate message"), size=wx.DefaultSize)
  cancelButton = wx.Button(panel, wx.ID_CANCEL, _(u"Close"), size=wx.DefaultSize)
  cancelButton.SetDefault()
  buttonsBox = wx.BoxSizer(wx.HORIZONTAL)
  buttonsBox.Add(self.spellcheck, 0, wx.ALL, 5)
  buttonsBox.Add(self.unshortenButton, 0, wx.ALL, 5)
  buttonsBox.Add(self.translateButton, 0, wx.ALL, 5)
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

 def set_text(self, text):
  self.text.ChangeValue(text)

 def get_text(self):
  return self.text.GetValue()

 def text_focus(self):
  self.text.SetFocus()

 def onSelect(self, ev):
  self.text.SelectAll()

 def enable_button(self, buttonName):
  if getattr(self, buttonName):
   return getattr(self, buttonName).Enable()

class viewNonTweet(widgetUtils.BaseDialog):

 def __init__(self, text):
  super(viewNonTweet, self).__init__(None, size=(850,850))
  self.SetTitle(_(u"View"))
  panel = wx.Panel(self)
  label = wx.StaticText(panel, -1, _(u"Item"))
  self.text = wx.TextCtrl(parent=panel, id=-1, value=text, style=wx.TE_READONLY|wx.TE_MULTILINE, size=(250, 180))
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
  self.spellcheck = wx.Button(panel, -1, _("Spelling correction"), size=wx.DefaultSize)
  self.unshortenButton = wx.Button(panel, -1, _(u"Expand URL"), size=wx.DefaultSize)
  self.unshortenButton.Disable()
  self.translateButton = wx.Button(panel, -1, _(u"Translate message"), size=wx.DefaultSize)
  cancelButton = wx.Button(panel, wx.ID_CANCEL, _(u"Close"), size=wx.DefaultSize)
  cancelButton.SetDefault()
  buttonsBox = wx.BoxSizer(wx.HORIZONTAL)
  buttonsBox.Add(self.spellcheck, 0, wx.ALL, 5)
  buttonsBox.Add(self.unshortenButton, 0, wx.ALL, 5)
  buttonsBox.Add(self.translateButton, 0, wx.ALL, 5)
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

 def set_text(self, text):
  self.text.ChangeValue(text)

 def get_text(self):
  return self.text.GetValue()

 def text_focus(self):
  self.text.SetFocus()

 def enable_button(self, buttonName):
  if getattr(self, buttonName):
   return getattr(self, buttonName).Enable()
