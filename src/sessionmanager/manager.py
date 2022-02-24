# -*- coding: cp1252 -*-
import config
import paths
import os
import logging
log = logging.getLogger("sessionmanager.manager")
from sessions import session_exceptions

manager = None
def setup():
    global manager
    if not manager:
        manager = sessionManager()

class sessionManager(object):

    def get_current_session(self):
        if self.is_valid(config.app["sessions"]["current_session"]):
            return config.app["sessions"]["current_session"]
        else:
            return False

    def add_session(self, id):
        log.debug("Adding a new session: %s" % (id,))
        path = os.path.join(paths.config_path(), id)
        if not os.path.exists(path):
            log.debug("Creating %s path" % (os.path.join(paths.config_path(), path),))
            os.mkdir(path)
            config.app["sessions"]["sessions"].append(id)

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
