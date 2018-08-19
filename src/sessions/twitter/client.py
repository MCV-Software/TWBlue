# -*- coding: utf-8 -*-
import random
import webbrowser
import logging
import config
from requests import certs
from twython import Twython, TwythonError
from keys import keyring

log = logging.getLogger("sessionTwitter")

class twitter(object):

 def login(self, user_key, user_secret, verify_credentials):
  self.twitter = Twython(keyring.get("api_key"), keyring.get("api_secret"), user_key, user_secret)
  if verify_credentials == True:
   self.credentials = self.twitter.verify_credentials()

 def authorise(self):
  twitter = Twython(keyring.get("api_key"), keyring.get("api_secret"))
  self.auth = twitter.get_authentication_tokens(callback_url="oob")
  webbrowser.open_new_tab(self.auth['auth_url'])

 def verify_authorisation(self, settings, pincode):
  self.twitter = Twython(keyring.get("api_key"), keyring.get("api_secret"), self.auth['oauth_token'], self.auth['oauth_token_secret'])
  final = self.twitter.get_authorized_tokens(pincode)
  self.save_configuration(settings, final["oauth_token"], final["oauth_token_secret"])

 def save_configuration(self, settings, user_key, user_secret):
  settings["twitter"]["user_key"] = user_key
  settings["twitter"]["user_secret"] = user_secret
  settings.write()
