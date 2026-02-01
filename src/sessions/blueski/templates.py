# -*- coding: utf-8 -*-
import arrow
import languageHandler
from string import Template


post_variables = [
    "date",
    "display_name",
    "screen_name",
    "source",
    "lang",
    "safe_text",
    "text",
    "image_descriptions",
    "visibility",
    "pinned",
]
person_variables = [
    "display_name",
    "screen_name",
    "description",
    "followers",
    "following",
    "favorites",
    "posts",
    "created_at",
]
notification_variables = ["display_name", "screen_name", "text", "date"]


def _g(obj, key, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _extract_labels(obj):
    labels = _g(obj, "labels", None)
    if labels is None:
        return []
    if isinstance(labels, dict):
        return labels.get("values", []) or []
    if isinstance(labels, list):
        return labels
    return []


def _extract_cw_text(post, record):
    labels = _extract_labels(post) + _extract_labels(record)
    for label in labels:
        val = _g(label, "val", "")
        if val == "warn":
            return _("Sensitive Content")
        if isinstance(val, str) and val.startswith("warn:"):
            return val.split("warn:", 1)[-1].strip()
    return ""


def _extract_image_descriptions(post, record):
    def collect_images(embed):
        if not embed:
            return []
        etype = _g(embed, "$type") or _g(embed, "py_type") or ""
        if "recordWithMedia" in etype:
            media = _g(embed, "media")
            mtype = _g(media, "$type") or _g(media, "py_type") or ""
            if "images" in mtype:
                return list(_g(media, "images", []) or [])
            return []
        if "images" in etype:
            return list(_g(embed, "images", []) or [])
        return []

    images = []
    images.extend(collect_images(_g(post, "embed")))
    if not images:
        images.extend(collect_images(_g(record, "embed")))

    descriptions = []
    for idx, img in enumerate(images, start=1):
        alt = _g(img, "alt", "") or ""
        if alt:
            descriptions.append(_("Media description {index}: {alt}").format(index=idx, alt=alt))
    return "\n".join(descriptions)


def process_date(field, relative_times=True, offset_hours=0):
    original_date = arrow.get(field)
    if relative_times:
        return original_date.humanize(locale=languageHandler.curLang[:2])
    return original_date.shift(hours=offset_hours).format(_("dddd, MMMM D, YYYY H:m:s"), locale=languageHandler.curLang[:2])


def render_post(post, template, settings, relative_times=False, offset_hours=0):
    actual_post = _g(post, "post", post)
    record = _g(actual_post, "record") or _g(post, "record") or {}
    author = _g(actual_post, "author") or _g(post, "author") or {}

    reason = _g(post, "reason")
    is_repost = False
    reposter = None
    if reason:
        rtype = _g(reason, "$type") or _g(reason, "py_type") or ""
        if "reasonRepost" in rtype:
            is_repost = True
            reposter = _g(reason, "by")

    if is_repost and reposter:
        display_name = _g(reposter, "displayName") or _g(reposter, "display_name") or _g(reposter, "handle", "")
        screen_name = _g(reposter, "handle", "")
    else:
        display_name = _g(author, "displayName") or _g(author, "display_name") or _g(author, "handle", "")
        screen_name = _g(author, "handle", "")

    text = _g(record, "text", "") or ""
    if is_repost:
        original_handle = _g(author, "handle", "")
        text = _("Reposted from @{handle}: {text}").format(handle=original_handle, text=text)

    cw_text = _extract_cw_text(actual_post, record)
    safe_text = text
    if cw_text:
        safe_text = _("Content warning: {cw}").format(cw=cw_text)

    created_at = _g(record, "createdAt") or _g(record, "created_at")
    indexed_at = _g(actual_post, "indexedAt") or _g(actual_post, "indexed_at")
    date_field = created_at or indexed_at
    date = process_date(date_field, relative_times, offset_hours) if date_field else ""

    langs = _g(record, "langs") or _g(record, "languages") or []
    lang = langs[0] if isinstance(langs, list) and langs else ""

    image_descriptions = _extract_image_descriptions(actual_post, record)

    available_data = dict(
        date=date,
        display_name=display_name,
        screen_name=screen_name,
        source="Bluesky",
        lang=lang,
        safe_text=safe_text,
        text=text,
        image_descriptions=image_descriptions,
        visibility=_("Public"),
        pinned="",
    )
    return Template(_(template)).safe_substitute(**available_data)


def render_user(user, template, settings, relative_times=True, offset_hours=0):
    display_name = _g(user, "displayName") or _g(user, "display_name") or _g(user, "handle", "")
    screen_name = _g(user, "handle", "")
    description = _g(user, "description", "") or ""
    followers = _g(user, "followersCount", 0) or 0
    following = _g(user, "followsCount", 0) or 0
    posts = _g(user, "postsCount", 0) or 0
    created_at = _g(user, "createdAt")
    created = ""
    if created_at:
        created = process_date(created_at, relative_times, offset_hours)

    available_data = dict(
        display_name=display_name,
        screen_name=screen_name,
        description=description,
        followers=followers,
        following=following,
        favorites="",
        posts=posts,
        created_at=created,
    )
    return Template(_(template)).safe_substitute(**available_data)


def render_notification(notification, template, post_template, settings, relative_times=False, offset_hours=0):
    author = _g(notification, "author") or {}
    display_name = _g(author, "displayName") or _g(author, "display_name") or _g(author, "handle", "")
    screen_name = _g(author, "handle", "")
    reason = _g(notification, "reason", "unknown")
    record = _g(notification, "record") or {}
    post_text = _g(record, "text", "") or ""

    if reason == "like":
        text = _("{username} has added to favorites: {status}").format(
            username=display_name, status=post_text
        ) if post_text else _("{username} has added to favorites").format(username=display_name)
    elif reason == "repost":
        text = _("{username} has reposted: {status}").format(
            username=display_name, status=post_text
        ) if post_text else _("{username} has reposted").format(username=display_name)
    elif reason == "follow":
        text = _("{username} has followed you.").format(username=display_name)
    elif reason == "mention":
        text = _("{username} has mentioned you: {status}").format(
            username=display_name, status=post_text
        ) if post_text else _("{username} has mentioned you").format(username=display_name)
    elif reason == "reply":
        text = _("{username} has replied: {status}").format(
            username=display_name, status=post_text
        ) if post_text else _("{username} has replied").format(username=display_name)
    elif reason == "quote":
        text = _("{username} has quoted your post: {status}").format(
            username=display_name, status=post_text
        ) if post_text else _("{username} has quoted your post").format(username=display_name)
    else:
        text = "{user}: {reason}".format(user=display_name or screen_name, reason=reason)

    indexed_at = _g(notification, "indexedAt") or _g(notification, "indexed_at")
    date = process_date(indexed_at, relative_times, offset_hours) if indexed_at else ""

    available_data = dict(
        display_name=display_name,
        screen_name=screen_name,
        text=text,
        date=date,
    )
    return Template(_(template)).safe_substitute(**available_data)
