# -*- coding: utf-8 -*-
""" Test case to check some of the scenarios we might face when storing tweets in cache, both loading into memory or rreading from disk. """
import unittest
import os
import paths
import sqlitedict
import shutil
# The base session module requires sound as a dependency, and this needs libVLC to be locatable.
os.environ['PYTHON_VLC_MODULE_PATH']=os.path.abspath(os.path.join(paths.app_path(), "..", "windows-dependencies", "x86"))
os.environ['PYTHON_VLC_LIB_PATH']=os.path.abspath(os.path.join(paths.app_path(), "..", "windows-dependencies", "x86", "libvlc.dll"))
from sessions import base

class cacheTestCase(unittest.TestCase):

    def setUp(self):
        """ Configures a fake session to check caching objects here. """
        self.session = base.baseSession("testing")
        if os.path.exists(os.path.join(paths.config_path(), "testing")) == False:
            os.mkdir(os.path.join(paths.config_path(), "testing"))
        self.session.get_configuration()

    def tearDown(self):
        """ Removes the previously configured session. """
        session_folder = os.path.join(paths.config_path(), "testing")
        if os.path.exists(session_folder):
            shutil.rmtree(session_folder)

    def generate_dataset(self):
        """ Generates a sample dataset"""
        dataset = dict(home_timeline=["message" for i in range(10000)], mentions_timeline=["mention" for i in range(20000)])
        return dataset

    ### Testing database being read from disk.

    def test_cache_in_disk_unlimited_size(self):
        """ Tests cache database being read from disk, storing the whole datasets. """
        dataset = self.generate_dataset()
        self.session.settings["general"]["load_cache_in_memory"] = False
        self.session.settings["general"]["persist_size"] = -1
        self.session.load_persistent_data()
        self.session.db["home_timeline"] = dataset["home_timeline"]
        self.session.db["mentions_timeline"] = dataset["mentions_timeline"]
        self.session.save_persistent_data()
        self.assertIsInstance(self.session.db, sqlitedict.SqliteDict)
        self.assertTrue(self.session.db.get("home_timeline") != None)
        self.assertTrue(self.session.db.get("mentions_timeline") != None)
        self.assertEquals(len(self.session.db.get("home_timeline")), 10000)
        self.assertEquals(len(self.session.db.get("mentions_timeline")), 20000)
        self.session.db.close()


    def test_cache_in_disk_limited_dataset(self):
        """ Tests wether the cache stores only the amount of items we ask it to store. """
        dataset = self.generate_dataset()
        self.session.settings["general"]["load_cache_in_memory"] = False
        self.session.settings["general"]["persist_size"] = 100
        self.session.load_persistent_data()
        self.session.db["home_timeline"] = dataset["home_timeline"]
        self.session.db["mentions_timeline"] = dataset["mentions_timeline"]
        # We need to save and load the db again because we cannot modify buffers' size while the database is opened.
        # As TWBlue reads directly from db when reading from disk, an attempt to modify buffers size while Blue is reading the db
        # Might cause an out of sync error between the GUI lists and the database.
        # So we perform the changes to buffer size when loading data during app startup if the DB is read from disk.
        self.session.save_persistent_data()
        self.session.load_persistent_data()
        self.assertIsInstance(self.session.db, sqlitedict.SqliteDict)
        self.assertTrue(self.session.db.get("home_timeline") != None)
        self.assertTrue(self.session.db.get("mentions_timeline") != None)
        self.assertEquals(len(self.session.db.get("home_timeline")), 100)
        self.assertEquals(len(self.session.db.get("mentions_timeline")), 100)
        self.session.db.close()

    def test_cache_in_disk_limited_dataset_unreversed(self):
        """Test if the cache is saved properly in unreversed buffers, when newest items are at the end of the list. """
        dataset = dict(home_timeline=[i for i in range(20)], mentions_timeline=[i for i in range(20)])
        self.session.settings["general"]["load_cache_in_memory"] = False
        self.session.settings["general"]["persist_size"] = 10
        self.session.load_persistent_data()
        self.session.db["home_timeline"] = dataset["home_timeline"]
        self.session.db["mentions_timeline"] = dataset["mentions_timeline"]
        # We need to save and load the db again because we cannot modify buffers' size while the database is opened.
        # As TWBlue reads directly from db when reading from disk, an attempt to modify buffers size while Blue is reading the db
        # Might cause an out of sync error between the GUI lists and the database.
        # So we perform the changes to buffer size when loading data during app startup if the DB is read from disk.
        self.session.save_persistent_data()
        self.session.load_persistent_data()
        self.assertIsInstance(self.session.db, sqlitedict.SqliteDict)
        self.assertTrue(self.session.db.get("home_timeline") != None)
        self.assertTrue(self.session.db.get("mentions_timeline") != None)
        self.assertEquals(self.session.db.get("home_timeline")[0], 10)
        self.assertEquals(self.session.db.get("mentions_timeline")[0], 10)
        self.assertEquals(self.session.db.get("home_timeline")[-1], 19)
        self.assertEquals(self.session.db.get("mentions_timeline")[-1], 19)
        self.session.db.close()

    def test_cache_in_disk_limited_dataset_reversed(self):
        """Test if the cache is saved properly in reversed buffers, when newest items are at the start of the list. """
        dataset = dict(home_timeline=[i for i in range(19, -1, -1)], mentions_timeline=[i for i in range(19, -1, -1)])
        self.session.settings["general"]["load_cache_in_memory"] = False
        self.session.settings["general"]["persist_size"] = 10
        self.session.settings["general"]["reverse_timelines"] = True
        self.session.load_persistent_data()
        self.session.db["home_timeline"] = dataset["home_timeline"]
        self.session.db["mentions_timeline"] = dataset["mentions_timeline"]
        # We need to save and load the db again because we cannot modify buffers' size while the database is opened.
        # As TWBlue reads directly from db when reading from disk, an attempt to modify buffers size while Blue is reading the db
        # Might cause an out of sync error between the GUI lists and the database.
        # So we perform the changes to buffer size when loading data during app startup if the DB is read from disk.
        self.session.save_persistent_data()
        self.session.load_persistent_data()
        self.assertIsInstance(self.session.db, sqlitedict.SqliteDict)
        self.assertTrue(self.session.db.get("home_timeline") != None)
        self.assertTrue(self.session.db.get("mentions_timeline") != None)
        self.assertEquals(self.session.db.get("home_timeline")[0], 19)
        self.assertEquals(self.session.db.get("mentions_timeline")[0], 19)
        self.assertEquals(self.session.db.get("home_timeline")[-1], 10)
        self.assertEquals(self.session.db.get("mentions_timeline")[-1], 10)
        self.session.db.close()

    ### Testing database being loaded into memory. Those tests should give the same results than before
    ### but as we have different code depending whether we load db into memory or read it from disk,
    ### We need to test this anyways.
    def test_cache_in_memory_unlimited_size(self):
        """ Tests cache database being loaded in memory, storing the whole datasets. """
        dataset = self.generate_dataset()
        self.session.settings["general"]["load_cache_in_memory"] = True
        self.session.settings["general"]["persist_size"] = -1
        self.session.load_persistent_data()
        self.session.db["home_timeline"] = dataset["home_timeline"]
        self.session.db["mentions_timeline"] = dataset["mentions_timeline"]
        self.session.save_persistent_data()
        self.session.load_persistent_data()
        self.assertIsInstance(self.session.db, dict)
        self.assertTrue(self.session.db.get("home_timeline") != None)
        self.assertTrue(self.session.db.get("mentions_timeline") != None)
        self.assertEquals(len(self.session.db.get("home_timeline")), 10000)
        self.assertEquals(len(self.session.db.get("mentions_timeline")), 20000)

    def test_cache_in_memory_limited_dataset(self):
        """ Tests wether the cache stores only the amount of items we ask it to store, when loaded in memory. """
        dataset = self.generate_dataset()
        self.session.settings["general"]["load_cache_in_memory"] = True
        self.session.settings["general"]["persist_size"] = 100
        self.session.load_persistent_data()
        self.session.db["home_timeline"] = dataset["home_timeline"]
        self.session.db["mentions_timeline"] = dataset["mentions_timeline"]
        self.session.save_persistent_data()
        self.session.load_persistent_data()
        self.assertIsInstance(self.session.db, dict)
        self.assertTrue(self.session.db.get("home_timeline") != None)
        self.assertTrue(self.session.db.get("mentions_timeline") != None)
        self.assertEquals(len(self.session.db.get("home_timeline")), 100)
        self.assertEquals(len(self.session.db.get("mentions_timeline")), 100)

    def test_cache_in_memory_limited_dataset_unreversed(self):
        """Test if the cache is saved properly when loaded in memory in unreversed buffers, when newest items are at the end of the list. """
        dataset = dict(home_timeline=[i for i in range(20)], mentions_timeline=[i for i in range(20)])
        self.session.settings["general"]["load_cache_in_memory"] = True
        self.session.settings["general"]["persist_size"] = 10
        self.session.load_persistent_data()
        self.assertTrue(len(self.session.db)==1)
        self.session.db["home_timeline"] = dataset["home_timeline"]
        self.session.db["mentions_timeline"] = dataset["mentions_timeline"]
        self.session.save_persistent_data()
        self.session.load_persistent_data()
        self.assertIsInstance(self.session.db, dict)
        self.assertTrue(self.session.db.get("home_timeline") != None)
        self.assertTrue(self.session.db.get("mentions_timeline") != None)
        self.assertEquals(self.session.db.get("home_timeline")[0], 10)
        self.assertEquals(self.session.db.get("mentions_timeline")[0], 10)
        self.assertEquals(self.session.db.get("home_timeline")[-1], 19)
        self.assertEquals(self.session.db.get("mentions_timeline")[-1], 19)

    def test_cache_in_memory_limited_dataset_reversed(self):
        """Test if the cache is saved properly in reversed buffers, when newest items are at the start of the list. This test if for db read into memory. """
        dataset = dict(home_timeline=[i for i in range(19, -1, -1)], mentions_timeline=[i for i in range(19, -1, -1)])
        self.session.settings["general"]["load_cache_in_memory"] = True
        self.session.settings["general"]["persist_size"] = 10
        self.session.settings["general"]["reverse_timelines"] = True
        self.session.load_persistent_data()
        self.session.db["home_timeline"] = dataset["home_timeline"]
        self.session.db["mentions_timeline"] = dataset["mentions_timeline"]
        self.session.save_persistent_data()
        self.session.load_persistent_data()
        self.assertIsInstance(self.session.db, dict)
        self.assertTrue(self.session.db.get("home_timeline") != None)
        self.assertTrue(self.session.db.get("mentions_timeline") != None)
        self.assertEquals(self.session.db.get("home_timeline")[0], 19)
        self.assertEquals(self.session.db.get("mentions_timeline")[0], 19)
        self.assertEquals(self.session.db.get("home_timeline")[-1], 10)
        self.assertEquals(self.session.db.get("mentions_timeline")[-1], 10)

if __name__ == "__main__":
    unittest.main()