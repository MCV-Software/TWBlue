from __future__ import unicode_literals
from gi.repository import Gtk
import widgetUtils

class sessionManagerWindow(widgetUtils.baseDialog):
 def __init__(self):
  super(sessionManagerWindow, self).__init__("Session Manager", None, 0, (Gtk.STOCK_OK, widgetUtils.OK, Gtk.STOCK_CANCEL, widgetUtils.CANCEL))
  self.list = widgetUtils.list("Session")
  self.box.add(self.list.list)
  btnBox = Gtk.Box(spacing=6)
  self.new = Gtk.Button("New account")
  self.remove = Gtk.Button("Remove account")
  self.configuration = Gtk.Button("Configuration")
  btnBox.add(self.new)
  btnBox.add(self.remove)
  btnBox.add(self.configuration)
  self.box.add(btnBox)
  self.show_all()

 def fill_list(self, sessionsList):
  for i in sessionsList:
   self.list.insert_item(False, i)
  if self.list.get_count() > 0:
   self.list.select_item(0)

 def new_account_dialog(self):
  dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO, "Authorization")
  dialog.format_secondary_text("The request to authorize your Twitter account will be opened in your browser. You only need to do this once. Would you like to continue?")
  answer = dialog.run()
  dialog.destroy()
  return answer

 def add_new_session_to_list(self):
  total = self.list.get_count()
  name = "Authorized account %d" % (total+1)
  self.list.insert_item(name)
  if self.list.get_count() == 1:
   self.list.select_item(0)

 def show_unauthorised_error(self):
  dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.CANCEL, "Invalid user token")
  dialog.format_secondary_text("Your access token is invalid or the authorization has failed. Please try again.")
  answer = dialog.run()
  return answer

 def remove_account_dialog(self):
  dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO, "Remove account")
  dialog.format_secondary_text("Do you really want delete this account?")
  answer = dialog.run()
  return answer

 def get_selected(self):
  return self.list.get_selected()

 def remove_session(self, sessionID):
  self.list.remove_item(sessionID)

