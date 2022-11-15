# -*- coding: utf-8 -*-
import widgetUtils
import output
import logging
from wxUI.dialogs import lists
from tweepy.errors import TweepyException
from sessions.twitter import compose, utils
from pubsub import pub

log = logging.getLogger("controller.listsController")

class listsController(object):
    def __init__(self, session, user=None, lists_buffer_position=0):
        super(listsController, self).__init__()
        self.session = session
        self.lists_buffer_position = lists_buffer_position
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
        self.lists = self.session.twitter.get_lists(reverse=True, screen_name=user)
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
                new_list = self.session.twitter.create_list(name=name, description=description, mode=mode)
                self.session.db["lists"].append(new_list)
                self.dialog.lista.insert_item(False, *compose.compose_list(new_list))
            except TweepyException as e:
                output.speak("error %s" % (str(e)))
                log.exception("error %s" % (str(e)))
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
                self.session.twitter.update_list(list_id=list.id, name=name, description=description, mode=mode)
                self.session.get_lists()
                self.dialog.populate_list(self.get_all_lists(), True)
            except TweepyException as e:
                output.speak("error %s" % (str(e)))
                log.exception("error %s" % (str(e)))
        dialog.destroy()

    def remove_list(self, *args, **kwargs):
        if self.dialog.lista.get_count() == 0: return
        list = self.session.db["lists"][self.dialog.get_item()].id
        if lists.remove_list() == widgetUtils.YES:
            try:
                self.session.twitter.destroy_list(list_id=list)
                self.session.db["lists"].pop(self.dialog.get_item())
                self.dialog.lista.remove_item(self.dialog.get_item())
            except TweepyException as e:
                output.speak("error %s" % (str(e)))
                log.exception("error %s" % (str(e)))

    def open_list_as_buffer(self, *args, **kwargs):
        if self.dialog.lista.get_count() == 0: return
        list = self.session.db["lists"][self.dialog.get_item()]
        pub.sendMessage("createBuffer", buffer_type="ListBuffer", session_type=self.session.type, buffer_title=_("List for {}").format(list.name), parent_tab=self.lists_buffer_position, start=True, kwargs=dict(function="list_timeline", name="%s-list" % (list.name,), sessionObject=self.session, account=self.session.get_name(), bufferType=None, sound="list_tweet.ogg", list_id=list.id, include_ext_alt_text=True, tweet_mode="extended"))

    def subscribe(self, *args, **kwargs):
        if self.dialog.lista.get_count() == 0: return
        list_id = self.lists[self.dialog.get_item()].id
        try:
            list = self.session.twitter.subscribe_list(list_id=list_id)
            item = utils.find_item(list.id, self.session.db["lists"])
            self.session.db["lists"].append(list)
        except TweepyException as e:
            output.speak("error %s" % (str(e)))
            log.exception("error %s" % (str(e)))

    def unsubscribe(self, *args, **kwargs):
        if self.dialog.lista.get_count() == 0: return
        list_id = self.lists[self.dialog.get_item()].id
        try:
            list = self.session.twitter.unsubscribe_list(list_id=list_id)
            self.session.db["lists"].remove(list)
        except TweepyException as e:
            output.speak("error %s" % (str(e)))
            log.exception("error %s" % (str(e)))
