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
        # Hide replies to users not followed by current account.
        if status.in_reply_to_user_id_str != None and status.in_reply_to_user_id_str not in self.users:
            return
        if status.user.id_str in self.users:
            pub.sendMessage("newStatus", status=status, user=self.user)



class Stream(tweepy.Stream):

    def _run(self):
        # Authenticate
        url = "https://%s%s" % (self.host, self.url)

        # Connect and process the stream
        error_counter = 0
        resp = None
        exc_info = None
        while self.running:
            if self.retry_count is not None:
                if error_counter > self.retry_count:
                    # quit if error count greater than retry count
                    break
            try:
                auth = self.auth.apply_auth()
                resp = self.session.request('POST',
                                            url,
                                            data=self.body,
                                            timeout=self.timeout,
                                            stream=True,
                                            auth=auth,
                                            verify=self.verify,
                                            proxies = self.proxies)
                if resp.status_code != 200:
                    if self.listener.on_error(resp.status_code) is False:
                        break
                    error_counter += 1
                    if resp.status_code == 420:
                        self.retry_time = max(self.retry_420_start,
                                              self.retry_time)
                    time.sleep(self.retry_time)
                    self.retry_time = min(self.retry_time * 2,
                                          self.retry_time_cap)
                else:
                    error_counter = 0
                    self.retry_time = self.retry_time_start
                    self.snooze_time = self.snooze_time_step
                    self.listener.on_connect()
                    self._read_loop(resp)
            except (requests.ConnectionError, requests.Timeout, ssl.SSLError, urllib3.exceptions.ReadTimeoutError, urllib3.exceptions.ProtocolError) as exc:
                # This is still necessary, as a SSLError can actually be
                # thrown when using Requests
                # If it's not time out treat it like any other exception
                if isinstance(exc, ssl.SSLError):
                    if not (exc.args and 'timed out' in str(exc.args[0])):
                        exc_info = sys.exc_info()
                        break
                if self.listener.on_timeout() is False:
                    break
                if self.running is False:
                    break
                time.sleep(self.snooze_time)
                self.snooze_time = min(self.snooze_time + self.snooze_time_step,
                                       self.snooze_time_cap)
            except Exception as exc:
                exc_info = sys.exc_info()
                # any other exception is fatal, so kill loop
                break

        # cleanup
        self.running = False
        if resp:
            resp.close()

        self.new_session()

        if exc_info:
            # call a handler first so that the exception can be logged.
            self.listener.on_exception(exc_info[1])
            six.reraise(*exc_info)
