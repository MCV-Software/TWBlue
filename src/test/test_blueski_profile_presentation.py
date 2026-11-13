from types import SimpleNamespace
from itertools import product

import pytest

from controller.blueski.profile_format import format_profile
from sessions.blueski.profile_policy import available_profile_actions


@pytest.mark.parametrize('as_object', [False, True])
def test_format_handles_sdk_aliases_without_gui(as_object):
    data = dict(did='did:alice', handle='alice.test', display_name='Alice',
                followers_count=0, follows_count=3, posts_count=4,
                viewer=SimpleNamespace(following='at://follow', blocked_by=True))
    result = format_profile(SimpleNamespace(**data) if as_object else data)
    assert result['displayName'] == 'Alice'
    assert result['followersCount'] == 0
    assert result['followsCount'] == 3
    assert result['postsCount'] == 4
    assert result['viewer']['following'] == 'at://follow'
    assert result['viewer']['blockedBy'] is True
    assert result['avatar'] is None


def test_format_missing_fields_and_handle_fallback():
    assert format_profile({'handle': 'alice.test'})['displayName'] == 'alice.test'
    assert format_profile({})['viewer']['blocking'] is None


@pytest.mark.parametrize('following,muted,blocking,blocked_by', list(product([False, True], repeat=4)))
def test_relationship_policy(following, muted, blocking, blocked_by):
    actions = available_profile_actions('did:alice', 'did:own', {
        'following': following, 'muted': muted, 'blocking': blocking, 'blockedBy': blocked_by})
    assert ('unblock_user' in actions) == blocking
    assert ('block_user' in actions) == (not blocking)
    expected = {'unblock_user' if blocking else 'block_user'}
    if not blocking and not blocked_by:
        expected |= {'unfollow_user' if following else 'follow_user',
                     'unmute_user' if muted else 'mute_user'}
    assert actions == expected


@pytest.mark.parametrize('did', [None, '', 'did:own'])
def test_no_relationship_actions_for_missing_or_own_identity(did):
    assert not available_profile_actions(did, 'did:own', {})
