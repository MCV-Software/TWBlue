"""Prepare Mastodon profile values without depending on wx."""
from types import SimpleNamespace
from sessions.mastodon.utils import html_filter


def format_profile(user):
    def get(obj, key, default=None):
        return obj.get(key, default) if isinstance(obj, dict) else getattr(obj, key, default)
    values = {key: get(user, key, '') or '' for key in (
        'display_name', 'url', 'header', 'avatar')}
    values['note'] = html_filter(get(user, 'note', '') or '')
    created = get(user, 'created_at')
    values['joined'] = created.strftime('%d %B, %Y') if created else ''
    values['fields'] = [SimpleNamespace(name=html_filter(get(field, 'name', '') or ''),
                                       value=html_filter(get(field, 'value', '') or ''))
                        for field in get(user, 'fields', []) or []]
    for key in ('locked', 'bot', 'discoverable'):
        values[key] = bool(get(user, key))
    for key in ('statuses_count', 'following_count', 'followers_count'):
        values[key] = get(user, key, 0) or 0
    return SimpleNamespace(**values)
