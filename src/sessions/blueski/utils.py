# -*- coding: utf-8 -*-
"""
Utility functions for Bluesky session.
"""

import logging
import re

log = logging.getLogger("sessions.blueski.utils")

url_re = re.compile(r'https?://[^\s<>\[\]()"\',]+[^\s<>\[\]()"\',.:;!?]')


def g(obj, key, default=None):
    """Helper to get attribute from dict or object."""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def is_audio_or_video(post):
    """
    Check if post contains audio or video content.

    Args:
        post: Bluesky post object (FeedViewPost or PostView)

    Returns:
        bool: True if post has audio/video media
    """
    actual_post = g(post, "post", post)
    embed = g(actual_post, "embed", None)
    if not embed:
        return False

    etype = g(embed, "$type") or g(embed, "py_type") or ""

    # Check for video embed
    if "video" in etype.lower():
        return True

    # Check for external link that might be video (YouTube, etc.)
    if "external" in etype.lower():
        ext = g(embed, "external", {})
        uri = g(ext, "uri", "")
        video_hosts = ["youtube.com", "youtu.be", "vimeo.com", "twitch.tv", "dailymotion.com"]
        for host in video_hosts:
            if host in uri.lower():
                return True

    # Check in recordWithMedia wrapper
    if "recordwithmedia" in etype.lower():
        media = g(embed, "media", {})
        mtype = g(media, "$type") or g(media, "py_type") or ""
        if "video" in mtype.lower():
            return True
        if "external" in mtype.lower():
            ext = g(media, "external", {})
            uri = g(ext, "uri", "")
            video_hosts = ["youtube.com", "youtu.be", "vimeo.com", "twitch.tv", "dailymotion.com"]
            for host in video_hosts:
                if host in uri.lower():
                    return True

    return False


def _extract_images_from_embed(embed):
    """Extract image URLs from an embed object."""
    images = []
    if not embed:
        return images

    etype = g(embed, "$type") or g(embed, "py_type") or ""

    def extract_images(img_list):
        result = []
        for img in (img_list or []):
            url = None
            # Try all possible URL field names
            for key in ["fullsize", "thumb", "thumbnail", "url", "uri", "src"]:
                val = g(img, key)
                if val and isinstance(val, str) and val.startswith("http"):
                    url = val
                    break
            # Also check for nested 'image' object
            if not url:
                image_obj = g(img, "image", {})
                if image_obj:
                    for key in ["ref", "$link", "url", "uri"]:
                        val = g(image_obj, key)
                        if val:
                            url = val
                            break
            if url:
                result.append({
                    "url": url,
                    "alt": g(img, "alt", "") or ""
                })
        return result

    # Direct images embed (app.bsky.embed.images or app.bsky.embed.images#view)
    if "images" in etype.lower():
        images.extend(extract_images(g(embed, "images", [])))

    # Gallery embed (app.bsky.embed.gallery or app.bsky.embed.gallery#view)
    if "gallery" in etype.lower():
        images.extend(extract_images(g(embed, "items", [])))

    # Check in recordWithMedia wrapper
    if "recordwithmedia" in etype.lower():
        media = g(embed, "media", {})
        mtype = g(media, "$type") or g(media, "py_type") or ""
        if "images" in mtype.lower():
            images.extend(extract_images(g(media, "images", [])))
        if "gallery" in mtype.lower():
            images.extend(extract_images(g(media, "items", [])))

    return images


def is_image(post):
    """
    Check if post contains image content.

    Args:
        post: Bluesky post object (FeedViewPost or PostView)

    Returns:
        bool: True if post has image media
    """
    actual_post = g(post, "post", post)
    embed = g(actual_post, "embed", None)
    if not embed:
        return False

    etype = g(embed, "$type") or g(embed, "py_type") or ""

    # Direct images embed
    if "images" in etype.lower():
        images = g(embed, "images", [])
        if images and len(images) > 0:
            return True

    # Gallery embed
    if "gallery" in etype.lower():
        items = g(embed, "items", [])
        if items and len(items) > 0:
            return True

    # Check in recordWithMedia wrapper
    if "recordwithmedia" in etype.lower():
        media = g(embed, "media", {})
        mtype = g(media, "$type") or g(media, "py_type") or ""
        if "images" in mtype.lower():
            images = g(media, "images", [])
            if images and len(images) > 0:
                return True
        if "gallery" in mtype.lower():
            items = g(media, "items", [])
            if items and len(items) > 0:
                return True

    return False


def get_image_urls(post):
    """
    Get URLs for image attachments from post for OCR.

    Args:
        post: Bluesky post object

    Returns:
        list: List of dicts with 'url' and 'alt' keys
    """
    actual_post = g(post, "post", post)
    embed = g(actual_post, "embed", None)
    return _extract_images_from_embed(embed)


def get_media_urls(post):
    """
    Get URLs for media attachments (video/audio) from post.

    Args:
        post: Bluesky post object

    Returns:
        list: List of media URLs
    """
    urls = []
    actual_post = g(post, "post", post)
    embed = g(actual_post, "embed", None)
    if not embed:
        return urls

    etype = g(embed, "$type") or g(embed, "py_type") or ""

    def extract_video_urls(video_embed):
        """Extract URLs from a video embed object."""
        result = []
        # Playlist URL (HLS stream)
        playlist = g(video_embed, "playlist", None)
        if playlist:
            result.append(playlist)
        # Alternative URL fields
        for key in ["url", "uri"]:
            val = g(video_embed, key)
            if val and val not in result:
                result.append(val)
        return result

    # Direct video embed (app.bsky.embed.video#view)
    if "video" in etype.lower():
        urls.extend(extract_video_urls(embed))

    # Check in recordWithMedia wrapper
    if "recordWithMedia" in etype or "record_with_media" in etype.lower():
        media = g(embed, "media", {})
        mtype = g(media, "$type") or g(media, "py_type") or ""
        if "video" in mtype.lower():
            urls.extend(extract_video_urls(media))
        # Also check for external in media
        if "external" in mtype.lower():
            ext = g(media, "external", {})
            uri = g(ext, "uri", "")
            if uri and uri not in urls:
                urls.append(uri)

    # External links (YouTube, etc.)
    if "external" in etype.lower():
        ext = g(embed, "external", {})
        uri = g(ext, "uri", "")
        if uri and uri not in urls:
            urls.append(uri)

    return urls


def find_urls(post):
    """
    Find all URLs in post content.

    Args:
        post: Bluesky post object

    Returns:
        list: List of URLs found
    """
    urls = []
    actual_post = g(post, "post", post)
    record = g(actual_post, "record", {})

    # Check facets for link annotations
    facets = g(record, "facets", []) or []
    for facet in facets:
        features = g(facet, "features", []) or []
        for feature in features:
            ftype = g(feature, "$type") or g(feature, "py_type")
            if ftype and "link" in ftype.lower():
                uri = g(feature, "uri", "")
                if uri and uri not in urls:
                    urls.append(uri)

    # Check embed for external links
    embed = g(actual_post, "embed", None)
    if embed:
        etype = g(embed, "$type") or g(embed, "py_type")
        if etype and "external" in etype:
            ext = g(embed, "external", {})
            uri = g(ext, "uri", "")
            if uri and uri not in urls:
                urls.append(uri)

    # Also search plain text for URLs using regex (fallback)
    text = g(record, "text", "")
    if text:
        text_urls = url_re.findall(text)
        for u in text_urls:
            if u not in urls:
                urls.append(u)

    # Include URLs from quoted post, if present.
    quote_info = extract_quoted_post_info(post)
    if quote_info and quote_info.get("kind") == "post":
        for uri in quote_info.get("urls", []):
            if uri and uri not in urls:
                urls.append(uri)

    return urls


def find_item(item, items_list):
    """
    Find item index in list by URI.

    Args:
        item: Item to find
        items_list: List to search

    Returns:
        int or None: Index if found, None otherwise
    """
    item_uri = g(item, "uri") or g(g(item, "post"), "uri")
    if not item_uri:
        return None

    for i, existing in enumerate(items_list):
        existing_uri = g(existing, "uri") or g(g(existing, "post"), "uri")
        if existing_uri == item_uri:
            return i

    return None


def _resolve_quoted_record_from_embed(embed):
    """Resolve quoted record payload from a Bluesky embed structure."""
    if not embed:
        return None

    etype = (g(embed, "$type") or g(embed, "py_type") or "").lower()

    candidate = None
    if "recordwithmedia" in etype:
        record_view = g(embed, "record")
        candidate = g(record_view, "record") or record_view
    elif "record" in etype:
        candidate = g(embed, "record") or embed
    else:
        record_view = g(embed, "record")
        if record_view is not None:
            candidate = g(record_view, "record") or record_view

    if not candidate:
        return None

    # Unwrap one extra layer if still wrapped in a record-view container.
    nested = g(candidate, "record")
    nested_type = (g(nested, "$type") or g(nested, "py_type") or "").lower() if nested else ""
    if nested and ("view" in nested_type or "record" in nested_type):
        return nested

    return candidate


def extract_reply_to_handle(post):
    """
    Best-effort extraction of the replied-to handle for a Bluesky post.

    Returns:
        str | None: Handle (without @) when available.
    """
    actual_post = g(post, "post", post)

    # Fast path: pre-hydrated by buffers/session.
    cached = g(post, "_reply_to_handle", None) or g(actual_post, "_reply_to_handle", None)
    if cached:
        return cached

    # Feed views frequently include hydrated reply context.
    reply_view = g(post, "reply", None) or g(actual_post, "reply", None)
    if reply_view:
        parent = g(reply_view, "parent", None) or g(reply_view, "post", None) or reply_view
        parent_post = g(parent, "post", None) or parent
        parent_author = g(parent_post, "author", None) or g(parent, "author", None)
        handle = g(parent_author, "handle", None)
        if handle:
            return handle

    # Some payloads include parent author directly under record.reply.parent.
    record = g(actual_post, "record", {}) or {}
    record_reply = g(record, "reply", None)
    if record_reply:
        parent = g(record_reply, "parent", None) or record_reply
        parent_post = g(parent, "post", None) or parent
        parent_author = g(parent_post, "author", None) or g(parent, "author", None)
        handle = g(parent_author, "handle", None)
        if handle:
            return handle

    # When only record.reply is available, we generally only have strong refs.
    # No handle can be resolved here without extra API calls.
    return None


def extract_quoted_post_info(post):
    """
    Extract quoted content metadata from a Bluesky post.

    Returns:
        dict | None: one of:
        - {"kind": "not_found"}
        - {"kind": "blocked"}
        - {"kind": "feed", "feed_name": "..."}
        - {"kind": "post", "handle": "...", "text": "...", "urls": ["..."]}
    """
    actual_post = g(post, "post", post)
    record = g(actual_post, "record", {}) or {}
    embed = g(actual_post, "embed", None) or g(record, "embed", None)
    quote_rec = _resolve_quoted_record_from_embed(embed)
    if not quote_rec:
        return None

    qtype = (g(quote_rec, "$type") or g(quote_rec, "py_type") or "").lower()
    if "viewnotfound" in qtype:
        return {"kind": "not_found"}
    if "viewblocked" in qtype:
        return {"kind": "blocked"}
    if "generatorview" in qtype:
        return {"kind": "feed", "feed_name": g(quote_rec, "displayName", "Feed")}

    q_author = g(quote_rec, "author", {}) or {}
    q_handle = g(q_author, "handle", "unknown") or "unknown"

    q_value = g(quote_rec, "value") or g(quote_rec, "record") or {}
    q_text = g(q_value, "text", "") or g(quote_rec, "text", "")
    if not q_text:
        nested_value = g(q_value, "value") or {}
        q_text = g(nested_value, "text", "")

    q_urls = []

    q_facets = g(q_value, "facets", []) or []
    for facet in q_facets:
        features = g(facet, "features", []) or []
        for feature in features:
            ftype = (g(feature, "$type") or g(feature, "py_type") or "").lower()
            if "link" in ftype:
                uri = g(feature, "uri", "")
                if uri and uri not in q_urls:
                    q_urls.append(uri)

    q_embed = g(quote_rec, "embed", None) or g(q_value, "embed", None)
    if q_embed:
        q_etype = (g(q_embed, "$type") or g(q_embed, "py_type") or "").lower()
        if "external" in q_etype:
            ext = g(q_embed, "external", {})
            uri = g(ext, "uri", "")
            if uri and uri not in q_urls:
                q_urls.append(uri)
        if "recordwithmedia" in q_etype:
            media = g(q_embed, "media", {})
            mtype = (g(media, "$type") or g(media, "py_type") or "").lower()
            if "external" in mtype:
                ext = g(media, "external", {})
                uri = g(ext, "uri", "")
                if uri and uri not in q_urls:
                    q_urls.append(uri)

    for uri in url_re.findall(q_text or ""):
        if uri not in q_urls:
            q_urls.append(uri)

    return {
        "kind": "post",
        "handle": q_handle,
        "text": q_text or "",
        "urls": q_urls,
    }
