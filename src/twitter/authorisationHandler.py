# -*- coding: utf-8 -*-
from future import standard_library
standard_library.install_aliases()
import http.server
import application
from urllib.parse import urlparse, parse_qs

logged = False
verifier = None
 
class handler(http.server.BaseHTTPRequestHandler):

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
        self.finish()
