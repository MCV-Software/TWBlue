# -*- coding: utf-8 -*-

from future import standard_library
standard_library.install_aliases()
from builtins import object
import config
import random
import http.server
import webbrowser
from twython import Twython, TwythonError
from keys import keyring
from . import authorisationHandler
from requests import certs
import logging
log = logging.getLogger("sessionTwitter")

class twitter(object):

 def login(self, user_key, user_secret, verify_credentials):
  self.twitter = Twython(keyring.get("api_key"), keyring.get("api_secret"), user_key, user_secret)
  if verify_credentials == True:
   self.credentials = self.twitter.verify_credentials()

 def authorise(self, settings):
  authorisationHandler.logged = False
  port = random.randint(30000, 65535)
  httpd = http.server.HTTPServer(('127.0.0.1', port), authorisationHandler.handler)
  twitter = Twython(keyring.get("api_key"), keyring.get("api_secret"), auth_endpoint='authorize')
  auth = twitter.get_authentication_tokens("http://127.0.0.1:{0}".format(port,))
  webbrowser.open_new_tab(auth['auth_url'])
  while authorisationHandler.logged == False:
   httpd.handle_request()
  self.twitter = Twython(keyring.get("api_key"), keyring.get("api_secret"), auth['oauth_token'], auth['oauth_token_secret'])
  final = self.twitter.get_authorized_tokens(authorisationHandler.verifier)
  self.save_configuration(settings, final["oauth_token"], final["oauth_token_secret"])
  httpd.server_close()

 def save_configuration(self, settings, user_key, user_secret):
  settings["twitter"]["user_key"] = user_key
  settings["twitter"]["user_secret"] = user_secret
  settings.write()

