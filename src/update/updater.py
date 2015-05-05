# -*- coding: utf-8 -*-
import application
import update
import platform
from wxUpdater import *
import logging
import output
logger = logging.getLogger("updater")

def do_update():
    try:
        return update.perform_update(endpoint=application.update_url, current_version=application.version, app_name=application.name, update_available_callback=available_update_dialog, progress_callback=progress_callback, update_complete_callback=update_finished)
    except:
        logger.exception("Update failed.")
        output.speak("An exception occurred while attempting to update " + application.name + ". If this message persists, contact the " + application.name + " developers. More information about the exception has been written to the error log.",True)