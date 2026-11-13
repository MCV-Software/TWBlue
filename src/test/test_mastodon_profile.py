from datetime import datetime
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from controller.mastodon.profile import ProfileController, download_image
from controller.mastodon.profile_format import format_profile
from sessions.mastodon.session import Session
from sessions.gotosocial.session import Session as GoToSocialSession


@pytest.fixture
def account():
    return SimpleNamespace(id=12, acct='alice@example.test', display_name='Alice',
        url='https://example.test/@alice', note='<p>Hello <b>world</b></p>',
        created_at=datetime(2020, 1, 2), header='header-url', avatar='avatar-url',
        fields=[SimpleNamespace(name='<b>Site</b>', value='<p>Example</p>')],
        locked=True, bot=False, discoverable=None,
        statuses_count=2, following_count=3, followers_count=4)


def test_profile_format_preserves_fields_dates_and_flags(account):
    result = format_profile(account)
    assert result.display_name == 'Alice'
    assert 'Hello world' in result.note
    assert '<' not in result.note
    assert result.joined == '02 January, 2020'
    assert result.fields[0].name == 'Site'
    assert result.fields[0].value.strip() == 'Example'
    assert result.locked and not result.bot and not result.discoverable
    assert result.followers_count == 4
    assert format_profile(vars(account)).note == result.note
    assert format_profile({}).fields == []


@pytest.fixture
def harness():
    session, view = Mock(), Mock()
    work, ui = [], []
    controller = ProfileController(session, view, work.append,
        lambda callback, *args: ui.append(lambda: callback(*args)), download=Mock(return_value=None))
    return controller, session, view, work, ui


def test_lookup_formats_and_delivers_on_ui(harness, account):
    controller, session, view, work, ui = harness
    session.get_profile.return_value = account
    controller.load(12)
    session.get_profile.assert_not_called()
    work.pop()()
    view.show_profile.assert_not_called()
    ui.pop()()
    user, data, owner = view.show_profile.call_args.args
    assert user is account and owner is controller and data.display_name == 'Alice'
    session.get_profile.assert_called_once_with(12)


@pytest.mark.parametrize('close', [False, True])
def test_profile_error_and_closed_destination(harness, close):
    controller, session, view, work, ui = harness
    error = RuntimeError('offline')
    session.get_profile.side_effect = error
    controller.load(12)
    work.pop()()
    if close:
        controller.close()
    ui.pop()()
    if close:
        view.show_error.assert_not_called()
    else:
        view.show_error.assert_called_once_with(error)
    view.show_profile.assert_not_called()


@pytest.mark.parametrize('close', [False, True])
def test_images_are_dispatched_and_ignored_after_close(harness, close):
    controller, session, view, work, ui = harness
    controller.download.side_effect = [None, b'avatar']
    controller.load_images('header', 'avatar')
    work.pop()()
    view.show_images.assert_not_called()
    if close:
        controller.close()
    ui.pop()()
    if close:
        view.show_images.assert_not_called()
    else:
        view.show_images.assert_called_once_with(None, b'avatar')


@pytest.mark.parametrize('session_type', [Session, GoToSocialSession])
@pytest.mark.parametrize('action', ['follow', 'unfollow', 'mute', 'unmute', 'block', 'unblock'])
def test_session_actions_preserve_provider_calls(session_type, action):
    session = session_type.__new__(session_type)
    session.api = Mock()
    session.perform_user_action(action, 12)
    getattr(session.api, 'account_' + action).assert_called_once_with(12)


def test_session_queries_and_invalid_action():
    session = Session.__new__(Session)
    session.api = Mock()
    assert session.get_profile(12) is session.api.account.return_value
    assert session.lookup_account('alice') is session.api.account_lookup.return_value
    session.api.reset_mock()
    with pytest.raises(ValueError):
        session.perform_user_action('delete', 12)
    assert session.api.mock_calls == []


def test_profile_dialog_images_actions_and_destroy(monkeypatch, account):
    import wx
    from wxUI.dialogs.mastodon import showUserProfile as module
    monkeypatch.setattr('builtins._', lambda text: text, raising=False)
    app = wx.App.Get() or wx.App()
    work, ui = [], []
    session = Mock()
    controller = ProfileController(session, Mock(), work.append,
        lambda callback, *args: ui.append(lambda: callback(*args)), download=Mock(return_value=None))
    dialog = module.ShowUserProfile(account, session=session, controller=controller)
    actions = Mock()
    monkeypatch.setattr(module.userActions, 'userActions', actions)
    try:
        work.pop()()
        ui.pop()()
        dialog.onAction()
        actions.assert_called_once_with(session, users=['alice@example.test'], on_complete=dialog._on_action_finished)
        dialog._getImages()
        dialog.Destroy()
        work.pop()()
        ui.pop()()
        assert controller.closed
    finally:
        if dialog:
            dialog.Destroy()


def test_action_selector_executes_after_dialog_cleanup(monkeypatch):
    from controller.mastodon import userActions as module
    confirmation = Mock()
    confirmation.ShowModal.return_value = module.wx.ID_YES
    monkeypatch.setattr(module.wx, 'MessageDialog', Mock(return_value=confirmation))
    dialog = Mock()
    dialog.get_response.return_value = module.widgetUtils.OK
    dialog.get_action.return_value = 'block'
    dialog.get_user.return_value = 'alice@example.test'
    monkeypatch.setattr(module.userActions, 'create_dialog', lambda self, users: setattr(self, 'dialog', dialog))
    session = Mock()
    session.lookup_account.return_value = SimpleNamespace(id=12)
    work = []
    module.userActions(session, users=['alice@example.test'], execute=work.append, dispatch=Mock())
    dialog.Destroy.assert_called_once()
    session.lookup_account.assert_not_called()
    work.pop()()
    session.perform_user_action.assert_called_once_with('block', 12)


@pytest.mark.parametrize('cancel', [False, True])
def test_action_selector_cancellation_and_error_feedback(monkeypatch, cancel):
    from controller.mastodon import userActions as module
    dialog = Mock()
    dialog.get_response.return_value = module.widgetUtils.CANCEL if cancel else module.widgetUtils.OK
    dialog.get_action.return_value = 'follow'
    dialog.get_user.return_value = 'alice'
    monkeypatch.setattr(module.userActions, 'create_dialog', lambda self, users: setattr(self, 'dialog', dialog))
    session, dispatch = Mock(), Mock()
    session.lookup_account.side_effect = RuntimeError('offline')
    work = []
    module.userActions(session, users=['alice'], execute=work.append, dispatch=dispatch)
    dialog.Destroy.assert_called_once()
    if cancel:
        assert not work
        session.lookup_account.assert_not_called()
    else:
        work.pop()()
        dispatch.assert_called_once_with(module.output.speak, 'Error offline', True)
        session.perform_user_action.assert_not_called()


@pytest.mark.parametrize('status,expected', [(200, b'image'), (404, None)])
def test_image_download_closes_response_and_checks_status(monkeypatch, status, expected):
    from contextlib import contextmanager
    closed = []
    @contextmanager
    def response(*args, **kwargs):
        assert kwargs == {'timeout': 10}
        try:
            yield SimpleNamespace(status_code=status, content=b'image')
        finally:
            closed.append(True)
    monkeypatch.setattr('controller.mastodon.profile.requests.get', response)
    assert download_image('https://example.test/avatar') == expected
    assert closed == [True]


def test_image_timeout_and_absent_url(monkeypatch):
    import requests
    get = Mock(side_effect=requests.Timeout())
    monkeypatch.setattr('controller.mastodon.profile.requests.get', get)
    assert download_image(None) is None
    get.assert_not_called()
    assert download_image('https://example.test/avatar') is None


@pytest.mark.parametrize('refresh_fails', [False, True])
def test_action_refresh_updates_same_dialog_and_keeps_actions_focus(monkeypatch, account, refresh_fails):
    import wx
    from wxUI.dialogs.mastodon import showUserProfile as module
    monkeypatch.setattr('builtins._', lambda text: text, raising=False)
    speech, messages = Mock(), Mock()
    monkeypatch.setattr(module.output, 'speak', speech)
    monkeypatch.setattr(wx, 'MessageBox', messages)
    app = wx.App.Get() or wx.App()
    work, ui = [], []
    session = Mock()
    controller = ProfileController(session, Mock(), work.append,
        lambda callback, *args: ui.append(lambda: callback(*args)), download=Mock(return_value=None))
    data = format_profile(account)
    data.actions = frozenset({'follow', 'mute', 'block'})
    session.get_own_account_id.return_value = 99
    session.get_profile_relationship.side_effect = [{}, {'following': True}]
    dialog = module.ShowUserProfile(account, session=session, controller=controller, profile_data=data)
    try:
        work.pop(0)()
        ui.pop(0)()
        dialog.Show()
        dialog.action_buttons['follow'].SetFocus()
        wx.Yield()
        name_control = dialog.name_ctrl
        dialog.on_user_action('follow')
        work.pop(0)()
        ui.pop(0)()
        session.perform_user_action.assert_called_once_with('follow', 12)
        if refresh_fails:
            session.get_profile.side_effect = RuntimeError('offline')
        else:
            session.get_profile.return_value = SimpleNamespace(**dict(vars(account), display_name='Updated Alice', fields=[]))
        work.pop(0)()
        ui.pop(0)()
        wx.Yield()
        expected = dialog.action_buttons['follow' if refresh_fails else 'unfollow']
        assert wx.Window.FindFocus() is expected
        assert dialog.name_ctrl is name_control
        assert name_control.GetValue() == ('Alice' if refresh_fails else 'Updated Alice')
        messages.assert_not_called()
        assert speech.call_count == (2 if refresh_fails else 1)
    finally:
        dialog.Destroy()
        app.ProcessPendingEvents()


@pytest.mark.parametrize('action', ['unfollow', 'block'])
def test_sensitive_action_can_be_cancelled_before_network(monkeypatch, action):
    from controller.mastodon import userActions as module
    monkeypatch.setattr('builtins._', lambda text: text, raising=False)
    dialog, confirmation = Mock(), Mock()
    dialog.get_response.return_value = module.widgetUtils.OK
    dialog.get_action.return_value = action
    dialog.get_user.return_value = 'alice'
    confirmation.ShowModal.return_value = module.wx.ID_NO
    monkeypatch.setattr(module.userActions, 'create_dialog', lambda self, users: setattr(self, 'dialog', dialog))
    monkeypatch.setattr(module.wx, 'MessageDialog', Mock(return_value=confirmation))
    session, execute = Mock(), Mock()
    selector = module.userActions(session, users=['alice'], execute=execute)
    assert not selector.started
    execute.assert_not_called()
    assert session.mock_calls == []
    confirmation.Destroy.assert_called_once()
    dialog.Destroy.assert_called_once()


@pytest.mark.parametrize('command,relationship', [
    ('follow', {}), ('unfollow', {'requested': True}),
    ('mute', {}), ('unmute', {'muting': True}),
    ('block', {}), ('unblock', {'blocking': True}),
])
def test_direct_profile_action_validates_relation_and_refreshes(harness, command, relationship):
    controller, session, view, work, ui = harness
    session.get_own_account_id.return_value = 99
    session.get_profile_relationship.return_value = relationship
    controller.act(command, 12)
    controller.act(command, 12)
    assert len(work) == 1
    session.perform_user_action.assert_not_called()
    work.pop()()
    session.perform_user_action.assert_called_once_with(command, 12)
    ui.pop()()
    view.finish_user_action.assert_called_once_with(None)
    assert len(work) == 1  # Refresh is separate; it never repeats the mutation.


def test_failed_direct_action_does_not_refresh(harness):
    controller, session, view, work, ui = harness
    session.get_own_account_id.return_value = 99
    session.get_profile_relationship.return_value = {}
    session.perform_user_action.side_effect = RuntimeError('offline')
    controller.act('follow', 12)
    work.pop()()
    ui.pop()()
    assert isinstance(view.finish_user_action.call_args.args[0], RuntimeError)
    assert not work
