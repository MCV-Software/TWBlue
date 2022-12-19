# -*- coding: utf-8 -*-
import time
import logging
import widgetUtils
from controller.buffers.mastodon.base import BaseBuffer
from sessions.mastodon import compose, templates
from wxUI import buffers

log = logging.getLogger("controller.buffers.mastodon.notifications")

class NotificationsBuffer(BaseBuffer):

    def get_message(self):
        notification = self.get_item()
        if notification == None:
            return
        template = self.session.settings["templates"]["notification"]
        post_template = self.session.settings["templates"]["post"]
        t = templates.render_notification(notification, template, post_template, relative_times=self.session.settings["general"]["relative_times"], offset_hours=self.session.db["utc_offset"])
        return t

    def create_buffer(self, parent, name):
        self.buffer = buffers.mastodon.notificationsPanel(parent, name)

    def onFocus(self, *args, **kwargs):
        item = self.get_item()
        if self.session.settings["general"]["relative_times"] == True:
            original_date = arrow.get(self.session.db[self.name][self.buffer.list.get_selected()].created_at)
            ts = original_date.humanize(locale=languageHandler.getLanguage())
            self.buffer.list.list.SetItem(self.buffer.list.get_selected(), 1, ts)

    def bind_events(self):
        widgetUtils.connect_event(self.buffer.list.list, widgetUtils.KEYPRESS, self.get_event)
        widgetUtils.connect_event(self.buffer, widgetUtils.BUTTON_PRESSED, self.post_status, self.buffer.post)
        widgetUtils.connect_event(self.buffer, widgetUtils.BUTTON_PRESSED, self.destroy_status, self.buffer.dismiss)

    def fav(self):
        pass

    def unfav(self):
        pass

    def can_share(self):
        return False

    def destroy_status(self, *args, **kwargs):
        index = self.buffer.list.get_selected()
        item = self.session.db[self.name][index]
        items = self.session.db[self.name]
        try:
            self.session.api.notifications_dismiss(id=item.id)
            items.pop(index)
            self.buffer.list.remove_item(index)
            output.speak(_("Notification dismissed."))
        except Exception as e:
            self.session.sound.play("error.ogg")
        self.session.db[self.name] = items
