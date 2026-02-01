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
            for key in ["fullsize", "thumb", "url", "uri", "src"]:
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

    # Check in recordWithMedia wrapper
    if "recordwithmedia" in etype.lower():
        media = g(embed, "media", {})
        mtype = g(media, "$type") or g(media, "py_type") or ""
        if "images" in mtype.lower():
            images.extend(extract_images(g(media, "images", [])))

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

    # Check in recordWithMedia wrapper
    if "recordwithmedia" in etype.lower():
        media = g(embed, "media", {})
        mtype = g(media, "$type") or g(media, "py_type") or ""
        if "images" in mtype.lower():
            images = g(media, "images", [])
            if images and len(images) > 0:
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
