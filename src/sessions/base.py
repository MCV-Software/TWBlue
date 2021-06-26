# -*- coding: utf-8 -*-
""" A base class to be derived in possible new sessions for TWBlue and services."""
from __future__ import absolute_import
from __future__ import unicode_literals
from builtins import str
from builtins import object
import os
import paths
import output
import time
import sound
import logging
import config_utils
import sqlitedict
import application
import os
from . import session_exceptions as Exceptions
log = logging.getLogger("sessionmanager.session")


class baseSession(object):
    """ toDo: Decorators does not seem to be working when using them in an inherited class."""

    # Decorators.

    def _require_login(fn):
        """ Decorator for checking if the user is logged in.
        Some functions may need this to avoid making unneeded calls."""
        def f(self, *args, **kwargs):
            if self.logged == True:
                fn(self, *args, **kwargs)
            else:
                raise Exceptions.NotLoggedSessionError("You are not logged in yet.")
        return f

    def _require_configuration(fn):
        """ Check if the user has a configured session."""
        def f(self, *args, **kwargs):
            if self.settings != None:
                fn(self, *args, **kwargs)
            else:
                raise Exceptions.NotConfiguredSessionError("Not configured.")
        return f

    def __init__(self, session_id):
        """ session_id (str): The name of the folder inside the config directory where the session is located."""
        super(baseSession, self).__init__()
        self.session_id = session_id
        self.logged = False
        self.settings = None
        self.db={}

    @property
    def is_logged(self):
        return self.logged

    def get_configuration(self):
        """ Get settings for a session."""
        file_ = "%s/session.conf" % (self.session_id,)
        log.debug("Creating config file %s" % (file_,))
        self.settings = config_utils.load_config(os.path.join(paths.config_path(), file_), os.path.join(paths.app_path(), "Conf.defaults"))
        self.init_sound()
        self.load_persistent_data()

    def init_sound(self):
        try: self.sound = sound.soundSystem(self.settings["sound"])
        except: pass

    @_require_configuration
    def login(self, verify_credentials=True):
        pass

    @_require_configuration
    def authorise(self):
        pass

    def save_persistent_data(self):
        """ Save the data to a persistant sqlite backed file. ."""
        dbname=os.path.join(paths.config_path(), str(self.session_id), "cache.db")
        # persist_size set to 0 means not saving data actually.
        if self.settings["general"]["persist_size"] == 0:
            if os.path.exists(dbname):
                os.remove(dbname)
            return
        # Let's check if we need to create a new SqliteDict object or we just need to call to commit in self.db.
        if self.settings["general"]["load_cache_in_memory"]:
            db=sqlitedict.SqliteDict(dbname, 'c')
            for k in self.db.keys():
                db[k] = self.db[k]
            db.close()
        else:
            try:
                self.db.commit()
            except:
                output.speak(_("An exception occurred while saving the {app} database. It will be deleted and rebuilt automatically. If this error persists, send the error log to the {app} developers.").format(app=application.name),True)
                log.exception("Exception while saving {}".format(dbname))
                os.remove(dbname)

    def load_persistent_data(self):
        """Import data from a database file from user config."""
        dbname=os.path.join(paths.config_path(), str(self.session_id), "cache.db")
        # If persist_size is set to 0, we should remove the db file as we are no longer going to save anything.
        if self.settings["general"]["persist_size"] == 0:
            if os.path.exists(dbname):
                os.remove(dbname)
            # Let's return from here, as we are not loading anything.
            return
        # try to load the db file.
        try:
            db=sqlitedict.SqliteDict(os.path.join(paths.config_path(), dbname), 'c')
            # If load_cache_in_memory is set to true, we will load the whole database into memory for faster access.
            # This is going to be faster when retrieving specific objects, at the cost of more memory.
            # Setting this to False will read the objects from database as they are needed, which might be slower for bigger datasets.
            if self.settings["general"]["load_cache_in_memory"]:
                for k in db.keys():
                    self.db[k] = db[k]
                db.close()
            else:
                self.db = db
            if self.db.get("cursors") == None:
                cursors = dict(direct_messages=-1)
                self.db["cursors"] = cursors
        except:
            output.speak(_("An exception occurred while loading the {app} database. It will be deleted and rebuilt automatically. If this error persists, send the error log to the {app} developers.").format(app=application.name), True)
            log.exception("Exception while loading {}".format(dbname))
            try: 
                os.remove(dbname)
            except:
                pass

