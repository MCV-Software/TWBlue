# -*- coding: utf-8 -*-
""" Streaming support for TWBlue. """
import time
import sys
import six
import requests
import urllib3
import ssl
import tweepy
import logging
from pubsub import pub

log = logging.getLogger("sessions.twitter.streaming")

class Stream(tweepy.Stream):

    def __init__(self, twitter_api, session_name, user_id, muted_users=[], *args, **kwargs):
        super(Stream, self).__init__(*args, **kwargs)
        log.debug("Starting streaming listener for session {}".format(session_name))
        self.started = False
        self.users = []
        self.api = twitter_api
        self.session_name = session_name
        self.user_id = user_id
        friends = self.api.get_friend_ids()
        log.debug("Retrieved {} friends to add to the streaming listener.".format(len(friends)))
        self.users.append(str(self.user_id))
        log.debug("Got {} muted users.".format(len(muted_users)))
        for user in friends:
            if user not in muted_users:
                self.users.append(str(user))
        self.started = True
        log.debug("Streaming listener started with {} users to follow.".format(len(self.users)))

    def on_connect(self):
        pub.sendMessage("twitter.stream_connected", session_name=self.session_name)

    def on_exception(self, ex):
        log.exception("Exception received on streaming endpoint for session {}".format(self.session_name))

    def on_status(self, status):
        """ Checks data arriving as a tweet. """
        # Hide replies to users not followed by current account.
        if status.in_reply_to_user_id_str != None and status.in_reply_to_user_id_str not in self.users and status.user.id != self.user_id:
            return
        if status.user.id_str in self.users:
            pub.sendMessage("twitter.new_status", status=status, session_name=self.session_name)
