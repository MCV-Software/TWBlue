# -*- coding: utf-8 -*-
from builtins import str
import wx
import widgetUtils

class textLimited(widgetUtils.BaseDialog):
 def __init__(self, *args, **kwargs):
  super(textLimited, self).__init__(parent=None, *args, **kwargs)

 def createTextArea(self, message="", text=""):
  if not hasattr(self, "panel"):
   self.panel = wx.Panel(self)
  self.label = wx.StaticText(self.panel, -1, message)
  self.SetTitle(str(len(text)))
  self.text = wx.TextCtrl(self.panel, -1, text, size=(439, -1),style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)
#  font = self.text.GetFont()
#  dc = wx.WindowDC(self.text)
#  dc.SetFont(font)
#  x, y = dc.GetTextExtent("00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000")
#  self.text.SetSize((x, y))
  self.Bind(wx.EVT_CHAR_HOOK, self.handle_keys, self.text)
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
  if hasattr(self, buttonName):
   return getattr(self, buttonName).Enable()

 def disable_button(self, buttonName):
  if hasattr(self, buttonName):
   return getattr(self, buttonName).Disable()

 def onSelect(self, ev):
  self.text.SelectAll()

 def handle_keys(self, event):
  shift=event.ShiftDown()
  if event.GetKeyCode() == wx.WXK_RETURN and shift==False and hasattr(self,'okButton'):
   wx.PostEvent(self.okButton.GetEventHandler(), wx.PyCommandEvent(wx.EVT_BUTTON.typeId,wx.ID_OK))
  else:
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
  self.long_tweet = wx.CheckBox(self.panel, -1, _("&Long tweet"))
  self.long_tweet.SetValue(True)
  self.upload_image = wx.Button(self.panel, -1, _("&Upload image..."), size=wx.DefaultSize)
  self.spellcheck = wx.Button(self.panel, -1, _("Check &spelling..."), size=wx.DefaultSize)
  self.attach = wx.Button(self.panel, -1, _("&Attach audio..."), size=wx.DefaultSize)
  self.shortenButton = wx.Button(self.panel, -1, _("Sh&orten URL"), size=wx.DefaultSize)
  self.unshortenButton = wx.Button(self.panel, -1, _("&Expand URL"), size=wx.DefaultSize)
  self.shortenButton.Disable()
  self.unshortenButton.Disable()
  self.translateButton = wx.Button(self.panel, -1, _("&Translate..."), size=wx.DefaultSize)
  self.autocompletionButton = wx.Button(self.panel, -1, _("Auto&complete users"))
  self.okButton = wx.Button(self.panel, wx.ID_OK, _("Sen&d"), size=wx.DefaultSize)
  self.okButton.SetDefault()
  cancelButton = wx.Button(self.panel, wx.ID_CANCEL, _("C&lose"), size=wx.DefaultSize)
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

 def __init__(self, title, message, text, *args, **kwargs):
  super(tweet, self).__init__()
  self.shift=False
  self.createControls(message, title, text)
  self.SetClientSize(self.mainBox.CalcMin())

 def get_image(self):
  openFileDialog = wx.FileDialog(self, _("Select the picture to be uploaded"), "", "", _("Image files (*.png, *.jpg, *.gif)|*.png; *.jpg; *.gif"), wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
  if openFileDialog.ShowModal() == wx.ID_CANCEL:
   return None
  return open(openFileDialog.GetPath(), "rb")
 

class retweet(tweet):
 def createControls(self, title, message,  text):
  self.mainBox = wx.BoxSizer(wx.VERTICAL)
  self.createTextArea(message, "")
  label = wx.StaticText(self.panel, -1, _("Retweet"))
  self.text2 = wx.TextCtrl(self.panel, -1, text, size=(439, -1), style=wx.TE_MULTILINE|wx.TE_READONLY)
  self.retweetBox = wx.BoxSizer(wx.HORIZONTAL)
  self.retweetBox.Add(label, 0, wx.ALL, 5)
  self.retweetBox.Add(self.text2, 0, wx.ALL, 5)
  self.mainBox.Add(self.textBox, 0, wx.ALL, 5)
  self.mainBox.Add(self.retweetBox, 0, wx.ALL, 5)
  self.upload_image = wx.Button(self.panel, -1, _("&Upload image..."), size=wx.DefaultSize)
  self.spellcheck = wx.Button(self.panel, -1, _("Check &spelling..."), size=wx.DefaultSize)
  self.attach = wx.Button(self.panel, -1, _("&Attach audio..."), size=wx.DefaultSize)
  self.shortenButton = wx.Button(self.panel, -1, _("Sh&orten URL"), size=wx.DefaultSize)
  self.unshortenButton = wx.Button(self.panel, -1, _("&Expand URL"), size=wx.DefaultSize)
  self.shortenButton.Disable()
  self.unshortenButton.Disable()
  self.translateButton = wx.Button(self.panel, -1, _("&Translate..."), size=wx.DefaultSize)
  self.autocompletionButton = wx.Button(self.panel, -1, _("Auto&complete users"))
  self.okButton = wx.Button(self.panel, wx.ID_OK, _("Sen&d"), size=wx.DefaultSize)
  self.okButton.SetDefault()
  cancelButton = wx.Button(self.panel, wx.ID_CANCEL, _("C&lose"), size=wx.DefaultSize)
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

 def __init__(self, title, message, text, *args, **kwargs):
  super(tweet, self).__init__()
  self.createControls(message, title, text)
#  self.onTimer(wx.EVT_CHAR_HOOK)
  self.SetClientSize(self.mainBox.CalcMin())

 def get_image(self):
  openFileDialog = wx.FileDialog(self, _("Select the picture to be uploaded"), "", "", _("Image files (*.png, *.jpg, *.gif)|*.png; *.jpg; *.gif"), wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
  if openFileDialog.ShowModal() == wx.ID_CANCEL:
   return None
  return open(openFileDialog.GetPath(), "rb")

class dm(textLimited):
 def createControls(self, title, message,  users):
  self.panel = wx.Panel(self)
  self.mainBox = wx.BoxSizer(wx.VERTICAL)
  label = wx.StaticText(self.panel, -1, _("&Recipient"))
  self.cb = wx.ComboBox(self.panel, -1, choices=users, value=users[0], size=wx.DefaultSize)
  self.autocompletionButton = wx.Button(self.panel, -1, _("Auto&complete users"))
  self.createTextArea(message, text="")
  userBox = wx.BoxSizer(wx.HORIZONTAL)
  userBox.Add(label, 0, wx.ALL, 5)
  userBox.Add(self.cb, 0, wx.ALL, 5)
  userBox.Add(self.autocompletionButton, 0, wx.ALL, 5)
  self.mainBox.Add(userBox, 0, wx.ALL, 5)
  self.mainBox.Add(self.textBox, 0, wx.ALL, 5)
  self.spellcheck = wx.Button(self.panel, -1, _("Check &spelling..."), size=wx.DefaultSize)
  self.attach = wx.Button(self.panel, -1, _("&Attach audio..."), size=wx.DefaultSize)
  self.shortenButton = wx.Button(self.panel, -1, _("Sh&orten URL"), size=wx.DefaultSize)
  self.unshortenButton = wx.Button(self.panel, -1, _("&Expand URL"), size=wx.DefaultSize)
  self.shortenButton.Disable()
  self.unshortenButton.Disable()
  self.translateButton = wx.Button(self.panel, -1, _("&Translate..."), size=wx.DefaultSize)
  self.okButton = wx.Button(self.panel, wx.ID_OK, _("Sen&d"), size=wx.DefaultSize)
  self.okButton.SetDefault()
  cancelButton = wx.Button(self.panel, wx.ID_CANCEL, _("C&lose"), size=wx.DefaultSize)
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
  self.SetClientSize(self.mainBox.CalcMin())

 def __init__(self, title, message,  users, *args, **kwargs):
  super(dm, self).__init__()
  self.createControls(message, title, users)
#  self.onTimer(wx.EVT_CHAR_HOOK)
#  self.SetClientSize(self.mainBox.CalcMin())

 def get_user(self):
  return self.cb.GetValue()

 def set_user(self, user):
  return self.cb.SetValue(user)

class reply(textLimited):

 def get_image(self):
  openFileDialog = wx.FileDialog(self, _("Select the picture to be uploaded"), "", "", _("Image files (*.png, *.jpg, *.gif)|*.png; *.jpg; *.gif"), wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
  if openFileDialog.ShowModal() == wx.ID_CANCEL:
   return None
  return open(openFileDialog.GetPath(), "rb")

 def createControls(self, title, message,  text):
  self.mainBox = wx.BoxSizer(wx.VERTICAL)
  self.createTextArea(message, text)
  self.mainBox.Add(self.textBox, 0, wx.ALL, 5)
  self.usersbox = wx.BoxSizer(wx.VERTICAL)
  self.mentionAll = wx.CheckBox(self.panel, -1, _("&Mention to all"), size=wx.DefaultSize)
  self.mentionAll.Disable()
  self.usersbox.Add(self.mentionAll, 0, wx.ALL, 5)
  self.checkboxes = []
  for i in self.users:
   user_checkbox = wx.CheckBox(self.panel, -1, "@"+i, size=wx.DefaultSize)
   self.checkboxes.append(user_checkbox)
   self.usersbox.Add(self.checkboxes[-1], 0, wx.ALL, 5)
  self.mainBox.Add(self.usersbox, 0, wx.ALL, 10)
  self.long_tweet = wx.CheckBox(self.panel, -1, _("&Long tweet"))
  self.long_tweet.SetValue(True)
  self.upload_image = wx.Button(self.panel, -1, _("&Upload image..."), size=wx.DefaultSize)
  self.spellcheck = wx.Button(self.panel, -1, _("Check &spelling..."), size=wx.DefaultSize)
  self.attach = wx.Button(self.panel, -1, _("&Attach audio..."), size=wx.DefaultSize)
  self.shortenButton = wx.Button(self.panel, -1, _("Sh&orten URL"), size=wx.DefaultSize)
  self.unshortenButton = wx.Button(self.panel, -1, _("&Expand URL"), size=wx.DefaultSize)
  self.shortenButton.Disable()
  self.unshortenButton.Disable()
  self.translateButton = wx.Button(self.panel, -1, _("&Translate..."), size=wx.DefaultSize)
  self.autocompletionButton = wx.Button(self.panel, -1, _("Auto&complete users"))
  self.okButton = wx.Button(self.panel, wx.ID_OK, _("Sen&d"), size=wx.DefaultSize)
  self.okButton.SetDefault()
  cancelButton = wx.Button(self.panel, wx.ID_CANCEL, _("C&lose"), size=wx.DefaultSize)
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
  self.mainBox.Add(self.ok_cancelSizer, 0, wx.ALL, 10)
  selectId = wx.NewId()
  self.Bind(wx.EVT_MENU, self.onSelect, id=selectId)
  self.accel_tbl = wx.AcceleratorTable([
(wx.ACCEL_CTRL, ord('A'), selectId),
])
  self.SetAcceleratorTable(self.accel_tbl)
  self.panel.SetSizer(self.mainBox)

 def __init__(self, title, message,  text, users=[], *args, **kwargs):
  self.users = users
  super(reply, self).__init__()
  self.shift=False
  self.createControls(message, title, text)
  self.SetClientSize(self.mainBox.CalcMin())

class viewTweet(widgetUtils.BaseDialog):
 def set_title(self, lenght):
  self.SetTitle(_("Tweet - %i characters ") % (lenght,))

 def __init__(self, text, rt_count, favs_count,source, *args, **kwargs):
  super(viewTweet, self).__init__(None, size=(850,850))
  panel = wx.Panel(self)
  label = wx.StaticText(panel, -1, _("Tweet"))
  self.text = wx.TextCtrl(panel, -1, text, style=wx.TE_READONLY|wx.TE_MULTILINE, size=(250, 180))
  dc = wx.WindowDC(self.text)
  dc.SetFont(self.text.GetFont())
  (x, y) = dc.GetMultiLineTextExtent("0"*140)
  self.text.SetSize((x, y))
  self.text.SetFocus()
  textBox = wx.BoxSizer(wx.HORIZONTAL)
  textBox.Add(label, 0, wx.ALL, 5)
  textBox.Add(self.text, 1, wx.EXPAND, 5)
  mainBox = wx.BoxSizer(wx.VERTICAL)
  mainBox.Add(textBox, 0, wx.ALL, 5)
  label2 = wx.StaticText(panel, -1, _("Image description"))
  self.image_description = wx.TextCtrl(panel, -1, style=wx.TE_READONLY|wx.TE_MULTILINE, size=(250, 180))
  dc = wx.WindowDC(self.image_description)
  dc.SetFont(self.image_description.GetFont())
  (x, y) = dc.GetMultiLineTextExtent("0"*450)
  self.image_description.SetSize((x, y))
  self.image_description.Enable(False)
  iBox = wx.BoxSizer(wx.HORIZONTAL)
  iBox.Add(label2, 0, wx.ALL, 5)
  iBox.Add(self.image_description, 1, wx.EXPAND, 5)
  mainBox.Add(iBox, 0, wx.ALL, 5)
  rtCountLabel = wx.StaticText(panel, -1, _("Retweets: "))
  rtCount = wx.TextCtrl(panel, -1, rt_count, size=wx.DefaultSize, style=wx.TE_READONLY|wx.TE_MULTILINE)
  rtBox = wx.BoxSizer(wx.HORIZONTAL)
  rtBox.Add(rtCountLabel, 0, wx.ALL, 5)
  rtBox.Add(rtCount, 0, wx.ALL, 5)
  favsCountLabel = wx.StaticText(panel, -1, _("Likes: "))
  favsCount = wx.TextCtrl(panel, -1, favs_count, size=wx.DefaultSize, style=wx.TE_READONLY|wx.TE_MULTILINE)
  favsBox = wx.BoxSizer(wx.HORIZONTAL)
  favsBox.Add(favsCountLabel, 0, wx.ALL, 5)
  favsBox.Add(favsCount, 0, wx.ALL, 5)
  sourceLabel = wx.StaticText(panel, -1, _("Source: "))
  sourceTweet = wx.TextCtrl(panel, -1, source, size=wx.DefaultSize, style=wx.TE_READONLY|wx.TE_MULTILINE)
  sourceBox = wx.BoxSizer(wx.HORIZONTAL)
  sourceBox.Add(sourceLabel, 0, wx.ALL, 5)
  sourceBox.Add(sourceTweet, 0, wx.ALL, 5)
  infoBox = wx.BoxSizer(wx.HORIZONTAL)
  infoBox.Add(rtBox, 0, wx.ALL, 5)
  infoBox.Add(favsBox, 0, wx.ALL, 5)
  infoBox.Add(sourceBox, 0, wx.ALL, 5)
  mainBox.Add(infoBox, 0, wx.ALL, 5)
  self.spellcheck = wx.Button(panel, -1, _("Check &spelling..."), size=wx.DefaultSize)
  self.unshortenButton = wx.Button(panel, -1, _("&Expand URL"), size=wx.DefaultSize)
  self.unshortenButton.Disable()
  self.translateButton = wx.Button(panel, -1, _("&Translate..."), size=wx.DefaultSize)
  cancelButton = wx.Button(panel, wx.ID_CANCEL, _("C&lose"), size=wx.DefaultSize)
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

 def set_image_description(self, desc):
  self.image_description.Enable(True)
  if len(self.image_description.GetValue()) == 0:
   self.image_description.SetValue(desc)
  else:
   self.image_description.SetValue(self.image_description.GetValue()+"\n"+desc)

 def text_focus(self):
  self.text.SetFocus()

 def onSelect(self, ev):
  self.text.SelectAll()

 def enable_button(self, buttonName):
  if hasattr(self, buttonName):
   return getattr(self, buttonName).Enable()

class viewNonTweet(widgetUtils.BaseDialog):

 def __init__(self, text, *args, **kwargs):
  super(viewNonTweet, self).__init__(None, size=(850,850))
  self.SetTitle(_("View"))
  panel = wx.Panel(self)
  label = wx.StaticText(panel, -1, _("Item"))
  self.text = wx.TextCtrl(parent=panel, id=-1, value=text, style=wx.TE_READONLY|wx.TE_MULTILINE, size=(250, 180))
  dc = wx.WindowDC(self.text)
  dc.SetFont(self.text.GetFont())
  (x, y) = dc.GetMultiLineTextExtent("0"*140)
  self.text.SetSize((x, y))
  self.text.SetFocus()
  textBox = wx.BoxSizer(wx.HORIZONTAL)
  textBox.Add(label, 0, wx.ALL, 5)
  textBox.Add(self.text, 1, wx.EXPAND, 5)
  mainBox = wx.BoxSizer(wx.VERTICAL)
  mainBox.Add(textBox, 0, wx.ALL, 5)
  self.spellcheck = wx.Button(panel, -1, _("Check &spelling..."), size=wx.DefaultSize)
  self.unshortenButton = wx.Button(panel, -1, _("&Expand URL"), size=wx.DefaultSize)
  self.unshortenButton.Disable()
  self.translateButton = wx.Button(panel, -1, _("&Translate..."), size=wx.DefaultSize)
  cancelButton = wx.Button(panel, wx.ID_CANCEL, _("C&lose"), size=wx.DefaultSize)
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
