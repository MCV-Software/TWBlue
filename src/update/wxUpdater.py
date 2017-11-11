# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from builtins import str
from past.utils import old_div
import wx
import application
from . import utils

progress_dialog = None

def available_update_dialog(version, description, date):
	dialog = wx.MessageDialog(None, _(u"There's a new %s version available, released on %s. Would you like to download it now?\n\n %s version: %s\n\nChanges:\n%s") % (application.name, date, application.name, version, description), _(u"New version for %s") % application.name, style=wx.YES|wx.NO|wx.ICON_WARNING)
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
		progress_dialog.Update(old_div((total_downloaded*100),total_size), _(u"Updating... %s of %s") % (str(utils.convert_bytes(total_downloaded)), str(utils.convert_bytes(total_size))))

def update_finished():
	ms = wx.MessageDialog(None, _(u"The update has been downloaded and installed successfully. Press OK to continue."), _(u"Done!")).ShowModal()