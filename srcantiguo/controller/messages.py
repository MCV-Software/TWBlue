# -*- coding: utf-8 -*-
import widgetUtils
import output
import config
from extra import SpellChecker
from extra.translator import TranslatorController

class basicMessage(object):
    def translate(self, event=None):
        t = TranslatorController(self.message.text.GetValue())
        if t.response == False:
            return
        msg = t.translate()
        self.message.text.ChangeValue(msg)
        self.message.text.SetInsertionPoint(len(self.message.text.GetValue()))
        self.text_processor()
        self.message.text.SetFocus()
        output.speak(_(u"Translated"))

    def text_processor(self, *args, **kwargs):
        pass

    def spellcheck(self, event=None):
        text = self.message.text.GetValue()
        checker = SpellChecker.spellchecker.spellChecker(text, "")
        if hasattr(checker, "fixed_text"):
            self.message.text.ChangeValue(checker.fixed_text)
            self.text_processor()
            self.message.text.SetFocus()

    def remove_attachment(self, *args, **kwargs):
        attachment = self.message.attachments.GetFocusedItem()
        if attachment > -1 and len(self.attachments) > attachment:
            self.attachments.pop(attachment)
            self.message.remove_item(list_type="attachment")
            self.text_processor()
            self.message.text.SetFocus()