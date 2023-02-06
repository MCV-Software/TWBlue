# -*- coding: utf-8 -*-
import wx
import sys
import application
from . import utils

progress_dialog = None

def available_update_dialog(version, description, date):
    if "3.7" not in sys.version: # Modern operating systems
        update_msg = _("There's a new %s version available, released on %s. Would you like to download it now?\n\n %s version: %s\n\nChanges:\n%s") % (application.name, date, application.name, version, description)
        styles = wx.YES|wx.NO|wx.ICON_WARNING
    else:
        update_msg = _("There's a new %s version available, released on %s. Updates are not automatic in Windows 7, so you would need to visit TWBlue's download website to get the latest version.\n\n %s version: %s\n\nChanges:\n%s") % (application.name, date, application.name, version, description)
        styles = wx.OK|wx.ICON_WARNING
    dialog = wx.MessageDialog(None, update_msg, _("New version for %s") % application.name, style=styles)
    if dialog.ShowModal() == wx.ID_YES:
        return True
    else:
        return False

def create_progress_dialog():
    return wx.ProgressDialog(_(u"Download in Progress"), _(u"Downloading the new version..."),  parent=None, maximum=100)

def progress_callback(total_downloaded, total_size):
    global progress_dialog
    if progress_dialog == None:
        progress_dialog = create_progress_dialog()
        progress_dialog.Show()
    if total_downloaded == total_size:
        progress_dialog.Destroy()
    else:
        progress_dialog.Update(int((total_downloaded*100)/total_size), _(u"Updating... %s of %s") % (str(utils.convert_bytes(total_downloaded)), str(utils.convert_bytes(total_size))))

def update_finished():
    ms = wx.MessageDialog(None, _(u"The update has been downloaded and installed successfully. Press OK to continue."), _(u"Done!")).ShowModal()
