from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from configobj import ConfigObj
from sessions.blueski.session import Session
from sessions.session_exceptions import AlreadyAuthorisedError, RequireCredentialsSessionError
from sessions.blueski import session as session_module


@pytest.fixture
def session(monkeypatch):
    monkeypatch.setattr('languageHandler.curLang', 'en')
    monkeypatch.setattr('builtins._', lambda text: text, raising=False)
    # Do not retain subscriptions between tests.
    monkeypatch.setattr('sessions.blueski.session.pub.subscribe', Mock())
    s = Session('testing')
    s.settings = ConfigObj({'blueski': {'handle': 'alice.test', 'app_password': 'fake'}, 'general': {}})
    s.settings.write = Mock()
    s.api = Mock(me=None)
    s.api.export_session_string.return_value = 'fake-session'
    return s


def test_login_caches_identity_and_saves_session(session):
    def login(handle, password):
        session.api.me = SimpleNamespace(handle=handle, did='did:plc:alice')
    session.api.login.side_effect = login
    session.login()
    assert session.logged
    assert session.db['user_id'] == 'did:plc:alice'
    assert session.settings['blueski']['session_string'] == 'fake-session'
    session.settings.write.assert_called_once()


def test_resume_avoids_password_login(session):
    session.settings['blueski']['session_string'] = 'saved'
    session.settings['blueski']['app_password'] = ''
    session.api.me = SimpleNamespace(handle='alice.test', did='did:plc:alice')
    session.login()
    session.api.import_session_string.assert_called_once_with('saved')
    session.api.login.assert_not_called()
    assert session.logged


def test_missing_credentials_does_not_call_client(session):
    session.settings['blueski']['app_password'] = ''
    with pytest.raises(RequireCredentialsSessionError):
        session.login()
    assert not session.logged
    session.api.login.assert_not_called()


def test_login_failure_does_not_save_success(session):
    session.api.login.side_effect = RuntimeError('rejected')
    with pytest.raises(RuntimeError, match='rejected'):
        session.login()
    assert not session.logged
    session.settings.write.assert_not_called()


@pytest.fixture
def authorization_ui(session, monkeypatch):
    handle = Mock()
    handle.ShowModal.return_value = session_module.wx.ID_OK
    handle.GetValue.return_value = '  alice.test  '
    password = Mock()
    password.ShowModal.return_value = session_module.wx.ID_OK
    password.GetValue.return_value = '  fake-password  '
    password_factory = Mock(return_value=password)
    monkeypatch.setattr(session_module.wx, 'TextEntryDialog', Mock(return_value=handle))
    monkeypatch.setattr(session_module.wx, 'PasswordEntryDialog', password_factory)
    error = Mock()
    monkeypatch.setattr(session_module.wx, 'MessageBox', error)
    # Authorization owns folder/config setup today. Keep these effects isolated;
    # real configuration I/O is exercised separately by migration tests below.
    monkeypatch.setattr(session, 'create_session_folder', Mock())
    monkeypatch.setattr(session, 'get_configuration', Mock())
    return SimpleNamespace(handle=handle, password=password,
                           password_factory=password_factory, error=error)


@pytest.mark.parametrize('cancel_at', ['handle', 'password'])
def test_authorization_cancellation_has_no_account_side_effects(session, authorization_ui, cancel_at):
    before = session.settings.dict()
    getattr(authorization_ui, cancel_at).ShowModal.return_value = session_module.wx.ID_CANCEL
    assert session.authorise() is None
    assert session.settings.dict() == before
    assert not session.logged
    session.settings.write.assert_not_called()
    session.create_session_folder.assert_not_called()
    session.get_configuration.assert_not_called()
    session.api.login.assert_not_called()
    authorization_ui.handle.Destroy.assert_called_once()
    if cancel_at == 'handle':
        authorization_ui.password_factory.assert_not_called()
    else:
        authorization_ui.password.Destroy.assert_called_once()
    authorization_ui.error.assert_not_called()


def test_authorization_success_uses_entered_credentials(session, authorization_ui):
    def login(handle, password):
        session.api.me = SimpleNamespace(handle=handle, did='did:plc:alice')
    session.api.login.side_effect = login
    assert session.authorise() is True
    session.api.login.assert_called_once_with('alice.test', 'fake-password')
    assert session.logged
    assert session.settings['blueski']['did'] == 'did:plc:alice'
    session.create_session_folder.assert_called_once()
    session.get_configuration.assert_called_once()
    authorization_ui.handle.Destroy.assert_called_once()
    authorization_ui.password.Destroy.assert_called_once()
    authorization_ui.error.assert_not_called()


def test_authorization_rejection_reports_error_and_does_not_activate(session, authorization_ui):
    session.api.login.side_effect = RuntimeError('rejected')
    assert session.authorise() is False
    assert not session.logged
    assert 'did' not in session.settings['blueski']
    authorization_ui.error.assert_called_once()
    # Characterize current behavior: credentials are written BEFORE login.
    # Transactional authorization would be a separate behavior change.
    assert session.settings['blueski']['app_password'] == 'fake-password'
    session.settings.write.assert_called_once()


def test_authorization_already_logged_does_not_prompt(session, authorization_ui):
    session.logged = True
    with pytest.raises(AlreadyAuthorisedError):
        session.authorise()
    authorization_ui.handle.ShowModal.assert_not_called()
    session.settings.write.assert_not_called()


@pytest.fixture
def legacy_config(session, tmp_path):
    config = ConfigObj()
    config.filename = str(tmp_path / 'session.conf')
    config['atprotosocial'] = {'handle': 'alice.test', 'app_password': 'fake', 'custom': 'keep'}
    config['templates'] = {'post': 'My custom $safe_text'}
    config['general'] = {'max_posts_per_call': '23'}
    config.write()
    session.settings = config
    return config


def test_namespace_migration_preserves_custom_values_and_is_idempotent(session, legacy_config, monkeypatch):
    session._ensure_settings_namespace()
    saved = ConfigObj(legacy_config.filename)
    assert 'atprotosocial' not in saved
    assert saved['blueski'] == {'handle': 'alice.test', 'app_password': 'fake', 'custom': 'keep'}
    assert saved['templates']['post'] == 'My custom $safe_text'
    assert saved['general']['max_posts_per_call'] == '23'
    original_bytes = Path(legacy_config.filename).read_bytes()
    write = Mock(wraps=legacy_config.write)
    monkeypatch.setattr(legacy_config, 'write', write)
    session._ensure_settings_namespace()
    write.assert_not_called()
    assert Path(legacy_config.filename).read_bytes() == original_bytes


def test_existing_namespace_is_not_overwritten(session, legacy_config):
    legacy_config['blueski'] = {'handle': 'current.test', 'custom': 'current'}
    legacy_config.write()
    session._ensure_settings_namespace()
    saved = ConfigObj(legacy_config.filename)
    assert saved['blueski']['handle'] == 'current.test'
    assert saved['atprotosocial']['handle'] == 'alice.test'


@pytest.mark.parametrize('old_template', [
    '$display_name, $safe_text $date.',
    '$display_name, $reply_to$safe_text $date.',
])
def test_old_default_template_upgrades_and_persists(session, legacy_config, old_template):
    legacy_config['templates']['post'] = old_template
    session._ensure_settings_namespace()
    saved = ConfigObj(legacy_config.filename)
    assert saved['templates']['post'] == '$display_name, $reply_to$safe_text $image_descriptions $date.'


def test_failed_migration_write_preserves_file_but_changes_memory(session, legacy_config, monkeypatch):
    path = Path(legacy_config.filename)
    original = path.read_bytes()
    write = Mock(side_effect=OSError('write denied'))
    monkeypatch.setattr(legacy_config, 'write', write)
    session._ensure_settings_namespace()
    write.assert_called_once()
    assert path.read_bytes() == original
    assert 'atprotosocial' in ConfigObj(str(path))
    # Existing implementation swallows write failures and migrates in memory.
    assert 'atprotosocial' not in session.settings
    assert session.settings['blueski']['custom'] == 'keep'
    session._ensure_settings_namespace()
    # It currently does not retry persistence on a second invocation.
    write.assert_called_once()
