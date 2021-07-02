# -*- coding: utf-8 -*-
""" Common logic to all buffers in TWBlue."""
import logging
import config
import widgetUtils
from pubsub import pub
from wxUI import buffers
from . import base

log = logging.getLogger("controller.buffers.base.account")

class AccountBuffer(base.Buffer):
    def __init__(self, parent, name, account, account_id):
        super(AccountBuffer, self).__init__(parent, None, name)
        log.debug("Initializing buffer %s, account %s" % (name, account,))
        self.buffer = buffers.accountPanel(parent, name)
        self.type = self.buffer.type
        self.compose_function = None
        self.session = None
        self.needs_init = False
        self.account = account
        self.buffer.account = account
        self.name = name
        self.account_id = account_id

    def setup_account(self):
        widgetUtils.connect_event(self.buffer, widgetUtils.CHECKBOX, self.autostart, menuitem=self.buffer.autostart_account)
        if self.account_id in config.app["sessions"]["ignored_sessions"]:
            self.buffer.change_autostart(False)
        else:
            self.buffer.change_autostart(True)
        if not hasattr(self, "logged"):
            self.buffer.change_login(login=False)
            widgetUtils.connect_event(self.buffer.login, widgetUtils.BUTTON_PRESSED, self.logout)
        else:
            self.buffer.change_login(login=True)
            widgetUtils.connect_event(self.buffer.login, widgetUtils.BUTTON_PRESSED, self.login)

    def login(self, *args, **kwargs):
        del self.logged
        self.setup_account()
        pub.sendMessage("login", session_id=self.account_id)

    def logout(self, *args, **kwargs):
        self.logged = False
        self.setup_account()
        pub.sendMessage("logout", session_id=self.account_id)

    def autostart(self, *args, **kwargs):
        if self.account_id in config.app["sessions"]["ignored_sessions"]:
            self.buffer.change_autostart(True)
            config.app["sessions"]["ignored_sessions"].remove(self.account_id)
        else:
            self.buffer.change_autostart(False)
            config.app["sessions"]["ignored_sessions"].append(self.account_id)
        config.app.write()