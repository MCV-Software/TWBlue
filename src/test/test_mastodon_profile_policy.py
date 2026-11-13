from itertools import product
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from sessions.mastodon.profile_policy import available_profile_actions
from sessions.mastodon.session import Session
from sessions.gotosocial.session import Session as GoToSocialSession


@pytest.mark.parametrize('following,requested,muting,blocking,blocked_by', list(product([False, True], repeat=5)))
def test_relationship_combinations(following, requested, muting, blocking, blocked_by):
    relation = dict(following=following, requested=requested, muting=muting,
                    blocking=blocking, blocked_by=blocked_by)
    expected = {'unblock'} if blocking else {'block'}
    if not blocking and not blocked_by:
        expected |= {'unfollow' if following or requested else 'follow',
                     'unmute' if muting else 'mute'}
    assert available_profile_actions(12, 99, relation) == expected
    assert available_profile_actions(12, 99, SimpleNamespace(**relation)) == expected


def test_self_and_unknown_relationship_offer_no_actions():
    assert not available_profile_actions('12', 12, {})
    assert not available_profile_actions(12, 99, None)


@pytest.mark.parametrize('session_type', [Session, GoToSocialSession])
def test_relationship_query_and_own_identity(session_type):
    session = session_type.__new__(session_type)
    session.api = Mock()
    session.db = {'user_id': 99}
    session.api.account_relationships.return_value = [{'following': True}]
    assert session.get_own_account_id() == 99
    assert session.get_profile_relationship(12) == {'following': True}
    session.api.account_relationships.assert_called_once_with(12)
    session.api.account_relationships.return_value = []
    with pytest.raises(RuntimeError):
        session.get_profile_relationship(12)
