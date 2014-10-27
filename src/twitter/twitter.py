# -*- coding: utf-8 -*-
import BaseHTTPServer
import webbrowser
from urlparse import urlparse, parse_qs
from twython import Twython, TwythonError
import config
import application
import output
import sound
import time

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

class twitter(object):

 def login(self, user_key=None, user_secret=None):
  if user_key != None and user_secret != None:
   self.twitter = Twython(application.app_key, application.app_secret, user_key, user_secret)
  elif config.main != None:
   self.twitter = Twython(application.app_key, application.app_secret, config.main["twitter"]["user_key"], config.main["twitter"]["user_secret"])
  else:
   self.twitter = Twython(application.app_key, application.app_secret, self.final_step['oauth_token'], self.final_step['oauth_token_secret'])
  self.credentials = self.twitter.verify_credentials()

 def authorise(self):
  httpd = BaseHTTPServer.HTTPServer(('127.0.0.1', 8080), handler)
  twitter = Twython(application.app_key, application.app_secret)
  auth = twitter.get_authentication_tokens("http://127.0.0.1:8080")
  webbrowser.open_new_tab(auth['auth_url'])
  global logged, verifier
  while logged == False:
   httpd.handle_request()
  self.twitter = Twython(application.app_key, application.app_secret, auth['oauth_token'], auth['oauth_token_secret'])
  final = self.twitter.get_authorized_tokens(verifier)
  self.save_configuration(final["oauth_token"], final["oauth_token_secret"])

 def save_configuration(self, user_key=None, user_secret=None):
  if user_key != None and user_secret != None:
   config.main["twitter"]["user_key"] = user_key
   config.main["twitter"]["user_secret"] = user_secret
  else:
   config.main['twitter']['user_key'] = self.final_step['oauth_token']
   config.main['twitter']['user_secret'] = self.final_step['oauth_token_secret']
  config.main.write()

 def api_call(self, call_name, action="", _sound=None, report_success=False, report_failure=True, preexec_message="", *args, **kwargs):
  finished = False
  tries = 0
  if preexec_message:
   output.speak(preexec_message, True)
  while finished==False and tries < 25:
   try:
    val = getattr(self.twitter, call_name)(*args, **kwargs)
    finished = True
   except TwythonError as e:
#    if hasattr(e, 'reason') and e.reason.startswith("Failed to send request"):
    output.speak(e.message)
    if report_failure and hasattr(e, 'message'):
     output.speak(_("%s failed.  Reason: %s") % (action, e.message))
    finished = True
   except:
    tries = tries + 1
    time.sleep(5)
     #   raise e
  if report_success:
   output.speak(_("%s succeeded.") % action)
  if _sound != None: sound.player.play(_sound)
#  return val