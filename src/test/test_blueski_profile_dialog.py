"""Exercise the actual wx view with deterministic workers and no network."""
from unittest.mock import Mock

import wx

from wxUI.dialogs.blueski import showUserProfile as module


def test_profile_images_and_action_share_controller(monkeypatch):
    app = wx.App.Get() or wx.App()
    work, deliveries = [], []
    monkeypatch.setattr(module, 'Thread', lambda target, daemon: Mock(start=lambda: work.append(target)))
    monkeypatch.setattr(wx, 'CallAfter', lambda callback, *args: deliveries.append(lambda: callback(*args)))
    monkeypatch.setattr(wx, 'MessageBox', Mock())
    session = Mock()
    session.get_own_did.return_value = 'did:own'
    session.get_profile.return_value = {
        'did': 'did:alice', 'handle': 'alice.test', 'displayName': 'Alice',
        'description': 'Bio', 'avatar': 'avatar-url', 'banner': 'banner-url',
        'postsCount': 3, 'followersCount': 4, 'followsCount': 5,
        'viewer': {},
    }
    dialog = module.ShowUserProfileDialog(None, session, 'alice.test')
    try:
        controller = dialog.profile_controller
        controller.download = Mock(return_value=None)
        work.pop(0)()
        deliveries.pop(0)()
        assert dialog.profile_field_ctrls['displayName'].GetValue() == 'Alice'
        assert dialog.target_user_did == 'did:alice'
        work.pop(0)()
        deliveries.pop(0)()
        assert controller.download.call_count == 2
        dialog.on_user_action(Mock(), 'follow_user')
        session.follow_user.assert_not_called()
        work.pop(0)()
        deliveries.pop(0)()
        session.follow_user.assert_called_once_with('did:alice')
        assert not dialog._action_busy
        # A successful action schedules a refresh. Destroy before it returns.
        dialog.Destroy()
        app.ProcessPendingEvents()
        wx.Yield()
        assert controller._closed
        work.pop(0)()
        deliveries.pop(0)()
    finally:
        if dialog:
            dialog.Destroy()
