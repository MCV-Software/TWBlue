# -*- coding: utf-8 -*-
import application
from . import update
import logging
import output
from requests.exceptions import ConnectionError
from .wxUpdater import *
logger = logging.getLogger("updater")

def do_update(endpoint=application.update_url):
    if not getattr(sys, 'frozen', False):
        logger.debug("Running from source, aborting update check")
        return False
    try:
        result = update.perform_update(endpoint=endpoint, current_version=application.version, app_name=application.name, update_available_callback=available_update_dialog, progress_callback=progress_callback, update_complete_callback=update_finished)
        return result
    except:
        logger.exception("Update failed.")
        output.speak("An exception occurred while attempting to update " + application.name + ". If this message persists, contact the " + application.name + " developers. More information about the exception has been written to the error log.",True)
        return None
