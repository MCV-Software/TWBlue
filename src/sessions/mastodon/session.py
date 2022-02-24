# -*- coding: utf-8 -*-
import os
import paths
import time
import logging
import wx
import mastodon
import config
import config_utils
import output
import application
from pubsub import pub
from mysc.thread_utils import call_threaded
from sessions import base
from .wxUI import authorisationDialog

log = logging.getLogger("sessions.mastodonSession")

class Session(base.baseSession):

    def __init__(self, *args, **kwargs):
        super(Session, self).__init__(*args, **kwargs)
        self.config_spec = "mastodon.defaults"
        self.supported_languages = []

    def login(self, verify_credentials=True):
        if self.settings["mastodon"]["access_token"] != None and self.settings["mastodon"]["instance"] != None:
            try:
                log.debug("Logging in to Mastodon instance {}...".format(self.settings["mastodon"]["instance"]))
                self.api = mastodon.Mastodon(access_token=self.settings["mastodon"]["access_token"], api_base_url=self.settings["mastodon"]["instance"])
                if verify_credentials == True:
                    credentials = self.api.account_verify_credentials()
                    self.db["user_name"] = credentials["username"]
                    self.db["user_id"] = credentials["id"]
                    self.settings["mastodon"]["user_name"] = credentials["username"]
                self.logged = True
                log.debug("Logged.")
                self.counter = 0
            except IOError:
                log.error("The login attempt failed.")
                self.logged = False
        else:
            self.logged = False
            raise Exceptions.RequireCredentialsSessionError

    def authorise(self):
        if self.logged == True:
            raise Exceptions.AlreadyAuthorisedError("The authorisation process is not needed at this time.")
        else:
            self.authorisation_dialog = authorisationDialog()
            answer = self.authorisation_dialog.ShowModal()
            if answer == wx.ID_OK:
                client_id, client_secret = mastodon.Mastodon.create_app("TWBlue", api_base_url=self.authorisation_dialog.instance.GetValue(), website="https://twblue.es")
                temporary_api = mastodon.Mastodon(client_id=client_id, client_secret=client_secret, api_base_url=self.authorisation_dialog.instance.GetValue())
                access_token = temporary_api.log_in(self.authorisation_dialog.email.GetValue(), self.authorisation_dialog.password.GetValue())
                self.settings["mastodon"]["access_token"] = access_token
                self.settings["mastodon"]["instance"] = self.authorisation_dialog.instance.GetValue()
                self.settings.write()

    def get_user_info(self):
        """ Retrieves some information required by TWBlue for setup."""
        # retrieve the current user's UTC offset so we can calculate dates properly.
        offset = time.timezone if (time.localtime().tm_isdst == 0) else time.altzone
        offset = offset / 60 / 60 * -1
        self.db["utc_offset"] = offset
        if len(self.supported_languages) == 0:
            self.supported_languages = self.api.instance().languages
        self.get_lists()
        self.get_muted_users()
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