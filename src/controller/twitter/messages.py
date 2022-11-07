# -*- coding: utf-8 -*-
import os
import arrow
import languageHandler
import wx
import widgetUtils
import output
import sound
import config
from pubsub import pub
from twitter_text import parse_tweet
from wxUI.dialogs import twitterDialogs, urlList
from wxUI import commonMessageDialogs
from extra import translator, SpellChecker
from extra.AudioUploader import audioUploader
from extra.autocompletionUsers import completion
from sessions.twitter import utils

class basicTweet(object):
    """ This class handles the tweet main features. Other classes should derive from this class."""
    def __init__(self, session, title, caption, text="", messageType="tweet", max=280, *args, **kwargs):
        super(basicTweet, self).__init__()
        self.max = max
        self.title = title
        self.session = session
        self.message = getattr(twitterDialogs, messageType)(title=title, caption=caption, message=text, *args, **kwargs)
        self.message.text.SetValue(text)
        self.message.text.SetInsertionPoint(len(self.message.text.GetValue()))
        widgetUtils.connect_event(self.message.spellcheck, widgetUtils.BUTTON_PRESSED, self.spellcheck)
        widgetUtils.connect_event(self.message.add_audio, widgetUtils.BUTTON_PRESSED, self.attach)
        widgetUtils.connect_event(self.message.text, widgetUtils.ENTERED_TEXT, self.text_processor)
        widgetUtils.connect_event(self.message.translate, widgetUtils.BUTTON_PRESSED, self.translate)
        if hasattr(self.message, "add"):
            widgetUtils.connect_event(self.message.add, widgetUtils.BUTTON_PRESSED, self.on_attach)
        self.attachments = []

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
        text = self.message.text.GetValue()
        results = parse_tweet(text)
        self.message.SetTitle(_("%s - %s of %d characters") % (self.title, results.weightedLength, self.max))
        if results.weightedLength > self.max:
            self.session.sound.play("max_length.ogg")

    def spellcheck(self, event=None):
        text = self.message.text.GetValue()
        checker = SpellChecker.spellchecker.spellChecker(text, "")
        if hasattr(checker, "fixed_text"):
            self.message.text.ChangeValue(checker.fixed_text)
            self.text_processor()
            self.message.text.SetFocus()

    def attach(self, *args, **kwargs):
        def completed_callback(dlg):
            url = dlg.uploaderFunction.get_url()
            pub.unsubscribe(dlg.uploaderDialog.update, "uploading")
            dlg.uploaderDialog.destroy()
            if "sndup.net/" in url:
                self.message.text.ChangeValue(self.message.text.GetValue()+url+" #audio")
                self.text_processor()
            else:
                commonMessageDialogs.common_error(url)
            dlg.cleanup()
        dlg = audioUploader.audioUploader(self.session.settings, completed_callback)
        self.message.text.SetFocus()

    def can_attach(self):
        if len(self.attachments) == 0:
            return True
        elif len(self.attachments) == 1 and (self.attachments[0]["type"] == "video" or self.attachments[0]["type"] == "gif"):
            return False
        elif len(self.attachments) < 4:
            return True
        return False

    def on_attach(self, *args, **kwargs):
        can_attach = self.can_attach()
        menu = self.message.attach_menu(can_attach)
        self.message.Bind(wx.EVT_MENU, self.on_attach_image, self.message.add_image)
        self.message.Bind(wx.EVT_MENU, self.on_attach_video, self.message.add_video)
        if hasattr(self.message, "add_poll"):
            self.message.Bind(wx.EVT_MENU, self.on_attach_poll, self.message.add_poll)
        self.message.PopupMenu(menu, self.message.add.GetPosition())

    def on_attach_image(self, *args, **kwargs):
        can_attach = self.can_attach()
        video_or_gif_present = False
        for a in self.attachments:
            if a["type"] == "video" or a["type"] == "gif":
                video_or_gif = True
                break
        if can_attach == False or video_or_gif_present == True:
            return self.message.unable_to_attach_file()
        image, description  = self.message.get_image()
        if image != None:
            if image.endswith("gif"):
                image_type = "gif"
            else:
                image_type = "photo"
            imageInfo = {"type": image_type, "file": image, "description": description}
            if len(self.attachments) > 0 and image_type == "gif":
                return self.message.unable_to_attach_file()
            self.attachments.append(imageInfo)
            self.message.add_item(item=[os.path.basename(imageInfo["file"]), imageInfo["type"], imageInfo["description"]])
            self.text_processor()

    def on_attach_video(self, *args, **kwargs):
        if len(self.attachments) > 0:
            return self.message.unable_to_attach_file()
        video = self.message.get_video()
        if video != None:
            videoInfo = {"type": "video", "file": video, "description": ""}
            if len(self.attachments) > 0:
                return self.message.unable_to_attach_file()
            self.attachments.append(videoInfo)
            self.message.add_item(item=[os.path.basename(videoInfo["file"]), videoInfo["type"], videoInfo["description"]])
            self.text_processor()

    def on_attach_poll(self, *args, **kwargs):
        dlg = twitterDialogs.poll()
        if dlg.ShowModal() == wx.ID_OK:
            self.poll_options = dlg.get_options()
            self.poll_period = 60*24*dlg.period.GetValue()
        dlg.Destroy()

    def remove_attachment(self, *args, **kwargs):
        attachment = self.message.attachments.GetFocusedItem()
        if attachment > -1 and len(self.attachments) > attachment:
            self.attachments.pop(attachment)
            self.message.remove_item(list_type="attachment")
            self.text_processor()
            self.message.text.SetFocus()

class tweet(basicTweet):
    def __init__(self, session, title, caption, text="", max=280, messageType="tweet", *args, **kwargs):
        self.thread = []
        self.poll_options = None
        self.poll_period = None
        super(tweet, self).__init__(session, title, caption, text, messageType, max, *args, **kwargs)
        widgetUtils.connect_event(self.message.autocomplete_users, widgetUtils.BUTTON_PRESSED, self.autocomplete_users)
        if hasattr(self.message, "add_tweet"):
            widgetUtils.connect_event(self.message.add_tweet, widgetUtils.BUTTON_PRESSED, self.add_tweet)
            widgetUtils.connect_event(self.message.remove_tweet, widgetUtils.BUTTON_PRESSED, self.remove_tweet)
        widgetUtils.connect_event(self.message.remove_attachment, widgetUtils.BUTTON_PRESSED, self.remove_attachment)
        self.text_processor()

    def autocomplete_users(self, *args, **kwargs):
        c = completion.autocompletionUsers(self.message, self.session.session_id)
        c.show_menu()

    def add_tweet(self, event, update_gui=True, *args, **kwargs):
        text = self.message.text.GetValue()
        attachments = self.attachments[::]
        tweetdata = dict(text=text, attachments=attachments, poll_options=self.poll_options, poll_period=self.poll_period)
        self.thread.append(tweetdata)
        self.attachments = []
        self.poll_options = None
        self.poll_period = None
        if update_gui:
            self.message.reset_controls()
            self.message.add_item(item=[text, len(attachments)], list_type="tweet")
            self.message.text.SetFocus()
            self.text_processor()

    def get_tweet_data(self):
        self.add_tweet(event=None, update_gui=False)
        return self.thread

    def text_processor(self, *args, **kwargs):
        super(tweet, self).text_processor(*args, **kwargs)
        if len(self.thread) > 0:
            self.message.tweets.Enable(True)
            self.message.remove_tweet.Enable(True)
        else:
            self.message.tweets.Enable(False)
            self.message.remove_tweet.Enable(False)
        if len(self.attachments) > 0:
            self.message.attachments.Enable(True)
            self.message.remove_attachment.Enable(True)
        else:
            self.message.attachments.Enable(False)
            self.message.remove_attachment.Enable(False)
        if hasattr(self.message, "add_tweet"):
            if len(self.message.text.GetValue()) > 0 or len(self.attachments) > 0:
                self.message.add_tweet.Enable(True)
            else:
                self.message.add_tweet.Enable(False)

    def remove_tweet(self, *args, **kwargs):
        tweet = self.message.tweets.GetFocusedItem()
        if tweet > -1 and len(self.thread) > tweet:
            self.thread.pop(tweet)
            self.message.remove_item(list_type="tweet")
            self.text_processor()
            self.message.text.SetFocus()


class reply(tweet):
    def __init__(self, session, title, caption, text, users=[], ids=[]):
        super(reply, self).__init__(session, title, caption, text, messageType="reply", users=users)
        self.ids = ids
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
        super(tweet, self).text_processor(*args, **kwargs)
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

    def get_ids(self):
        excluded_ids  = []
        for i in range(0, len(self.message.checkboxes)):
            if self.message.checkboxes[i].GetValue() == False:
                excluded_ids.append(self.ids[i])
        return excluded_ids

    def get_people(self):
        people  = ""
        for i in range(0, len(self.message.checkboxes)):
            if self.message.checkboxes[i].GetValue() == True:
                people = people + "{0} ".format(self.message.checkboxes[i].GetLabel(),)
        return people

class dm(basicTweet):
    def __init__(self, session, title, caption, users):
        super(dm, self).__init__(session, title, caption, messageType="dm", max=10000, users=users)
        widgetUtils.connect_event(self.message.autocomplete_users, widgetUtils.BUTTON_PRESSED, self.autocomplete_users)
        self.text_processor()
        widgetUtils.connect_event(self.message.cb, widgetUtils.ENTERED_TEXT, self.user_changed)

    def user_changed(self, *args, **kwargs):
        self.title = _("Direct message to %s") % (self.message.cb.GetValue())
        self.text_processor()

    def autocomplete_users(self, *args, **kwargs):
        c = completion.autocompletionUsers(self.message, self.session.session_id)
        c.show_menu("dm")

    def text_processor(self, *args, **kwargs):
        super(dm, self).text_processor(*args, **kwargs)
        if len(self.attachments) > 0:
            self.message.attachments.Enable(True)
            self.message.remove_attachment.Enable(True)
        else:
            self.message.attachments.Enable(False)
            self.message.remove_attachment.Enable(False)

    def can_attach(self):
        if len(self.attachments) == 0:
            return True
        return False

class viewTweet(basicTweet):
    def __init__(self, tweet, tweetList, is_tweet=True, utc_offset=0, date="", item_url=""):
        """ This represents a tweet displayer. However it could be used for showing something wich is not a tweet, like a direct message or an event.
         param tweet: A dictionary that represents a full tweet or a string for non-tweets.
         param tweetList: If is_tweet is set to True, this could be a list of quoted tweets.
         param is_tweet: True or false, depending wether the passed object is a tweet or not."""
        if is_tweet == True:
            self.title = _(u"Tweet")
            image_description = []
            text = ""
            for i in range(0, len(tweetList)):
                # tweets with message keys are longer tweets, the message value is the full messaje taken from twishort.
                if hasattr(tweetList[i], "message")  and tweetList[i].is_quote_status == False:
                    value = "message"
                else:
                    value = "full_text"
                if hasattr(tweetList[i], "retweeted_status") and tweetList[i].is_quote_status == False:
                    if not hasattr(tweetList[i], "message"):
                        text = text + "rt @%s: %s\n" % (tweetList[i].retweeted_status.user.screen_name, tweetList[i].retweeted_status.full_text)
                    else:
                        text = text + "rt @%s: %s\n" % (tweetList[i].retweeted_status.user.screen_name, getattr(tweetList[i], value))
                else:
                    text = text + " @%s: %s\n" % (tweetList[i].user.screen_name, getattr(tweetList[i], value))
                # tweets with extended_entities could include image descriptions.
                if hasattr(tweetList[i], "extended_entities") and "media" in tweetList[i].extended_entities:
                    for z in tweetList[i].extended_entities["media"]:
                        if "ext_alt_text" in z and z["ext_alt_text"] != None:
                            image_description.append(z["ext_alt_text"])
                if hasattr(tweetList[i], "retweeted_status") and hasattr(tweetList[i].retweeted_status, "extended_entities") and "media" in tweetList[i].retweeted_status["extended_entities"]:
                    for z in tweetList[i].retweeted_status.extended_entities["media"]:
                        if "ext_alt_text" in z and z["ext_alt_text"] != None:
                            image_description.append(z["ext_alt_text"])
            # set rt and likes counters.
            rt_count = str(tweet.retweet_count)
            favs_count = str(tweet.favorite_count)
            # Gets the client from where this tweet was made.
            source = tweet.source
            original_date = arrow.get(tweet.created_at, locale="en")
            date = original_date.shift(seconds=utc_offset).format(_(u"MMM D, YYYY. H:m"), locale=languageHandler.getLanguage())
            if text == "":
                if hasattr(tweet, "message"):
                    value = "message"
                else:
                    value = "full_text"
                if hasattr(tweet, "retweeted_status"):
                    if not hasattr(tweet, "message"):
                        text = "rt @%s: %s" % (tweet.retweeted_status.user.screen_name, tweet.retweeted_status.full_text)
                    else:
                        text = "rt @%s: %s" % (tweet.retweeted_status.user.screen_name, getattr(tweet, value))
                else:
                    text = getattr(tweet, value)
            text = self.clear_text(text)
            if hasattr(tweet, "extended_entities") and "media" in tweet.extended_entities:
                for z in tweet.extended_entities["media"]:
                    if "ext_alt_text" in z and z["ext_alt_text"] != None:
                        image_description.append(z["ext_alt_text"])
            if hasattr(tweet, "retweeted_status") and hasattr(tweet.retweeted_status, "extended_entities") and "media" in tweet.retweeted_status.extended_entities:
                for z in tweet.retweeted_status.extended_entities["media"]:
                    if "ext_alt_text" in z and z["ext_alt_text"] != None:
                        image_description.append(z["ext_alt_text"])
            self.message = twitterDialogs.viewTweet(text, rt_count, favs_count, source, date)
            results = parse_tweet(text)
            self.message.set_title(results.weightedLength)
            [self.message.set_image_description(i) for i in image_description]
        else:
            self.title = _(u"View item")
            text = tweet
            self.message = twitterDialogs.viewNonTweet(text, date)
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

    def clear_text(self, text):
        text = utils.StripChars(text)
        urls = utils.find_urls_in_text(text)
        for i in urls:
            if "https://twitter.com/" in i:
                text = text.replace(i, "\n")
        return text

    def share(self, *args, **kwargs):
        if hasattr(self, "item_url"):
            output.copy(self.item_url)
            output.speak(_("Link copied to clipboard."))