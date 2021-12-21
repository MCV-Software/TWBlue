# -*- coding: utf-8 -*-
import re
import wx
from typing import List
from sessions.twitter.templates import tweet_variables, dm_variables, person_variables
from wxUI.dialogs.twitterDialogs import templateDialogs

class EditTemplate(object):
    def __init__(self, template: str, type: str) -> None:
        super(EditTemplate, self).__init__()
        self.default_template = template
        if type == "tweet":
            self.variables = tweet_variables
        elif type == "dm":
            self.variables = dm_variables
        else:
            self.variables = person_variables
        self.template: str = template

    def validate_template(self, template: str) -> bool:
        used_variables: List[str] = re.findall("\$\w+", template)
        validated: bool = True
        for var in used_variables:
            if var[1:] not in self.variables:
                validated = False
        return validated

    def run_dialog(self) -> str:
        dialog = templateDialogs.EditTemplateDialog(template=self.template, variables=self.variables, default_template=self.default_template)
        response = dialog.ShowModal()
        if response == wx.ID_SAVE:
            validated: bool = self.validate_template(dialog.template.GetValue())
            if validated == False:
                templateDialogs.invalid_template()
                self.template = dialog.template.GetValue()
                return self.run_dialog()
            else:
                return dialog.template.GetValue()
        else:
            return ""