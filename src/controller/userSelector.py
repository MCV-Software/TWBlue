# -*- coding: utf-8 -*-
""" Small utility dessigned to select users from the currently focused item or the autocomplete database. """
import wx
import widgetUtils
from wxUI.dialogs import utils
from extra.autocompletionUsers import completion

class userSelector(object):

    def __init__(self, users, session_id, title=_("Select user")):
        """ Creates a dialog that chooses an user selector, from where users who have the autocomplete database already filled can also use that feature.

        :param users: lists of users extracted from the currently focused item.
        :type users: list
        :param session_id: ID of the session to instantiate autocomplete database.
        :type session_id: str
        :param title: Title of the user selector dialog.
        :type title: str
        """
        self.session_id = session_id
        self.dlg = utils.selectUserDialog(users=users, title=title)
        widgetUtils.connect_event(self.dlg.autocompletion, widgetUtils.BUTTON_PRESSED, self.on_autocomplete_users)

    def on_autocomplete_users(self, *args, **kwargs):
        """ performs user autocompletion, if configured properly. """
        c = completion.autocompletionUsers(self.dlg, self.session_id)
        c.show_menu("dm")

    def get_user(self):
        """ Actually shows the dialog and returns an user if the dialog was accepted, None otherwise.

        :rtype: str or None
        """
        if self.dlg.ShowModal() == wx.ID_OK:
            user = self.dlg.get_user()
        else:
            user = None
        self.dlg.Destroy()
        return user
