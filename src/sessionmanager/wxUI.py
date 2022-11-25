# -*- coding: utf-8 -*-
""" Base GUI (Wx) class for the Session manager module."""
import wx
from pubsub import pub
from multiplatform_widgets import widgets

class sessionManagerWindow(wx.Dialog):
    """ Dialog that displays all session managing capabilities to users. """
    def __init__(self):
        super(sessionManagerWindow, self).__init__(parent=None, title=_(u"Session manager"), size=wx.DefaultSize)
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(panel, -1, _(u"Accounts list"), size=wx.DefaultSize)
        listSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.list = widgets.list(panel, _(u"Account"), style=wx.LC_SINGLE_SEL|wx.LC_REPORT)
        listSizer.Add(label, 0, wx.ALL, 5)
        listSizer.Add(self.list.list, 0, wx.ALL, 5)
        sizer.Add(listSizer, 0, wx.ALL, 5)
        self.new = wx.Button(panel, -1, _(u"New account"), size=wx.DefaultSize)
        self.new.Bind(wx.EVT_BUTTON, self.on_new_account)
        self.remove = wx.Button(panel, -1, _(u"Remove account"))
        self.remove.Bind(wx.EVT_BUTTON, self.on_remove)
        self.configuration = wx.Button(panel, -1, _(u"Global Settings"))
        self.configuration.Bind(wx.EVT_BUTTON, self.on_configuration)
        ok = wx.Button(panel, wx.ID_OK, size=wx.DefaultSize)
        ok.SetDefault()
        cancel = wx.Button(panel, wx.ID_CANCEL, size=wx.DefaultSize)
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        buttons.Add(self.new, 0, wx.ALL, 5)
        buttons.Add(self.configuration, 0, wx.ALL, 5)
        buttons.Add(ok, 0, wx.ALL, 5)
        buttons.Add(cancel, 0, wx.ALL, 5)
        sizer.Add(buttons, 0, wx.ALL, 5)
        panel.SetSizer(sizer)
        min = sizer.CalcMin()
        self.SetClientSize(min)

    def fill_list(self, sessionsList):
        for i in sessionsList:
            self.list.insert_item(False, i)
        if self.list.get_count() > 0:
            self.list.select_item(0)
        self.list.list.SetSize(self.list.list.GetBestSize())

    def ok(self, ev):
        if self.list.get_count() == 0:
            wx.MessageDialog(None, _(u"You need to configure an account."), _(u"Account Error"), wx.ICON_ERROR).ShowModal()
            return
        self.EndModal(wx.ID_OK)

    def on_new_account(self, *args, **kwargs):
        menu = wx.Menu()
        twitter = menu.Append(wx.ID_ANY, _("Twitter"))
        mastodon = menu.Append(wx.ID_ANY, _("Mastodon"))
        menu.Bind(wx.EVT_MENU, self.on_new_twitter_account, twitter)
        menu.Bind(wx.EVT_MENU, self.on_new_mastodon_account, mastodon)
        self.PopupMenu(menu, self.new.GetPosition())

    def on_new_mastodon_account(self, *args, **kwargs):
        dlg =  wx.MessageDialog(self, _("You will be prompted for your Mastodon data (instance URL, email address and password) so we can authorise TWBlue in your instance. Would you like to authorise your account now?"), _(u"Authorization"), wx.YES_NO)
        response = dlg.ShowModal()
        dlg.Destroy()
        if response == wx.ID_YES:
            pub.sendMessage("sessionmanager.new_account", type="mastodon")

    def on_new_twitter_account(self, *args, **kwargs):
        dlg = wx.MessageDialog(self, _(u"The request to authorize your Twitter account will be opened in your browser. You only need to do this once. Would you like to continue?"), _(u"Authorization"), wx.YES_NO)
        response = dlg.ShowModal()
        dlg.Destroy()
        if response == wx.ID_YES:
            pub.sendMessage("sessionmanager.new_account", type="twitter")

    def add_new_session_to_list(self):
        total = self.list.get_count()
        name = _(u"Authorized account %d") % (total+1)
        self.list.insert_item(False, name)
        if self.list.get_count() == 1:
            self.list.select_item(0)

    def show_unauthorised_error(self):
        wx.MessageDialog(None, _(u"Your access token is invalid or the authorization has failed. Please try again."), _(u"Invalid user token"), wx.ICON_ERROR).ShowModal()

    def get_response(self):
        return self.ShowModal()

    def on_remove(self, *args, **kwargs):
        dlg = wx.MessageDialog(self, _(u"Do you really want to delete this account?"), _(u"Remove account"), wx.YES_NO)
        response = dlg.ShowModal()
        dlg.Destroy()
        if response == wx.ID_YES:
            selected = self.list.get_selected()
            pub.sendMessage("sessionmanager.remove_account", index=selected)

    def on_configuration(self, *args, **kwargs):
        pub.sendMessage("sessionmanager.configuration")

    def get_selected(self):
        return self.list.get_selected()

    def remove_session(self, sessionID):
        self.list.remove_item(sessionID)


    def hide_configuration(self):
        self.configuration.Hide()

    def destroy(self):
        self.Destroy()

def auth_error(user_name):
    return wx.MessageDialog(None, _("TWBlue is unable to authenticate the account for {} in Twitter. It might be due to an invalid or expired token, revoqued access to the application, or after an account reactivation. Please remove the account manually from your Twitter sessions in order to stop seeing this message.").format(user_name,), _("Authentication error for session {}").format(user_name,), wx.OK).ShowModal()
