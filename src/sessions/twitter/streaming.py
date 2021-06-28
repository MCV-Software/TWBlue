# -*- coding: utf-8 -*-
import tweepy
from pubsub import pub

class StreamListener(tweepy.StreamListener):

    def __init__(self, twitter_api, user, *args, **kwargs):
        super(StreamListener, self).__init__(*args, **kwargs)
        self.api = twitter_api
        self.user = user
        self.users = [str(id) for id in self.api.friends_ids()]

    def on_status(self, status):
        """ Checks data arriving as a tweet. """
        if status.user.id_str in self.users:
            pub.sendMessage("newStatus", status=status, user=self.user)
#            print(status.text)

