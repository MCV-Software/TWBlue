# -*- coding: utf-8 -*-
import re
import platform
import attach
import arrow
import languageHandler
system = platform.system()
import widgetUtils
import output
import url_shortener
import sound
import config
from pubsub import pub
if system == "Windows":
 from wxUI.dialogs import message, urlList
 from wxUI import commonMessageDialogs

 from extra import translator, SpellChecker, autocompletionUsers
 from extra.AudioUploader import audioUploader
elif system == "Linux":
 from gtkUI.dialogs import message
from sessions.twitter import utils

class basicTweet(object):
 """ This class handles the tweet main features. Other classes should derive from this class."""
 def __init__(self, session, title, caption, text, messageType="tweet", max=280, *args, **kwargs):
  super(basicTweet, self).__init__()
  self.max = max
  self.title = title
  self.session = session
  self.message = getattr(message, messageType)(title, caption, text, *args, **kwargs)
  widgetUtils.connect_event(self.message.spellcheck, widgetUtils.BUTTON_PRESSED, self.spellcheck)
  widgetUtils.connect_event(self.message.attach, widgetUtils.BUTTON_PRESSED, self.attach)
  widgetUtils.connect_event(self.message.text, widgetUtils.ENTERED_TEXT, self.text_processor)
  widgetUtils.connect_event(self.message.shortenButton, widgetUtils.BUTTON_PRESSED, self.shorten)
  widgetUtils.connect_event(self.message.unshortenButton, widgetUtils.BUTTON_PRESSED, self.unshorten)
  widgetUtils.connect_event(self.message.translateButton, widgetUtils.BUTTON_PRESSED, self.translate)
  if hasattr(self.message, "long_tweet"):
   widgetUtils.connect_event(self.message.long_tweet, widgetUtils.CHECKBOX, self.text_processor)
   if config.app["app-settings"]["remember_mention_and_longtweet"]:
    self.message.long_tweet.SetValue(config.app["app-settings"]["longtweet"])
  self.attachments = []

 def translate(self, event=None):
  dlg = translator.gui.translateDialog()
  if dlg.get_response() == widgetUtils.OK:
   text_to_translate = self.message.get_text()
   dest = [x[0] for x in translator.translator.available_languages()][dlg.get("dest_lang")]
   msg = translator.translator.translate(text=text_to_translate, target=dest)
   self.message.set_text(msg)
   self.text_processor()
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
   self.text_processor()
   self.message.text_focus()
  elif len(urls) > 1:
   list_urls = urlList.urlList()
   list_urls.populate_list(urls)
   if list_urls.get_response() == widgetUtils.OK:
    self.message.set_text(self.message.get_text().replace(urls[list_urls.get_item()], url_shortener.shorten(list_urls.get_string())))
    output.speak(_(u"URL shortened"))
    self.text_processor()
    self.message.text_focus()

 def unshorten(self, event=None):
  urls = utils.find_urls_in_text(self.message.get_text())
  if len(urls) == 0:
   output.speak(_(u"There's no URL to be expanded"))
   self.message.text_focus()
  elif len(urls) == 1:
   self.message.set_text(self.message.get_text().replace(urls[0], url_shortener.unshorten(urls[0])))
   output.speak(_(u"URL expanded"))
   self.text_processor()
   self.message.text_focus()
  elif len(urls) > 1:
   list_urls = urlList.urlList()
   list_urls.populate_list(urls)
   if list_urls.get_response() == widgetUtils.OK:
    self.message.set_text(self.message.get_text().replace(urls[list_urls.get_item()], url_shortener.unshorten(list_urls.get_string())))
    output.speak(_(u"URL expanded"))
    self.text_processor()
    self.message.text_focus()

 def text_processor(self, *args, **kwargs):
  if len(self.message.get_text()) > 1:
   self.message.enable_button("shortenButton")
   self.message.enable_button("unshortenButton")
  else:
   self.message.disable_button("shortenButton")
   self.message.disable_button("unshortenButton")
  if self.message.get("long_tweet") == False:
   self.message.set_title(_(u"%s - %s of %d characters") % (self.title, len(self.message.get_text()), self.max))
   if len(self.message.get_text()) > self.max:
    self.session.sound.play("max_length.ogg")
  else:
   self.message.set_title(_(u"%s - %s characters") % (self.title, len(self.message.get_text())))

 def spellcheck(self, event=None):
  text = self.message.get_text()
  checker = SpellChecker.spellchecker.spellChecker(text, "")
  if hasattr(checker, "fixed_text"):
   self.message.set_text(checker.fixed_text)
   self.text_processor()
   self.message.text_focus()

 def attach(self, *args, **kwargs):
  def completed_callback(dlg):
   url = dlg.uploaderFunction.get_url()
   pub.unsubscribe(dlg.uploaderDialog.update, "uploading")
   dlg.uploaderDialog.destroy()
   if "sndup.net/" in url:
    self.message.set_text(self.message.get_text()+url+" #audio")
    self.text_processor()
   else:
    commonMessageDialogs.common_error(url)

   dlg.cleanup()
  dlg = audioUploader.audioUploader(self.session.settings, completed_callback)
  self.message.text_focus()

class tweet(basicTweet):
 def __init__(self, session, title, caption, text, max=280, messageType="tweet", *args, **kwargs):
  super(tweet, self).__init__(session, title, caption, text, messageType, max, *args, **kwargs)
  self.image = None
  widgetUtils.connect_event(self.message.upload_image, widgetUtils.BUTTON_PRESSED, self.upload_image)
  widgetUtils.connect_event(self.message.autocompletionButton, widgetUtils.BUTTON_PRESSED, self.autocomplete_users)
  self.text_processor()

 def upload_image(self, *args, **kwargs):
  a = attach.attach()
  if len(a.attachments) != 0:
   self.attachments = a.attachments

 def autocomplete_users(self, *args, **kwargs):
  c = autocompletionUsers.completion.autocompletionUsers(self.message, self.session.session_id)
  c.show_menu()

class reply(tweet):
 def __init__(self, session, title, caption, text, users=[], ids=[]):
  super(reply, self).__init__(session, title, caption, text, messageType="reply", users=users)
  self.ids = ids
  self.users = users
  if len(users) > 0:
   widgetUtils.connect_event(self.message.mentionAll, widgetUtils.CHECKBOX, self.mention_all)
   self.message.enable_button("mentionAll")
   if config.app["app-settings"]["remember_mention_and_longtweet"]:
    self.message.mentionAll.SetValue(config.app["app-settings"]["mention_all"])
   self.mention_all()
  self.message.set_cursor_at_end()
  self.text_processor()

 def mention_all(self, *args, **kwargs):
  if self.message.mentionAll.GetValue() == True:
   for i in self.message.checkboxes:
    i.SetValue(True)
    i.Hide()
  else:
   for i in self.message.checkboxes:
    i.SetValue(False)
    i.Show()

 def get_ids(self):
  excluded_ids  = ""
  for i in xrange(0, len(self.message.checkboxes)):
   if self.message.checkboxes[i].GetValue() == False:
    excluded_ids = excluded_ids + "{0},".format(self.ids[i],)
  return excluded_ids

 def get_people(self):
  people  = ""
  for i in xrange(0, len(self.message.checkboxes)):
   if self.message.checkboxes[i].GetValue() == True:
    people = people + "{0} ".format(self.message.checkboxes[i].GetLabel(),)
  return people

class dm(basicTweet):
 def __init__(self, session, title, caption, text):
  super(dm, self).__init__(session, title, caption, text, messageType="dm", max=10000)
  widgetUtils.connect_event(self.message.autocompletionButton, widgetUtils.BUTTON_PRESSED, self.autocomplete_users)
  self.text_processor()

 def autocomplete_users(self, *args, **kwargs):
  c = autocompletionUsers.completion.autocompletionUsers(self.message, self.session.session_id)
  c.show_menu("dm")

class viewTweet(basicTweet):
 def __init__(self, tweet, tweetList, is_tweet=True, utc_offset=0, date=""):
  """ This represents a tweet displayer. However it could be used for showing something wich is not a tweet, like a direct message or an event.
   param tweet: A dictionary that represents a full tweet or a string for non-tweets.
   param tweetList: If is_tweet is set to True, this could be a list of quoted tweets.
   param is_tweet: True or false, depending wether the passed object is a tweet or not."""
  if is_tweet == True:
   self.title = _(u"Tweet")
   image_description = []
   text = ""
   for i in xrange(0, len(tweetList)):
    # tweets with message keys are longer tweets, the message value is the full messaje taken from twishort.
    if tweetList[i].has_key("message") and tweetList[i]["is_quote_status"] == False:
     value = "message"
    else:
     value = "full_text"
    if tweetList[i].has_key("retweeted_status") and tweetList[i]["is_quote_status"] == False:
     if tweetList[i].has_key("message") == False:
      text = text + "rt @%s: %s\n" % (tweetList[i]["retweeted_status"]["user"]["screen_name"], tweetList[i]["retweeted_status"]["full_text"])
     else:
      text = text + "rt @%s: %s\n" % (tweetList[i]["retweeted_status"]["user"]["screen_name"], tweetList[i][value])
    else:
     text = text + " @%s: %s\n" % (tweetList[i]["user"]["screen_name"], tweetList[i][value])
    # tweets with extended_entities could include image descriptions.
    if tweetList[i].has_key("extended_entities") and tweetList[i]["extended_entities"].has_key("media"):
     for z in tweetList[i]["extended_entities"]["media"]:
      if z.has_key("ext_alt_text") and z["ext_alt_text"] != None:
       image_description.append(z["ext_alt_text"])
    if tweetList[i].has_key("retweeted_status") and tweetList[i]["retweeted_status"].has_key("extended_entities") and tweetList[i]["retweeted_status"]["extended_entities"].has_key("media"):
     for z in tweetList[i]["retweeted_status"]["extended_entities"]["media"]:
      if z.has_key("ext_alt_text") and z["ext_alt_text"] != None:
       image_description.append(z["ext_alt_text"])
   # set rt and likes counters.
   rt_count = str(tweet["retweet_count"])
   favs_count = str(tweet["favorite_count"])
   # Gets the client from where this tweet was made.
   source = str(re.sub(r"(?s)<.*?>", "", tweet["source"].encode("utf-8")))
   original_date = arrow.get(tweet["created_at"], "ddd MMM DD H:m:s Z YYYY", locale="en")
   date = original_date.replace(seconds=utc_offset).format(_(u"MMM D, YYYY. H:m"), locale=languageHandler.getLanguage())
   if text == "":
    if tweet.has_key("message"):
     value = "message"
    else:
     value = "full_text"
    if tweet.has_key("retweeted_status"):
     if tweet.has_key("message") == False:
      text = "rt @%s: %s" % (tweet["retweeted_status"]["user"]["screen_name"], tweet["retweeted_status"]["full_text"])
     else:
      text = "rt @%s: %s" % (tweet["retweeted_status"]["user"]["screen_name"], tweet[value])
    else:
     text = tweet[value]
   text = self.clear_text(text)
   if tweet.has_key("extended_entities") and tweet["extended_entities"].has_key("media"):
    for z in tweet["extended_entities"]["media"]:
     if z.has_key("ext_alt_text") and z["ext_alt_text"] != None:
      image_description.append(z["ext_alt_text"])
   if tweet.has_key("retweeted_status") and tweet["retweeted_status"].has_key("extended_entities") and tweet["retweeted_status"]["extended_entities"].has_key("media"):
    for z in tweet["retweeted_status"]["extended_entities"]["media"]:
     if z.has_key("ext_alt_text") and z["ext_alt_text"] != None:
      image_description.append(z["ext_alt_text"])
   self.message = message.viewTweet(text, rt_count, favs_count, source.decode("utf-8"), date)
   self.message.set_title(len(text))
   [self.message.set_image_description(i) for i in image_description]
  else:
   self.title = _(u"View item")
   text = tweet
   self.message = message.viewNonTweet(text, date)
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

 def clear_text(self, text):
  urls = utils.find_urls_in_text(text)
  for i in urls:
   if "https://twitter.com/" in i:
    text = text.replace(i, "\n")
  return text
