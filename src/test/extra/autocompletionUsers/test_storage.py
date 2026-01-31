# -*- coding: utf-8 -*-
"""Tests for the autocompletion storage module."""
import os
import pytest
import tempfile
import shutil

# path where we will save our test config
temp_base_dir = None

@pytest.fixture
def temp_config_dir():
    """Create a temporary directory for test database."""
    global temp_base_dir
    temp_base_dir = tempfile.mkdtemp()
    session_dir = os.path.join(temp_base_dir, "test_session")
    os.makedirs(session_dir)
    yield temp_base_dir
    # Cleanup handled by storage_instance fixture

@pytest.fixture
def storage_instance(temp_config_dir, monkeypatch):
    """Create a storage instance with mocked paths."""
    # Mock paths.config_path to return our temp directory
    import paths
    monkeypatch.setattr(paths, "config_path", lambda: temp_config_dir)
    
    from extra.autocompletionUsers import storage
    s = storage.storage("test_session")
    yield s
    # Explicitly close database connection before cleanup
    s.cursor.close()
    s.connection.close()
    # Now cleanup temp directory
    if os.path.exists(temp_config_dir):
        shutil.rmtree(temp_config_dir)

def test_create_table(storage_instance):
    """Test that the users table is created."""
    assert storage_instance.table_exist("users") == True

def test_set_user_new(storage_instance):
    """Test adding a new user returns True."""
    result = storage_instance.set_user("user1@instance.social", "User One", 1)
    assert result == True

def test_set_user_duplicate(storage_instance):
    """Test adding a duplicate user returns False."""
    storage_instance.set_user("user1@instance.social", "User One", 1)
    result = storage_instance.set_user("user1@instance.social", "User One Updated", 1)
    assert result == False

def test_get_users(storage_instance):
    """Test searching for users."""
    storage_instance.set_user("alice@instance.social", "Alice Smith", 1)
    storage_instance.set_user("bob@instance.social", "Bob Jones", 1)
    storage_instance.set_user("charlie@instance.social", "Charlie Brown", 1)
    
    # Search by username
    results = storage_instance.get_users("alice")
    assert len(results) == 1
    assert results[0][0] == "alice@instance.social"
    
    # Search by display name
    results = storage_instance.get_users("jones")
    assert len(results) == 1
    assert results[0][1] == "Bob Jones"

def test_get_all_users(storage_instance):
    """Test getting all users."""
    storage_instance.set_user("user1@instance.social", "User One", 1)
    storage_instance.set_user("user2@instance.social", "User Two", 1)
    storage_instance.set_user("user3@instance.social", "User Three", 1)
    
    results = storage_instance.get_all_users()
    assert len(results) == 3

def test_remove_user(storage_instance):
    """Test removing a user."""
    storage_instance.set_user("user1@instance.social", "User One", 1)
    storage_instance.set_user("user2@instance.social", "User Two", 1)
    
    storage_instance.remove_user("user1@instance.social")
    
    results = storage_instance.get_all_users()
    assert len(results) == 1
    assert results[0][0] == "user2@instance.social"

def test_remove_by_buffer(storage_instance):
    """Test removing users by buffer type."""
    storage_instance.set_user("friend1@instance.social", "Friend One", 1)
    storage_instance.set_user("friend2@instance.social", "Friend Two", 1)
    storage_instance.set_user("manual@instance.social", "Manual User", 0)
    
    # Remove all users added from buffer type 1 (friends/following)
    storage_instance.remove_by_buffer(1)
    
    results = storage_instance.get_all_users()
    assert len(results) == 1
    assert results[0][0] == "manual@instance.social"

def test_case_insensitive_search(storage_instance):
    """Test that search is case insensitive."""
    storage_instance.set_user("Alice@Instance.Social", "ALICE SMITH", 1)
    
    # Search with different cases
    results = storage_instance.get_users("alice")
    assert len(results) == 1
    
    results = storage_instance.get_users("ALICE")
    assert len(results) == 1
    
    results = storage_instance.get_users("Alice")
    assert len(results) == 1

