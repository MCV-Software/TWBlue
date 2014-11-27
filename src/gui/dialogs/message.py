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
import twitter
import config
import output
import sound
import urlList
import url_shortener
import json
from mysc.thread_utils import call_threaded
from mysc.repeating_timer import RepeatingTimer
from twython import TwythonError
from extra import translator, AudioUploader
import platform
from extra.AudioUploader import transfer
from extra.autocompletionUsers  import completion
if platform.system() != "Darwin":
 from extra.AudioUploader import dropbox_transfer
 from extra.SpellChecker import gui as spellCheckerGUI

class textLimited(wx.Dialog):
 def __init__(self, message, title, text, parent):
  wx.Dialog.__init__(self, parent)
  self.twitter = parent.twitter
  self.parent = parent
  self.title = title
  self.SetTitle(_(u"%s - %s of 140 characters") % (self.title, str(len(text))))
  self.panel = wx.Panel(self)

 def createTextArea(self, message, text):
  self.label = wx.StaticText(self.panel, -1, message)
  self.text = wx.TextCtrl(self.panel, -1, text)
  font = self.text.GetFont()
  dc = wx.WindowDC(self.text)
  dc.SetFont(font)
  x, y = dc.GetTextExtent("00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000")
  self.text.SetSize((x, y))
  self.text.SetFocus()
  if platform.system() != "Darwin":
   self.text.Bind(wx.EVT_TEXT, self.onTimer)
  self.textBox = wx.BoxSizer(wx.HORIZONTAL)
  self.textBox.Add(self.label, 0, wx.ALL, 5)
  self.textBox.Add(self.text, 0, wx.ALL, 5)

 def onCheck(self, ev):
  if platform.system() == "Darwin":
   return
  text = self.text.GetValue()
  dlg = spellCheckerGUI.spellCheckerDialog(text, "")
  if dlg.ShowModal() == wx.ID_OK:
   self.text.ChangeValue(dlg.checker.get_text())
   dlg.Destroy()

 def onAttach(self, ev):
  ev.Skip()
  self.recording = AudioUploader.gui.audioDialog(self.parent)
  if self.recording.ShowModal() != wx.ID_OK:
   self.recording.cleanup()
   return
  self.recording.postprocess()
  output.speak(_(u"Attaching..."))
  self.uploaderDialog = AudioUploader.transfer_dialogs.UploadDialog(parent=self.parent, title=_(u"Uploading..."), filename=self.recording.file)
  if self.recording.services.GetValue() == "Dropbox" and platform.system() != "Darwin":
   self.uploader = dropbox_transfer.dropboxUploader(filename=self.recording.file, completed_callback=self.upload_completed, wxDialog=self.uploaderDialog)
  elif self.recording.services.GetValue() == "SNDUp":
   base_url = 'http://sndup.net/post.php'
   if len(config.main["sound"]["sndup_api_key"]) > 0:
    url = base_url + '?apikey=' + config.main['sound']['sndup_api_key']
   else:
    url = base_url
   self.uploader = transfer.Upload(field='file', url=url, filename=self.recording.file, completed_callback=self.upload_completed, wxDialog=self.uploaderDialog)
  elif self.recording.services.GetValue() == "TwUp":
   url = 'http://api.twup.me/post.json'
   self.uploader = transfer.Upload(field='file', url=url, filename=self.recording.file, completed_callback=self.upload_completed, wxDialog=self.uploaderDialog)
  self.uploaderDialog.Show()
  self.uploader.perform_threaded()

 def upload_completed(self):
  url = self.uploader.get_url()
  self.uploaderDialog.Destroy()
  if url != 0:
   self.text.SetValue(self.text.GetValue()+url+" #audio")
  else:
   output.speak(_(u"Unable to upload the audio"))

 def onTranslate(self, ev):
  dlg = translator.gui.translateDialog()
  selection = dlg.ShowModal()
  if selection != wx.ID_CANCEL:
   text_to_translate = self.text.GetValue().encode("utf-8")
   source = [x[0] for x in translator.available_languages()][dlg.source_lang.GetSelection()]
   dest = [x[0] for x in translator.available_languages()][dlg.dest_lang.GetSelection()]
   t = translator.translator.Translator()
   t.from_lang = source
   t.to_lang = dest
   msg = t.translate(text_to_translate)
   self.text.ChangeValue(msg)
   output.speak(_(u"Translated"))
   self.text.SetFocus()
  else:
   return
  dlg.Destroy()

 def onSelect(self, ev):
  self.text.SelectAll()

 def onShorten(self, ev):
  urls =  twitter.utils.find_urls_in_text(self.text.GetValue())
  if len(urls) == 0:
   output.speak(_(u"There's no URL to be shortened"))
  elif len(urls) == 1:
   self.text.SetValue(self.text.GetValue().replace(urls[0], url_shortener.shorten(urls[0])))
   output.speak(_(u"URL shortened"))
  elif len(urls) > 1:
   urlList.shorten(urls, self).ShowModal()
  self.text.SetFocus()

 def onUnshorten(self, ev):
  urls =  twitter.utils.find_urls_in_text(self.text.GetValue())
  if len(urls) == 0:
   output.speak(_(u"There's no URL to be expanded"))
  elif len(urls) == 1:
   self.text.SetValue(self.text.GetValue().replace(urls[0], url_shortener.unshorten(urls[0])))
   output.speak(_(u"URL expanded"))
  elif len(urls) > 1:
   urlList.unshorten(urls, self).ShowModal()
  self.text.SetFocus()

 def onTimer(self, ev):
  self.SetTitle(_(u"%s - %s of 140 characters") % (self.title, str(len(self.text.GetValue()))))
  if len(self.text.GetValue()) > 1:
   self.shortenButton.Enable()
   self.unshortenButton.Enable()
  else:
   self.shortenButton.Disable()
   self.unshortenButton.Disable()
  if len(self.text.GetValue()) > 140:
   sound.player.play("max_length.ogg")
   self.okButton.Disable()
  elif len(self.text.GetValue()) <= 140:
   self.okButton.Enable()

 def onCancel(self, ev):
  self.Destroy()


class tweet(textLimited):
 def createControls(self, message, title, text):
  self.mainBox = wx.BoxSizer(wx.VERTICAL)
  self.createTextArea(message, text)
  self.mainBox.Add(self.textBox, 0, wx.ALL, 5)
  self.upload_image = wx.Button(self.panel, -1, _(u"Upload a picture"), size=wx.DefaultSize)
  self.upload_image.Bind(wx.EVT_BUTTON, self.onUpload_image)
  if platform.system() != "Darwin":
   self.spellcheck = wx.Button(self.panel, -1, _("Spelling correction"), size=wx.DefaultSize)
   self.spellcheck.Bind(wx.EVT_BUTTON, self.onCheck)
  self.attach = wx.Button(self.panel, -1, _(u"Attach audio"), size=wx.DefaultSize)
  self.attach.Bind(wx.EVT_BUTTON, self.onAttach)
  self.shortenButton = wx.Button(self.panel, -1, _(u"Shorten URL"), size=wx.DefaultSize)
  self.shortenButton.Bind(wx.EVT_BUTTON, self.onShorten)
  self.unshortenButton = wx.Button(self.panel, -1, _(u"Expand URL"), size=wx.DefaultSize)
  self.unshortenButton.Bind(wx.EVT_BUTTON, self.onUnshorten)
  self.shortenButton.Disable()
  self.unshortenButton.Disable()
  self.translateButton = wx.Button(self.panel, -1, _(u"Translate message"), size=wx.DefaultSize)
  self.translateButton.Bind(wx.EVT_BUTTON, self.onTranslate)
  self.okButton = wx.Button(self.panel, wx.ID_OK, _(u"Send"), size=wx.DefaultSize)
  self.okButton.Bind(wx.EVT_BUTTON, self.onSend)
  self.okButton.SetDefault()
  autocompletionButton = wx.Button(self.panel, -1, _(u"&Autocomplete users"))
  self.Bind(wx.EVT_BUTTON, self.autocompletion, autocompletionButton)
  cancelButton = wx.Button(self.panel, wx.ID_CANCEL, _(u"Close"), size=wx.DefaultSize)
  cancelButton.Bind(wx.EVT_BUTTON, self.onCancel)
  self.buttonsBox1 = wx.BoxSizer(wx.HORIZONTAL)
  self.buttonsBox1.Add(self.upload_image, 0, wx.ALL, 5)
  if platform.system() != "Darwin":
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
#  autocompletionId = wx.NewId()
#  self.Bind(wx.EVT_MENU, self.autocompletion, id=autocompletionId)
  self.accel_tbl = wx.AcceleratorTable([
(wx.ACCEL_CTRL, ord('A'), selectId),
#(wx.ACCEL_ALT, ord('A'), autocompletionId),
])
  self.SetAcceleratorTable(self.accel_tbl)
  self.panel.SetSizer(self.mainBox)

 def __init__(self, message, title, text, parent):
  super(tweet, self).__init__(message, title, text, parent)
  self.image = None
  self.createControls(message, title, text)
  self.onTimer(wx.EVT_CHAR_HOOK)
  self.SetClientSize(self.mainBox.CalcMin())

 def autocompletion(self, event=None):
  c = completion.autocompletionUsers(self)
  c.show_menu()

 def onUpload_image(self, ev):
  if self.upload_image.GetLabel() == _(u"Discard image"):
   self.image = None
   del self.file
   output.speak(_(u"Discarded"))
   self.upload_image.SetLabel(_(u"Upload a picture"))
  else:
   openFileDialog = wx.FileDialog(self, _(u"Select the picture to be uploaded"), "", "", _("Image files (*.png, *.jpg, *.gif)|*.png; *.jpg; *.gif"), wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
   if openFileDialog.ShowModal() == wx.ID_CANCEL:
    return
   self.file = open(openFileDialog.GetPath(), "rb")
   self.image = True
   self.upload_image.SetLabel(_(u"Discard image"))
  ev.Skip()

 def onSend(self, ev):
   self.EndModal(wx.ID_OK)

class retweet(tweet):
 def __init__(self, message, title, text, parent):
  super(retweet, self).__init__(message, title, text, parent)
#  self.createControls(message, title, text)
  self.in_reply_to = parent.db.settings[parent.name_buffer][parent.list.get_selected()]["id"]
  self.text.SetInsertionPoint(0)

 def onSend(self, ev):
  self.EndModal(wx.ID_OK)

class dm(textLimited):
 def createControls(self, message, title, text):
  self.mainBox = wx.BoxSizer(wx.VERTICAL)
  if self.parent.name_buffer == "followers" or self.parent.name_buffer == "friends":
   list = [self.parent.db.settings[self.parent.name_buffer][self.parent.list.get_selected()]["screen_name"]]
  else:
   list =twitter.utils.get_all_users(self.parent.db.settings[self.parent.name_buffer][self.parent.list.get_selected()], self.parent.db)
  label = wx.StaticText(self.panel, -1, _(u"Recipient"))
  self.cb = wx.ComboBox(self.panel, -1, choices=list, value=list[0], size=wx.DefaultSize)
  self.createTextArea(message, text)
  self.mainBox.Add(self.cb, 0, wx.ALL, 5)
  self.mainBox.Add(self.textBox, 0, wx.ALL, 5)
  if platform.system() != "Darwin":
   self.spellcheck = wx.Button(self.panel, -1, _("Spelling correction"), size=wx.DefaultSize)
   self.spellcheck.Bind(wx.EVT_BUTTON, self.onCheck)
  self.attach = wx.Button(self.panel, -1, _(u"Attach audio"), size=wx.DefaultSize)
  self.attach.Bind(wx.EVT_BUTTON, self.onAttach)
  self.shortenButton = wx.Button(self.panel, -1, _(u"Shorten URL"), size=wx.DefaultSize)
  self.shortenButton.Bind(wx.EVT_BUTTON, self.onShorten)
  self.unshortenButton = wx.Button(self.panel, -1, _(u"Expand URL"), size=wx.DefaultSize)
  self.unshortenButton.Bind(wx.EVT_BUTTON, self.onUnshorten)
  self.shortenButton.Disable()
  self.unshortenButton.Disable()
  self.translateButton = wx.Button(self.panel, -1, _(u"Translate message"), size=wx.DefaultSize)
  self.translateButton.Bind(wx.EVT_BUTTON, self.onTranslate)
  self.okButton = wx.Button(self.panel, wx.ID_OK, _(u"Send"), size=wx.DefaultSize)
  self.okButton.Bind(wx.EVT_BUTTON, self.onSend)
  self.okButton.SetDefault()
  cancelButton = wx.Button(self.panel, wx.ID_CANCEL, _(u"Close"), size=wx.DefaultSize)
  cancelButton.Bind(wx.EVT_BUTTON, self.onCancel)
  self.buttonsBox = wx.BoxSizer(wx.HORIZONTAL)
  if platform.system() != "Darwin":
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
  
 def __init__(self, message, title, text, parent):
  super(dm, self).__init__(message, title, text, parent)
  self.parent = parent
  self.image = None
  self.createControls(message, title, text)
  self.onTimer(wx.EVT_CHAR_HOOK)
  self.SetClientSize(self.mainBox.CalcMin())
  
 def onSend(self, ev):
  self.EndModal(wx.ID_OK)

class reply(tweet):
 def __init__(self, message, title, text, parent):
  super(reply, self).__init__(message, title, text, parent)
  self.in_reply_to = parent.db.settings[parent.name_buffer][parent.list.get_selected()]["id"]
  self.text.SetInsertionPoint(len(self.text.GetValue()))
  self.mentionAll = wx.Button(self, -1, _(u"Mention to all"), size=wx.DefaultSize)
  self.mentionAll.Disable()
  self.mentionAll.Bind(wx.EVT_BUTTON, self.mentionAllUsers)
  self.buttonsBox1.Add(self.mentionAll, 0, wx.ALL, 5)
  self.buttonsBox1.Layout()
  self.mainBox.Layout()
  self.check_if_users()
  self.SetClientSize(self.mainBox.CalcMin())

 def check_if_users(self):
  try:
   if len(self.parent.db.settings[self.parent.name_buffer][self.parent.list.get_selected()]["entities"]["user_mentions"]) > 0:
    self.mentionAll.Enable()
  except KeyError:
   pass

 def mentionAllUsers(self, ev):
  self.text.SetValue(self.text.GetValue()+twitter.utils.get_all_mentioned(self.parent.db.settings[self.parent.name_buffer][self.parent.list.get_selected()], self.parent.db))
  self.text.SetInsertionPoint(len(self.text.GetValue()))
  self.text.SetFocus()

 def onSend(self, ev):
  self.EndModal(wx.ID_OK)

class viewTweet(wx.Dialog):
 def __init__(self, tweet):
  super(viewTweet, self).__init__(None, size=(850,850))
  self.SetTitle(_(u"Tweet - %i characters ") % (len(tweet["text"])))
  panel = wx.Panel(self)
  label = wx.StaticText(panel, -1, _(u"Tweet"))
  self.text = wx.TextCtrl(panel, -1, tweet["text"], style=wx.TE_READONLY|wx.TE_MULTILINE, size=(250, 180))
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
  rtCount = wx.TextCtrl(panel, -1, str(tweet["retweet_count"]), size=wx.DefaultSize, style=wx.TE_READONLY|wx.TE_MULTILINE)
  rtBox = wx.BoxSizer(wx.HORIZONTAL)
  rtBox.Add(rtCountLabel, 0, wx.ALL, 5)
  rtBox.Add(rtCount, 0, wx.ALL, 5)
  favsCountLabel = wx.StaticText(panel, -1, _(u"Favourites: "))
  favsCount = wx.TextCtrl(panel, -1, str(tweet["favorite_count"]), size=wx.DefaultSize, style=wx.TE_READONLY|wx.TE_MULTILINE)
  favsBox = wx.BoxSizer(wx.HORIZONTAL)
  favsBox.Add(favsCountLabel, 0, wx.ALL, 5)
  favsBox.Add(favsCount, 0, wx.ALL, 5)
  infoBox = wx.BoxSizer(wx.HORIZONTAL)
  infoBox.Add(rtBox, 0, wx.ALL, 5)
  infoBox.Add(favsBox, 0, wx.ALL, 5)
  mainBox.Add(infoBox, 0, wx.ALL, 5)
  if platform.system() != "Darwin":
   spellcheck = wx.Button(panel, -1, _("Spelling correction"), size=wx.DefaultSize)
   spellcheck.Bind(wx.EVT_BUTTON, self.onCheck)
  self.unshortenButton = wx.Button(panel, -1, _(u"Expand URL"), size=wx.DefaultSize)
  self.unshortenButton.Bind(wx.EVT_BUTTON, self.onUnshorten)
  self.unshortenButton.Disable()
  translateButton = wx.Button(panel, -1, _(u"Translate message"), size=wx.DefaultSize)
  translateButton.Bind(wx.EVT_BUTTON, self.onTranslate)
  cancelButton = wx.Button(panel, wx.ID_CANCEL, _(u"Close"), size=wx.DefaultSize)
  cancelButton.SetDefault()
  buttonsBox = wx.BoxSizer(wx.HORIZONTAL)
  if platform.system() != "Darwin":
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
  self.check_urls()
  self.SetClientSize(mainBox.CalcMin())

 def check_urls(self):
  if len(twitter.utils.find_urls_in_text(self.text.GetValue())) > 0:
   self.unshortenButton.Enable()

 def onCheck(self, ev):
  if platform.system() != "Darwin": return
  text = self.text.GetValue()
  dlg = spellCheckerGUI.spellCheckerDialog(text, "")
  if dlg.ShowModal() == wx.ID_OK:
   self.text.ChangeValue(dlg.checker.get_text())
   dlg.Destroy()

 def onTranslate(self, ev):
  dlg = translator.gui.translateDialog()
  selection = dlg.ShowModal()
  if selection != wx.ID_CANCEL:
   text_to_translate = self.text.GetValue().encode("utf-8")
   source = [x[0] for x in translator.available_languages()][dlg.source_lang.GetSelection()]
   dest = [x[0] for x in translator.available_languages()][dlg.dest_lang.GetSelection()]
   t = translator.translator.Translator()
   t.from_lang = source
   t.to_lang = dest
   msg = t.translate(text_to_translate)
   self.text.ChangeValue(msg)
   output.speak(_(u"Translated"))
   self.text.SetFocus()
  else:
   return
  dlg.Destroy()

 def onSelect(self, ev):
  self.text.SelectAll()

 def onUnshorten(self, ev):
  urls =  twitter.utils.find_urls_in_text(self.text.GetValue())
  if len(urls) == 0:
   output.speak(_(u"There's no URL to be expanded"))
  elif len(urls) == 1:
   self.text.SetValue(self.text.GetValue().replace(urls[0], url_shortener.unshorten(urls[0])))
   output.speak(_(u"URL expanded"))
  elif len(urls) > 1:
   urlList.unshorten(urls, self).ShowModal()
  self.text.SetFocus()

class viewNonTweet(wx.Dialog):
 def __init__(self, tweet):
  super(viewNonTweet, self).__init__(None, size=(850,850))
  self.SetTitle(_(u"View"))
  panel = wx.Panel(self)
  label = wx.StaticText(panel, -1, _(u"Item"))
  self.text = wx.TextCtrl(parent=panel, id=-1, value=tweet, style=wx.TE_READONLY|wx.TE_MULTILINE, size=(250, 180))
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
  spellcheck.Bind(wx.EVT_BUTTON, self.onCheck)
  self.unshortenButton = wx.Button(panel, -1, _(u"Expand URL"), size=wx.DefaultSize)
  self.unshortenButton.Bind(wx.EVT_BUTTON, self.onUnshorten)
  self.unshortenButton.Disable()
  translateButton = wx.Button(panel, -1, _(u"Translate message"), size=wx.DefaultSize)
  translateButton.Bind(wx.EVT_BUTTON, self.onTranslate)
  cancelButton = wx.Button(panel, wx.ID_CANCEL, _(u"Close"), size=wx.DefaultSize)
  cancelButton.SetDefault()
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
  self.check_urls()

 def check_urls(self):
  if len(twitter.utils.find_urls_in_text(self.text.GetValue())) > 0:
   self.unshortenButton.Enable()

 def onCheck(self, ev):
  text = self.text.GetValue()
  dlg = spellCheckerGUI.spellCheckerDialog(text, "")
  if dlg.ShowModal() == wx.ID_OK:
   self.text.ChangeValue(dlg.checker.get_text())
   dlg.Destroy()

 def onTranslate(self, ev):
  dlg = translator.gui.translateDialog()
  selection = dlg.ShowModal()
  if selection != wx.ID_CANCEL:
   text_to_translate = self.text.GetValue().encode("utf-8")
   source = [x[0] for x in translator.available_languages()][dlg.source_lang.GetSelection()]
   dest = [x[0] for x in translator.available_languages()][dlg.dest_lang.GetSelection()]
   t = translator.translator.Translator()
   t.from_lang = source
   t.to_lang = dest
   msg = t.translate(text_to_translate)
   self.text.ChangeValue(msg)
   output.speak(_(u"Translated"))
   self.text.SetFocus()
  else:
   return
  dlg.Destroy()

 def onSelect(self, ev):
  self.text.SelectAll()

 def onUnshorten(self, ev):
  urls =  twitter.utils.find_urls_in_text(self.text.GetValue())
  if len(urls) == 0:
   output.speak(_(u"There's no URL to be expanded"))
  elif len(urls) == 1:
   self.text.SetValue(self.text.GetValue().replace(urls[0], url_shortener.unshorten(urls[0])))
   output.speak(_(u"URL expanded"))
  elif len(urls) > 1:
   urlList.unshorten(urls, self).ShowModal()
  self.text.SetFocus()
