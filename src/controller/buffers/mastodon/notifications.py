# -*- coding: utf-8 -*-
import time
import logging
import widgetUtils
import output
from pubsub import pub
from controller.buffers.mastodon.base import BaseBuffer
from controller.mastodon import messages
from sessions.mastodon import compose, templates
from wxUI import buffers
from wxUI.dialogs.mastodon import dialogs as mastodon_dialogs
from wxUI.dialogs.mastodon import menus
from mysc.thread_utils import call_threaded

log = logging.getLogger("controller.buffers.mastodon.notifications")

class NotificationsBuffer(BaseBuffer):

    def __init__(self, *args, **kwargs):
        super(NotificationsBuffer, self).__init__(*args, **kwargs)
        self.type = "notificationsBuffer"

    def get_message(self):
        notification = self.get_item()
        if notification == None:
            return
        template = self.session.settings["templates"]["notification"]
        post_template = self.session.settings["templates"]["post"]
        t = templates.render_notification(notification, template, post_template, self.session.settings, relative_times=self.session.settings["general"]["relative_times"], offset_hours=self.session.db["utc_offset"])
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

    def vote(self):
        pass

    def can_share(self, *args, **kwargs):
        if self.is_post():
            item = self.get_item()
            return super(NotificationsBuffer, self).can_share(item=item.status)
        return False

    def add_to_favorites(self):
        if self.is_post():
            item = self.get_item()
            super(NotificationsBuffer, self).add_to_favorites(item=item.status)

    def remove_from_favorites(self):
        if self.is_post():
            item = self.get_item()
            super(NotificationsBuffer, self).remove_from_favorites(item=item.status)

    def toggle_favorite(self, *args, **kwargs):
        if self.is_post():
            item = self.get_item()
            super(NotificationsBuffer, self).toggle_favorite(item=item.status)

    def toggle_bookmark(self, *args, **kwargs):
        if self.is_post():
            item = self.get_item()
            super(NotificationsBuffer, self).toggle_bookmark(item=item.status)

    def reply(self, *args, **kwargs):
        if self.is_post():
            item = self.get_item()
            super(NotificationsBuffer, self).reply(item=item.status)

    def share_item(self, *args, **kwargs):
        if self.is_post():
            item = self.get_item()
            super(NotificationsBuffer, self).share_item(item=item.status)

    def url(self, *args, **kwargs):
        if self.is_post():
            item = self.get_item()
            super(NotificationsBuffer, self).url(item=item.status, *args, **kwargs)

    def audio(self, *args, **kwargs):
        if self.is_post():
            item = self.get_item()
            super(NotificationsBuffer, self).audio(item=item.status)

    def view_item(self, *args, **kwargs):
        if self.is_post():
            item = self.get_item()
            super(NotificationsBuffer, self).view_item(item=item.status)
        else:
            pub.sendMessage("execute-action", action="user_details")

    def open_in_browser(self, *args, **kwargs):
        if self.is_post():
            item = self.get_item()
            super(NotificationsBuffer, self).open_in_browser(item=item.status)

    def send_message(self, *args, **kwargs):
        if self.is_post():
            item = self.get_item()
            super(NotificationsBuffer, self).send_message(item=item.status)
        else:
            item = self.get_item()
            title = _("New conversation with {}").format(item.account.username)
            caption = _("Write your message here")
            users_str = "@{} ".format(item.account.acct)
            post = messages.post(session=self.session, title=title, caption=caption, text=users_str)
            post.message.visibility.SetSelection(3)
            response = post.message.ShowModal()
            if response == wx.ID_OK:
                post_data = post.get_data()
                call_threaded(self.session.send_post, posts=post_data, visibility="direct")
            if hasattr(post.message, "destroy"):
                post.message.destroy()

    def is_post(self):
        post_types = ["status", "mention", "reblog", "favourite", "update", "poll"]
        item = self.get_item()
        if item.type in post_types:
            return True
        return False

    def destroy_status(self, *args, **kwargs):
        index = self.buffer.list.get_selected()
        item = self.session.db[self.name][index]
        answer = mastodon_dialogs.delete_notification_dialog()
        if answer == False:
            return
        items = self.session.db[self.name]
        try:
            self.session.api.notifications_dismiss(id=item.id)
            items.pop(index)
            self.buffer.list.remove_item(index)
            output.speak(_("Notification dismissed."))
        except Exception as e:
            self.session.sound.play("error.ogg")
            log.exception("")
        self.session.db[self.name] = items

    def show_menu(self, ev, pos=0, *args, **kwargs):
        if self.buffer.list.get_count() == 0:
            return
        notification = self.get_item()
        menu = menus.notification(notification.type)
        if self.is_post():
            widgetUtils.connect_event(menu, widgetUtils.MENU, self.reply, menuitem=menu.reply)
            widgetUtils.connect_event(menu, widgetUtils.MENU, self.user_actions, menuitem=menu.userActions)
            if self.can_share() == True:
                widgetUtils.connect_event(menu, widgetUtils.MENU, self.share_item, menuitem=menu.boost)
            else:
                menu.boost.Enable(False)
            widgetUtils.connect_event(menu, widgetUtils.MENU, self.fav, menuitem=menu.fav)
            widgetUtils.connect_event(menu, widgetUtils.MENU, self.unfav, menuitem=menu.unfav)
            widgetUtils.connect_event(menu, widgetUtils.MENU, self.url_, menuitem=menu.openUrl)
            widgetUtils.connect_event(menu, widgetUtils.MENU, self.audio, menuitem=menu.play)
        widgetUtils.connect_event(menu, widgetUtils.MENU, self.view, menuitem=menu.view)
        widgetUtils.connect_event(menu, widgetUtils.MENU, self.copy, menuitem=menu.copy)
        widgetUtils.connect_event(menu, widgetUtils.MENU, self.destroy_status, menuitem=menu.remove)
        if hasattr(menu, "openInBrowser"):
            widgetUtils.connect_event(menu, widgetUtils.MENU, self.open_in_browser, menuitem=menu.openInBrowser)
        if pos != 0:
            self.buffer.PopupMenu(menu, pos)
        else:
            self.buffer.PopupMenu(menu, self.buffer.list.list.GetPosition())