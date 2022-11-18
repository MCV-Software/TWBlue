# -*- coding: utf-8 -*-
import mastodon
from pubsub import pub

class StreamListener(mastodon.StreamListener):

    def __init__(self, session_name, user_id):
        self.session_name = session_name
        self.user_id = user_id
        super(StreamListener, self).__init__()

    def on_update(self, status):
        pub.sendMessage("mastodon.new_status", status=status, session_name=self.session_name)