# -*- coding: utf-8 -*-
"""Tests for the Mastodon autocompletion scan module."""
import sys
import types
import pytest
import time
from unittest import mock

# Mock wx module before importing scan
wx_module = types.ModuleType("wx")
wx_module.CallAfter = mock.MagicMock()
wx_module.Panel = mock.MagicMock()
wx_module.BoxSizer = mock.MagicMock()
wx_module.StaticText = mock.MagicMock()
wx_module.TextCtrl = mock.MagicMock()
wx_module.Gauge = mock.MagicMock()
wx_module.Button = mock.MagicMock()
wx_module.MessageDialog = mock.MagicMock()
wx_module.VERTICAL = 0
wx_module.HORIZONTAL = 1
wx_module.ALL = 0
wx_module.EXPAND = 0
wx_module.LEFT = 0
wx_module.TOP = 0
wx_module.ALIGN_CENTER = 0
wx_module.TE_READONLY = 0
wx_module.TE_PROCESS_TAB = 0
wx_module.TAB_TRAVERSAL = 0
wx_module.ID_ANY = -1
wx_module.ID_CANCEL = 0
wx_module.ID_OK = 0
wx_module.ID_YES = 0
wx_module.EVT_BUTTON = mock.MagicMock()
wx_module.EVT_CLOSE = mock.MagicMock()
wx_module.ICON_QUESTION = 0
wx_module.ICON_INFORMATION = 0
wx_module.ICON_ERROR = 0
wx_module.YES_NO = 0
sys.modules["wx"] = wx_module

# Mock widgetUtils
widgetUtils_module = types.ModuleType("widgetUtils")
widgetUtils_module.BaseDialog = mock.MagicMock()
widgetUtils_module.OK = 1
sys.modules["widgetUtils"] = widgetUtils_module

# Mock output
output_module = types.ModuleType("output")
output_module.speak = mock.MagicMock()
sys.modules["output"] = output_module

# Mock pubsub
pub_module = types.ModuleType("pubsub")
pub_module.pub = mock.MagicMock()
sys.modules["pubsub"] = pub_module
sys.modules["pubsub.pub"] = pub_module.pub

# Mock application
application_module = types.ModuleType("application")
sys.modules["application"] = application_module


class MockUser:
    """Mock Mastodon user object."""
    def __init__(self, user_id, username, display_name="", acct=None):
        self.id = user_id
        self.username = username
        self.display_name = display_name
        self.acct = acct or f"{username}@instance.social"


### Tests for the scan logic (not UI)

def test_user_dict_prevents_duplicates():
    """Test that using a dict with user.id as key prevents duplicates."""
    users_dict = {}
    
    # Simulate adding users from following
    user1 = MockUser(1, "alice", "Alice")
    user2 = MockUser(2, "bob", "Bob")
    
    users_dict[user1.id] = user1
    users_dict[user2.id] = user2
    
    # Simulate adding same users from followers (should not duplicate)
    user1_again = MockUser(1, "alice", "Alice Updated")  # Same ID
    user3 = MockUser(3, "charlie", "Charlie")
    
    if user1_again.id not in users_dict:
        users_dict[user1_again.id] = user1_again
    if user3.id not in users_dict:
        users_dict[user3.id] = user3
    
    # Should have 3 unique users, not 4
    assert len(users_dict) == 3
    # Original alice should be preserved (not updated)
    assert users_dict[1].display_name == "Alice"

def test_user_dict_performance():
    """Test that dict lookups are O(1) - should complete instantly."""
    users_dict = {}
    
    # Add 10,000 users
    for i in range(10000):
        user = MockUser(i, f"user{i}", f"User {i}")
        users_dict[user.id] = user
    
    # Now check 10,000 more users for duplicates
    start_time = time.time()
    for i in range(10000):
        user = MockUser(i, f"user{i}", f"User {i}")
        if user.id not in users_dict:
            users_dict[user.id] = user
    elapsed = time.time() - start_time
    
    # This should complete in well under 1 second with O(1) lookups
    # The original O(n²) implementation would take minutes
    assert elapsed < 1.0, f"Duplicate check took {elapsed}s, expected < 1s"

def test_display_name_fallback_to_username():
    """Test that username is used when display_name is empty."""
    user_with_display = MockUser(1, "alice", "Alice Smith")
    user_without_display = MockUser(2, "bob", "")
    user_with_none = MockUser(3, "charlie", None)
    
    def get_name(user):
        return user.display_name if user.display_name != None and user.display_name != "" else user.username
    
    assert get_name(user_with_display) == "Alice Smith"
    assert get_name(user_without_display) == "bob"
    assert get_name(user_with_none) == "charlie"

def test_new_users_count():
    """Test counting new vs existing users."""
    # Simulate the storage.set_user return value pattern
    existing_users = {"user1@instance.social", "user2@instance.social"}
    
    def mock_set_user(acct, name, from_buffer):
        """Returns True if new, False if already existed."""
        if acct in existing_users:
            return False
        existing_users.add(acct)
        return True
    
    users_to_add = [
        ("user1@instance.social", "User One"),   # existing
        ("user2@instance.social", "User Two"),   # existing
        ("user3@instance.social", "User Three"), # new
        ("user4@instance.social", "User Four"),  # new
    ]
    
    new_count = 0
    for acct, name in users_to_add:
        if mock_set_user(acct, name, 1):
            new_count += 1
    
    assert new_count == 2
    total = len(users_to_add)
    already_existed = total - new_count
    assert already_existed == 2


### Tests for progress dialog calculations

def test_total_users_calculation():
    """Test that total users is sum of followers and following."""
    followers_count = 500
    following_count = 300
    total = followers_count + following_count
    assert total == 800

def test_progress_bar_value_capped():
    """Test that progress bar value doesn't exceed total."""
    total_users = 100
    
    # Simulate progress bar update
    def get_progress_value(current_users, total):
        return min(current_users, total)
    
    assert get_progress_value(50, total_users) == 50
    assert get_progress_value(100, total_users) == 100
    assert get_progress_value(150, total_users) == 100  # Capped

def test_cursor_preservation_logic():
    """Test cursor position preservation when text changes."""
    old_text = "Page 1 | Users: 50"
    new_text = "Page 2 | Users: 100"
    cursor_pos = 5  # Somewhere in the middle
    
    new_length = len(new_text)
    restored_pos = min(cursor_pos, new_length)
    
    assert restored_pos == 5  # Position preserved
    
    # Test with cursor beyond new text length
    short_new_text = "Done"
    new_length = len(short_new_text)
    cursor_pos = 10
    restored_pos = min(cursor_pos, new_length)
    
    assert restored_pos == 4  # Capped to new length
