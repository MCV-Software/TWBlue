# -*- coding: utf-8 -*-
import os, sys, wx
from mysc import paths
import application, updater
from mysc.thread_utils import call_threaded
import logging as original_logger
log = original_logger.getLogger("update_manager")

def check_for_update(msg=False):
 log.debug(u"Checking for updates...")
 url = updater.find_update_url(application.update_url, application.version)
 if url is None:
  if msg == True:
   wx.MessageDialog(None, _(u"Your TW Blue version is up to date"), _(u"Update"), style=wx.OK).ShowModal()
  return
 else:
  log.debug(u"New version from %s " % url)
  new_path = os.path.join(paths.app_path("delete-me"), 'updates', 'update.zip')
  log.debug(u"Descargando actualización en %s" % new_path)
  d = wx.MessageDialog(None, _(u"There's a new TW Blue version available. Would you like to download it now?"), _(u"New version for %s") % application.name, style=wx.YES|wx.NO|wx.ICON_WARNING)
  if d.ShowModal() == wx.ID_YES:
   progress = wx.ProgressDialog(_(u"Download in Progress"), _(u"Downloading the new version..."),  parent=None, maximum=100,                                style = wx.PD_APP_MODAL)
   def update(percent):
    if percent == 100:
     progress.Destroy()
    else:
     progress.Update(percent, _(u"Update"))
   def update_complete():
    wx.MessageDialog(None, _(u"The new TW Blue version has been downloaded and installed. Press OK to start the application."), _(u"Done!")).ShowModal()
    sys.exit()
   app_updater = updater.AutoUpdater(url, new_path, 'bootstrap.exe', app_path=paths.app_path(), postexecute=paths.app_path("TWBlue.exe"), finish_callback=update_complete, percentage_callback=update)
   app_updater.start_update()
   progress.ShowModal()
  else:
   return

