# -*- coding: utf-8 -*-
import sys
import unittest
from unittest.mock import patch, AsyncMock, MagicMock, PropertyMock

# Assuming paths are set up correctly for test environment to find these
from sessions.atprotosocial.session import Session as ATProtoSocialSession
from sessions.session_exceptions import SessionLoginError, SessionError
from approve.notifications import NotificationError # Assuming this is the correct import path
from atproto.xrpc_client.models.common import XrpcError
from atproto.xrpc_client import models as atp_models # For ATProto models
from atproto.xrpc_client.models import ids # For lexicon IDs

# Mock wx for headless testing
class MockWxDialog:
    def __init__(self, parent, message, caption, value="", style=0):
        self.message = message
        self.caption = caption
        self.value = value
        self.return_code = mock_wx.ID_CANCEL # Default to cancel, specific tests can change this

    def ShowModal(self):
        return self.return_code

    def GetValue(self):
        return self.value

    def Destroy(self):
        pass

class MockWxMessageBox(MockWxDialog):
    pass

# Need to mock wx before it's imported by other modules if they do it at import time.
# Patching directly where used in session.py is generally safer.
mock_wx = MagicMock()
mock_wx.TextEntryDialog = MockWxDialog
mock_wx.PasswordEntryDialog = MockWxDialog
mock_wx.MessageBox = MockWxMessageBox
mock_wx.ID_OK = 1
mock_wx.ID_CANCEL = 2
mock_wx.ICON_ERROR = 16
mock_wx.ICON_INFORMATION = 64
mock_wx.OK = 4
mock_wx.YES_NO = 1 # Example, actual value might differ but not critical for test logic
mock_wx.YES = 1   # Example
mock_wx.ICON_QUESTION = 32 # Example

# Mock config objects
# This structure tries to mimic how config is accessed in session.py
# e.g., config.sessions.atprotosocial[user_id].handle
class MockConfigNode:
    def __init__(self, initial_value=None):
        self._value = initial_value
        self.get = MagicMock(return_value=self._value)
        self.set = AsyncMock() # .set() is async

class MockUserSessionConfig:
    def __init__(self):
        self.handle = MockConfigNode("")
        self.app_password = MockConfigNode("")
        self.did = MockConfigNode("")
        # Add other config values if session.py uses them for atprotosocial

class MockATProtoSocialConfig:
    def __init__(self):
        self._user_configs = {"test_user": MockUserSessionConfig()}
    def __getitem__(self, key):
        return self._user_configs.get(key, MagicMock(return_value=MockUserSessionConfig())) # Return a mock if key not found

class MockSessionsConfig:
    def __init__(self):
        self.atprotosocial = MockATProtoSocialConfig()

mock_config_global = MagicMock()
mock_config_global.sessions = MockSessionsConfig()


class TestATProtoSocialSession(unittest.IsolatedAsyncioTestCase):

    @patch('sessions.atprotosocial.session.wx', mock_wx)
    @patch('sessions.atprotosocial.session.config', mock_config_global)
    def setUp(self):
        self.mock_approval_api = MagicMock()

        # Reset mocks for user_config part of global mock_config_global for each test
        self.mock_user_config_instance = MockUserSessionConfig()
        mock_config_global.sessions.atprotosocial.__getitem__.return_value = self.mock_user_config_instance

        self.session = ATProtoSocialSession(approval_api=self.mock_approval_api, user_id="test_user", channel_id="test_channel")

        self.session.db = {}
        self.session.save_db = AsyncMock()
        self.session.notify_session_ready = AsyncMock()
        self.session.send_text_notification = MagicMock()

        # Mock the util property to return a MagicMock for ATProtoSocialUtils
        self.mock_util_instance = AsyncMock() # Make it an AsyncMock if its methods are async
        self.mock_util_instance._own_did = None # These are set directly by session.login
        self.mock_util_instance._own_handle = None
        # Add any methods from util that are directly called by session methods being tested
        # e.g., self.mock_util_instance.get_own_did = MagicMock(return_value="did:plc:test")
        self.session._util = self.mock_util_instance
        self.session.util # Call property to ensure _util is set if it's lazy loaded

    def test_session_initialization(self):
        self.assertIsInstance(self.session, ATProtoSocialSession)
        self.assertEqual(self.session.KIND, "atprotosocial")
        self.assertIsNone(self.session.client)
        self.assertEqual(self.session.user_id, "test_user")

    @patch('sessions.atprotosocial.session.AsyncClient')
    async def test_login_successful(self, MockAsyncClient):
        mock_client_instance = MockAsyncClient.return_value
        # Use actual ATProto models for spec if possible for better type checking in mocks
        mock_profile = MagicMock(spec=atp_models.ComAtprotoServerDefs.Session)
        mock_profile.access_jwt = "fake_access_jwt"
        mock_profile.refresh_jwt = "fake_refresh_jwt"
        mock_profile.did = "did:plc:testdid"
        mock_profile.handle = "testhandle.bsky.social"
        mock_client_instance.login = AsyncMock(return_value=mock_profile)

        self.session.config_get = MagicMock(return_value=None) # Simulate no pre-existing config

        result = await self.session.login("testhandle.bsky.social", "test_password")

        self.assertTrue(result)
        self.assertIsNotNone(self.session.client)
        mock_client_instance.login.assert_called_once_with("testhandle.bsky.social", "test_password")

        self.assertEqual(self.session.db.get("access_jwt"), "fake_access_jwt")
        self.assertEqual(self.session.db.get("did"), "did:plc:testdid")
        self.assertEqual(self.session.db.get("handle"), "testhandle.bsky.social")
        self.session.save_db.assert_called_once()

        self.mock_user_config_instance.handle.set.assert_called_once_with("testhandle.bsky.social")
        self.mock_user_config_instance.app_password.set.assert_called_once_with("test_password")
        self.mock_user_config_instance.did.set.assert_called_once_with("did:plc:testdid")

        self.assertEqual(self.session._util._own_did, "did:plc:testdid")
        self.assertEqual(self.session._util._own_handle, "testhandle.bsky.social")

        self.session.notify_session_ready.assert_called_once()

    @patch('sessions.atprotosocial.session.AsyncClient')
    async def test_login_failure_xrpc(self, MockAsyncClient):
        mock_client_instance = MockAsyncClient.return_value
        mock_client_instance.login = AsyncMock(side_effect=XrpcError(error="AuthenticationFailed", message="Invalid credentials"))
        self.session.config_get = MagicMock(return_value=None)

        with self.assertRaises(NotificationError) as ctx:
            await self.session.login("testhandle.bsky.social", "wrong_password")

        self.assertTrue("Invalid handle or app password." in str(ctx.exception) or "Invalid credentials" in str(ctx.exception))
        self.assertIsNone(self.session.client)
        self.session.notify_session_ready.assert_not_called()

    @patch('sessions.atprotosocial.session.wx', new=mock_wx)
    @patch.object(ATProtoSocialSession, 'login', new_callable=AsyncMock)
    async def test_authorise_successful(self, mock_login_method):
        mock_login_method.return_value = True

        mock_wx.TextEntryDialog.return_value.GetValue = MagicMock(return_value="test_handle")
        mock_wx.TextEntryDialog.return_value.ShowModal = MagicMock(return_value=mock_wx.ID_OK)
        mock_wx.PasswordEntryDialog.return_value.GetValue = MagicMock(return_value="password_ok")
        mock_wx.PasswordEntryDialog.return_value.ShowModal = MagicMock(return_value=mock_wx.ID_OK)

        self.session.config_get = MagicMock(return_value="prefill_handle") # For pre-filling handle dialog

        result = await self.session.authorise()

        self.assertTrue(result)
        mock_login_method.assert_called_once_with("test_handle", "password_ok")
        # Further check if wx.MessageBox was called with success
        # This requires more complex mocking or inspection of calls to mock_wx.MessageBox

    @patch('sessions.atprotosocial.session.wx', new=mock_wx)
    @patch.object(ATProtoSocialSession, 'login', new_callable=AsyncMock)
    async def test_authorise_login_fails_with_notification_error(self, mock_login_method):
        mock_login_method.side_effect = NotificationError("Specific login failure from mock.")

        mock_wx.TextEntryDialog.return_value.GetValue = MagicMock(return_value="test_handle")
        mock_wx.TextEntryDialog.return_value.ShowModal = MagicMock(return_value=mock_wx.ID_OK)
        mock_wx.PasswordEntryDialog.return_value.GetValue = MagicMock(return_value="any_password")
        mock_wx.PasswordEntryDialog.return_value.ShowModal = MagicMock(return_value=mock_wx.ID_OK)

        self.session.config_get = MagicMock(return_value="")

        result = await self.session.authorise()
        self.assertFalse(result)
        mock_login_method.assert_called_once()


    # --- Test Sending Posts ---
    async def test_send_simple_post_successful(self):
        self.session.is_ready = MagicMock(return_value=True) # Assume session is ready
        self.session.util.post_status = AsyncMock(return_value="at://mock_post_uri")

        post_uri = await self.session.send_message("Test text post")

        self.assertEqual(post_uri, "at://mock_post_uri")
        self.session.util.post_status.assert_called_once_with(
            text="Test text post", media_ids=None, reply_to_uri=None, quote_uri=None,
            cw_text=None, is_sensitive=False, langs=None, tags=None
        )

    async def test_send_post_with_quote_and_lang(self):
        self.session.is_ready = MagicMock(return_value=True)
        self.session.util.post_status = AsyncMock(return_value="at://mock_post_uri_quote")

        post_uri = await self.session.send_message(
            "Quoting another post",
            quote_uri="at://did:plc:someuser/app.bsky.feed.post/somepostid",
            langs=["en", "es"]
        )
        self.assertEqual(post_uri, "at://mock_post_uri_quote")
        self.session.util.post_status.assert_called_once_with(
            text="Quoting another post", media_ids=None, reply_to_uri=None,
            quote_uri="at://did:plc:someuser/app.bsky.feed.post/somepostid",
            cw_text=None, is_sensitive=False, langs=["en", "es"], tags=None
        )

    @patch('sessions.atprotosocial.session.os.path.basename', return_value="image.png") # Mock os.path.basename
    async def test_send_post_with_media(self, mock_basename):
        self.session.is_ready = MagicMock(return_value=True)
        mock_blob_info = {"blob_ref": MagicMock(spec=atp_models.ComAtprotoRepoStrongRef.Blob), "alt_text": "A test image"}
        self.session.util.upload_media = AsyncMock(return_value=mock_blob_info)
        self.session.util.post_status = AsyncMock(return_value="at://mock_post_uri_media")

        post_uri = await self.session.send_message(
            "Post with media", files=["dummy/path/image.png"], media_alt_texts=["A test image"]
        )
        self.assertEqual(post_uri, "at://mock_post_uri_media")
        self.session.util.upload_media.assert_called_once_with("dummy/path/image.png", "image/png", alt_text="A test image")
        self.session.util.post_status.assert_called_once_with(
            text="Post with media", media_ids=[mock_blob_info], reply_to_uri=None, quote_uri=None,
            cw_text=None, is_sensitive=False, langs=None, tags=None
        )

    async def test_send_post_util_failure(self):
        self.session.is_ready = MagicMock(return_value=True)
        self.session.util.post_status = AsyncMock(side_effect=NotificationError("Failed to post from util"))
        with self.assertRaisesRegex(NotificationError, "Failed to post from util"):
            await self.session.send_message("This will fail")

    # --- Test Fetching Timelines ---
    def _create_mock_feed_view_post(self, uri_suffix):
        post_view = MagicMock(spec=atp_models.AppBskyFeedDefs.PostView)
        post_view.uri = f"at://did:plc:test/app.bsky.feed.post/{uri_suffix}"
        post_view.cid = f"cid_{uri_suffix}"
        author_mock = MagicMock(spec=atp_models.AppBskyActorDefs.ProfileViewBasic)
        author_mock.did = "did:plc:author"
        author_mock.handle = "author.bsky.social"
        post_view.author = author_mock
        record_mock = MagicMock(spec=atp_models.AppBskyFeedPost.Main)
        record_mock.text = f"Text of post {uri_suffix}"
        record_mock.createdAt = "2024-01-01T00:00:00Z"
        post_view.record = record_mock
        feed_view_post = MagicMock(spec=atp_models.AppBskyFeedDefs.FeedViewPost)
        feed_view_post.post = post_view
        feed_view_post.reason = None
        feed_view_post.reply = None
        return feed_view_post

    async def test_fetch_home_timeline_successful(self):
        self.session.is_ready = MagicMock(return_value=True)
        mock_post1 = self._create_mock_feed_view_post("post1")
        mock_post2 = self._create_mock_feed_view_post("post2")
        self.session.util.get_timeline = AsyncMock(return_value=([mock_post1, mock_post2], "cursor_for_home"))
        self.session.order_buffer = AsyncMock(return_value=["uri1", "uri2"])

        processed_uris, next_cursor = await self.session.fetch_home_timeline(limit=5, new_only=True)

        self.session.util.get_timeline.assert_called_once_with(algorithm=None, limit=5, cursor=None)
        self.session.order_buffer.assert_called_once_with(items=[mock_post1, mock_post2], new_only=True, buffer_name="home_timeline_buffer")
        self.assertEqual(self.session.home_timeline_cursor, "cursor_for_home")
        self.assertEqual(processed_uris, ["uri1", "uri2"])

    async def test_fetch_user_timeline_successful(self):
        self.session.is_ready = MagicMock(return_value=True)
        mock_post3 = self._create_mock_feed_view_post("post3")
        self.session.util.get_author_feed = AsyncMock(return_value=([mock_post3], "cursor_for_user"))
        self.session.order_buffer = AsyncMock(return_value=["uri3"])

        processed_uris, next_cursor = await self.session.fetch_user_timeline(
            user_did="did:plc:targetuser", limit=10, filter_type="posts_no_replies"
        )
        self.session.util.get_author_feed.assert_called_once_with(
            actor_did="did:plc:targetuser", limit=10, cursor=None, filter="posts_no_replies"
        )
        self.session.order_buffer.assert_called_once_with(items=[mock_post3], new_only=False, buffer_name='user_timeline_did:plc:targetuser')
        self.assertEqual(next_cursor, "cursor_for_user")
        self.assertEqual(processed_uris, ["uri3"])

    async def test_fetch_timeline_failure(self):
        self.session.is_ready = MagicMock(return_value=True)
        self.session.util.get_timeline = AsyncMock(side_effect=NotificationError("API error for timeline"))
        with self.assertRaisesRegex(NotificationError, "API error for timeline"):
            await self.session.fetch_home_timeline()

    # --- Test Fetching Notifications ---
    def _create_mock_notification(self, reason: str, uri_suffix: str, isRead: bool = False):
        notif = MagicMock(spec=atp_models.AppBskyNotificationListNotifications.Notification)
        notif.uri = f"at://did:plc:test/app.bsky.feed.like/{uri_suffix}"
        notif.cid = f"cid_notif_{uri_suffix}"
        author_mock = MagicMock(spec=atp_models.AppBskyActorDefs.ProfileView)
        author_mock.did = f"did:plc:otheruser{uri_suffix}"
        author_mock.handle = f"other{uri_suffix}.bsky.social"
        author_mock.displayName = f"Other User {uri_suffix}"
        author_mock.avatar = "http://example.com/avatar.png"
        notif.author = author_mock
        notif.reason = reason
        notif.reasonSubject = f"at://did:plc:test/app.bsky.feed.post/mypost{uri_suffix}" if reason != "follow" else None
        if reason in ["mention", "reply", "quote"]:
            record_mock = MagicMock(spec=atp_models.AppBskyFeedPost.Main)
            record_mock.text = f"Notification related text for {reason}"
            record_mock.createdAt = "2024-01-02T00:00:00Z"
            notif.record = record_mock
        else:
            notif.record = MagicMock()
        notif.isRead = isRead
        notif.indexedAt = "2024-01-02T00:00:00Z"
        return notif

    async def test_fetch_notifications_successful_and_handler_dispatch(self):
        self.session.is_ready = MagicMock(return_value=True)
        self.session.util = AsyncMock()
        mock_like_notif = self._create_mock_notification("like", "like1", isRead=False)
        mock_mention_notif = self._create_mock_notification("mention", "mention1", isRead=False)
        self.session.util.get_notifications = AsyncMock(return_value=([mock_like_notif, mock_mention_notif], "next_notif_cursor"))

        self.session._handle_like_notification = AsyncMock()
        self.session._handle_mention_notification = AsyncMock()
        self.session._handle_repost_notification = AsyncMock()
        self.session._handle_follow_notification = AsyncMock()
        self.session._handle_reply_notification = AsyncMock()
        self.session._handle_quote_notification = AsyncMock()

        returned_cursor = await self.session.fetch_notifications(limit=10)

        self.session.util.get_notifications.assert_called_once_with(limit=10, cursor=None)
        self.session._handle_like_notification.assert_called_once_with(mock_like_notif)
        self.session._handle_mention_notification.assert_called_once_with(mock_mention_notif)
        self.assertEqual(returned_cursor, "next_notif_cursor")

if __name__ == '__main__':
    unittest.main()

# Minimal wx mock for running tests headlessly
if 'wx' not in sys.modules: # type: ignore
    sys.modules['wx'] = MagicMock()
    mock_wx_module = sys.modules['wx']
    mock_wx_module.ID_OK = 1
    mock_wx_module.ID_CANCEL = 2
    mock_wx_module.ICON_ERROR = 16
    mock_wx_module.ICON_INFORMATION = 64
    mock_wx_module.OK = 4
    mock_wx_module.TextEntryDialog = MockWxDialog
    mock_wx_module.PasswordEntryDialog = MockWxDialog
    mock_wx_module.MessageBox = MockWxMessageBox
    mock_wx_module.CallAfter = MagicMock()
    mock_wx_module.GetApp = MagicMock()
>>>>>>> REPLACE
