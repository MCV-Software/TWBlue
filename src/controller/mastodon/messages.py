# -*- coding: utf-8 -*-
import os
import wx
import widgetUtils
import config
import output
from controller.twitter import messages
from sessions.mastodon import templates
from wxUI.dialogs.mastodon import tootDialogs

class toot(messages.basicTweet):
    def __init__(self, session, title, caption, text="", max=500, *args, **kwargs):
        self.max = max
        self.title = title
        self.session = session
        self.message = tootDialogs.Toot(caption=caption, text=text, *args, **kwargs)
        self.message.SetTitle(title)
        self.message.text.SetInsertionPoint(len(self.message.text.GetValue()))
        widgetUtils.connect_event(self.message.spellcheck, widgetUtils.BUTTON_PRESSED, self.spellcheck)
        widgetUtils.connect_event(self.message.text, widgetUtils.ENTERED_TEXT, self.text_processor)
        widgetUtils.connect_event(self.message.translate, widgetUtils.BUTTON_PRESSED, self.translate)
        widgetUtils.connect_event(self.message.add, widgetUtils.BUTTON_PRESSED, self.on_attach)
        widgetUtils.connect_event(self.message.remove_attachment, widgetUtils.BUTTON_PRESSED, self.remove_attachment)
        # ToDo: Add autocomplete feature to mastodon and uncomment this.
        # widgetUtils.connect_event(self.message.autocomplete_users, widgetUtils.BUTTON_PRESSED, self.autocomplete_users)
        widgetUtils.connect_event(self.message.add_toot, widgetUtils.BUTTON_PRESSED, self.add_toot)
        widgetUtils.connect_event(self.message.remove_toot, widgetUtils.BUTTON_PRESSED, self.remove_toot)
        self.attachments = []
        self.thread = []
        self.text_processor()

    def add_toot(self, event, update_gui=True, *args, **kwargs):
        text = self.message.text.GetValue()
        attachments = self.attachments[::]
        tootdata = dict(text=text, attachments=attachments, sensitive=self.message.sensitive.GetValue(), spoiler_text=None)
        if tootdata.get("sensitive") == True:
            tootdata.update(spoiler_text=self.message.spoiler.GetValue())
        self.thread.append(tootdata)
        self.attachments = []
        if update_gui:
            self.message.reset_controls()
            self.message.add_item(item=[text, len(attachments)], list_type="toot")
            self.message.text.SetFocus()
            self.text_processor()

    def get_toot_data(self):
        self.add_toot(event=None, update_gui=False)
        return self.thread

    def text_processor(self, *args, **kwargs):
        super(toot, self).text_processor(*args, **kwargs)
        if len(self.thread) > 0:
            if hasattr(self.message, "toots"):
                self.message.toots.Enable(True)
                self.message.remove_toot.Enable(True)
            else:
                self.message.toots.Enable(False)
                self.message.remove_toot.Enable(False)
        if len(self.attachments) > 0:
            self.message.attachments.Enable(True)
            self.message.remove_attachment.Enable(True)
        else:
            self.message.attachments.Enable(False)
            self.message.remove_attachment.Enable(False)
        if len(self.message.text.GetValue()) > 0 or len(self.attachments) > 0:
            self.message.add_toot.Enable(True)
        else:
            self.message.add_toot.Enable(False)

    def remove_toot(self, *args, **kwargs):
        toot = self.message.toots.GetFocusedItem()
        if toot > -1 and len(self.thread) > toot:
            self.thread.pop(toot)
            self.message.remove_item(list_type="toot")
            self.text_processor()
            self.message.text.SetFocus()

    def can_attach(self):
        if len(self.attachments) == 0:
            return True
        elif len(self.attachments) == 1 and (self.attachments[0]["type"] == "poll" or self.attachments[0]["type"] == "video" or self.attachments[0]["type"] == "audio"):
            return False
        elif len(self.attachments) < 4:
            return True
        return False

    def on_attach(self, *args, **kwargs):
        can_attach = self.can_attach()
        menu = self.message.attach_menu(can_attach)
        self.message.Bind(wx.EVT_MENU, self.on_attach_image, self.message.add_image)
        self.message.Bind(wx.EVT_MENU, self.on_attach_video, self.message.add_video)
        self.message.Bind(wx.EVT_MENU, self.on_attach_audio, self.message.add_audio)
        self.message.Bind(wx.EVT_MENU, self.on_attach_poll, self.message.add_poll)
        self.message.PopupMenu(menu, self.message.add.GetPosition())

    def on_attach_image(self, *args, **kwargs):
        can_attach = self.can_attach()
        big_media_present = False
        for a in self.attachments:
            if a["type"] == "video" or a["type"] == "audio" or a["type"] == "poll":
                big_media_present = True
                break
        if can_attach == False or big_media_present == True:
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
        if len(self.attachments) >= 4:
            return self.message.unable_to_attach_file()
        can_attach = self.can_attach()
        big_media_present = False
        for a in self.attachments:
            if a["type"] == "video" or a["type"] == "audio" or a["type"] == "poll":
                big_media_present = True
                break
        if can_attach == False or big_media_present == True:
            return self.message.unable_to_attach_file()
        video = self.message.get_video()
        if video != None:
            videoInfo = {"type": "video", "file": video, "description": ""}
            self.attachments.append(videoInfo)
            self.message.add_item(item=[os.path.basename(videoInfo["file"]), videoInfo["type"], videoInfo["description"]])
            self.text_processor()

    def on_attach_audio(self, *args, **kwargs):
        if len(self.attachments) >= 4:
            return self.message.unable_to_attach_file()
        can_attach = self.can_attach()
        big_media_present = False
        for a in self.attachments:
            if a["type"] == "video" or a["type"] == "audio" or a["type"] == "poll":
                big_media_present = True
                break
        if can_attach == False or big_media_present == True:
            return self.message.unable_to_attach_file()
        audio = self.message.get_audio()
        if audio != None:
            audioInfo = {"type": "audio", "file": audio, "description": ""}
            self.attachments.append(audioInfo)
            self.message.add_item(item=[os.path.basename(audioInfo["file"]), audioInfo["type"], audioInfo["description"]])
            self.text_processor()

    def on_attach_poll(self, *args, **kwargs):
        if len(self.attachments) > 0:
            return self.message.unable_to_attach_poll()
        can_attach = self.can_attach()
        big_media_present = False
        for a in self.attachments:
            if a["type"] == "video" or a["type"] == "audio" or a["type"] == "poll":
                big_media_present = True
                break
        if can_attach == False or big_media_present == True:
            return self.message.unable_to_attach_file()
        dlg = tootDialogs.poll()
        if dlg.ShowModal() == wx.ID_OK:
            day = 86400
            periods = [300, 1800, 3600, 21600, day, day*2, day*3, day*4, day*5, day*6, day*7]
            period = periods[dlg.period.GetSelection()]
            poll_options = dlg.get_options()
            multiple = dlg.multiple.GetValue()
            hide_totals = dlg.hide_votes.GetValue()
            data = dict(type="poll", file="", description=_("Poll with {} options").format(len(poll_options)), options=poll_options, expires_in=period, multiple=multiple, hide_totals=hide_totals)
            self.attachments.append(data)
            self.message.add_item(item=[data["file"], data["type"], data["description"]])
            self.text_processor()
        dlg.Destroy()

    def get_data(self):
        self.add_toot(event=None, update_gui=False)
        return self.thread

    def get_visibility(self):
        visibility_settings = ["public", "unlisted", "private", "direct"]
        return visibility_settings[self.message.visibility.GetSelection()]

class viewToot(toot):
    def __init__(self, toot, offset_hours=0, date="", item_url=""):
        if toot.reblog != None:
            toot = toot.reblog
        author = toot.account.display_name if toot.account.display_name != "" else toot.account.username
        title = _(u"Toot from {}").format(author)
        image_description = templates.process_image_descriptions(toot.media_attachments)
        text = templates.process_text(toot, safe=False)
        date = templates.process_date(toot.created_at, relative_times=False, offset_hours=offset_hours)
        privacy_settings = dict(public=_("Public"), unlisted=_("Not listed"), private=_("followers only"), direct=_("Direct"))
        privacy = privacy_settings.get(toot.visibility)
        boost_count = str(toot.reblogs_count)
        favs_count = str(toot.favourites_count)
        # Gets the client from where this toot was made.
        source_obj = toot.get("application")
        if source_obj == None:
            source = _("Remote instance")
        else:
            source = source_obj.get("name")
        self.message = tootDialogs.viewToot(text=text, boosts_count=boost_count, favs_count=favs_count, source=source, date=date, privacy=privacy)
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