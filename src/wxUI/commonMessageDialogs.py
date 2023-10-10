# -*- coding: utf-8 -*-
import wx
import application

def exit_dialog(parent):
    dlg = wx.MessageDialog(parent, _(u"Do you really want to close {0}?").format(application.name,), _(u"Exit"), wx.YES_NO|wx.ICON_QUESTION)
    return dlg.ShowModal()

def needs_restart():
    wx.MessageDialog(None, _(u" {0} must be restarted for these changes to take effect.").format(application.name,), _("Restart {0} ").format(application.name,), wx.OK).ShowModal()

def delete_user_from_db():
    return wx.MessageDialog(None, _(u"Are you sure you want to delete this user from the database? This user will not appear in autocomplete results anymore."), _(u"Confirm"), wx.YES_NO|wx.ICON_QUESTION).ShowModal()

def clear_list():
    dlg = wx.MessageDialog(None, _(u"Do you really want to empty this buffer? It's  items will be removed from the list but not from Twitter"), _(u"Empty buffer"), wx.ICON_QUESTION|wx.YES_NO)
    return dlg.ShowModal()

def remove_buffer():
    return wx.MessageDialog(None, _(u"Do you really want to destroy this buffer?"), _(u"Attention"), style=wx.ICON_QUESTION|wx.YES_NO).ShowModal()

def user_not_exist():
    return wx.MessageDialog(None, _(u"That user does not exist"), _(u"Error"), wx.ICON_ERROR).ShowModal()

def timeline_exist():
    return wx.MessageDialog(None, _(u"A timeline for this user already exists. You can't open another"), _(u"Existing timeline"), wx.ICON_ERROR).ShowModal()

def donation():
    dlg = wx.MessageDialog(None, _(u"If you like {0} we need your help to keep it going. Help us by donating to the project. This will help us pay for the server, the domain and some other things to ensure that {0} will be actively maintained. Your donation will give us the means to continue the development of {0}, and to keep {0} free. Would you like to donate now?").format(application.name), _(u"We need your help"), wx.ICON_QUESTION|wx.YES_NO)
    return dlg.ShowModal()

def changed_keymap():
    return wx.MessageDialog(None, _(u"TWBlue has detected that you're running windows 10 and has changed the default keymap to the Windows 10 keymap. It means that some keyboard shorcuts could be different. Please check the keystroke editor by pressing Alt+Win+K to see all available keystrokes for this keymap."), _(u"Information"), wx.OK).ShowModal()

def invalid_configuration():
    return wx.MessageDialog(None, _("The configuration file is invalid."), _("Error"), wx.ICON_ERROR).ShowModal()

def dead_pid():
    return wx.MessageDialog(None, _(u"{0} quit unexpectedly the last time it was run. If the problem persists, please report it to the {0} developers.").format(application.name), _(u"Warning"), wx.OK).ShowModal()

def cant_update_source() -> wx.MessageDialog:
    """Shows a dialog telling a user he /she can't update because he / she is
    running from source
    """
    dlg = wx.MessageDialog(None, _("Sorry, you can't update while running {} from source.").format(application.name), _("Error"), wx.OK)
    return dlg.ShowModal()
