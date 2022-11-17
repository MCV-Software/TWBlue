# -*- coding: cp1252 -*-
""" Lightweigth module that saves session position across global config and performs validation of config files. """
import os
import logging
import config
import paths
log = logging.getLogger("sessionmanager.manager")
from sessions import session_exceptions

manager = None
def setup():
    """ Creates the singleton instance used within TWBlue to access this object. """
    global manager
    if not manager:
        manager = sessionManager()

class sessionManager(object):

    def get_current_session(self):
        """ Returns the currently focused session, if valid. """
        if self.is_valid(config.app["sessions"]["current_session"]):
            return config.app["sessions"]["current_session"]

    def set_current_session(self, sessionID):
        config.app["sessions"]["current_session"] = sessionID
        config.app.write()

    def is_valid(self, id):
        if not os.path.exists(os.path.join(paths.config_path(), id)):
            raise session_exceptions.NonExistentSessionError("That session does not exist.")
            config.app["sessions"]["current_session"] = ""
            return False
        else:
            return True
