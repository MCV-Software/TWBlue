# -*- coding: utf-8 -*-
import application
import update
import platform
from wxUpdater import *
from requests.exceptions import ConnectionError

def do_update():
	try:
		return update.perform_update(endpoint=application.update_url, current_version=application.version, app_name=application.name, update_available_callback=available_update_dialog, progress_callback=progress_callback, update_complete_callback=update_finished)
	except ConnectionError:
		pass