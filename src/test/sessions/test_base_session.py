# -*- coding: utf-8 -*-
import sys
import types
import pytest
import os
import sqlitedict
import shutil
from unittest import mock

# Mock sound module, so LibVLc won't complain.
sound_module = types.ModuleType("sound")
sys.modules["sound"] = sound_module
sound_module.soundManager = mock.MagicMock(name="sound.soundManager")
from sessions import base

# path where we will save our test config, as we can't rely on paths module due to pytest's paths being different.
session_path = os.path.join(os.getcwd(), "config", "testing")

@pytest.fixture
def session():
    """ Configures a fake base session from where we can test things. """
    global session_path
    s = base.baseSession("testing")
    if os.path.exists(session_path) == False:
        os.mkdir(session_path)
    # Patches paths.app_path and paths.config_path, so we will not have issues during session configuration.
    with mock.patch("paths.app_path", return_value=os.getcwd()) as app_path:
        with mock.patch("paths.config_path", return_value=os.path.join(os.getcwd(), "config")) as config_path:
            s.get_configuration()
            yield s
            # Session's cleanup code.
            if os.path.exists(session_path):
                shutil.rmtree(session_path)
            del s

@pytest.fixture
def dataset():
    """ Generates a sample dataset"""
    dataset = dict(home_timeline=["message" for i in range(10000)], mentions_timeline=["mention" for i in range(20000)])
    yield dataset

### Testing database being read from disk.
def test_cache_in_disk_unlimited_size(session, dataset):
    """ Tests cache database being read from disk, storing the whole datasets. """
    session.settings["general"]["load_cache_in_memory"] = False
    session.settings["general"]["persist_size"] = -1
    session.load_persistent_data()
    session.db["home_timeline"] = dataset["home_timeline"]
    session.db["mentions_timeline"] = dataset["mentions_timeline"]
    session.save_persistent_data()
    assert isinstance(session.db, sqlitedict.SqliteDict)
    assert session.db.get("home_timeline") != None
    assert session.db.get("mentions_timeline") != None
    assert len(session.db.get("home_timeline")) == 10000
    assert len(session.db.get("mentions_timeline")) == 20000
    session.db.close()

def test_cache_in_disk_limited_dataset(session, dataset):
    """ Tests wether the cache stores only the amount of items we ask it to store. """
    session.settings["general"]["load_cache_in_memory"] = False
    session.settings["general"]["persist_size"] = 100
    session.load_persistent_data()
    session.db["home_timeline"] = dataset["home_timeline"]
    session.db["mentions_timeline"] = dataset["mentions_timeline"]
    # We need to save and load the db again because we cannot modify buffers' size while the database is opened.
    # As TWBlue reads directly from db when reading from disk, an attempt to modify buffers size while Blue is reading the db
    # Might cause an out of sync error between the GUI lists and the database.
    # So we perform the changes to buffer size when loading data during app startup if the DB is read from disk.
    session.save_persistent_data()
    session.db = dict()
    session.load_persistent_data()
    assert isinstance(session.db, sqlitedict.SqliteDict)
    assert session.db.get("home_timeline") != None
    assert session.db.get("mentions_timeline") != None
    assert len(session.db.get("home_timeline")) == 100
    assert len(session.db.get("mentions_timeline")) == 100
    session.db.close()

def test_cache_in_disk_limited_dataset_unreversed(session):
    """Test if the cache is saved properly in unreversed buffers, when newest items are at the end of the list. """
    dataset = dict(home_timeline=[i for i in range(20)], mentions_timeline=[i for i in range(20)])
    session.settings["general"]["load_cache_in_memory"] = False
    session.settings["general"]["persist_size"] = 10
    session.load_persistent_data()
    session.db["home_timeline"] = dataset["home_timeline"]
    session.db["mentions_timeline"] = dataset["mentions_timeline"]
    # We need to save and load the db again because we cannot modify buffers' size while the database is opened.
    # As TWBlue reads directly from db when reading from disk, an attempt to modify buffers size while Blue is reading the db
    # Might cause an out of sync error between the GUI lists and the database.
    # So we perform the changes to buffer size when loading data during app startup if the DB is read from disk.
    session.save_persistent_data()
    session.db = dict()
    session.load_persistent_data()
    assert isinstance(session.db, sqlitedict.SqliteDict)
    assert session.db.get("home_timeline") != None
    assert session.db.get("mentions_timeline") != None
    assert session.db.get("home_timeline")[0] == 10
    assert session.db.get("mentions_timeline")[0] == 10
    assert session.db.get("home_timeline")[-1] == 19
    assert session.db.get("mentions_timeline")[-1] == 19
    session.db.close()

def test_cache_in_disk_limited_dataset_reversed(session):
    """Test if the cache is saved properly in reversed buffers, when newest items are at the start of the list. """
    dataset = dict(home_timeline=[i for i in range(19, -1, -1)], mentions_timeline=[i for i in range(19, -1, -1)])
    session.settings["general"]["load_cache_in_memory"] = False
    session.settings["general"]["persist_size"] = 10
    session.settings["general"]["reverse_timelines"] = True
    session.load_persistent_data()
    session.db["home_timeline"] = dataset["home_timeline"]
    session.db["mentions_timeline"] = dataset["mentions_timeline"]
    # We need to save and load the db again because we cannot modify buffers' size while the database is opened.
    # As TWBlue reads directly from db when reading from disk, an attempt to modify buffers size while Blue is reading the db
    # Might cause an out of sync error between the GUI lists and the database.
    # So we perform the changes to buffer size when loading data during app startup if the DB is read from disk.
    session.save_persistent_data()
    session.db = dict()
    session.load_persistent_data()
    assert isinstance(session.db, sqlitedict.SqliteDict)
    assert session.db.get("home_timeline") != None
    assert session.db.get("mentions_timeline") != None
    assert session.db.get("home_timeline")[0] == 19
    assert session.db.get("mentions_timeline")[0] == 19
    assert session.db.get("home_timeline")[-1] == 10
    assert session.db.get("mentions_timeline")[-1] == 10
    session.db.close()

### Testing database being loaded into memory. Those tests should give the same results than before
### but as we have different code depending whether we load db into memory or read it from disk,
### We need to test this anyways.
def test_cache_in_memory_unlimited_size(session, dataset):
    """ Tests cache database being loaded in memory, storing the whole datasets. """
    session.settings["general"]["load_cache_in_memory"] = True
    session.settings["general"]["persist_size"] = -1
    session.load_persistent_data()
    session.db["home_timeline"] = dataset["home_timeline"]
    session.db["mentions_timeline"] = dataset["mentions_timeline"]
    session.save_persistent_data()
    session.db = dict()
    session.load_persistent_data()
    assert isinstance(session.db, dict)
    assert session.db.get("home_timeline") != None
    assert session.db.get("mentions_timeline") != None
    assert len(session.db.get("home_timeline")) == 10000
    assert len(session.db.get("mentions_timeline")) == 20000

def test_cache_in_memory_limited_dataset(session, dataset):
    """ Tests wether the cache stores only the amount of items we ask it to store, when loaded in memory. """
    session.settings["general"]["load_cache_in_memory"] = True
    session.settings["general"]["persist_size"] = 100
    session.load_persistent_data()
    session.db["home_timeline"] = dataset["home_timeline"]
    session.db["mentions_timeline"] = dataset["mentions_timeline"]
    session.save_persistent_data()
    session.db = dict()
    session.load_persistent_data()
    assert isinstance(session.db, dict)
    assert session.db.get("home_timeline") != None
    assert session.db.get("mentions_timeline") != None
    assert len(session.db.get("home_timeline")) == 100
    assert len(session.db.get("mentions_timeline")) == 100

def test_cache_in_memory_limited_dataset_unreversed(session):
    """Test if the cache is saved properly when loaded in memory in unreversed buffers, when newest items are at the end of the list. """
    dataset = dict(home_timeline=[i for i in range(20)], mentions_timeline=[i for i in range(20)])
    session.settings["general"]["load_cache_in_memory"] = True
    session.settings["general"]["persist_size"] = 10
    session.load_persistent_data()
    assert len(session.db)==1
    session.db["home_timeline"] = dataset["home_timeline"]
    session.db["mentions_timeline"] = dataset["mentions_timeline"]
    session.save_persistent_data()
    session.db = dict()
    session.load_persistent_data()
    assert isinstance(session.db, dict)
    assert session.db.get("home_timeline") != None
    assert session.db.get("mentions_timeline") != None
    assert session.db.get("home_timeline")[0] == 10
    assert session.db.get("mentions_timeline")[0] == 10
    assert session.db.get("home_timeline")[-1] == 19
    assert session.db.get("mentions_timeline")[-1] == 19

def test_cache_in_memory_limited_dataset_reversed(session):
    """Test if the cache is saved properly in reversed buffers, when newest items are at the start of the list. This test if for db read into memory. """
    dataset = dict(home_timeline=[i for i in range(19, -1, -1)], mentions_timeline=[i for i in range(19, -1, -1)])
    session.settings["general"]["load_cache_in_memory"] = True
    session.settings["general"]["persist_size"] = 10
    session.settings["general"]["reverse_timelines"] = True
    session.load_persistent_data()
    session.db["home_timeline"] = dataset["home_timeline"]
    session.db["mentions_timeline"] = dataset["mentions_timeline"]
    session.save_persistent_data()
    session.db = dict()
    session.load_persistent_data()
    assert isinstance(session.db, dict)
    assert session.db.get("home_timeline") != None
    assert session.db.get("mentions_timeline") != None
    assert session.db.get("home_timeline")[0] == 19
    assert session.db.get("mentions_timeline")[0] == 19
    assert session.db.get("home_timeline")[-1] == 10
    assert session.db.get("mentions_timeline")[-1] == 10
