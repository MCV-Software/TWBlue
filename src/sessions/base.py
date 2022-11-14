# -*- coding: utf-8 -*-
""" A base class to be derived in possible new sessions for TWBlue and services."""
import os
import paths
import output
import time
import sound
import logging
import config_utils
import sqlitedict
import application
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
        # Config specification file.
        self.config_spec = "conf.defaults"
        # Session type.
        self.type = "base"

    @property
    def is_logged(self):
        return self.logged

    def get_configuration(self):
        """ Get settings for a session."""
        file_ = "%s/session.conf" % (self.session_id,)
        log.debug("Creating config file %s" % (file_,))
        self.settings = config_utils.load_config(os.path.join(paths.config_path(), file_), os.path.join(paths.app_path(), self.config_spec))
        self.init_sound()
        self.load_persistent_data()

    def get_name(self):
        pass


    def init_sound(self):
        try: self.sound = sound.soundSystem(self.settings["sound"])
        except: pass

    @_require_configuration
    def login(self, verify_credentials=True):
        pass

    @_require_configuration
    def authorise(self):
        pass

    def get_sized_buffer(self, buffer, size, reversed=False):
        """ Returns a list with the amount of items specified by size."""
        if isinstance(buffer, list) and size != -1 and len(buffer) > size:
            log.debug("Requesting {} items from a list of {} items. Reversed mode: {}".format(size, len(buffer), reversed))
            if reversed == True:
                return buffer[:size]
            else:
                return buffer[len(buffer)-size:]
        else:
            return buffer

    def save_persistent_data(self):
        """ Save the data to a persistent sqlite backed file. ."""
        dbname=os.path.join(paths.config_path(), str(self.session_id), "cache.db")
        log.debug("Saving storage information...")
        # persist_size set to 0 means not saving data actually.
        if self.settings["general"]["persist_size"] == 0:
            if os.path.exists(dbname):
                os.remove(dbname)
            return
        # Let's check if we need to create a new SqliteDict object (when loading db in memory) or we just need to call to commit in self (if reading from disk).db.
        # If we read from disk, we cannot modify the buffer size here as we could damage the app's integrity.
        # We will modify buffer's size (managed by persist_size) upon loading the db into memory in app startup.
        if self.settings["general"]["load_cache_in_memory"] and isinstance(self.db, dict):
            log.debug("Opening database to dump memory contents...")
            db=sqlitedict.SqliteDict(dbname, 'c')
            for k in self.db.keys():
                sized_buff = self.get_sized_buffer(self.db[k], self.settings["general"]["persist_size"], self.settings["general"]["reverse_timelines"])
                db[k] = sized_buff
            db.commit(blocking=True)
            db.close()
            log.debug("Data has been saved in the database.")
        else:
            try:
                log.debug("Syncing new data to disk...")
                if hasattr(self.db, "commit"):
                    self.db.commit()
            except:
                output.speak(_("An exception occurred while saving the {app} database. It will be deleted and rebuilt automatically. If this error persists, send the error log to the {app} developers.").format(app=application.name),True)
                log.exception("Exception while saving {}".format(dbname))
                os.remove(dbname)

    def load_persistent_data(self):
        """Import data from a database file from user config."""
        log.debug("Loading storage data...")
        dbname=os.path.join(paths.config_path(), str(self.session_id), "cache.db")
        # If persist_size is set to 0, we should remove the db file as we are no longer going to save anything.
        if self.settings["general"]["persist_size"] == 0:
            if os.path.exists(dbname):
                os.remove(dbname)
            # Let's return from here, as we are not loading anything.
            return
        # try to load the db file.
        try:
            log.debug("Opening database...")
            db=sqlitedict.SqliteDict(os.path.join(paths.config_path(), dbname), 'c')
            # If load_cache_in_memory is set to true, we will load the whole database into memory for faster access.
            # This is going to be faster when retrieving specific objects, at the cost of more memory.
            # Setting this to False will read the objects from database as they are needed, which might be slower for bigger datasets.
            if self.settings["general"]["load_cache_in_memory"]:
                log.debug("Loading database contents into memory...")
                for k in db.keys():
                    self.db[k] = db[k]
                db.commit(blocking=True)
                db.close()
                log.debug("Contents were loaded successfully.")
            else:
                log.debug("Instantiating database from disk.")
                self.db = db
                # We must make sure we won't load more than the amount of buffer specified.
                log.debug("Checking if we will load all content...")
                for k in self.db.keys():
                    sized_buffer = self.get_sized_buffer(self.db[k], self.settings["general"]["persist_size"], self.settings["general"]["reverse_timelines"])
                    self.db[k] = sized_buffer
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

