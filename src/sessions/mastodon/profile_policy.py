"""Relationship actions offered by a Mastodon profile, without UI dependencies."""


def available_profile_actions(account_id, own_id, relationship):
    if account_id is None or str(account_id) == str(own_id) or relationship is None:
        return frozenset()
    def flag(key):
        return bool(relationship.get(key)) if isinstance(relationship, dict) else bool(getattr(relationship, key, False))
    if flag('blocking'):
        return frozenset({'unblock'})
    actions = {'block'}
    if not flag('blocked_by'):
        actions.add('unfollow' if flag('following') or flag('requested') else 'follow')
        actions.add('unmute' if flag('muting') else 'mute')
    return frozenset(actions)
