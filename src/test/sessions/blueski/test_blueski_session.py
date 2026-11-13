from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from configobj import ConfigObj
from sessions.blueski.session import Session
from sessions.session_exceptions import RequireCredentialsSessionError


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
