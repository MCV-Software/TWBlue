# -*- coding: utf-8 -*-
import platform
system = platform.system()
import widgetUtils
import output
import url_shortener
import sound
from pubsub import pub
if system == "Windows":
 from wxUI.dialogs import message, urlList
 from extra import translator, SpellChecker, autocompletionUsers
 from extra.AudioUploader import audioUploader
elif system == "Linux":
 from gtkUI.dialogs import message
from twitter import utils

class basicTweet(object):
 """ This class handles the tweet main features. Other classes should derive from this class."""
 def __init__(self, session, title, caption, text, messageType="tweet"):
  super(basicTweet, self).__init__()
  self.title = title
  self.session = session
  self.message = getattr(message, messageType)(title, caption, text)
  widgetUtils.connect_event(self.message.spellcheck, widgetUtils.BUTTON_PRESSED, self.spellcheck)
  widgetUtils.connect_event(self.message.attach, widgetUtils.BUTTON_PRESSED, self.attach)
#  if system == "Windows":
  widgetUtils.connect_event(self.message.text, widgetUtils.ENTERED_TEXT, self.text_processor)
  self.text_processor()
  widgetUtils.connect_event(self.message.shortenButton, widgetUtils.BUTTON_PRESSED, self.shorten)
  widgetUtils.connect_event(self.message.unshortenButton, widgetUtils.BUTTON_PRESSED, self.unshorten)
  widgetUtils.connect_event(self.message.translateButton, widgetUtils.BUTTON_PRESSED, self.translate)

 def translate(self, event=None):
  dlg = translator.gui.translateDialog()
  if dlg.get_response() == widgetUtils.OK:
   text_to_translate = self.message.get_text().encode("utf-8")
   source = [x[0] for x in translator.translator.available_languages()][dlg.get("source_lang")]
   dest = [x[0] for x in translator.translator.available_languages()][dlg.get("dest_lang")]
   t = translator.translator.Translator()
   t.from_lang = source
   t.to_lang = dest
   msg = t.translate(text_to_translate)
   self.message.set_text(msg)
   self.message.text_focus()
   output.speak(_(u"Translated"))
  else:
   return

 def shorten(self, event=None):
  urls = utils.find_urls_in_text(self.message.get_text())
  if len(urls) == 0:
   output.speak(_(u"There's no URL to be shortened"))
   self.message.text_focus()
  elif len(urls) == 1:
   self.message.set_text(self.message.get_text().replace(urls[0], url_shortener.shorten(urls[0])))
   output.speak(_(u"URL shortened"))
   self.message.text_focus()
  elif len(urls) > 1:
   list_urls = urlList.urlList()
   list_urls.populate_list(urls)
   if list_urls.get_response() == widgetUtils.OK:
    self.message.set_text(self.message.get_text().replace(urls[list_urls.get_item()], url_shortener.shorten(list_urls.get_string())))
    output.speak(_(u"URL shortened"))
    self.message.text_focus()

 def unshorten(self, event=None):
  urls = utils.find_urls_in_text(self.message.get_text())
  if len(urls) == 0:
   output.speak(_(u"There's no URL to be expanded"))
   self.message.text_focus()
  elif len(urls) == 1:
   self.message.set_text(self.message.get_text().replace(urls[0], url_shortener.unshorten(urls[0])))
   output.speak(_(u"URL expanded"))
   self.message.text_focus()
  elif len(urls) > 1:
   list_urls = urlList.urlList()
   list_urls.populate_list(urls)
   if list_urls.get_response() == widgetUtils.OK:
    self.message.set_text(self.message.get_text().replace(urls[list_urls.get_item()], url_shortener.unshorten(list_urls.get_string())))
    output.speak(_(u"URL expanded"))
    self.message.text_focus()

 def text_processor(self, *args, **kwargs):
  self.message.set_title(_(u"%s - %s of 140 characters") % (self.title, len(self.message.get_text())))
  if len(self.message.get_text()) > 1:
   self.message.enable_button("shortenButton")
   self.message.enable_button("unshortenButton")
  else:
   self.message.disable_button("shortenButton")
   self.message.disable_button("unshortenButton")
  if len(self.message.get_text()) > 140:
   self.session.sound.play("max_length.ogg")

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
 def __init__(self, session, title, caption, text, messageType="tweet"):
  super(tweet, self).__init__(session, title, caption, text, messageType)
  self.image = None
  widgetUtils.connect_event(self.message.upload_image, widgetUtils.BUTTON_PRESSED, self.upload_image)
  widgetUtils.connect_event(self.message.autocompletionButton, widgetUtils.BUTTON_PRESSED, self.autocomplete_users)

 def upload_image(self, *args, **kwargs):
  if self.message.get("upload_image") == _(u"Discard image"):
   del self.image
   self.image = None
   output.speak(_(u"Discarded"))
   self.message.set("upload_image", _(u"Upload a picture"))
  else:
   self.image = self.message.get_image()
   if self.image != None:
    self.message.set("upload_image", _(u"Discard image"))

 def autocomplete_users(self, *args, **kwargs):
  c = autocompletionUsers.completion.autocompletionUsers(self.message, self.session.session_id)
  c.show_menu()

class reply(tweet):
 def __init__(self, session, title, caption, text, users=None):
  super(reply, self).__init__(session, title, caption, text, messageType="reply")
  self.users = users
  if self.users != None and len(self.users) > 1:
   widgetUtils.connect_event(self.message.mentionAll, widgetUtils.BUTTON_PRESSED, self.mention_all)
   self.message.enable_button("mentionAll")
  self.message.set_cursor_at_end()

 def mention_all(self, *args, **kwargs):
  self.message.set_text(self.message.get_text()+self.users)
  self.message.set_cursor_at_end()
  self.message.text_focus()

class dm(basicTweet):
 def __init__(self, session, title, caption, text):
  super(dm, self).__init__(session, title, caption, text, messageType="dm")
  widgetUtils.connect_event(self.message.autocompletionButton, widgetUtils.BUTTON_PRESSED, self.autocomplete_users)

 def autocomplete_users(self, *args, **kwargs):
  c = autocompletionUsers.completion.autocompletionUsers(self.message, self.session.session_id)
  c.show_menu("dm")

class viewTweet(basicTweet):
 def __init__(self, tweet, is_tweet=True):
  if is_tweet == True:
   if tweet.has_key("retweeted_status"):
    text = "rt @%s: %s" % (tweet["retweeted_status"]["user"]["screen_name"], tweet["retweeted_status"]["text"])
   else:
    text = tweet["text"]
   rt_count = str(tweet["retweet_count"])
   favs_count = str(tweet["favorite_count"])
   self.message = message.viewTweet(text, rt_count, favs_count)
   self.message.set_title(len(text))
  else:
   text = tweet
   self.message = message.viewNonTweet(text)
  widgetUtils.connect_event(self.message.spellcheck, widgetUtils.BUTTON_PRESSED, self.spellcheck)
  widgetUtils.connect_event(self.message.translateButton, widgetUtils.BUTTON_PRESSED, self.translate)
  if self.contain_urls() == True:
   self.message.enable_button("unshortenButton")
   widgetUtils.connect_event(self.message.unshortenButton, widgetUtils.BUTTON_PRESSED, self.unshorten)
  self.message.get_response()

 def contain_urls(self):
  if len(utils.find_urls_in_text(self.message.get_text())) > 0:
   return True
  return False
