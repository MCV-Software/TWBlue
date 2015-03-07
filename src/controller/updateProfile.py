# -*- coding: utf-8 -*-
import widgetUtils
import output
from wxUI.dialogs import update_profile
from twython import TwythonError

class updateProfileController(object):
 def __init__(self, session, user=None):
  super(updateProfileController, self).__init__()
  self.file = None
  self.session = session
  self.user = user
  self.dialog = update_profile.updateProfileDialog()
  if user == None:
   self.get_data(screen_name=self.session.db["user_name"])
   self.uploaded = False
   widgetUtils.connect_event(self.dialog.upload_image, widgetUtils.BUTTON_PRESSED, self.upload_image)
  else:
   self.get_data(screen_name=self.user)
   self.dialog.set_readonly()
  if self.dialog.get_response() == widgetUtils.OK and self.user == None:
   self.do_update()


 def get_data(self, screen_name):
  data = self.session.twitter.twitter.show_user(screen_name=screen_name)
  self.dialog.set_name(data["name"])
  if data["url"] != None:
   self.dialog.set_url(data["url"])
  if len(data["location"]) > 0:
   self.dialog.set_location(data["location"])
  if len(data["description"]) > 0:
   self.dialog.set_description(data["description"])

 def get_image(self):
  file = self.dialog.upload_picture()
  if file != None:
   self.file = open(file, "rb")
   self.uploaded = True
   self.dialog.change_upload_button(self.uploaded)

 def discard_image(self):
  self.file = None
  output.speak(_(u"Discarded"))
  self.uploaded = False
  self.dialog.change_upload_button(self.uploaded)

 def upload_image(self, *args, **kwargs):
  if self.uploaded == False:
   self.get_image()
  elif self.uploaded == True:
   self.discard_image()

 def do_update(self):
  name = self.dialog.get("name")
  description = self.dialog.get("description")
  location = self.dialog.get("location")
  url = self.dialog.get("url")
  if self.file != None:
   try:
    self.session.twitter.twitter.update_profile_image(image=self.file)
   except TwythonError as e:
    output.speak(u"Error %s. %s" % (e.error_code, e.msg))
  try:
   self.session.twitter.twitter.update_profile(name=name, description=description, location=location, url=url)
  except TwythonError as e:
   output.speak(u"Error %s. %s" % (e.error_code, e.msg))