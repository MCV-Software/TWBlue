# -*- coding: utf-8 -*-
from requests.auth import HTTPProxyAuth
import config
import random
import BaseHTTPServer
import webbrowser
from twython import Twython, TwythonError
from keys import keyring
import authorisationHandler
from requests import certs
import logging
log = logging.getLogger("sessionTwitter")

class twitter(object):

 def login(self, user_key, user_secret, verify_credentials):
  if config.app["proxy"]["server"] != "" and config.app["proxy"]["port"] != "":
   args = {"proxies": {"http": "http://{0}:{1}".format(config.app["proxy"]["server"], config.app["proxy"]["port"]),
  "https": "https://{0}:{1}".format(config.app["proxy"]["server"], config.app["proxy"]["port"])}}
   if config.app["proxy"]["user"] != "" and config.app["proxy"]["password"] != "":
    auth = HTTPProxyAuth(config.app["proxy"]["user"], config.app["proxy"]["password"])
    args["auth"] = auth
   self.twitter = Twython(keyring.get("api_key"), keyring.get("api_secret"), user_key, user_secret, client_args=args)
  else:
   self.twitter = Twython(keyring.get("api_key"), keyring.get("api_secret"), user_key, user_secret)
  if verify_credentials == True:
   self.credentials = self.twitter.verify_credentials()

 def authorise(self, settings):
  authorisationHandler.logged = False
  port = random.randint(30000, 66000)
  httpd = BaseHTTPServer.HTTPServer(('127.0.0.1', port), authorisationHandler.handler)
  if config.app["proxy"]["server"] != "" and config.app["proxy"]["port"] != "":
   args = {"proxies": {"http": "http://{0}:{1}".format(config.app["proxy"]["server"], config.app["proxy"]["port"]),
  "https": "https://{0}:{1}".format(config.app["proxy"]["server"], config.app["proxy"]["port"])}}
   if config.app["proxy"]["user"] != "" and config.app["proxy"]["password"] != "":
    auth = HTTPProxyAuth(config.app["proxy"]["user"], config.app["proxy"]["password"])
    args["auth"] = auth
   twitter = Twython(keyring.get("api_key"), keyring.get("api_secret"), auth_endpoint='authorize', client_args=args)
  else:
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

 def __init__(self):
  log.error(certs.where())