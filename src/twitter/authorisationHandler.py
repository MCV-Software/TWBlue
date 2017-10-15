# -*- coding: utf-8 -*-
import BaseHTTPServer
import application
from urlparse import urlparse, parse_qs
from pubsub import pub

logged = False
verifier = None
 
class handler(BaseHTTPServer.BaseHTTPRequestHandler, object):

    def do_GET(self):
        global logged
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        logged = True
        params = parse_qs(urlparse(self.path).query)
        global verifier
        verifier = params.get('oauth_verifier', [None])[0]
        self.wfile.write(u"You have successfully logged into Twitter with {0}. You can close this window now.".format(application.name))
        pub.sendMessage("authorisation-accepted")
        pub.unsubscribe(self.cancelled, "authorisation-cancelled")
        self.finish()

    def __init__(self, *args, **kwargs):
        pub.subscribe(self.cancelled, "authorisation-cancelled")
        super(handler, self).__init__(*args, **kwargs)

    def cancelled(self):
        pub.unsubscribe(self.cancelled, "authorisation-cancelled")
        self.finish()