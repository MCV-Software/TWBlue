# -*- coding: utf-8 -*-
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any
from datetime import datetime
import arrow
import languageHandler

if TYPE_CHECKING:
    from sessions.blueski.session import Session as BlueskiSession
    from atproto.xrpc_client import models # For type hinting ATProto models

logger = logging.getLogger(__name__)

# For SUPPORTED_LANG_CHOICES in composeDialog.py
SUPPORTED_LANG_CHOICES_COMPOSE = {
    _("English"): "en", _("Spanish"): "es", _("French"): "fr", _("German"): "de",
    _("Japanese"): "ja", _("Portuguese"): "pt", _("Russian"): "ru", _("Chinese"): "zh",
}


class BlueskiCompose:
    MAX_CHARS = 300
    MAX_MEDIA_ATTACHMENTS = 4
    MAX_LANGUAGES = 3
    MAX_IMAGE_SIZE_BYTES = 1_000_000

    def __init__(self, session: BlueskiSession) -> None:
        self.session = session
        self.supported_media_types: list[str] = ["image/jpeg", "image/png"]
        self.max_image_size_bytes: int = self.MAX_IMAGE_SIZE_BYTES

    def get_panel_configuration(self) -> dict[str, Any]:
        """Returns configuration for the compose panel specific to Blueski."""
        return {
            "max_chars": self.MAX_CHARS,
            "max_media_attachments": self.MAX_MEDIA_ATTACHMENTS,
            "supports_content_warning": True,
            "supports_scheduled_posts": False,
            "supported_media_types": self.supported_media_types,
            "max_media_size_bytes": self.max_image_size_bytes,
            "supports_alternative_text": True,
            "sensitive_reasons_options": self.session.get_sensitive_reason_options(),
            "supports_language_selection": True,
            "max_languages": self.MAX_LANGUAGES,
            "supports_quoting": True,
            "supports_polls": False,
        }

    async def get_quote_text(self, message_id: str, url: str) -> str | None:
        return ""

    async def get_reply_text(self, message_id: str, author_handle: str) -> str | None:
        if not author_handle.startswith("@"):
            return f"@{author_handle} "
        return f"{author_handle} "

    def get_text_formatting_rules(self) -> dict[str, Any]:
        return {
            "markdown_enabled": False,
            "custom_emojis_enabled": False,
            "max_length": self.MAX_CHARS,
            "line_break_char": "\n",
            "link_format": "Full URL (e.g., https://example.com)",
            "mention_format": "@handle.bsky.social",
            "tag_format": "#tag (becomes a facet link)",
        }

    def is_media_type_supported(self, mime_type: str) -> bool:
        return mime_type.lower() in self.supported_media_types

    def get_max_schedule_date(self) -> str | None:
        return None

    def get_poll_configuration(self) -> dict[str, Any] | None:
        return None

    def compose_post_for_display(self, post_data: dict[str, Any], session_settings: dict[str, Any] | None = None) -> str:
        """
        Composes a string representation of a Bluesky post for display in UI timelines.
        """
        if not post_data or not isinstance(post_data, dict):
            return _("Invalid post data.")

        author_info = post_data.get("author", {})
        record = post_data.get("record", {})
        embed_data = post_data.get("embed")
        viewer_state = post_data.get("viewer", {})

        display_name = author_info.get("displayName", "") or author_info.get("handle", _("Unknown User"))
        handle = author_info.get("handle", _("unknown.handle"))

        post_text = getattr(record, 'text', '') if not isinstance(record, dict) else record.get('text', '')

        reason = post_data.get("reason")
        if reason:
            rtype = getattr(reason, "$type", "") if not isinstance(reason, dict) else reason.get("$type", "")
            if not rtype and not isinstance(reason, dict):
                rtype = getattr(reason, "py_type", "")
            if rtype and "reasonRepost" in rtype:
                by = getattr(reason, "by", None) if not isinstance(reason, dict) else reason.get("by")
                by_handle = getattr(by, "handle", "") if by and not isinstance(by, dict) else (by.get("handle", "") if by else "")
                reason_line = _("Reposted by @{handle}").format(handle=by_handle) if by_handle else _("Reposted")
                post_text = f"{reason_line}\n{post_text}" if post_text else reason_line

        created_at_str = getattr(record, 'createdAt', '') if not isinstance(record, dict) else record.get('createdAt', '')
        timestamp_str = ""
        if created_at_str:
            try:
                ts = arrow.get(created_at_str)
                timestamp_str = ts.format(_("dddd, MMMM D, YYYY H:m"), locale=languageHandler.curLang[:2])
            except Exception as e:
                logger.debug(f"Could not parse timestamp {created_at_str}: {e}")
                timestamp_str = created_at_str

        header = f"{display_name} (@{handle}) - {timestamp_str}"

        labels = post_data.get("labels", [])
        spoiler_text = None
        is_sensitive_post = False
        if labels:
            for label_obj in labels:
                label_val = getattr(label_obj, 'val', '') if not isinstance(label_obj, dict) else label_obj.get('val', '')
                if label_val == "!warn":
                    is_sensitive_post = True
                elif label_val in ["porn", "sexual", "nudity", "gore", "graphic-media", "corpse", "self-harm", "hate", "spam", "impersonation"]:
                    is_sensitive_post = True
                    if not spoiler_text: spoiler_text = _("Sensitive Content: {label}").format(label=label_val)
                elif label_val.startswith("warn:") and len(label_val) > 5:
                     spoiler_text = label_val.split("warn:", 1)[-1].strip()
                     is_sensitive_post = True

        post_text_display = post_text
        if spoiler_text:
            post_text_display = f"CW: {spoiler_text}\n\n{post_text}"
        elif is_sensitive_post and not spoiler_text:
            post_text_display = f"CW: {_('Sensitive Content')}\n\n{post_text}"

        embed_display = ""
        if embed_data:
            embed_type = getattr(embed_data, '$type', '')
            if not embed_type and isinstance(embed_data, dict): embed_type = embed_data.get('$type', '')

            if embed_type in ['app.bsky.embed.images#view', 'app.bsky.embed.images']:
                images = getattr(embed_data, 'images', []) if hasattr(embed_data, 'images') else embed_data.get('images', [])
                if images:
                    img_count = len(images)
                    alt_texts_present = any(getattr(img, 'alt', '') for img in images if hasattr(img, 'alt')) or \
                                        any(img_dict.get('alt', '') for img_dict in images if isinstance(img_dict, dict))
                    embed_display += f"\n[{img_count} Image"
                    if img_count > 1: embed_display += "s"
                    if alt_texts_present: embed_display += _(" (Alt text available)")
                    embed_display += "]"

            elif embed_type in ['app.bsky.embed.record#view', 'app.bsky.embed.record', 'app.bsky.embed.recordWithMedia#view', 'app.bsky.embed.recordWithMedia']:
                record_embed_data = getattr(embed_data, 'record', None) if hasattr(embed_data, 'record') else embed_data.get('record', None)
                if record_embed_data and isinstance(record_embed_data, dict):
                    record_embed_data = record_embed_data.get("record") or record_embed_data
                record_embed_type = getattr(record_embed_data, '$type', '')
                if not record_embed_type and isinstance(record_embed_data, dict): record_embed_type = record_embed_data.get('$type', '')

                if record_embed_type == 'app.bsky.embed.record#viewNotFound':
                    embed_display += f"\n[{_('Quoted post not found or unavailable')}]"
                elif record_embed_type == 'app.bsky.embed.record#viewBlocked':
                    embed_display += f"\n[{_('Content from the quoted account is blocked')}]"
                elif record_embed_data and (isinstance(record_embed_data, dict) or hasattr(record_embed_data, 'author')):
                    quote_author_info = getattr(record_embed_data, 'author', record_embed_data.get('author'))
                    quote_value = getattr(record_embed_data, 'value', record_embed_data.get('value'))

                    if quote_author_info and quote_value:
                        quote_author_handle = getattr(quote_author_info, 'handle', 'unknown')
                        quote_text_content = getattr(quote_value, 'text', '') if not isinstance(quote_value, dict) else quote_value.get('text', '')
                        quote_text_snippet = (quote_text_content[:75] + "...") if quote_text_content else _("post content")
                        embed_display += f"\n[ {_('Quote by')} @{quote_author_handle}: \"{quote_text_snippet}\" ]"
                    else:
                         embed_display += f"\n[{_('Quoted Post')}]"

            elif embed_type in ['app.bsky.embed.external#view', 'app.bsky.embed.external']:
                external_data = getattr(embed_data, 'external', None) if hasattr(embed_data, 'external') else embed_data.get('external', None)
                if external_data:
                    ext_uri = getattr(external_data, 'uri', _('External Link'))
                    ext_title = getattr(external_data, 'title', '') or ext_uri
                    embed_display += f"\n[{_('Link')}: {ext_title}]"

        reply_context_str = ""
        actual_record = post_data.get("record", {})
        reply_ref = getattr(actual_record, 'reply', None) if not isinstance(actual_record, dict) else actual_record.get('reply')

        if reply_ref:
            reply_context_str = f"[{_('In reply to a post')}] "

        counts_str_parts = []
        reply_count = post_data.get("replyCount", 0)
        repost_count = post_data.get("repostCount", 0)
        like_count = post_data.get("likeCount", 0)

        if reply_count > 0: counts_str_parts.append(f"{_('Replies')}: {reply_count}")
        if repost_count > 0: counts_str_parts.append(f"{_('Reposts')}: {repost_count}")
        if like_count > 0: counts_str_parts.append(f"{_('Likes')}: {like_count}")

        viewer_liked_uri = viewer_state.get("like") if isinstance(viewer_state, dict) else getattr(viewer_state, 'like', None)
        viewer_reposted_uri = viewer_state.get("repost") if isinstance(viewer_state, dict) else getattr(viewer_state, 'repost', None)

        if viewer_liked_uri: counts_str_parts.append(f"({_('Liked by you')})")
        if viewer_reposted_uri: counts_str_parts.append(f"({_('Reposted by you')})")

        counts_line = ""
        if counts_str_parts:
            counts_line = "\n" + " | ".join(counts_str_parts)

        full_display = f"{header}\n{reply_context_str}{post_text_display}{embed_display}{counts_line}"
        return full_display.strip()

    def compose_notification_for_display(self, notif_data: dict[str, Any]) -> str:
        """
        Composes a string representation of a Bluesky notification for display.

        Args:
            notif_data: A dictionary representing the notification,
                        typically from BlueskiSession._handle_*_notification methods
                        which create an approve.notifications.Notification object and then
                        convert it to dict or pass relevant parts.
                        Expected keys: 'title', 'body', 'author_name', 'timestamp_dt', 'kind'.
                        The 'title' usually already contains the core action.
        Returns:
            A formatted string for display.
        """
        if not notif_data or not isinstance(notif_data, dict):
            return _("Invalid notification data.")

        title = notif_data.get('title', _("Notification"))
        body = notif_data.get('body', '')
        author_name = notif_data.get('author_name') # Author of the action (e.g. who liked)
        timestamp_dt = notif_data.get('timestamp_dt') # datetime object

        timestamp_str = ""
        if timestamp_dt and isinstance(timestamp_dt, datetime):
            try:
                timestamp_str = timestamp_dt.strftime("%I:%M %p - %b %d, %Y")
            except Exception as e:
                logger.debug(f"Could not format notification timestamp {timestamp_dt}: {e}")
                timestamp_str = str(timestamp_dt)

        display_parts = []
        if timestamp_str:
            display_parts.append(f"[{timestamp_str}]")

        # Title already contains good info like "UserX liked your post"
        display_parts.append(title)

        if body: # Body might be text of a reply/mention/quote
            # Truncate body if too long for a list display
            body_snippet = (body[:100] + "...") if len(body) > 103 else body
            display_parts.append(f"\"{body_snippet}\"")

        return " ".join(display_parts).strip()


def compose_post(post, db, settings, relative_times, show_screen_names=False, safe=True):
    """
    Compose a Bluesky post into a list of strings [User, Text, Date, Source].
    post: dict or ATProto model object.
    """
    # Extract data using getattr for models or .get for dicts
    def g(obj, key, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    # Resolve Post View or Feed View structure
    # Feed items often have .post field. Direct post objects don't.
    actual_post = g(post, "post", post) 
    
    record = g(actual_post, "record", {})
    author = g(actual_post, "author", {})
    
    # Author
    handle = g(author, "handle", "")
    display_name = g(author, "displayName") or g(author, "display_name") or handle or "Unknown"
    
    if show_screen_names:
        user_str = f"@{handle}"
    else:
        # "Display Name (@handle)"
        if handle and display_name != handle:
            user_str = f"{display_name} (@{handle})"
        else:
            user_str = f"@{handle}"
    
    # Text
    text = g(record, "text", "")

    # Repost reason (so users know why they see an unfamiliar post)
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
    is_sensitive = False
    
    for label in labels:
        val = g(label, "val", "")
        if val in ["!warn", "porn", "sexual", "nudity", "gore", "graphic-media", "corpse", "self-harm", "hate", "spam", "impersonation"]:
            is_sensitive = True
            if not cw_text: cw_text = _("Sensitive Content")
        elif val.startswith("warn:"):
            is_sensitive = True
            cw_text = val.split("warn:", 1)[-1].strip()

    if cw_text:
        text = f"CW: {cw_text}\n\n{text}"
    
    # Embeds (Images, Quotes)
    embed = g(actual_post, "embed", None)
    if embed:
        etype = g(embed, "$type") or g(embed, "py_type")
        if etype and ("images" in etype):
            images = g(embed, "images", [])
            if images:
                text += f"\n[{len(images)} {_('Images')}]"
        
        # Handle Record (Quote) or RecordWithMedia (Quote + Media)
        quote_rec = None
        if etype and ("recordWithMedia" in etype):
             # Extract the nested record
             rec_embed = g(embed, "record", {})
             if rec_embed:
                 quote_rec = g(rec_embed, "record", None) or rec_embed
             # Also check for media in the wrapper
             media = g(embed, "media", {})
             mtype = g(media, "$type") or g(media, "py_type")
             if mtype and "images" in mtype:
                 images = g(media, "images", [])
                 if images: text += f"\n[{len(images)} {_('Images')}]"
                 
        elif etype and ("record" in etype):
             # Direct quote
             quote_rec = g(embed, "record", {})
             if isinstance(quote_rec, dict):
                 quote_rec = quote_rec.get("record") or quote_rec
        
        if quote_rec:
             # It is likely a ViewRecord
             # Check type (ViewRecord, ViewNotFound, ViewBlocked, etc)
             qtype = g(quote_rec, "$type") or g(quote_rec, "py_type")
             
             if qtype and "viewNotFound" in qtype:
                  text += f"\n[{_('Quoted post not found')}]"
             elif qtype and "viewBlocked" in qtype:
                  text += f"\n[{_('Quoted post blocked')}]"
             elif qtype and "generatorView" in qtype:
                  # Feed generator
                  gen = g(quote_rec, "displayName", "Feed")
                  text += f"\n[{_('Quoting Feed')}: {gen}]"
             else:
                  # Assume ViewRecord
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
            uri = g(ext, "uri", "")
            title = g(ext, "title", "")
            text += f"\n[{_('Link')}: {title}]"

    # Date
    indexed_at = g(actual_post, "indexed_at", "")
    ts_str = ""
    if indexed_at:
        try:
             # Try arrow parsing
             import arrow
             ts = arrow.get(indexed_at)
             if relative_times:
                 ts_str = ts.humanize(locale=languageHandler.curLang[:2])
             else:
                 ts_str = ts.format(_("dddd, MMMM D, YYYY H:m"), locale=languageHandler.curLang[:2])
        except Exception:
             ts_str = str(indexed_at)[:16].replace("T", " ")

    # Source (not always available in Bsky view, often just client)
    # We'll leave it empty or mock it if needed
    source = "Bluesky"


    return [user_str, text, ts_str, source]

def compose_user(user, db, settings, relative_times, show_screen_names=False, safe=True):
    """
    Compose a Bluesky user for list display.
    Returns: [User summary string]
    """
    # Extract data using getattr for models or .get for dicts
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
            import arrow
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
    Returns: [Participants, Last Message, Date]
    """
    def g(obj, key, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    members = g(convo, "members", [])
    self_did = db.get("user_id") if isinstance(db, dict) else None
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
    
    last_msg_obj = g(convo, "lastMessage") or g(convo, "last_message")
    last_text = ""
    last_sender = ""
    if last_msg_obj:
        last_text = g(last_msg_obj, "text", "")
        sender = g(last_msg_obj, "sender", None)
        if sender:
            last_sender = g(sender, "displayName") or g(sender, "display_name") or g(sender, "handle", "")
    
    # Date (using lastMessage.sentAt)
    date_str = ""
    sent_at = None
    if last_msg_obj:
        sent_at = g(last_msg_obj, "sentAt") or g(last_msg_obj, "sent_at")
        
    if sent_at:
        try:
            import arrow
            ts = arrow.get(sent_at)
            if relative_times:
                date_str = ts.humanize(locale=languageHandler.curLang[:2])
            else:
                date_str = ts.format(_("dddd, MMMM D, YYYY H:m"), locale=languageHandler.curLang[:2])
        except:
            date_str = str(sent_at)[:16]

    if last_sender and last_text:
        last_text = _("Last message from {user}: {text}").format(user=last_sender, text=last_text)
    elif last_text:
        last_text = _("Last message: {text}").format(text=last_text)

    return [participants, last_text, date_str]

def compose_chat_message(msg, db, settings, relative_times, show_screen_names=False, safe=True):
    """
    Compose an individual chat message for display in a thread.
    Returns: [Sender, Text, Date]
    """
    def g(obj, key, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    sender = g(msg, "sender", {})
    handle = g(sender, "displayName") or g(sender, "display_name") or g(sender, "handle", "unknown")
    
    text = g(msg, "text", "")
    
    sent_at = g(msg, "sentAt") or g(msg, "sent_at")
    date_str = ""
    if sent_at:
        try:
            import arrow
            ts = arrow.get(sent_at)
            if relative_times:
                date_str = ts.humanize(locale=languageHandler.curLang[:2])
            else:
                date_str = ts.format(_("dddd, MMMM D, YYYY H:m"), locale=languageHandler.curLang[:2])
        except:
            date_str = str(sent_at)[:16]
            
    return [handle, text, date_str]
