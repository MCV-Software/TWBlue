# -*- coding: utf-8 -*-
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any
from datetime import datetime

from approve.translation import translate as _
from approve.util import parse_iso_datetime # For parsing ISO timestamps

if TYPE_CHECKING:
    from approve.sessions.blueski.session import Session as BlueskiSession
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

        created_at_str = getattr(record, 'createdAt', '') if not isinstance(record, dict) else record.get('createdAt', '')
        timestamp_str = ""
        if created_at_str:
            try:
                dt_obj = parse_iso_datetime(created_at_str)
                timestamp_str = dt_obj.strftime("%I:%M %p - %b %d, %Y") if dt_obj else created_at_str
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

            elif embed_type in ['app.bsky.embed.record#view', 'app.bsky.embed.record']:
                record_embed_data = getattr(embed_data, 'record', None) if hasattr(embed_data, 'record') else embed_data.get('record', None)
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
