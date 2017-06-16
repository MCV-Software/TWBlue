# -*- coding: utf-8 -*-
from future import standard_library
standard_library.install_aliases()
import http.server, application
 
logged = False

class handler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        global logged
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        logged = True
        self.wfile.write("You have successfully logged into Pocket with" + application.name + ". "
                             "You can close this window now.")