# -*- coding: utf-8 -*-
import platform
if platform.system() == "Windows":
    from wxUI import dialogs, commonMessageDialogs
elif platform.system() == "Linux":
    from gi.repository import Gtk
    from gtkUI import dialogs, commonMessageDialogs
import widgetUtils
import logging
from tweepy.cursor import Cursor
from . import base

log = logging.getLogger("controller.buffers.twitter.listBuffer")

class ListBuffer(base.BaseBuffer):
    def __init__(self, parent, function, name, sessionObject, account, sound=None, bufferType=None, list_id=None, *args, **kwargs):
        super(ListBuffer, self).__init__(parent, function, name, sessionObject, account, sound=None, bufferType=None, *args, **kwargs)
        self.users = []
        self.list_id = list_id
        self.kwargs["list_id"] = list_id

    def start_stream(self, mandatory=False, play_sound=True, avoid_autoreading=False):
        self.get_user_ids()
        super(ListBuffer, self).start_stream(mandatory, play_sound, avoid_autoreading)

    def get_user_ids(self):
        for i in Cursor(self.session.twitter.get_list_members, list_id=self.list_id, include_entities=False, skip_status=True, count=5000).items():
            if i.id not in self.users:
                self.users.append(i.id)

    def remove_buffer(self, force=False):
        if force == False:
            dlg = commonMessageDialogs.remove_buffer()
        else:
            dlg = widgetUtils.YES
        if dlg == widgetUtils.YES:
            if self.name[:-5] in self.session.settings["other_buffers"]["lists"]:
                self.session.settings["other_buffers"]["lists"].remove(self.name[:-5])
                if self.name in self.session.db:
                    self.session.db.pop(self.name)
                self.session.settings.write()
                return True
        elif dlg == widgetUtils.NO:
            return False
