# -*- coding: utf-8 -*-
import widgetUtils
import output
import url_shortener
import sound
from pubsub import pub
from wxUI.dialogs import message, urlList
from extra import translator, SpellChecker
from extra.AudioUploader import audioUploader
from twitter import utils

class basicTweet(object):
 """ This class handles the tweet main features. Other classes should derive from this class."""
 def __init__(self, session):
  super(basicTweet, self).__init__()
  self.session = session
  self.message = message.tweet(_(u"Write the tweet here"), _(u"tweet - 0 characters"), "")
  widgetUtils.connect_event(self.message.spellcheck, widgetUtils.BUTTON_PRESSED, self.spellcheck)
  widgetUtils.connect_event(self.message.attach, widgetUtils.BUTTON_PRESSED, self.attach)
  widgetUtils.connect_event(self.message.text, widgetUtils.ENTERED_TEXT, self.text_processor)
  widgetUtils.connect_event(self.message.shortenButton, widgetUtils.BUTTON_PRESSED, self.shorten)
  widgetUtils.connect_event(self.message.unshortenButton, widgetUtils.BUTTON_PRESSED, self.unshorten)
  widgetUtils.connect_event(self.message.translateButton, widgetUtils.BUTTON_PRESSED, self.translate)

 def translate(self, event=None):
  dlg = translator.gui.translateDialog()
  if dlg.get_response() == widgetUtils.OK:
   text_to_translate = self.message.get_text()
   source = [x[0] for x in translator.translator.available_languages()][dlg.get("source_lang")]
   dest = [x[0] for x in translator.translator.available_languages()][dlg.get("dest_lang")]
   t = translator.translator.Translator()
   t.from_lang = source
   t.to_lang = dest
   msg = t.translate(text_to_translate)
   self.message.set_text(msg)
   output.speak(_(u"Translated"))
  else:
   return

 def shorten(self, event=None):
  urls = utils.find_urls_in_text(self.message.get_text())
  if len(urls) == 0:
   output.speak(_(u"There's no URL to be shortened"))
  elif len(urls) == 1:
   self.message.set_text(self.message.get_text().replace(urls[0], url_shortener.shorten(urls[0])))
   output.speak(_(u"URL shortened"))
  elif len(urls) > 1:
   list_urls = urlList.urlList()
   list_urls.populate_list(urls)
   if list_urls.get_response() == widgetUtils.OK:
    self.message.set_text(self.message.get_text().replace(urls[list_urls.get_item()], url_shortener.shorten(list_urls.get_string())))
    output.speak(_(u"URL shortened"))

 def unshorten(self, event=None):
  urls = utils.find_urls_in_text(self.message.get_text())
  if len(urls) == 0:
   output.speak(_(u"There's no URL to be sexpanded"))
  elif len(urls) == 1:
   self.message.set_text(self.message.get_text().replace(urls[0], url_shortener.unshorten(urls[0])))
   output.speak(_(u"URL expanded"))
  elif len(urls) > 1:
   list_urls = urlList.urlList()
   list_urls.populate_list(urls)
   if list_urls.get_response() == widgetUtils.OK:
    self.message.set_text(self.message.get_text().replace(urls[list_urls.get_item()], url_shortener.unshorten(list_urls.get_string())))
    output.speak(_(u"URL expanded"))

 def text_processor(self, event=None):
  self.message.set_title("%s of 140 characters" % (len(self.message.get_text())))
  if len(self.message.get_text()) > 1:
   self.message.enable_button("shortenButton")
   self.message.enable_button("unshortenButton")
  else:
   self.message.disable_button("shortenButton")
   self.message.disable_button("unshortenButton")
  if len(self.message.get_text()) > 140:
   sound.player.play("max_length.ogg")

 def spellcheck(self, event=None):
  text = self.message.get_text()
  checker = SpellChecker.spellchecker.spellChecker(text, "")
  if hasattr(checker, "fixed_text"):
   self.message.set_text(checker.fixed_text)

 def attach(self, *args, **kwargs):
  def completed_callback():
   url = dlg.uploaderFunction.get_url()
   pub.unsubscribe(dlg.uploaderDialog.update, "uploading")
   dlg.uploaderDialog.destroy()
   if url != 0:
    self.message.set_text(self.message.get_text()+url+" #audio")
   else:
    output.speak(_(u"Unable to upload the audio"))
   dlg.cleanup()
  dlg = audioUploader.audioUploader(self.session.settings, completed_callback)

class tweet(basicTweet):
 def __init__(self, session):
  super(tweet, self).__init__(session)
  self.image = None
  widgetUtils.connect_event(self.message.upload_image, widgetUtils.BUTTON_PRESSED, self.upload_image)

 def upload_image(self, *args, **kwargs):
  if self.message.get("upload_image") == _(u"Discard image"):
   del self.image
   self.image = None
   output.speak(_(u"Discarded"))
   self.message.set("upload_image", _(u"Upload a picture"))
  else:
   self.image = self.message.get_image()
   self.message.set("upload_image", _(u"Discard image"))