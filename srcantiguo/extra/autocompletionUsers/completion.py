# -*- coding: utf-8 -*-
""" Module to display the user autocompletion menu in post dialogs. """
import output
from . import storage
from . import wx_menu

class autocompletionUsers(object):
    def __init__(self, window, session_id):
        """ Class constructor. Displays a menu with users matching the specified pattern for autocompletion.

        :param window: A wx control where the menu should be displayed. Normally this is going to be the wx.TextCtrl indicating the tweet's text or direct message recipient.
        :type window: wx.Dialog
        :param session_id: Session ID which calls this class. We will load the users database from this session.
        :type session_id: str.
        """
        super(autocompletionUsers, self).__init__()
        self.window = window
        self.db = storage.storage(session_id)

    def show_menu(self, mode="mastodon"):
        """ displays a menu with possible users matching the specified pattern.

        this menu can be displayed in dialogs where an username is expected. For Mastodon's post dialogs, the string should start with an at symbol (@), otherwise it won't match the pattern.

        Of course, users must be already loaded in database before attempting this.

        If no users are found, an error message will be spoken.

        :param mode: this controls how the dialog will behave. Possible values are 'mastodon' and 'free'. In mastodon mode, the matching pattern will be @user (@ is required), while in 'free' mode the matching pattern will be anything written in the text control.
        :type mode: str
        """
        if mode == "mastodon":
            position = self.window.text.GetInsertionPoint()
            text = self.window.text.GetValue()
            text = text[:position]
            try:
                pattern = text.split()[-1]
            except IndexError:
                output.speak(_(u"You have to start writing"))
                return
            if pattern.startswith("@") == True:
                menu = wx_menu.menu(self.window.text, pattern[1:], mode=mode)
                users = self.db.get_users(pattern[1:])
                if len(users) > 0:
                    menu.append_options(users)
                    self.window.PopupMenu(menu, self.window.text.GetPosition())
                    menu.destroy()
                else:
                    output.speak(_(u"There are no results in your users database"))
            else:
                output.speak(_(u"Autocompletion only works for users."))
        elif mode == "free":
            text = self.window.cb.GetValue()
            try:
                pattern = text.split()[-1]
            except IndexError:
                output.speak(_(u"You have to start writing"))
                return
            menu = wx_menu.menu(self.window.cb, pattern, mode=mode)
            users = self.db.get_users(pattern)
            if len(users) > 0:
                menu.append_options(users)
                self.window.PopupMenu(menu, self.window.cb.GetPosition())
                menu.destroy()
            else:
                output.speak(_(u"There are no results in your users database"))
