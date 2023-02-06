# -*- coding: utf-8 -*-
import os
import paths
import time
import logging
import webbrowser
import wx
import mastodon
import config
import config_utils
import output
import application
from mastodon import MastodonError, MastodonNotFoundError, MastodonUnauthorizedError
from pubsub import pub
from mysc.thread_utils import call_threaded
from sessions import base
from sessions.mastodon import utils, streaming

log = logging.getLogger("sessions.mastodonSession")

MASTODON_VERSION = "4.0.1"

class Session(base.baseSession):

    def __init__(self, *args, **kwargs):
        super(Session, self).__init__(*args, **kwargs)
        self.config_spec = "mastodon.defaults"
        self.supported_languages = []
        self.type = "mastodon"
        self.db["pagination_info"] = dict()
        self.char_limit = 500
        self.post_visibility = "public"
        self.expand_spoilers = False
        pub.subscribe(self.on_status, "mastodon.status_received")
        pub.subscribe(self.on_status_updated, "mastodon.status_updated")
        pub.subscribe(self.on_notification, "mastodon.notification_received")

    def login(self, verify_credentials=True):
        if self.settings["mastodon"]["access_token"] != None and self.settings["mastodon"]["instance"] != None:
            try:
                log.debug("Logging in to Mastodon instance {}...".format(self.settings["mastodon"]["instance"]))
                self.api = mastodon.Mastodon(access_token=self.settings["mastodon"]["access_token"], api_base_url=self.settings["mastodon"]["instance"], mastodon_version=MASTODON_VERSION, user_agent="TWBlue/{}".format(application.version))
                if verify_credentials == True:
                    credentials = self.api.account_verify_credentials()
                    self.db["user_name"] = credentials["username"]
                    self.db["user_id"] = credentials["id"]
                    self.settings["mastodon"]["user_name"] = credentials["username"]
                self.logged = True
                log.debug("Logged.")
                self.counter = 0
            except MastodonError:
                log.exception("The login attempt failed.")
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
            temporary_api = mastodon.Mastodon(client_id=client_id, client_secret=client_secret, api_base_url=instance, mastodon_version=MASTODON_VERSION, user_agent="TWBlue/{}".format(application.version))
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
            self.supported_languages = instance.languages
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
        self.db["lists"] = self.api.lists()

    def get_muted_users(self):
        ### ToDo: Use a function to retrieve all muted users.
        self.db["muted_users"] = self.api.mutes()

    def get_user_alias(self, user):
        aliases = self.settings.get("user-aliases")
        if aliases == None:
            log.error("Aliases are not defined for this config spec.")
            return user.name
        user_alias = aliases.get(user.id_str)
        if user_alias != None:
            return user_alias
        return user.name

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
            if ignore_older and last_id != None:
                if i.id < last_id:
                    log.error("Ignoring an older tweet... Last id: {0}, tweet id: {1}".format(last_id, i.id))
                    continue
            if utils.find_item(i, self.db[name]) == None:
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
        while finished==False and tries < 25:
            try:
                val = getattr(self.api, call_name)(*args, **kwargs)
                finished = True
            except MastodonError as e:
                output.speak(str(e))
                val = None
                if type(e) != MastodonNotFoundError  and type(e) != MastodonUnauthorizedError :
                    tries = tries+1
                    time.sleep(5)
                elif report_failure:
                    output.speak(_("%s failed.  Reason: %s") % (action, str(e)))
                finished = True
#   except:
#    tries = tries + 1
#    time.sleep(5)
        if report_success:
            output.speak(_("%s succeeded.") % action)
        if _sound != None: self.sound.play(_sound)
        return val

    def send_post(self, reply_to=None, users=None, visibility=None, posts=[]):
        """ Convenience function to send a thread. """
        in_reply_to_id = reply_to
        for obj in posts:
            text = obj.get("text")
            if len(obj["attachments"]) == 0:
                item = self.api_call(call_name="status_post", status=text, _sound="tweet_send.ogg",  in_reply_to_id=in_reply_to_id, visibility=visibility, sensitive=obj["sensitive"], spoiler_text=obj["spoiler_text"])
                if item != None:
                    in_reply_to_id = item["id"]
            else:
                media_ids = []
                poll = None
                if len(obj["attachments"]) == 1 and obj["attachments"][0]["type"] == "poll":
                    poll = self.api.make_poll(options=obj["attachments"][0]["options"], expires_in=obj["attachments"][0]["expires_in"], multiple=obj["attachments"][0]["multiple"], hide_totals=obj["attachments"][0]["hide_totals"])
                else:
                    for i in obj["attachments"]:
                        img = self.api_call("media_post", media_file=i["file"], description=i["description"])
                        media_ids.append(img.id)
                item = self.api_call(call_name="status_post", status=text, _sound="tweet_send.ogg", in_reply_to_id=in_reply_to_id, media_ids=media_ids, visibility=visibility, poll=poll, sensitive=obj["sensitive"], spoiler_text=obj["spoiler_text"])
                if item != None:
                    in_reply_to_id = item["id"]

    def get_name(self):
        instance = self.settings["mastodon"]["instance"]
        instance = instance.replace("https://", "")
        user = self.settings["mastodon"]["user_name"]
        return "Mastodon: {}@{}".format(user, instance)

    def start_streaming(self):
        if self.settings["general"]["disable_streaming"]:
            log.info("Streaming is disabled for session {}. Skipping...".format(self.get_name()))
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