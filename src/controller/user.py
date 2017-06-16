# -*- coding: utf-8 -*-
from builtins import object
import wx
import webbrowser
import widgetUtils
import output
from wxUI.dialogs import update_profile, show_user
import logging
log = logging.getLogger("controller.user")
from twython import TwythonError

class profileController(object):
 def __init__(self, session, user=None):
  super(profileController, self).__init__()
  self.file = None
  self.session = session
  self.user = user
  if user == None:
   self.get_data(screen_name=self.session.db["user_name"])
   self.dialog = update_profile.updateProfileDialog()
   self.fill_profile_fields()
   self.uploaded = False
   widgetUtils.connect_event(self.dialog.upload_image, widgetUtils.BUTTON_PRESSED, self.upload_image)
  else:
   try:
    self.get_data(screen_name=self.user)
   except TwythonError as err:
    if err.error_code == 404:
     wx.MessageDialog(None, _("That user does not exist"), _("Error"), wx.ICON_ERROR).ShowModal()
    if err.error_code == 403:
     wx.MessageDialog(None, _("User has been suspended"), _("Error"), wx.ICON_ERROR).ShowModal()
    log.error("error %d: %s" % (err.error_code, err.msg))
    return
   self.dialog = show_user.showUserProfile()
   string = self.get_user_info()
   self.dialog.set("text", string)
   self.dialog.set_title(_("Information for %s") % (self.data["screen_name"]))
   if self.data["url"] != None:
    self.dialog.enable_url()
    widgetUtils.connect_event(self.dialog.url, widgetUtils.BUTTON_PRESSED, self.visit_url)
  if self.dialog.get_response() == widgetUtils.OK and self.user == None:
   self.do_update()

 def get_data(self, screen_name):
  self.data = self.session.twitter.twitter.show_user(screen_name=screen_name)
  if screen_name != self.session.db["user_name"]:
   self.friendship_status = self.session.twitter.twitter.show_friendship(source_screen_name=self.session.db["user_name"], target_screen_name=screen_name)

 def fill_profile_fields(self):
  self.dialog.set_name(self.data["name"])
  if self.data["url"] != None:
   self.dialog.set_url(self.data["url"])
  if len(self.data["location"]) > 0:
   self.dialog.set_location(self.data["location"])
  if len(self.data["description"]) > 0:
   self.dialog.set_description(self.data["description"])

 def get_image(self):
  file = self.dialog.upload_picture()
  if file != None:
   self.file = open(file, "rb")
   self.uploaded = True
   self.dialog.change_upload_button(self.uploaded)

 def discard_image(self):
  self.file = None
  output.speak(_("Discarded"))
  self.uploaded = False
  self.dialog.change_upload_button(self.uploaded)

 def upload_image(self, *args, **kwargs):
  if self.uploaded == False:
   self.get_image()
  elif self.uploaded == True:
   self.discard_image()

 def do_update(self):
  if self.user != None: return
  name = self.dialog.get("name")
  description = self.dialog.get("description")
  location = self.dialog.get("location")
  url = self.dialog.get("url")
  if self.file != None:
   try:
    self.session.twitter.twitter.update_profile_image(image=self.file)
   except TwythonError as e:
    output.speak("Error %s. %s" % (e.error_code, e.msg))
  try:
   self.session.twitter.twitter.update_profile(name=name, description=description, location=location, url=url)
  except TwythonError as e:
   output.speak("Error %s. %s" % (e.error_code, e.msg))

 def get_user_info(self):
 
  string = ""
  string = string + _("Username: @%s\n") % (self.data["screen_name"])
  string = string + _("Name: %s\n") % (self.data["name"])
  if self.data["location"] != "":
   string = string + _("Location: %s\n") % (self.data["location"])
  if self.data["url"] != None:
   string = string+ _("URL: %s\n") % (self.data["url"])
  if self.data["description"] != "":
   string = string+ _("Bio: %s\n") % (self.data["description"])
  if self.data["protected"] == True: protected = _("Yes")
  else: protected = _("No")
  string = string+ _("Protected: %s\n") % (protected)
  if hasattr(self, "friendship_status"):
   relation = False
   friendship = "Relationship: "
   if self.friendship_status["relationship"]["target"]["followed_by"]:
    friendship += _("You follow {0}. ").format(self.data["name"],)
    relation = True
   if self.friendship_status["relationship"]["target"]["following"]:
    friendship += _("{0} is following you.").format(self.data["name"],)
    relation = True
   if relation == True:
    string = string+friendship+"\n"
  string = string+_("Followers: %s\n Friends: %s\n") % (self.data["followers_count"], self.data["friends_count"])
  if self.data["verified"] == True: verified = _("Yes")
  else: verified = _("No")
  string = string+ _("Verified: %s\n") % (verified)
  string = string+ _("Tweets: %s\n") % (self.data["statuses_count"])
  string = string+ _("Likes: %s") % (self.data["favourites_count"])
  return string

 def visit_url(self, *args, **kwargs):
  webbrowser.open_new_tab(self.data["url"])