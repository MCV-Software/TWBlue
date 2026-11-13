"""Available relationship actions, independent of presentation and wx."""


def available_profile_actions(did, own_did, viewer):
    if not did or did == own_did:
        return frozenset()
    blocking = bool(viewer.get('blocking'))
    actions = {'unblock_user' if blocking else 'block_user'}
    if not blocking and not viewer.get('blockedBy'):
        actions.add('unfollow_user' if viewer.get('following') else 'follow_user')
        actions.add('unmute_user' if viewer.get('muted') else 'mute_user')
    return frozenset(actions)
