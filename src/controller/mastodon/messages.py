# -*- coding: utf-8 -*-
import widgetUtils
import config
from controller.twitter import messages

class toot(messages.tweet):
    def __init__(self, max=500, *args, **kwargs):
        super(toot, self).__init__(max=max, *args, **kwargs)
        if hasattr(self.message, "add_tweet"):
            self.message.add_tweet.SetLabel(_("Add toot"))

class reply(toot):
    def __init__(self, users=[], *a, **b):
        super(reply, self).__init__(messageType="reply", users=users, *a, **b)
        self.users = users
        if len(users) > 0:
            widgetUtils.connect_event(self.message.mention_all, widgetUtils.CHECKBOX, self.mention_all)
            self.message.mention_all.Enable(True)
            if config.app["app-settings"]["remember_mention_and_longtweet"]:
                self.message.mention_all.SetValue(config.app["app-settings"]["mention_all"])
            self.mention_all()
        self.message.text.SetInsertionPoint(len(self.message.text.GetValue()))
        self.text_processor()

    def text_processor(self, *args, **kwargs):
        super(toot, self).text_processor(*args, **kwargs)
        if len(self.attachments) > 0:
            self.message.attachments.Enable(True)
            self.message.remove_attachment.Enable(True)
        else:
            self.message.attachments.Enable(False)
            self.message.remove_attachment.Enable(False)

    def mention_all(self, *args, **kwargs):
        if self.message.mention_all.GetValue() == True:
            for i in self.message.checkboxes:
                i.SetValue(True)
                i.Hide()
        else:
            for i in self.message.checkboxes:
                i.SetValue(False)
                i.Show()

    def get_people(self):
        people  = ""
        for i in range(0, len(self.message.checkboxes)):
            if self.message.checkboxes[i].GetValue() == True:
                people = people + "{0} ".format(self.message.checkboxes[i].GetLabel(),)
        return people
