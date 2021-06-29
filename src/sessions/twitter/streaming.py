# -*- coding: utf-8 -*-
import tweepy
import logging
from pubsub import pub

log = logging.getLogger("sessions.twitter.streaming")

class StreamListener(tweepy.StreamListener):

    def __init__(self, twitter_api, user, user_id, *args, **kwargs):
        super(StreamListener, self).__init__(*args, **kwargs)
        self.api = twitter_api
        self.user = user
        self.user_id = user_id
        self.users = [str(id) for id in self.api.friends_ids()]
        self.users.append(str(self.user_id))
        log.debug("Started streaming object for user {}".format(self.user))

    def on_connect(self):
        pub.sendMessage("streamConnected", user=self.user)

    def on_exception(self, ex):
        log.exception("Exception received on streaming endpoint for user {}".format(self.user))

    def on_status(self, status):
        """ Checks data arriving as a tweet. """
        if status.user.id_str in self.users:
            pub.sendMessage("newStatus", status=status, user=self.user)
#            print(status.text)

