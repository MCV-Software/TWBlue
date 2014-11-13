# -*- coding: utf-8 -*-
import BaseHTTPServer
from urlparse import urlparse, parse_qs

logged = False
verifier = None
 
class handler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_GET(self):
        global logged
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        logged = True
        params = parse_qs(urlparse(self.path).query)
        global verifier
        verifier = params.get('oauth_verifier', [None])[0]
        self.wfile.write("You have successfully logged in to Twitter with TW Blue. "
                             "You can close this window now.")