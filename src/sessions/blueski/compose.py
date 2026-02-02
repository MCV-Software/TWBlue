# -*- coding: utf-8 -*-
"""
Compose functions for Bluesky content display in TWBlue.

These functions format API data into user-readable strings for display in
list controls. They follow the TWBlue compose function pattern:
    compose_function(item, db, relative_times, show_screen_names, session)
    Returns a list of strings for display columns.
"""

import logging
import arrow
import languageHandler

log = logging.getLogger("sessions.blueski.compose")


def compose_post(post, db, settings, relative_times, show_screen_names=False, safe=True):
    """
    Compose a Bluesky post into a list of strings for display.
    Format matches Mastodon: [user+", ", text, date+", ", source]
    """
    def g(obj, key, default=None):
        """Helper to get attribute from dict or object."""
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    # Resolve Post View or Feed View structure
    actual_post = g(post, "post", post)
    record = g(actual_post, "record", {})
    author = g(actual_post, "author", {})

    # Original author info
    original_handle = g(author, "handle", "")
    original_display_name = g(author, "displayName") or g(author, "display_name") or original_handle or "Unknown"

    # Check if this is a repost
    reason = g(post, "reason", None)
    is_repost = False
    reposter_handle = ""
    reposter_display_name = ""

    if reason:
        rtype = g(reason, "$type") or g(reason, "py_type")
        if rtype and "reasonRepost" in rtype:
            is_repost = True
            by = g(reason, "by", {})
            reposter_handle = g(by, "handle", "")
            reposter_display_name = g(by, "displayName") or g(by, "display_name") or reposter_handle

    # User column: show reposter if repost, otherwise original author (like Mastodon)
    if is_repost and reposter_handle:
        if show_screen_names:
            user_str = f"@{reposter_handle}"
        else:
            if reposter_display_name and reposter_display_name != reposter_handle:
                user_str = f"{reposter_display_name} (@{reposter_handle})"
            else:
                user_str = f"@{reposter_handle}"
    else:
        if show_screen_names:
            user_str = f"@{original_handle}"
        else:
            if original_display_name and original_display_name != original_handle:
                user_str = f"{original_display_name} (@{original_handle})"
            else:
                user_str = f"@{original_handle}"

    # Text
    original_text = g(record, "text", "")

    # Build text - if repost, format like Mastodon: "Reposted from @original: text"
    if is_repost:
        text = _("Reposted from @{}: {}").format(original_handle, original_text)
    else:
        text = original_text

    # Check facets for links not visible in text and append them
    facets = g(record, "facets", []) or []
    hidden_urls = []
    for facet in facets:
        features = g(facet, "features", []) or []
        for feature in features:
            ftype = g(feature, "$type") or g(feature, "py_type") or ""
            if "link" in ftype.lower():
                uri = g(feature, "uri", "")
                if uri and uri not in text and uri not in hidden_urls:
                    # Check if a truncated version is in text (e.g., "example.com/path...")
                    # by checking if the domain is present
                    domain_match = False
                    try:
                        from urllib.parse import urlparse
                        parsed = urlparse(uri)
                        domain = parsed.netloc.replace("www.", "")
                        if domain and domain in text:
                            domain_match = True
                    except:
                        pass
                    if not domain_match:
                        hidden_urls.append(uri)

    if hidden_urls:
        text += " " + " ".join(f"[{url}]" for url in hidden_urls)

    # Labels / Content Warning
    labels = g(actual_post, "labels", [])
    cw_text = ""
    for label in labels:
        val = g(label, "val", "")
        if val in ["!warn", "porn", "sexual", "nudity", "gore", "graphic-media", "corpse", "self-harm", "hate", "spam", "impersonation"]:
            if not cw_text:
                cw_text = _("Sensitive Content")
        elif val.startswith("warn:"):
            cw_text = val.split("warn:", 1)[-1].strip()

    if cw_text:
        text = f"CW: {cw_text}\n\n{text}"

    # Embeds (Images, Quotes, Links)
    embed = g(actual_post, "embed", None)
    if embed:
        etype = g(embed, "$type") or g(embed, "py_type")

        # Images
        if etype and ("images" in etype):
            images = g(embed, "images", [])
            if images:
                text += f" [{len(images)} {_('images')}]"

        # Quote posts
        quote_rec = None
        if etype and ("recordWithMedia" in etype):
            rec_embed = g(embed, "record", {})
            if rec_embed:
                quote_rec = g(rec_embed, "record", None) or rec_embed
            media = g(embed, "media", {})
            mtype = g(media, "$type") or g(media, "py_type")
            if mtype and "images" in mtype:
                images = g(media, "images", [])
                if images:
                    text += f" [{len(images)} {_('images')}]"
            elif mtype and "external" in mtype:
                ext = g(media, "external", {})
                title = g(ext, "title", "")
                if title:
                    text += f" [{_('Link')}: {title}]"

        elif etype and ("record" in etype):
            quote_rec = g(embed, "record", {})
            if isinstance(quote_rec, dict):
                quote_rec = quote_rec.get("record") or quote_rec

        if quote_rec:
            qtype = g(quote_rec, "$type") or g(quote_rec, "py_type")
            if qtype and "viewNotFound" in qtype:
                text += f" [{_('Quoted post not found')}]"
            elif qtype and "viewBlocked" in qtype:
                text += f" [{_('Quoted post blocked')}]"
            elif qtype and "generatorView" in qtype:
                gen = g(quote_rec, "displayName", "Feed")
                text += f" [{_('Quoting Feed')}: {gen}]"
            else:
                q_author = g(quote_rec, "author", {})
                q_handle = g(q_author, "handle", "unknown")
                q_val = g(quote_rec, "value", {})
                q_text = g(q_val, "text", "")
                if q_text:
                    text += " " + _("Quoting @{}: {}").format(q_handle, q_text)
                else:
                    text += " " + _("Quoting @{}").format(q_handle)

        elif etype and ("external" in etype):
            ext = g(embed, "external", {})
            title = g(ext, "title", "")
            if title:
                text += f" [{_('Link')}: {title}]"

    # Date
    indexed_at = g(actual_post, "indexed_at", "") or g(actual_post, "indexedAt", "")
    ts_str = ""
    if indexed_at:
        try:
            ts = arrow.get(indexed_at)
            if relative_times:
                ts_str = ts.humanize(locale=languageHandler.curLang[:2])
            else:
                ts_str = ts.format(_("dddd, MMMM D, YYYY H:m"), locale=languageHandler.curLang[:2])
        except Exception:
            ts_str = str(indexed_at)[:16].replace("T", " ")

    # Source / Client
    source = "Bluesky"

    # Format like Mastodon: add ", " after user and date
    return [user_str + ", ", text, ts_str + ", ", source]


def compose_notification(notification, db, settings, relative_times, show_screen_names=False, safe=True):
    """
    Compose a Bluesky notification into a list of strings for display.
    Format matches Mastodon: [user, text, date]
    """
    def g(obj, key, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    # Author of the notification (who performed the action)
    author = g(notification, "author", {})
    handle = g(author, "handle", "unknown")
    display_name = g(author, "displayName") or g(author, "display_name") or handle

    if show_screen_names:
        user_str = f"@{handle}"
    else:
        if display_name and display_name != handle:
            user_str = f"{display_name} (@{handle})"
        else:
            user_str = f"@{handle}"

    # Notification reason/type
    reason = g(notification, "reason", "unknown")

    # Get post text if available
    record = g(notification, "record", {})
    post_text = g(record, "text", "")

    # Format like Mastodon: "{username} has action: {status}"
    if reason == "like":
        if post_text:
            text = _("{username} has added to favorites: {status}").format(username=user_str, status=post_text)
        else:
            text = _("{username} has added to favorites").format(username=user_str)
    elif reason == "repost":
        if post_text:
            text = _("{username} has reposted: {status}").format(username=user_str, status=post_text)
        else:
            text = _("{username} has reposted").format(username=user_str)
    elif reason == "follow":
        text = _("{username} has followed you.").format(username=user_str)
    elif reason == "mention":
        if post_text:
            text = _("{username} has mentioned you: {status}").format(username=user_str, status=post_text)
        else:
            text = _("{username} has mentioned you").format(username=user_str)
    elif reason == "reply":
        if post_text:
            text = _("{username} has replied: {status}").format(username=user_str, status=post_text)
        else:
            text = _("{username} has replied").format(username=user_str)
    elif reason == "quote":
        if post_text:
            text = _("{username} has quoted your post: {status}").format(username=user_str, status=post_text)
        else:
            text = _("{username} has quoted your post").format(username=user_str)
    elif reason == "starterpack-joined":
        text = _("{username} has joined your starter pack.").format(username=user_str)
    else:
        text = f"{user_str}: {reason}"

    # Date
    indexed_at = g(notification, "indexedAt", "") or g(notification, "indexed_at", "")
    ts_str = ""
    if indexed_at:
        try:
            ts = arrow.get(indexed_at)
            if relative_times:
                ts_str = ts.humanize(locale=languageHandler.curLang[:2])
            else:
                ts_str = ts.format(_("dddd, MMMM D, YYYY H:m"), locale=languageHandler.curLang[:2])
        except Exception:
            ts_str = str(indexed_at)[:16].replace("T", " ")

    return [user_str, text, ts_str]


def compose_user(user, db, settings, relative_times, show_screen_names=False, safe=True):
    """
    Compose a Bluesky user profile for list display.
    Format matches Mastodon: single string with all info.
    """
    def g(obj, key, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    def resolve_profile(obj):
        if g(obj, "handle") or g(obj, "did"):
            return obj
        for key in ("subject", "actor", "profile", "user"):
            nested = g(obj, key)
            if nested and (g(nested, "handle") or g(nested, "did")):
                return nested
        return obj

    profile = resolve_profile(user)
    handle = g(profile, "handle", "unknown")
    display_name = g(profile, "displayName") or g(profile, "display_name") or handle
    followers = g(profile, "followersCount") or g(profile, "followers_count") or 0
    following = g(profile, "followsCount") or g(profile, "follows_count") or 0
    posts = g(profile, "postsCount") or g(profile, "posts_count") or 0
    created_at = g(profile, "createdAt") or g(profile, "created_at")

    ts = ""
    if created_at:
        try:
            original_date = arrow.get(created_at)
            if relative_times:
                ts = original_date.humanize(locale=languageHandler.curLang[:2])
            else:
                offset = db.get("utc_offset", 0) if isinstance(db, dict) else 0
                ts = original_date.shift(hours=offset).format(_("dddd, MMMM D, YYYY H:m"), locale=languageHandler.curLang[:2])
        except Exception:
            ts = ""

    # Format like Mastodon: "Name (@handle). X followers, Y following, Z posts. Joined date"
    if ts:
        return [_("%s (@%s). %s followers, %s following, %s posts. Joined %s") % (display_name, handle, followers, following, posts, ts)]
    else:
        return [_("%s (@%s). %s followers, %s following, %s posts.") % (display_name, handle, followers, following, posts)]


def compose_convo(convo, db, settings, relative_times, show_screen_names=False, safe=True):
    """
    Compose a Bluesky chat conversation for list display.

    Args:
        convo: Conversation dict or ATProto model
        db: Session database dict
        settings: Session settings
        relative_times: If True, use relative time formatting
        show_screen_names: If True, show only @handle
        safe: If True, handle exceptions gracefully

    Returns:
        List of strings: [Participants, Last Message, Date]
    """
    def g(obj, key, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    members = g(convo, "members", [])
    self_did = db.get("user_id") if isinstance(db, dict) else None

    # Get other participants (exclude self)
    others = []
    for m in members:
        did = g(m, "did", None)
        if self_did and did == self_did:
            continue
        label = g(m, "displayName") or g(m, "display_name") or g(m, "handle", "unknown")
        others.append(label)

    if not others:
        others = [g(m, "displayName") or g(m, "display_name") or g(m, "handle", "unknown") for m in members]

    participants = ", ".join(others)

    # Last message
    last_msg_obj = g(convo, "lastMessage") or g(convo, "last_message")
    last_text = ""
    last_sender = ""

    if last_msg_obj:
        last_text = g(last_msg_obj, "text", "")
        sender = g(last_msg_obj, "sender", None)
        if sender:
            last_sender = g(sender, "displayName") or g(sender, "display_name") or g(sender, "handle", "")

    # Date
    date_str = ""
    if last_msg_obj:
        sent_at = g(last_msg_obj, "sentAt") or g(last_msg_obj, "sent_at")
        if sent_at:
            try:
                ts = arrow.get(sent_at)
                if relative_times:
                    date_str = ts.humanize(locale=languageHandler.curLang[:2])
                else:
                    date_str = ts.format(_("dddd, MMMM D, YYYY H:m"), locale=languageHandler.curLang[:2])
            except Exception:
                date_str = str(sent_at)[:16]

    if last_sender and last_text:
        last_text = _("Last message from {user}: {text}").format(user=last_sender, text=last_text)
    elif last_text:
        last_text = _("Last message: {text}").format(text=last_text)

    return [participants, last_text, date_str]


def compose_chat_message(msg, db, settings, relative_times, show_screen_names=False, safe=True):
    """
    Compose an individual chat message for display.

    Args:
        msg: Chat message dict or ATProto model
        db: Session database dict
        settings: Session settings
        relative_times: If True, use relative time formatting
        show_screen_names: If True, show only @handle
        safe: If True, handle exceptions gracefully

    Returns:
        List of strings: [Sender, Text, Date]
    """
    def g(obj, key, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    sender = g(msg, "sender", {})
    handle = g(sender, "displayName") or g(sender, "display_name") or g(sender, "handle", "unknown")

    text = g(msg, "text", "")

    # Date
    sent_at = g(msg, "sentAt") or g(msg, "sent_at")
    date_str = ""
    if sent_at:
        try:
            ts = arrow.get(sent_at)
            if relative_times:
                date_str = ts.humanize(locale=languageHandler.curLang[:2])
            else:
                date_str = ts.format(_("dddd, MMMM D, YYYY H:m"), locale=languageHandler.curLang[:2])
        except Exception:
            date_str = str(sent_at)[:16]

    return [handle, text, date_str]
