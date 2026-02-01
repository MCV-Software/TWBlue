# -*- coding: utf-8 -*-
"""
Utility functions for Bluesky session.
"""

import logging

log = logging.getLogger("sessions.blueski.utils")


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

    etype = g(embed, "$type") or g(embed, "py_type")

    # Check for video embed
    if etype and "video" in etype.lower():
        return True

    # Check for external link that might be video (YouTube, etc.)
    if etype and "external" in etype:
        ext = g(embed, "external", {})
        uri = g(ext, "uri", "")
        # Common video hosting sites
        video_hosts = ["youtube.com", "youtu.be", "vimeo.com", "twitch.tv", "dailymotion.com"]
        for host in video_hosts:
            if host in uri.lower():
                return True

    # Check in recordWithMedia wrapper
    if etype and "recordWithMedia" in etype:
        media = g(embed, "media", {})
        mtype = g(media, "$type") or g(media, "py_type")
        if mtype and "video" in mtype.lower():
            return True

    return False


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

    etype = g(embed, "$type") or g(embed, "py_type")

    # Direct images embed
    if etype and "images" in etype:
        images = g(embed, "images", [])
        return len(images) > 0

    # Check in recordWithMedia wrapper
    if etype and "recordWithMedia" in etype:
        media = g(embed, "media", {})
        mtype = g(media, "$type") or g(media, "py_type")
        if mtype and "images" in mtype:
            images = g(media, "images", [])
            return len(images) > 0

    return False


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

    etype = g(embed, "$type") or g(embed, "py_type")

    # Video embed
    if etype and "video" in etype.lower():
        playlist = g(embed, "playlist", None)
        if playlist:
            urls.append(playlist)
        # Alternative URL fields
        for key in ["url", "uri", "thumb"]:
            val = g(embed, key)
            if val and val not in urls:
                urls.append(val)

    # External links (YouTube, etc.)
    if etype and "external" in etype:
        ext = g(embed, "external", {})
        uri = g(ext, "uri", "")
        if uri:
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
    facets = g(record, "facets", [])
    for facet in facets:
        features = g(facet, "features", [])
        for feature in features:
            ftype = g(feature, "$type") or g(feature, "py_type")
            if ftype and "link" in ftype:
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
