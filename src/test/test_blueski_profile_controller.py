from unittest.mock import Mock

import pytest

from controller.blueski.profile import ProfileController
from controller.blueski.profile_format import format_profile


@pytest.fixture
def harness():
    session, view = Mock(), Mock()
    work, ui = [], []
    controller = ProfileController(session, view, work.append,
                                   lambda callback, *args: ui.append(lambda: callback(*args)))
    return controller, session, view, work, ui


@pytest.mark.parametrize('profile', [{'did': 'did:plc:alice', 'handle': 'alice.test'}, None])
def test_profile_result_is_delivered_on_ui_dispatch(harness, profile):
    controller, session, view, work, ui = harness
    session.get_profile.return_value = profile
    controller.load('alice.test')
    view.show_profile_loading.assert_called_once()
    session.get_profile.assert_not_called()
    work.pop()()
    session.get_profile.assert_called_once_with('alice.test')
    view._apply_profile_data.assert_not_called()
    ui.pop()()
    view._apply_profile_data.assert_called_once_with(format_profile(profile) if profile else None)
    view._apply_profile_error.assert_not_called()


def test_query_error_is_delivered_to_view(harness):
    controller, session, view, work, ui = harness
    error = RuntimeError('offline')
    session.get_profile.side_effect = error
    controller.load('alice.test')
    work.pop()()
    ui.pop()()
    view._apply_profile_error.assert_called_once_with(error)
    view._apply_profile_data.assert_not_called()


@pytest.mark.parametrize('close_before_query', [False, True])
@pytest.mark.parametrize('failed', [False, True])
def test_closed_view_receives_no_late_result(harness, close_before_query, failed):
    controller, session, view, work, ui = harness
    if failed:
        session.get_profile.side_effect = RuntimeError('offline')
    controller.load('alice.test')
    if close_before_query:
        controller.close()
    work.pop()()
    controller.close()
    ui.pop()()
    view._apply_profile_data.assert_not_called()
    view._apply_profile_error.assert_not_called()
    controller.load('another.test')
    assert not work


def test_reloading_ignores_previous_query(harness):
    controller, session, view, work, ui = harness
    session.get_profile.side_effect = [{'handle': 'old'}, {'handle': 'new'}]
    controller.load('old.test')
    controller.load('new.test')
    for query in work:
        query()
    for callback in ui:
        callback()
    view._apply_profile_data.assert_called_once_with(format_profile({'handle': 'new'}))


@pytest.mark.parametrize('command,argument', [
    ('follow_user', 'did:alice'), ('unfollow_user', 'at://follow'),
    ('mute_user', 'did:alice'), ('unmute_user', 'did:alice'),
    ('block_user', 'did:alice'), ('unblock_user', 'at://block'),
])
def test_actions_run_in_worker_and_refresh_profile(harness, command, argument):
    controller, session, view, work, ui = harness
    session.get_profile.return_value = {'did': 'did:alice', 'handle': 'alice.test'}
    controller.act(command, 'did:alice', {'following': 'at://follow', 'blocking': 'at://block'}, 'alice.test')
    controller.act(command, 'did:alice', {}, 'alice.test')
    assert len(work) == 1  # Ignore repeated clicks while pending.
    getattr(session, command).assert_not_called()
    work.pop()()
    getattr(session, command).assert_called_once_with(argument)
    view.finish_user_action.assert_not_called()
    ui.pop()()
    view.finish_user_action.assert_called_once_with(None)
    work.pop()()
    ui.pop()()
    view._apply_profile_data.assert_called_once_with(format_profile(session.get_profile.return_value))


@pytest.mark.parametrize('command,viewer', [('unfollow_user', {}), ('unblock_user', {}), ('unknown', {})])
def test_invalid_action_does_not_mutate_session(harness, command, viewer):
    controller, session, view, work, ui = harness
    controller.act(command, 'did:alice', viewer, 'alice.test')
    work.pop()()
    ui.pop()()
    assert isinstance(view.finish_user_action.call_args.args[0], RuntimeError)
    assert session.mock_calls == []
    assert not work


@pytest.mark.parametrize('raises', [False, True])
def test_action_failure_allows_retry_without_refresh(harness, raises):
    controller, session, view, work, ui = harness
    session.follow_user.return_value = False
    if raises:
        session.follow_user.side_effect = RuntimeError('offline')
    controller.act('follow_user', 'did:alice', {}, 'alice.test')
    work.pop()()
    ui.pop()()
    assert isinstance(view.finish_user_action.call_args.args[0], RuntimeError)
    assert not work
    controller.act('follow_user', 'did:alice', {}, 'alice.test')
    assert len(work) == 1


def test_images_and_action_results_are_ignored_after_close(harness):
    controller, session, view, work, ui = harness
    controller.download = Mock(side_effect=[b'banner', b'avatar'])
    controller.load_images('banner-url', 'avatar-url')
    controller.act('follow_user', 'did:alice', {}, 'alice.test')
    controller.close()
    for query in work:
        query()
    for callback in ui:
        callback()
    view._draw_images.assert_not_called()
    view.finish_user_action.assert_not_called()


def test_profile_images_are_delivered_together_on_ui(harness):
    controller, session, view, work, ui = harness
    controller.download = Mock(side_effect=[None, b'avatar'])
    controller.load_images(None, 'avatar-url')
    work.pop()()
    view._draw_images.assert_not_called()
    ui.pop()()
    view._draw_images.assert_called_once_with(None, b'avatar')


def test_profile_reload_discards_old_images(harness):
    controller, session, view, work, ui = harness
    controller.download = Mock(return_value=b'old')
    controller.load_images('banner', 'avatar')
    work.pop()()
    controller.load('new.test')
    ui.pop()()
    view._draw_images.assert_not_called()


@pytest.mark.parametrize('status,expected', [(200, b'image'), (404, None)])
def test_image_download_transport(monkeypatch, status, expected):
    from controller.blueski.profile import download_image
    response = Mock(status_code=status, content=b'image')
    context = Mock()
    context.__enter__ = Mock(return_value=response)
    context.__exit__ = Mock(return_value=False)
    get = Mock(return_value=context)
    monkeypatch.setattr('controller.blueski.profile.requests.get', get)
    assert download_image('https://example.test/image') == expected
    get.assert_called_once_with('https://example.test/image', timeout=10)
    context.__exit__.assert_called_once()


def test_image_timeout_or_missing_url_does_not_fail_profile(monkeypatch):
    from controller.blueski.profile import download_image
    import requests
    get = Mock(side_effect=requests.Timeout())
    monkeypatch.setattr('controller.blueski.profile.requests.get', get)
    assert download_image(None) is None
    get.assert_not_called()
    assert download_image('https://example.test/image') is None
