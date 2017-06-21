# -*- coding: utf-8 -*-
from builtins import object
import re
import widgetUtils
import output
from wxUI.dialogs import userActions
from pubsub import pub
from twython import TwythonError
from extra import autocompletionUsers

class userActionsController(object):
 def __init__(self, buffer, users=[], default="follow"):
  super(userActionsController, self).__init__()
  self.buffer = buffer
  self.session = buffer.session
  self.dialog = userActions.UserActionsDialog(users, default)
  widgetUtils.connect_event(self.dialog.autocompletion, widgetUtils.BUTTON_PRESSED, self.autocomplete_users)
  if self.dialog.get_response() == widgetUtils.OK:
   self.process_action()

 def autocomplete_users(self, *args, **kwargs):
  c = autocompletionUsers.completion.autocompletionUsers(self.dialog, self.session.session_id)
  c.show_menu("dm")

 def process_action(self):
  action = self.dialog.get_action()
  user = self.dialog.get_user()
  if user == "": return
  getattr(self, action)(user)

 def follow(self, user):
  try:
   self.session.twitter.twitter.create_friendship(screen_name=user )
  except TwythonError as err:
   output.speak("Error %s: %s" % (err.error_code, err.msg), True)

 def unfollow(self, user):
  try:
   id = self.session.twitter.twitter.destroy_friendship(screen_name=user )
  except TwythonError as err:
   output.speak("Error %s: %s" % (err.error_code, err.msg), True)

 def mute(self, user):
  try:
   id = self.session.twitter.twitter.create_mute(screen_name=user )
  except TwythonError as err:
   output.speak("Error %s: %s" % (err.error_code, err.msg), True)

 def unmute(self, user):
  try:
   id = self.session.twitter.twitter.destroy_mute(screen_name=user )
  except TwythonError as err:
   output.speak("Error %s: %s" % (err.error_code, err.msg), True)

 def report(self, user):
  try:
   id = self.session.twitter.twitter.report_spam(screen_name=user )
  except TwythonError as err:
   output.speak("Error %s: %s" % (err.error_code, err.msg), True)

 def block(self, user):
  try:
   id = self.session.twitter.twitter.create_block(screen_name=user )
  except TwythonError as err:
   output.speak("Error %s: %s" % (err.error_code, err.msg), True)

 def unblock(self, user):
  try:
   id = self.session.twitter.twitter.destroy_block(screen_name=user )
  except TwythonError as err:
   output.speak("Error %s: %s" % (err.error_code, err.msg), True)

 def ignore_client(self, user):
  tweet = self.buffer.get_right_tweet()
  if "sender" in tweet:
   output.speak(_("You can't ignore direct messages"))
   return
  client = re.sub(r"(?s)<.*?>", "", tweet["source"])
  if client not in self.session.settings["twitter"]["ignored_clients"]:
   self.session.settings["twitter"]["ignored_clients"].append(client)
   self.session.settings.write()