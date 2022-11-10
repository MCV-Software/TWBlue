# -*- coding: utf-8 -*-
import widgetUtils
import config
import output
from controller.twitter import messages
from sessions.mastodon import templates
from wxUI.dialogs.mastodon import tootDialogs

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

class viewToot(toot):
    def __init__(self, toot, offset_hours=0, date="", item_url=""):
        if toot.reblog != None:
            toot = toot.reblog
        author = toot.account.display_name if toot.account.display_name != "" else toot.account.username
        title = _(u"Toot from {}").format(author)
        image_description = templates.process_image_descriptions(toot.media_attachments)
        text = templates.process_text(toot, safe=False)
        date = templates.process_date(toot.created_at, relative_times=False, offset_hours=offset_hours)
        boost_count = str(toot.reblogs_count)
        favs_count = str(toot.favourites_count)
        # Gets the client from where this toot was made.
        source_obj = toot.get("application")
        if source_obj == None:
            source = _("Remote instance")
        else:
            source = source_obj.get("name")
        self.message = tootDialogs.viewToot(text=text, boosts_count=boost_count, favs_count=favs_count, source=source, date=date)
        self.message.SetTitle(title)
        if image_description != "":
            self.message.image_description.Enable(True)
            self.message.image_description.ChangeValue(image_description)
        widgetUtils.connect_event(self.message.spellcheck, widgetUtils.BUTTON_PRESSED, self.spellcheck)
        if item_url != "":
            self.message.enable_button("share")
            widgetUtils.connect_event(self.message.share, widgetUtils.BUTTON_PRESSED, self.share)
            self.item_url = item_url
        widgetUtils.connect_event(self.message.translateButton, widgetUtils.BUTTON_PRESSED, self.translate)
        self.message.ShowModal()

    # We won't need text_processor in this dialog, so let's avoid it.
    def text_processor(self):
        pass

    def share(self, *args, **kwargs):
        if hasattr(self, "item_url"):
            output.copy(self.item_url)
            output.speak(_("Link copied to clipboard."))