# -*- coding: utf-8 -*-
import widgetUtils
import output
from wxUI.dialogs import message
from extra import translator

class tweet(object):
 def __init__(self, session):
  super(tweet, self).__init__()
  self.message = message.tweet(_(u"Write the tweet here"), _(u"tweet - 0 characters"), "")
#  widgetUtils.connect_event(self.message.upload_image, widgetUtils.BUTTON_PRESSED, self.upload_image)
#  widgetUtils.connect_event(self.message.spellcheck, widgetUtils.BUTTON_PRESSED, self.spellcheck)
#  widgetUtils.connect_event(self.message.attach, widgetUtils.BUTTON_PRESSED, self.attach)
#  widgetUtils.connect_event(self.message.shortenButton, widgetUtils.BUTTON_PRESSED, self.shorten)
#  widgetUtils.connect_event(self.message.unshortenButton, widgetUtils.BUTTON_PRESSED, self.unshorten)
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
