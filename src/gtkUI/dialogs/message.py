# -*- coding: utf-8 -*-
from gi.repository import Gtk
import widgetUtils

class textLimited(widgetUtils.baseDialog):
 def __init__(self, *args, **kwargs):
  super(textLimited, self).__init__(buttons=(Gtk.STOCK_OK, widgetUtils.OK, Gtk.STOCK_CANCEL, widgetUtils.CANCEL), *args, **kwargs)

 def createTextArea(self, message="", text=""):
  self.label = Gtk.Label(message)
  self.text = Gtk.Entry()
  self.text.set_text(text)
  self.text.set_placeholder_text(message)
  self.set_title(str(len(text)))
  self.textBox = Gtk.Box(spacing=10)
  self.textBox.add(self.label)
  self.textBox.add(self.text)

 def text_focus(self):
  self.text.grab_focus()

 def get_text(self):
  return self.text.get_text()

 def set_text(self, text):
  self.text.set_text(text)

 def set_title(self, new_title):
  self.text.set_placeholder_text(new_title)
#  self.set_title(new_title)

 def enable_button(self, buttonName):
  if getattr(self, buttonName):
   return getattr(self, buttonName).show()

 def disable_button(self, buttonName):
  if getattr(self, buttonName):
   return getattr(self, buttonName).hide()

 def set_cursor_at_end(self):
  self.text.set_position(-1)

 def set_cursor_at_position(self, position):
  self.text.set_position()

 def get_position(self):
  return self.text.get_position()

class tweet(textLimited):
 def createControls(self, title, message,  text):
  self.createTextArea(message, text)
  self.box.add(self.textBox)
  self.upload_image = Gtk.Button(_(u"Upload a picture"))
  self.spellcheck = Gtk.Button(_("Spelling correction"))
  self.attach = Gtk.Button(_(u"Attach audio"))
  self.shortenButton = Gtk.Button(_(u"Shorten URL"))
  self.unshortenButton = Gtk.Button(_(u"Expand URL"))
  self.shortenButton.hide()
  self.shortenButton.set_no_show_all(True)
  self.unshortenButton.hide()
  self.unshortenButton.set_no_show_all(True)
  self.translateButton = Gtk.Button(_(u"Translate message"))
  self.autocompletionButton = Gtk.Button(_(u"&Autocomplete users"))
  self.buttonsBox1 = Gtk.Box(spacing=6)
  self.buttonsBox1.add(self.upload_image)
  self.buttonsBox1.add(self.spellcheck)
  self.buttonsBox1.add(self.attach)
  self.box.add(self.buttonsBox1)
  self.buttonsBox2 = Gtk.Box(spacing=6)
  self.buttonsBox2.add(self.shortenButton)
  self.buttonsBox2.add(self.unshortenButton)
  self.buttonsBox2.add(self.translateButton)
  self.box.add(self.buttonsBox2)

 def __init__(self, title, message, text):
  super(tweet, self).__init__()
  self.createControls(message, title, text)
  self.show_all()

 def get_image(self):
  openFileDialog = wx.FileDialog(self, _(u"Select the picture to be uploaded"), "", "", _("Image files (*.png, *.jpg, *.gif)|*.png; *.jpg; *.gif"), wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
  if openFileDialog.ShowModal() == wx.ID_CANCEL:
   return None
  return open(openFileDialog.GetPath(), "rb")

class dm(textLimited):
 def createControls(self, title, message,  users):
  label = Gtk.Label(_(u"Recipient"))
  self.cb = Gtk.ComboBoxText.new_with_entry()
  self.cb.set_entry_text_column(0)
  for user in users:
   self.cb.append_text(user)
  self.cb.get_child().set_placeholder_text(_(u"Recipient"))
  self.cb.get_child().set_text(users[0])
  self.autocompletionButton = Gtk.Button(_(u"&Autocomplete users"))
  self.createTextArea(message, text="")
  userBox = Gtk.Box(spacing=8)
  userBox.add(label)
  userBox.add(self.cb)
  userBox.add(self.autocompletionButton)
  self.box.add(userBox)
#  self.mainBox.Add(self.cb, 0, wx.ALL, 5)
  self.box.add(self.textBox)
  self.spellcheck = Gtk.Button(_("Spelling correction"))
  self.attach = Gtk.Button(_(u"Attach audio"))
  self.shortenButton = Gtk.Button(_(u"Shorten URL"))
  self.unshortenButton = Gtk.Button(_(u"Expand URL"))
  self.shortenButton.hide()
  self.shortenButton.set_no_show_all(True)
  self.unshortenButton.hide()
  self.unshortenButton.set_no_show_all(True)
  self.translateButton = Gtk.Button(_(u"Translate message"))
  self.buttonsBox = Gtk.Box(spacing=6)
  self.buttonsBox.add(self.spellcheck)
  self.buttonsBox.add(self.attach)
  self.box.add(self.buttonsBox)
  self.buttonsBox1 = Gtk.Box(spacing=6)
  self.buttonsBox1.add(self.shortenButton)
  self.buttonsBox1.add(self.unshortenButton)
  self.buttonsBox1.add(self.translateButton)
  self.box.add(self.buttonsBox1)
  self.text.grab_focus()


 def get(self, control):
  if control == "cb":
   return self.cb.get_active_text()

 def __init__(self, title, message,  users):
  super(dm, self).__init__()
  self.createControls(message, title, users)
#  self.onTimer(wx.EVT_CHAR_HOOK)
  self.show_all()

 def get_user(self):
  return self.cb.get_text()

 def set_user(self, user):
  return self.cb.set_value()

class reply(tweet):
 def __init__(self, title, message,  text):
  super(reply, self).__init__(message, title, text)
  self.text.set_position(-1)
  self.mentionAll = Gtk.Button(_(u"Men&tion to all"))
  self.mentionAll.set_no_show_all(True)
  self.mentionAll.hide()
  self.buttonsBox1.add(self.mentionAll)

class viewTweet(widgetUtils.baseDialog):
 def set_title(self, lenght):
  pass
#  self.set_title(_(u"Tweet - %i characters ") % (lenght,))

 def __init__(self, text, rt_count, favs_count):
  super(viewTweet, self).__init__(buttons=(Gtk.STOCK_OK, widgetUtils.OK, Gtk.STOCK_CANCEL, widgetUtils.CANCEL))
  label = Gtk.Label(_(u"Tweet"))
  self.text = Gtk.TextView()
  self.textBuffer = self.text.get_buffer()
  self.textBuffer.set_text(text)
  self.textBuffer.set_editable(False)
  self.text.set_placeholder_text(message)
  textBox = Gtk.Box(spacing=6)
  textBox.add(label)
  textBox.add(self.text)
  self.box.add(textBox)
  rtCountLabel = Gtk.Label(_(u"Retweets: "))
  rtCount = Gtk.Entry()
  rtCount.set_text(rt_count)
  rtCount.set_editable(False)
  rtBox = Gtk.Box(spacing=2)
  rtBox.add(rtCountLabel)
  rtBox.add(rtCount)
  favsCountLabel = Gtk.Label(_(u"Favourites: "))
  favsCount = Gtk.Entry()
  favsCount.set_text(favs_count)
  favsCount.set_editable(False)
  favsBox = Gtk.Box(spacing=2)
  favsBox.add(favsCountLabel)
  favsBox.add(favsCount)
  infoBox = Gtk.Box(spacing=4)
  infoBox.add(rtBox)
  infoBox.add(favsBox)
  self.box.add(infoBox)
  self.spellcheck = Gtk.Button(_("Spelling correction"))
  self.unshortenButton = Gtk.Button(_(u"Expand URL"))
  self.unshortenButton.hide()
  self.unshortenButton.set_no_show_all(True)
  self.translateButton = Gtk.Button(_(u"Translate message"))
  buttonsBox = Gtk.Box(spacing=6)
  buttonsBox.add(self.spellcheck)
  buttonsBox.add(self.unshortenButton)
  buttonsBox.add(self.translateButton)
  self.box.Add(buttonsBox)
  self.show_all()

 def set_text(self, text):
  self.textBuffer.set_text(text)

 def get_text(self):
  return self.textBuffer.get_text(self.textBuffer.get_start_iter(), self.textBuffer.get_end_iter(), False)

 def text_focus(self):
  self.text.grab_focus()

 def enable_button(self, buttonName):
  if getattr(self, buttonName):
   return getattr(self, buttonName).show()

class viewNonTweet(widgetUtils.baseDialog):

 def __init__(self, text):
  super(viewNonTweet, self).__init__(buttons=(Gtk.STOCK_OK, widgetUtils.OK, Gtk.STOCK_CANCEL, widgetUtils.CANCEL))
  self.set_title(_(u"View"))
  label = Gtk.Label(_(u"Item"))
  self.text = Gtk.TextView()
  self.text.set_editable(False)
  self.text.get_buffer().set_text(text)
  textBox = Gtk.Box(spacing=5)
  textBox.add(label)
  textBox.add(self.text)
  self.box.Add(textBox)
  self.spellcheck = Gtk.Button(_("Spelling correction"))
  self.unshortenButton = Gtk.Button(_(u"Expand URL"))
  self.unshortenButton.hide()
  self.unshortenButton.set_no_show_all(True)
  self.translateButton = Gtk.Button(_(u"Translate message"))
  buttonsBox = Gtk.Box(spacing=6)
  buttonsBox.add(self.spellcheck)
  buttonsBox.add(self.unshortenButton)
  buttonsBox.add(self.translateButton)
  self.box.Add(buttonsBox)
  self.show_all()

 def set_text(self, text):
  self.text.get_buffer().set_text()

 def get_text(self):
  return self.text.get_buffer().get_text()

 def text_focus(self):
  self.text.grab_focus()

 def enable_button(self, buttonName):
  if getattr(self, buttonName):
   return getattr(self, buttonName).show()
