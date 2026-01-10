# -*- coding: utf-8 -*-
import os
import re
import wx
import logging
import widgetUtils
import config
import output
import languageHandler
from twitter_text import parse_tweet, config
from mastodon import MastodonError
from controller import messages
from sessions.mastodon import templates
from wxUI.dialogs.mastodon import postDialogs
from extra.autocompletionUsers import completion
from . import userList

log = logging.getLogger("controller.mastodon.messages")

def character_count(post_text, post_cw, character_limit=500):
    # We will use text for counting character limit only.
    full_text = post_text+post_cw
    # find remote users as Mastodon doesn't count the domain in char limit.
    users = re.findall("@[\w\.-]+@[\w\.-]+", full_text)
    for user in users:
        domain = user.split("@")[-1]
        full_text = full_text.replace("@"+domain, "")
    options = config.config.get("defaults")
    options.update(max_weighted_tweet_length=character_limit, default_weight=100)
    parsed = parse_tweet(full_text, options=options)
    return parsed.weightedLength

class post(messages.basicMessage):
    def __init__(self, session, title, caption, text="", *args, **kwargs):
        # take max character limit from session as this might be different for some instances.
        self.max = session.char_limit
        self.title = title
        self.session = session
        langs = self.session.supported_languages
        display_langs = [l.name for l in langs]
        self.message = postDialogs.Post(caption=caption, text=text, languages=display_langs, *args, **kwargs)
        self.message.SetTitle(title)
        self.message.text.SetInsertionPoint(len(self.message.text.GetValue()))
        self.set_language(self.session.default_language)
        widgetUtils.connect_event(self.message.spellcheck, widgetUtils.BUTTON_PRESSED, self.spellcheck)
        widgetUtils.connect_event(self.message.text, widgetUtils.ENTERED_TEXT, self.text_processor)
        widgetUtils.connect_event(self.message.spoiler, widgetUtils.ENTERED_TEXT, self.text_processor)
        widgetUtils.connect_event(self.message.translate, widgetUtils.BUTTON_PRESSED, self.translate)
        widgetUtils.connect_event(self.message.add, widgetUtils.BUTTON_PRESSED, self.on_attach)
        widgetUtils.connect_event(self.message.remove_attachment, widgetUtils.BUTTON_PRESSED, self.remove_attachment)
        widgetUtils.connect_event(self.message.autocomplete_users, widgetUtils.BUTTON_PRESSED, self.autocomplete_users)
        widgetUtils.connect_event(self.message.add_post, widgetUtils.BUTTON_PRESSED, self.add_post)
        widgetUtils.connect_event(self.message.remove_post, widgetUtils.BUTTON_PRESSED, self.remove_post)
        self.attachments = []
        self.thread = []
        self.text_processor()

    def autocomplete_users(self, *args, **kwargs):
        c = completion.autocompletionUsers(self.message, self.session.session_id)
        c.show_menu()

    def add_post(self, event, update_gui=True, *args, **kwargs):
        text = self.message.text.GetValue()
        attachments = self.attachments[::]
        postdata = dict(text=text, attachments=attachments, sensitive=self.message.sensitive.GetValue(), spoiler_text=None)
        if postdata.get("sensitive") == True:
            postdata.update(spoiler_text=self.message.spoiler.GetValue())
        self.thread.append(postdata)
        self.attachments = []
        if update_gui:
            self.message.reset_controls()
            self.message.add_item(item=[text, len(attachments)], list_type="post")
            self.message.text.SetFocus()
            self.text_processor()

    def get_post_data(self):
        self.add_post(event=None, update_gui=False)
        return self.thread

    def set_language(self, language=None):
        """ Attempt to set the default language for a post. """
        # language can be provided in a post (replying or recovering from errors).
        # Also it can be provided in user preferences (retrieved in the session).
        # If no language is provided, let's fallback to TWBlue's user language.
        if language != None: 
            language_code = language
        else:
            # Let's cut langcode_VARIANT to ISO-639 two letter code only.
            language_code = languageHandler.curLang[:2]
        for lang in self.session.supported_languages:
            if lang.code == language_code:
                self.message.language.SetStringSelection(lang.name)

    def set_post_data(self, visibility, data, language):
        if len(data) == 0:
            return
        if len(data) > 1:
            self.thread = data[:-1]
            for p in self.thread:
                self.message.add_item(item=[p.get("text") or "", len(p.get("attachments") or [])], list_type="post")
        post = data[-1]
        self.attachments = post.get("attachments") or []
        self.message.text.SetValue(post.get("text") or "")
        self.message.sensitive.SetValue(post.get("sensitive") or False)
        self.message.spoiler.SetValue(post.get("spoiler_text") or "")
        visibility_settings = dict(public=0, unlisted=1, private=2, direct=3)
        self.message.visibility.SetSelection(visibility_settings.get(visibility))
        self.message.on_sensitivity_changed()
        for attachment in self.attachments:
            self.message.add_item(item=[attachment["file"], attachment["type"], attachment["description"]])
        self.set_language(language)
        self.text_processor()

    def text_processor(self, *args, **kwargs):
        text = self.message.text.GetValue()
        cw = self.message.spoiler.GetValue()
        results = character_count(text, cw, character_limit=self.max)
        self.message.SetTitle(_("%s - %s of %d characters") % (self.title, results, self.max))
        if results > self.max:
            self.session.sound.play("max_length.ogg")
        if len(self.thread) > 0:
            if hasattr(self.message, "posts"):
                self.message.posts.Enable(True)
                self.message.remove_post.Enable(True)
            else:
                self.message.posts.Enable(False)
                self.message.remove_post.Enable(False)
        if len(self.attachments) > 0:
            self.message.attachments.Enable(True)
            self.message.remove_attachment.Enable(True)
        else:
            self.message.attachments.Enable(False)
            self.message.remove_attachment.Enable(False)
        if len(self.message.text.GetValue()) > 0 or len(self.attachments) > 0:
            self.message.add_post.Enable(True)
        else:
            self.message.add_post.Enable(False)

    def remove_post(self, *args, **kwargs):
        post = self.message.posts.GetFocusedItem()
        if post > -1 and len(self.thread) > post:
            self.thread.pop(post)
            self.message.remove_item(list_type="post")
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
        video, description = self.message.get_video()
        if video != None:
            videoInfo = {"type": "video", "file": video, "description": description}
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
        audio, description = self.message.get_audio()
        if audio != None:
            audioInfo = {"type": "audio", "file": audio, "description": description}
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
        dlg = postDialogs.poll()
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
        self.add_post(event=None, update_gui=False)
        return self.thread

    def get_visibility(self):
        visibility_settings = ["public", "unlisted", "private", "direct"]
        return visibility_settings[self.message.visibility.GetSelection()]

    def get_language(self):
        langs = self.session.supported_languages
        lang = self.message.language.GetSelection()
        if lang >= 0:
            return langs[lang].code
        return None

    def set_visibility(self, setting):
        visibility_settings = ["public", "unlisted", "private", "direct"]
        visibility_setting = visibility_settings.index(setting)
        self.message.visibility.SetSelection(setting)

class editPost(post):
    def __init__(self, session, item, title, caption, *args, **kwargs):
        """ Initialize edit dialog with existing post data.

        Note: Per Mastodon API, visibility and language cannot be changed when editing.
        These fields will be displayed but disabled in the UI.
        """
        # Extract text from post
        if item.reblog != None:
            item = item.reblog
        text = item.content
        # Remove HTML tags from content
        import re
        text = re.sub('<[^<]+?>', '', text)
        # Initialize parent class
        super(editPost, self).__init__(session, title, caption, text=text, *args, **kwargs)
        # Store the post ID for editing
        self.post_id = item.id
        # Set visibility (read-only, cannot be changed)
        visibility_settings = dict(public=0, unlisted=1, private=2, direct=3)
        self.message.visibility.SetSelection(visibility_settings.get(item.visibility, 0))
        self.message.visibility.Enable(False)  # Disable as it cannot be edited
        # Set language (read-only, cannot be changed)
        if item.language:
            self.set_language(item.language)
        self.message.language.Enable(False)  # Disable as it cannot be edited
        # Set sensitive content and spoiler
        if item.sensitive:
            self.message.sensitive.SetValue(True)
            if item.spoiler_text:
                self.message.spoiler.ChangeValue(item.spoiler_text)
            self.message.on_sensitivity_changed()
        # Load existing poll (if any)
        # Note: You cannot have both media and a poll, so check poll first
        if hasattr(item, 'poll') and item.poll is not None:
            log.debug("Loading existing poll for post {}".format(self.post_id))
            poll = item.poll
            # Extract poll options (just the text, not the votes)
            poll_options = [option.title for option in poll.options]
            # Calculate expires_in based on current time and expires_at
            # For editing, we need to provide a new expiration time
            # Since we can't get the original expires_in, use a default or let user configure
            # For now, use 1 day (86400 seconds) as default
            expires_in = 86400
            if hasattr(poll, 'expires_at') and poll.expires_at and not poll.expired:
                # Calculate remaining time if poll hasn't expired
                from dateutil import parser as date_parser
                import datetime
                try:
                    expires_at = poll.expires_at
                    if isinstance(expires_at, str):
                        expires_at = date_parser.parse(expires_at)
                    now = datetime.datetime.now(datetime.timezone.utc)
                    remaining = (expires_at - now).total_seconds()
                    if remaining > 0:
                        expires_in = int(remaining)
                except Exception as e:
                    log.warning("Could not calculate poll expiration: {}".format(e))

            poll_info = {
                "type": "poll",
                "file": "",
                "description": _("Poll with {} options").format(len(poll_options)),
                "options": poll_options,
                "expires_in": expires_in,
                "multiple": poll.multiple if hasattr(poll, 'multiple') else False,
                "hide_totals": poll.voters_count == 0 if hasattr(poll, 'voters_count') else False
            }
            self.attachments.append(poll_info)
            self.message.add_item(item=[poll_info["file"], poll_info["type"], poll_info["description"]])
            log.debug("Loaded poll with {} options. WARNING: Editing will reset all votes!".format(len(poll_options)))
        # Load existing media attachments (only if no poll)
        elif hasattr(item, 'media_attachments'):
            log.debug("Loading existing media attachments for post {}".format(self.post_id))
            log.debug("Item has media_attachments attribute, count: {}".format(len(item.media_attachments)))
            if len(item.media_attachments) > 0:
                for media in item.media_attachments:
                    log.debug("Processing media: id={}, type={}, url={}".format(media.id, media.type, media.url))
                    media_info = {
                        "id": media.id,  # Keep the existing media ID
                        "type": media.type,
                        "file": media.url,  # URL of existing media
                        "description": media.description or ""
                    }
                    # Include focus point if available
                    if hasattr(media, 'meta') and media.meta and 'focus' in media.meta:
                        focus = media.meta['focus']
                        media_info["focus"] = (focus.get('x'), focus.get('y'))
                        log.debug("Added focus point: {}".format(media_info["focus"]))
                    self.attachments.append(media_info)
                    # Display in the attachment list
                    display_name = media.url.split('/')[-1]
                    log.debug("Adding item to UI: name={}, type={}, desc={}".format(display_name, media.type, media.description or ""))
                    self.message.add_item(item=[display_name, media.type, media.description or ""])
                log.debug("Total attachments loaded: {}".format(len(self.attachments)))
            else:
                log.debug("media_attachments list is empty")
        else:
            log.debug("Item has no poll or media attachments")
        # Update text processor to reflect the loaded content
        self.text_processor()

class viewPost(post):
    def __init__(self, session, post, offset_hours=0, date="", item_url=""):
        self.session = session
        if post.reblog != None:
            post = post.reblog
        self.post_id = post.id
        author = post.account.display_name if post.account.display_name != "" else post.account.username
        title = _(u"Post from {}").format(author)
        image_description = templates.process_image_descriptions(post.media_attachments)
        text = templates.process_text(post, safe=False)
        date = templates.process_date(post.created_at, relative_times=False, offset_hours=offset_hours)
        privacy_settings = dict(public=_("Public"), unlisted=_("Not listed"), private=_("followers only"), direct=_("Direct"))
        privacy = privacy_settings.get(post.visibility)
        boost_count = str(post.reblogs_count)
        favs_count = str(post.favourites_count)
        # Gets the client from where this post was made.
        source_obj = post.get("application")
        if source_obj == None:
            source = _("Remote instance")
        else:
            source = source_obj.get("name")
        self.message = postDialogs.viewPost(text=text, boosts_count=boost_count, favs_count=favs_count, source=source, date=date, privacy=privacy)
        participants = [post.account.id] + [account.id for account in post.mentions]
        if self.session.db["user_id"] in participants:
            self.message.mute.Enable(True)
            if post.muted:
                self.message.mute.SetLabel(_("Unmute conversation"))
            widgetUtils.connect_event(self.message.mute, widgetUtils.BUTTON_PRESSED, self.mute_unmute)
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
        widgetUtils.connect_event(self.message.boosts_button, widgetUtils.BUTTON_PRESSED, self.on_boosts)
        widgetUtils.connect_event(self.message.favorites_button, widgetUtils.BUTTON_PRESSED, self.on_favorites)
        self.message.ShowModal()

    # We won't need text_processor in this dialog, so let's avoid it.
    def text_processor(self):
        pass

    def mute_unmute(self, *args, **kwargs):
        post = self.session.api.status(self.post_id)
        if post.muted == True:
            action = "status_unmute"
            new_label = _("Mute conversation")
            msg = _("Conversation unmuted.")
        else:
            action = "status_mute"
            new_label = _("Unmute conversation")
            msg = _("Conversation muted.")
        try:
            getattr(self.session.api, action)(self.post_id)
            self.message.mute.SetLabel(new_label)
            output.speak(msg)
        except MastodonError:
            return


    def on_boosts(self, *args, **kwargs):
        users = self.session.api.status_reblogged_by(self.post_id)
        title = _("people who boosted this post")
        user_list = userList.MastodonUserList(session=self.session, users=users, title=title)

    def on_favorites(self, *args, **kwargs):
        users = self.session.api.status_favourited_by(self.post_id)
        title = _("people who favorited this post")
        user_list = userList.MastodonUserList(session=self.session, users=users, title=title)

    def share(self, *args, **kwargs):
        if hasattr(self, "item_url"):
            output.copy(self.item_url)
            output.speak(_("Link copied to clipboard."))

class text(messages.basicMessage):
    def __init__(self, title, text="", *args, **kwargs):
        self.title = title
        self.message = postDialogs.viewText(title=title, text=text, *args, **kwargs)
        self.message.text.SetInsertionPoint(len(self.message.text.GetValue()))
        widgetUtils.connect_event(self.message.spellcheck, widgetUtils.BUTTON_PRESSED, self.spellcheck)
        widgetUtils.connect_event(self.message.translateButton, widgetUtils.BUTTON_PRESSED, self.translate)