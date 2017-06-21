# -*- coding: utf-8 -*-

import application
from . import update
import platform
import logging
import output
from requests.exceptions import ConnectionError
from .wxUpdater import *
logger = logging.getLogger("updater")

def do_update(endpoint=application.update_url):
 try:
  update.perform_update(endpoint=endpoint, current_version=application.version, app_name=application.name, update_available_callback=available_update_dialog, progress_callback=progress_callback, update_complete_callback=update_finished)
 except:
  if endpoint == application.update_url:
   logger.error("Update failed! Using mirror URL...")
   return do_update(endpoint=application.mirror_update_url)
  else:
   logger.exception("Update failed.")
   output.speak("An exception occurred while attempting to update " + application.name + ". If this message persists, contact the " + application.name + " developers. More information about the exception has been written to the error log.",True)