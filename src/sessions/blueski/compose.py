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

    Args:
        post: dict or ATProto model object (FeedViewPost or PostView)
        db: Session database dict
        settings: Session settings
        relative_times: If True, use relative time formatting
        show_screen_names: If True, show only @handle instead of display name
        safe: If True, handle exceptions gracefully

    Returns:
        List of strings: [User, Text, Date, Source]
    """
    def g(obj, key, default=None):
        """Helper to get attribute from dict or object."""
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    # Resolve Post View or Feed View structure
    # Feed items have .post field, direct post objects don't
    actual_post = g(post, "post", post)

    record = g(actual_post, "record", {})
    author = g(actual_post, "author", {})

    # Author
    handle = g(author, "handle", "")
    display_name = g(author, "displayName") or g(author, "display_name") or handle or "Unknown"

    if show_screen_names:
        user_str = f"@{handle}"
    else:
        if handle and display_name != handle:
            user_str = f"{display_name} (@{handle})"
        else:
            user_str = f"@{handle}"

    # Text
    text = g(record, "text", "")

    # Repost reason
    reason = g(post, "reason", None)
    if reason:
        rtype = g(reason, "$type") or g(reason, "py_type")
        if rtype and "reasonRepost" in rtype:
            by = g(reason, "by", {})
            by_handle = g(by, "handle", "")
            reason_line = _("Reposted by @{handle}").format(handle=by_handle) if by_handle else _("Reposted")
            text = f"{reason_line}\n{text}" if text else reason_line

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
                text += f"\n[{len(images)} {_('Images')}]"

        # Quote posts
        quote_rec = None
        if etype and ("recordWithMedia" in etype):
            rec_embed = g(embed, "record", {})
            if rec_embed:
                quote_rec = g(rec_embed, "record", None) or rec_embed
            # Media in wrapper
            media = g(embed, "media", {})
            mtype = g(media, "$type") or g(media, "py_type")
            if mtype and "images" in mtype:
                images = g(media, "images", [])
                if images:
                    text += f"\n[{len(images)} {_('Images')}]"

        elif etype and ("record" in etype):
            quote_rec = g(embed, "record", {})
            if isinstance(quote_rec, dict):
                quote_rec = quote_rec.get("record") or quote_rec

        if quote_rec:
            qtype = g(quote_rec, "$type") or g(quote_rec, "py_type")

            if qtype and "viewNotFound" in qtype:
                text += f"\n[{_('Quoted post not found')}]"
            elif qtype and "viewBlocked" in qtype:
                text += f"\n[{_('Quoted post blocked')}]"
            elif qtype and "generatorView" in qtype:
                gen = g(quote_rec, "displayName", "Feed")
                text += f"\n[{_('Quoting Feed')}: {gen}]"
            else:
                q_author = g(quote_rec, "author", {})
                q_handle = g(q_author, "handle", "unknown")
                q_val = g(quote_rec, "value", {})
                q_text = g(q_val, "text", "")

                if q_text:
                    text += f"\n[{_('Quoting')} @{q_handle}: {q_text}]"
                else:
                    text += f"\n[{_('Quoting')} @{q_handle}]"

        elif etype and ("external" in etype):
            ext = g(embed, "external", {})
            title = g(ext, "title", "")
            text += f"\n[{_('Link')}: {title}]"

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
    
    # Viewer state (liked, reposted, etc.)
    viewer_indicators = []
    viewer = g(actual_post, "viewer") or g(post, "viewer")
    if viewer:
        if g(viewer, "like"):
            viewer_indicators.append("♥")  # Liked
        if g(viewer, "repost"):
            viewer_indicators.append("🔁")  # Reposted
    
    # Add viewer indicators to the source column or create a prefix for text
    if viewer_indicators:
        indicator_str = " ".join(viewer_indicators)
        # Add to beginning of text for visibility
        text = f"{indicator_str} {text}"

    return [user_str, text, ts_str, source]


def compose_notification(notification, db, settings, relative_times, show_screen_names=False, safe=True):
    """
    Compose a Bluesky notification into a list of strings for display.

    Args:
        notification: ATProto notification object
        db: Session database dict
        settings: Session settings
        relative_times: If True, use relative time formatting
        show_screen_names: If True, show only @handle
        safe: If True, handle exceptions gracefully

    Returns:
        List of strings: [User, Action/Text, Date]
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
        user_str = f"{display_name} (@{handle})"

    # Notification reason/type
    reason = g(notification, "reason", "unknown")

    # Map reason to user-readable text
    reason_text_map = {
        "like": _("liked your post"),
        "repost": _("reposted your post"),
        "follow": _("followed you"),
        "mention": _("mentioned you"),
        "reply": _("replied to you"),
        "quote": _("quoted your post"),
        "starterpack-joined": _("joined your starter pack"),
    }

    action_text = reason_text_map.get(reason, reason)

    # For mentions/replies/quotes, include snippet of the text
    record = g(notification, "record", {})
    post_text = g(record, "text", "")
    if post_text and reason in ["mention", "reply", "quote"]:
        snippet = post_text[:100] + "..." if len(post_text) > 100 else post_text
        action_text = f"{action_text}: {snippet}"

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

    return [user_str, action_text, ts_str]


def compose_user(user, db, settings, relative_times, show_screen_names=False, safe=True):
    """
    Compose a Bluesky user profile for list display.

    Args:
        user: User profile dict or ATProto model
        db: Session database dict
        settings: Session settings
        relative_times: If True, use relative time formatting
        show_screen_names: If True, show only @handle
        safe: If True, handle exceptions gracefully

    Returns:
        List of strings: [User summary]
    """
    def g(obj, key, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    handle = g(user, "handle", "unknown")
    display_name = g(user, "displayName") or g(user, "display_name") or handle
    followers = g(user, "followersCount", None)
    following = g(user, "followsCount", None)
    posts = g(user, "postsCount", None)
    created_at = g(user, "createdAt", None)

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
            ts = str(created_at)

    parts = [f"{display_name} (@{handle})."]
    if followers is not None and following is not None and posts is not None:
        parts.append(_("{followers} followers, {following} following, {posts} posts.").format(
            followers=followers, following=following, posts=posts
        ))
    if ts:
        parts.append(_("Joined {date}").format(date=ts))

    return [" ".join(parts).strip()]


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
