# -*- coding: utf-8 -*-
import widgetUtils
import output
from extra import translator, SpellChecker

class basicMessage(object):
    def translate(self, event=None):
        dlg = translator.gui.translateDialog()
        if dlg.get_response() == widgetUtils.OK:
            text_to_translate = self.message.text.GetValue()
            language_dict = translator.translator.available_languages()
            for k in language_dict:
                if language_dict[k] == dlg.dest_lang.GetStringSelection():
                    dst = k
            msg = translator.translator.translate(text=text_to_translate, target=dst)
            self.message.text.ChangeValue(msg)
            self.message.text.SetInsertionPoint(len(self.message.text.GetValue()))
            self.text_processor()
            self.message.text.SetFocus()
            output.speak(_(u"Translated"))
        else:
            return

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