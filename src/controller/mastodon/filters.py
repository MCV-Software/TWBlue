# -*- coding: utf-8 -*-
import widgetUtils
from wxUI.dialogs.mastodon import filters as dialogs
from mastodon import MastodonAPIError

class FilterController(object):
    def __init__(self, session, filter_data=None):
        super(FilterController, self).__init__()
        self.session = session
        self.filter_data = filter_data
        self.dialog = dialogs.MastodonFilterDialog(parent=None)
        if self.filter_data is not None:
            self.keywords = self.filter_data.get("keywords")
            self.load_filter_data()
        else:
            self.keywords = []
        widgetUtils.connect_event(self.dialog.keyword_panel.add_button, widgetUtils.BUTTON_PRESSED, self.on_add_keyword)
        widgetUtils.connect_event(self.dialog.keyword_panel.remove_button, widgetUtils.BUTTON_PRESSED, self.on_remove_keyword)

    def on_add_keyword(self, event):
        """ Adds a keyword to the list. """
        keyword = self.dialog.keyword_panel.keyword_text.GetValue().strip()
        whole_word = self.dialog.keyword_panel.whole_word_checkbox.GetValue()
        if keyword:
            for idx, kw in enumerate(self.keywords):
                if kw['keyword'] == keyword:
                    return
            keyword_data = {
                'keyword': keyword,
                'whole_word': whole_word
            }
            self.keywords.append(keyword_data)
            self.dialog.keyword_panel.add_keyword(keyword, whole_word)

    def on_remove_keyword(self, event):
        removed = self.dialog.keyword_panel.remove_keyword()
        if removed is not None:
            self.keywords.pop(removed)

    def get_expires_in_seconds(self, selection, value):
        if selection == 0:
            return None
        if selection == 1:
            return value * 3600
        elif selection == 2:
            return value * 86400
        elif selection == 3:
            return value * 604800
        elif selection == 4:
            return value * 2592000
        return None

    def set_expires_in(self, seconds):
        if seconds is None:
            self.dialog.expiration_choice.SetSelection(0)
            self.dialog.expiration_value.Enable(False)
            return
        if seconds % 2592000 == 0 and seconds >= 2592000:
            self.dialog.expiration_choice.SetSelection(4)
            self.dialog.expiration_value.SetValue(seconds // 2592000)
        elif seconds % 604800 == 0 and seconds >= 604800:
            self.dialog.expiration_choice.SetSelection(3)
            self.dialog.expiration_value.SetValue(seconds // 604800)
        elif seconds % 86400 == 0 and seconds >= 86400:
            self.dialog.expiration_choice.SetSelection(2)
            self.dialog.expiration_value.SetValue(seconds // 86400)
        else:
            self.dialog.expiration_choice.SetSelection(1)
            self.dialog.expiration_value.SetValue(max(1, seconds // 3600))
        self.dialog.expiration_value.Enable(True)

    def load_filter_data(self):
        if 'title' in self.filter_data:
            self.dialog.name_ctrl.SetValue(self.filter_data['title'])
        if 'context' in self.filter_data:
            for context in self.filter_data['context']:
                if context in self.dialog.context_checkboxes:
                    self.dialog.context_checkboxes[context].SetValue(True)
        if 'filter_action' in self.filter_data:
            action_index = self.dialog.actions.index(self.filter_data['filter_action']) if self.filter_data['filter_action'] in self.dialog.actions else 0
            self.dialog.action_choice.SetSelection(action_index)
        if 'expires_in' in self.filter_data:
            self.set_expires_in(self.filter_data['expires_in'])
        if 'keywords' in self.filter_data:
            self.keywords = self.filter_data['keywords']
            self.dialog.keyword_panel.set_keywords(self.filter_data['keywords'])

    def get_filter_data(self):
        filter_data = {
            'title': self.dialog.name_ctrl.GetValue(),
            'context': [],
            'filter_action': self.dialog.actions[self.dialog.action_choice.GetSelection()],
            'expires_in': self.get_expires_in_seconds(selection=self.dialog.expiration_choice.GetSelection(), value=self.dialog.expiration_value.GetValue()),
            'keywords': self.keywords
        }
        for context, checkbox in self.dialog.context_checkboxes.items():
            if checkbox.GetValue():
                filter_data['context'].append(context)
        return filter_data

    def get_response(self):
        return self.dialog.ShowModal()