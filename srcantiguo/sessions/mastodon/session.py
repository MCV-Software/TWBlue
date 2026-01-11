# -*- coding: utf-8 -*-
import os
import paths
import time
import logging
import webbrowser
import wx
import mastodon
import demoji
import config
import config_utils
import output
import application
from mastodon import MastodonError, MastodonAPIError, MastodonNotFoundError, MastodonUnauthorizedError, MastodonVersionError
from pubsub import pub
from mysc.thread_utils import call_threaded
from sessions import base
from sessions.mastodon import utils, streaming

log = logging.getLogger("sessions.mastodonSession")

MASTODON_VERSION = "4.3.2"

class Session(base.baseSession):
    version_check_mode = "created"
    name = "Mastodon"

    def __init__(self, *args, **kwargs):
        super(Session, self).__init__(*args, **kwargs)
        self.config_spec = "mastodon.defaults"
        self.supported_languages = []
        self.default_language = None
        self.type = "mastodon"
        self.db["pagination_info"] = dict()
        self.char_limit = 500
        self.post_visibility = "public"
        self.expand_spoilers = False
        self.software = "mastodon"
        pub.subscribe(self.on_status, "mastodon.status_received")
        pub.subscribe(self.on_status_updated, "mastodon.status_updated")
        pub.subscribe(self.on_notification, "mastodon.notification_received")

    def login(self, verify_credentials=True):
        if self.settings["mastodon"]["access_token"] != None and self.settings["mastodon"]["instance"] != None:
            try:
                log.debug("Logging in to Mastodon instance {}...".format(self.settings["mastodon"]["instance"]))
                self.api = mastodon.Mastodon(access_token=self.settings["mastodon"]["access_token"], api_base_url=self.settings["mastodon"]["instance"], mastodon_version=MASTODON_VERSION, user_agent="TWBlue/{}".format(application.version), version_check_mode=self.version_check_mode)
                if verify_credentials == True:
                    credentials = self.api.account_verify_credentials()
                    self.db["user_name"] = credentials["username"]
                    self.db["user_id"] = credentials["id"]
                    if hasattr(credentials, "source") and hasattr(credentials.source, "language"):
                        log.info(f"Setting default language on account {credentials.username} to {credentials.source.language}")
                        self.default_language = credentials.source.language
                    self.settings["mastodon"]["user_name"] = credentials["username"]
                self.logged = True
                log.debug("Logged.")
                self.counter = 0
            except MastodonError:
                log.exception(f"The login attempt failed on instance {self.settings['mastodon']['instance']}.")
                self.logged = False
        else:
            self.logged = False
            raise Exceptions.RequireCredentialsSessionError

    def authorise(self):
        if self.logged == True:
            raise Exceptions.AlreadyAuthorisedError("The authorisation process is not needed at this time.")
        authorisation_dialog = wx.TextEntryDialog(None, _("Please enter your instance URL."), _("Mastodon instance"))
        answer = authorisation_dialog.ShowModal()
        instance = authorisation_dialog.GetValue()
        authorisation_dialog.Destroy()
        if answer != wx.ID_OK:
            return
        try:
            client_id, client_secret = mastodon.Mastodon.create_app("TWBlue", api_base_url=authorisation_dialog.GetValue(), website="https://twblue.es")
            temporary_api = mastodon.Mastodon(client_id=client_id, client_secret=client_secret, api_base_url=instance, mastodon_version=MASTODON_VERSION, user_agent="TWBlue/{}".format(application.version), version_check_mode="none") # disable version check so we can handle more platforms than Mastodon.
            auth_url = temporary_api.auth_request_url()
        except MastodonError:
            dlg = wx.MessageDialog(None, _("We could not connect to your mastodon instance. Please verify that the domain exists and the instance is accessible via a web browser."), _("Instance error"), wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        webbrowser.open_new_tab(auth_url)
        verification_dialog = wx.TextEntryDialog(None, _("Enter the verification code"), _("PIN code authorization"))
        answer = verification_dialog.ShowModal()
        code = verification_dialog.GetValue()
        verification_dialog.Destroy()
        if answer != wx.ID_OK:
            return
        try:
            access_token = temporary_api.log_in(code=verification_dialog.GetValue())
        except MastodonError:
            dlg = wx.MessageDialog(None, _("We could not authorice your mastodon account to be used in TWBlue. This might be caused due to an incorrect verification code. Please try to add the session again."), _("Authorization error"), wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        self.create_session_folder()
        self.get_configuration()
        # handle when the instance is GoTosocial.
        # this might be extended for other activity pub software later on.
        nodeinfo = temporary_api.instance_nodeinfo()
        if nodeinfo.software.get("name") == "gotosocial":
            self.settings["mastodon"]["type"] = nodeinfo.software.get("name")
            # GoToSocial doesn't support certain buffers so we redefine all of them here.
            self.settings["general"]["buffer_order"] = ['home', 'local', 'mentions', 'sent', 'favorites', 'bookmarks', 'followers', 'following', 'blocked', 'notifications']
        self.settings["mastodon"]["access_token"] = access_token
        self.settings["mastodon"]["instance"] = instance
        self.settings.write()
        return True

    def get_user_info(self):
        """ Retrieves some information required by TWBlue for setup."""
        # retrieve the current user's UTC offset so we can calculate dates properly.
        offset = time.timezone if (time.localtime().tm_isdst == 0) else time.altzone
        offset = offset / 60 / 60 * -1
        self.db["utc_offset"] = offset
        instance = self.api.instance()
        if len(self.supported_languages) == 0:
            try:
                self.supported_languages = self.api.instance_languages()
            except (Exception, MastodonVersionError):
                pass
        self.get_lists()
        self.get_muted_users()
        # determine instance custom characters limit.
        if hasattr(instance, "configuration") and hasattr(instance.configuration, "statuses") and hasattr(instance.configuration.statuses, "max_characters"):
            self.char_limit = instance.configuration.statuses.max_characters
        # User preferences for some things.
        preferences = self.api.preferences()
        self.post_visibility = preferences.get("posting:default:visibility")
        self.expand_spoilers = preferences.get("reading:expand:spoilers")
        self.settings.write()

    def get_lists(self):
        """ Gets the lists that the user is subscribed to and stores them in the database. Returns None."""
        if self.software == "gotosocial":
            self.db["lists"] = []
            return
        self.db["lists"] = self.api.lists()

    def get_muted_users(self):
        ### ToDo: Use a function to retrieve all muted users.
        if self.software == "gotosocial":
            self.db["muted_users"] = []
            return
        try:
            self.db["muted_users"] = self.api.mutes()
        except MastodonNotFoundError:
            self.db["muted_users"] = []

    def order_buffer(self, name, data, ignore_older=False):
        num = 0
        last_id = None
        if self.db.get(name) == None:
            self.db[name] = []
        objects = self.db[name]
        if ignore_older and len(self.db[name]) > 0:
            if self.settings["general"]["reverse_timelines"] == False:
                last_id = self.db[name][0].id
            else:
                last_id = self.db[name][-1].id
        for i in data:
            # handle empty notifications.
            post_types = ["status", "mention", "reblog", "favourite", "update", "poll"]
            if hasattr(i, "type") and i.type in post_types and i.status == None:
                continue
            if ignore_older and last_id != None:
                if i.id < last_id:
                    log.error("Ignoring an older tweet... Last id: {0}, tweet id: {1}".format(last_id, i.id))
                    continue
            if utils.find_item(i, self.db[name]) == None:
                filter_status = utils.evaluate_filters(post=i, current_context=utils.get_current_context(name))
                if filter_status == "hide":
                    continue
                if self.settings["general"]["reverse_timelines"] == False: objects.append(i)
                else: objects.insert(0, i)
                num = num+1
        self.db[name] = objects
        return num

    def update_item(self, name, item):
        if name not in self.db:
            return False
        items = self.db[name]
        if type(items) != list:
            return False
        # determine item position in buffer.
        item_position = next((x for x in range(len(items)) if items[x].id == item.id), None)
        if item_position != None:
            self.db[name][item_position] = item
            return item_position
        return False

    def api_call(self, call_name, action="", _sound=None, report_success=False, report_failure=True, preexec_message="", *args, **kwargs):
        finished = False
        tries = 0
        if preexec_message:
            output.speak(preexec_message, True)
        while finished==False and tries < 5:
            try:
                val = getattr(self.api, call_name)(*args, **kwargs)
                finished = True
            except Exception as e:
                output.speak(str(e))
                if isinstance(e, MastodonAPIError):
                    log.exception("API Error returned when making a Call on {}. Call name={}, args={}, kwargs={}".format(self.get_name(), call_name, args, kwargs))
                    raise e
                val = None
                tries = tries+1
                time.sleep(5)
                if tries == 4 and finished == False:
                    raise e
        if report_success:
            output.speak(_("%s succeeded.") % action)
        if _sound != None:
            self.sound.play(_sound)
        return val

    def send_post(self, reply_to=None, visibility=None, language=None, posts=[]):
        """ Convenience function to send a thread. """
        in_reply_to_id = reply_to
        for obj in posts:
            text = obj.get("text")
            scheduled_at = obj.get("scheduled_at")
            if len(obj["attachments"]) == 0:
                try:
                    item = self.api_call(call_name="status_post", status=text, _sound="tweet_send.ogg",  in_reply_to_id=in_reply_to_id, visibility=visibility, sensitive=obj["sensitive"], spoiler_text=obj["spoiler_text"], language=language, scheduled_at=scheduled_at)
                # If it fails, let's basically send an event with all passed info so we will catch it later.
                except Exception as e:
                    pub.sendMessage("mastodon.error_post", name=self.get_name(), reply_to=reply_to, visibility=visibility, posts=posts, lang=language)
                    return
                if item != None:
                    in_reply_to_id = item["id"]
            else:
                media_ids = []
                try:
                    poll = None
                    if len(obj["attachments"]) == 1 and obj["attachments"][0]["type"] == "poll":
                        poll = self.api.make_poll(options=obj["attachments"][0]["options"], expires_in=obj["attachments"][0]["expires_in"], multiple=obj["attachments"][0]["multiple"], hide_totals=obj["attachments"][0]["hide_totals"])
                    else:
                        for i in obj["attachments"]:
                            media = self.api_call("media_post", media_file=i["file"], description=i["description"], synchronous=True)
                            media_ids.append(media.id)
                    item = self.api_call(call_name="status_post", status=text, _sound="tweet_send.ogg", in_reply_to_id=in_reply_to_id, media_ids=media_ids, visibility=visibility, poll=poll, sensitive=obj["sensitive"], spoiler_text=obj["spoiler_text"], language=language, scheduled_at=scheduled_at)
                    if item != None:
                        in_reply_to_id = item["id"]
                except Exception as e:
                    pub.sendMessage("mastodon.error_post", name=self.get_name(), reply_to=reply_to, visibility=visibility, posts=posts, lang=language)
                    return

    def edit_post(self, post_id, posts=[]):
        """ Convenience function to edit a post. Only the first item in posts list is used as threads cannot be edited.

        Note: According to Mastodon API, not all fields can be edited. Visibility, language, and reply context cannot be changed.

        Args:
            post_id: ID of the status to edit
            posts: List with post data. Only first item is used.

        Returns:
            Updated status object or None on failure
        """
        if len(posts) == 0:
            log.warning("edit_post called with empty posts list")
            return None

        obj = posts[0]
        text = obj.get("text")

        if not text:
            log.warning("edit_post called without text content")
            return None

        media_ids = []
        media_attributes = []

        try:
            poll = None
            # Handle poll attachments
            if len(obj["attachments"]) == 1 and obj["attachments"][0]["type"] == "poll":
                poll = self.api.make_poll(
                    options=obj["attachments"][0]["options"],
                    expires_in=obj["attachments"][0]["expires_in"],
                    multiple=obj["attachments"][0]["multiple"],
                    hide_totals=obj["attachments"][0]["hide_totals"]
                )
                log.debug("Editing post with poll (this will reset votes)")
            # Handle media attachments
            elif len(obj["attachments"]) > 0:
                for i in obj["attachments"]:
                    # If attachment has an 'id', it's an existing media that we keep
                    if "id" in i:
                        media_ids.append(i["id"])
                        # If existing media has metadata to update, use generate_media_edit_attributes
                        if "description" in i or "focus" in i:
                            media_attr = self.api.generate_media_edit_attributes(
                                id=i["id"],
                                description=i.get("description"),
                                focus=i.get("focus")
                            )
                            media_attributes.append(media_attr)
                    # Otherwise it's a new file to upload
                    elif "file" in i:
                        description = i.get("description", "")
                        focus = i.get("focus", None)
                        media = self.api_call(
                            "media_post",
                            media_file=i["file"],
                            description=description,
                            focus=focus,
                            synchronous=True
                        )
                        media_ids.append(media.id)
                        log.debug("Uploaded new media with id: {}".format(media.id))

            # Prepare parameters for status_update
            update_params = {
                "id": post_id,
                "status": text,
                "_sound": "tweet_send.ogg",
                "sensitive": obj.get("sensitive", False),
                "spoiler_text": obj.get("spoiler_text", None),
            }

            # Add optional parameters only if provided
            if media_ids:
                update_params["media_ids"] = media_ids
            if media_attributes:
                update_params["media_attributes"] = media_attributes
            if poll:
                update_params["poll"] = poll

            # Call status_update API
            log.debug("Editing post {} with params: {}".format(post_id, {k: v for k, v in update_params.items() if k not in ["_sound"]}))
            item = self.api_call(call_name="status_update", **update_params)

            if item:
                log.info("Successfully edited post {}".format(post_id))
            return item

        except MastodonAPIError as e:
            log.exception("Mastodon API error updating post {}: {}".format(post_id, str(e)))
            output.speak(_("Error editing post: {}").format(str(e)))
            pub.sendMessage("mastodon.error_edit", name=self.get_name(), post_id=post_id, error=str(e))
            return None
        except Exception as e:
            log.exception("Unexpected error updating post {}: {}".format(post_id, str(e)))
            output.speak(_("Error editing post: {}").format(str(e)))
            return None

    def get_name(self):
        instance = self.settings["mastodon"]["instance"]
        instance = instance.replace("https://", "")
        user = self.settings["mastodon"]["user_name"]
        return "{}@{} ({})".format(user, instance, self.name)

    def start_streaming(self):
        if self.settings["general"]["disable_streaming"]:
            log.info("Streaming is disabled for session {}. Skipping...".format(self.get_name()))
            return
        if self.software == "gotosocial":
            return
        listener = streaming.StreamListener(session_name=self.get_name(), user_id=self.db["user_id"])
        try:
            stream_healthy = self.api.stream_healthy()
            if stream_healthy == True:
                self.user_stream = self.api.stream_user(listener, run_async=True, reconnect_async=True, reconnect_async_wait_sec=30)
                self.direct_stream = self.api.stream_direct(listener, run_async=True, reconnect_async=True, reconnect_async_wait_sec=30)
                log.debug("Started streams for session {}.".format(self.get_name()))
        except Exception as e:
            log.exception("Detected streaming unhealthy in {} session.".format(self.get_name()))

    def stop_streaming(self):
        if config.app["app-settings"]["no_streaming"]:
            return

    def check_streams(self):
        pass

    def check_buffers(self, status):
        buffers = []
        buffers.append("home_timeline")
        if status.account.id == self.db["user_id"]:
            buffers.append("sent")
        return buffers

    def on_status(self, status, session_name):
        # Discard processing the status if the streaming sends a tweet for another account.
        if self.get_name() != session_name:
            return
        buffers = self.check_buffers(status)
        for b in buffers[::]:
            num = self.order_buffer(b, [status])
            if num == 0:
                buffers.remove(b)
        pub.sendMessage("mastodon.new_item", session_name=self.get_name(), item=status, _buffers=buffers)

    def on_status_updated(self, status, session_name):
        # Discard processing the status if the streaming sends a tweet for another account.
        if self.get_name() != session_name:
            return
        buffers = {}
        for b in list(self.db.keys()):
            updated = self.update_item(b, status)
            if updated != False:
                buffers[b] = updated
        pub.sendMessage("mastodon.updated_item", session_name=self.get_name(), item=status, _buffers=buffers)

    def on_notification(self, notification, session_name):
        # Discard processing the notification if the streaming sends a tweet for another account.
        if self.get_name() != session_name:
            return
        buffers = []
        obj = None
        if notification.type == "mention":
            buffers = ["mentions"]
            obj = notification
        elif notification.type == "follow":
            buffers = ["followers"]
            obj = notification.account
        for b in buffers[::]:
            num = self.order_buffer(b, [obj])
            if num == 0:
                buffers.remove(b)
        pub.sendMessage("mastodon.new_item", session_name=self.get_name(), item=obj, _buffers=buffers)
        # Now, add notification to its buffer.
        num = self.order_buffer("notifications", [notification])
        if num > 0:
            pub.sendMessage("mastodon.new_item", session_name=self.get_name(), item=notification, _buffers=["notifications"])