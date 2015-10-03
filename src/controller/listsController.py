# -*- coding: utf-8 -*-
import widgetUtils
import output
from wxUI.dialogs import lists
from twython import TwythonError
from twitter import compose, utils
from pubsub import pub

class listsController(object):
 def __init__(self, session, user=None):
  super(listsController, self).__init__()
  self.session = session
  if user == None:
   self.dialog = lists.listViewer()
   self.dialog.populate_list(self.get_all_lists())
   widgetUtils.connect_event(self.dialog.createBtn, widgetUtils.BUTTON_PRESSED, self.create_list)
   widgetUtils.connect_event(self.dialog.editBtn, widgetUtils.BUTTON_PRESSED, self.edit_list)
   widgetUtils.connect_event(self.dialog.deleteBtn, widgetUtils.BUTTON_PRESSED, self.remove_list)
   widgetUtils.connect_event(self.dialog.view, widgetUtils.BUTTON_PRESSED, self.open_list_as_buffer)
   widgetUtils.connect_event(self.dialog.deleteBtn, widgetUtils.BUTTON_PRESSED, self.remove_list)
  else:
   self.dialog = lists.userListViewer(user)
   self.dialog.populate_list(self.get_user_lists(user))
   widgetUtils.connect_event(self.dialog.createBtn, widgetUtils.BUTTON_PRESSED, self.subscribe)
   widgetUtils.connect_event(self.dialog.deleteBtn, widgetUtils.BUTTON_PRESSED, self.unsubscribe)
  self.dialog.get_response()

 def get_all_lists(self):
  return [compose.compose_list(item) for item in self.session.db["lists"]]

 def get_user_lists(self, user):
  self.lists = self.session.twitter.twitter.show_lists(reverse=True, screen_name=user)
  return [compose.compose_list(item) for item in self.lists]

 def create_list(self, *args, **kwargs):
  dialog = lists.createListDialog()
  if dialog.get_response() == widgetUtils.OK:
   name = dialog.get("name")
   description = dialog.get("description")
   p = dialog.get("public")
   if p == True:
    mode = "public"
   else:
    mode = "private"
   try:
    new_list = self.session.twitter.twitter.create_list(name=name, description=description, mode=mode)
    self.session.db["lists"].append(new_list)
    self.dialog.lista.insert_item(False, *compose.compose_list(new_list))
   except TwythonError as e:
    output.speak("error %s: %s" % (e.status_code, e.msg))
  dialog.destroy()

 def edit_list(self, *args, **kwargs):
  if self.dialog.lista.get_count() == 0: return
  list = self.session.db["lists"][self.dialog.get_item()]
  dialog = lists.editListDialog(list)
  if dialog.get_response() == widgetUtils.OK:
   name = dialog.get("name")
   description = dialog.get("description")
   p = dialog.get("public")
   if p == True:
    mode = "public"
   else:
    mode = "private"
   try:
    self.session.twitter.twitter.update_list(list_id=list["id"], name=name, description=description, mode=mode)
    self.session.get_lists()
    self.dialog.populate_list(self.get_all_lists(), True)
   except TwythonError as e:
    output.speak("error %s: %s" % (e.error_code, e.msg))
  dialog.destroy()

 def remove_list(self, *args, **kwargs):
  if self.dialog.lista.get_count() == 0: return
  list = self.session.db["lists"][self.dialog.get_item()]["id"]
  if lists.remove_list() == widgetUtils.YES:
   try:
    self.session.twitter.twitter.delete_list(list_id=list)
    self.session.db["lists"].pop(self.dialog.get_item())
    self.dialog.lista.remove_item(self.dialog.get_item())
   except TwythonError as e:
    output.speak("error %s: %s" % (e.error_code, e.msg))

 def open_list_as_buffer(self, *args, **kwargs):
  if self.dialog.lista.get_count() == 0: return
  list = self.session.db["lists"][self.dialog.get_item()]
  pub.sendMessage("create-new-buffer", buffer="list", account=self.session.db["user_name"], create=list["name"])

 def subscribe(self, *args, **kwargs):
  if self.dialog.lista.get_count() == 0: return
  list_id = self.lists[self.dialog.get_item()]["id"]
  try:
   list = self.session.twitter.twitter.subscribe_to_list(list_id=list_id)
   item = utils.find_item(list["id"], self.session.db["lists"])
   self.session.db["lists"].append(list)
  except TwythonError as e:
   output.speak("error %s: %s" % (e.status_code, e.msg))

 def unsubscribe(self, *args, **kwargs):
  if self.dialog.lista.get_count() == 0: return
  list_id = self.lists[self.dialog.get_item()]["id"]
  try:
   list = self.session.twitter.twitter.unsubscribe_from_list(list_id=list_id)
   self.session.db["lists"].remove(list)
  except TwythonError as e:
   output.speak("error %s: %s" % (e.status_code, e.msg))
