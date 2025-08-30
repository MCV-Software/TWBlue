# -*- coding: utf-8 -*-
import wx
import languageHandler  # Ensure _() is available
import logging
import wx
import config
from mysc.repeating_timer import RepeatingTimer
from datetime import datetime

from multiplatform_widgets import widgets

log = logging.getLogger("wxUI.buffers.atprotosocial.panels")


class ATProtoSocialHomeTimelinePanel(object):
    """Minimal Home timeline buffer for Bluesky.

    Exposes a .buffer wx.Panel with a List control and provides
    start_stream()/get_more_items() to fetch items from atproto.
    """

    def __init__(self, parent, name: str, session):
        super().__init__()
        self.session = session
        self.account = session.get_name()
        self.name = name
        self.type = "home_timeline"
        self.invisible = True
        self.needs_init = True
        self.buffer = _HomePanel(parent, name)
        self.buffer.session = session
        self.buffer.name = name
        # Ensure controller can resolve current account from the GUI panel
        self.buffer.account = self.account
        self.items = []  # list of dicts: {uri, author, text, indexed_at}
        self.cursor = None
        self._auto_timer = None

    def start_stream(self, mandatory=False, play_sound=True):
        """Fetch newest items and render them."""
        try:
            count = self.session.settings["general"]["max_posts_per_call"] or 40
        except Exception:
            count = 40
        try:
            api = self.session._ensure_client()
            # The atproto SDK expects params, not raw kwargs
            try:
                from atproto import models as at_models  # type: ignore
                params = at_models.AppBskyFeedGetTimeline.Params(limit=count)
                res = api.app.bsky.feed.get_timeline(params)
            except Exception:
                # Fallback to plain dict params if typed models unavailable
                res = api.app.bsky.feed.get_timeline({"limit": count})
            feed = getattr(res, "feed", [])
            self.cursor = getattr(res, "cursor", None)
            self.items = []
            for it in feed:
                post = getattr(it, "post", None)
                if not post:
                    continue
                record = getattr(post, "record", None)
                author = getattr(post, "author", None)
                text = getattr(record, "text", "") if record else ""
                handle = getattr(author, "handle", "") if author else ""
                indexed_at = getattr(post, "indexed_at", None)
                self.items.append({
                    "uri": getattr(post, "uri", ""),
                    "author": handle,
                    "text": text,
                    "indexed_at": indexed_at,
                })
            self._render_list(replace=True)
            return len(self.items)
        except Exception:
            log.exception("Failed to load Bluesky home timeline")
            self.buffer.list.clear()
            self.buffer.list.insert_item(False, _("Error"), _("Could not load timeline."), "")
            return 0

    def get_more_items(self):
        if not self.cursor:
            return 0
        try:
            api = self.session._ensure_client()
            try:
                from atproto import models as at_models  # type: ignore
                params = at_models.AppBskyFeedGetTimeline.Params(limit=40, cursor=self.cursor)
                res = api.app.bsky.feed.get_timeline(params)
            except Exception:
                res = api.app.bsky.feed.get_timeline({"limit": 40, "cursor": self.cursor})
            feed = getattr(res, "feed", [])
            self.cursor = getattr(res, "cursor", None)
            new_items = []
            for it in feed:
                post = getattr(it, "post", None)
                if not post:
                    continue
                record = getattr(post, "record", None)
                author = getattr(post, "author", None)
                text = getattr(record, "text", "") if record else ""
                handle = getattr(author, "handle", "") if author else ""
                indexed_at = getattr(post, "indexed_at", None)
                new_items.append({
                    "uri": getattr(post, "uri", ""),
                    "author": handle,
                    "text": text,
                    "indexed_at": indexed_at,
                })
            if not new_items:
                return 0
            self.items.extend(new_items)
            self._render_list(replace=False, start=len(self.items) - len(new_items))
            return len(new_items)
        except Exception:
            log.exception("Failed to load more Bluesky timeline items")
            return 0

    def _render_list(self, replace: bool, start: int = 0):
        if replace:
            self.buffer.list.clear()
        for i in range(start, len(self.items)):
            it = self.items[i]
            dt = ""
            if it.get("indexed_at"):
                try:
                    # indexed_at is ISO format; show HH:MM or date
                    dt = str(it["indexed_at"])[:16].replace("T", " ")
                except Exception:
                    dt = ""
            text = it.get("text", "").replace("\n", " ")
            if len(text) > 200:
                text = text[:197] + "..."
            self.buffer.list.insert_item(False, it.get("author", ""), text, dt)

    # For compatibility with controller expectations
    def save_positions(self):
        try:
            pos = self.buffer.list.get_selected()
            self.session.db[self.name + "_pos"] = pos
        except Exception:
            pass

    # Support actions that need a selected item identifier (e.g., reply)
    def get_selected_item_id(self):
        try:
            idx = self.buffer.list.get_selected()
            if idx is None or idx < 0:
                return None
            return self.items[idx].get("uri")
        except Exception:
            return None

    # Auto-refresh support (polling) to simulate near real-time updates
    def _periodic_refresh(self):
        try:
            # Ensure UI updates happen on the main thread
            wx.CallAfter(self.start_stream, False, False)
        except Exception:
            pass

    def enable_auto_refresh(self, seconds: int | None = None):
        try:
            if self._auto_timer:
                return
            if seconds is None:
                # Use global update_period (minutes) → seconds; minimum 15s
                minutes = config.app["app-settings"].get("update_period", 2)
                seconds = max(15, int(minutes * 60))
            self._auto_timer = RepeatingTimer(seconds, self._periodic_refresh)
            self._auto_timer.start()
        except Exception:
            log.exception("Failed to enable auto refresh for Bluesky panel %s", self.name)

    def disable_auto_refresh(self):
        try:
            if self._auto_timer:
                self._auto_timer.stop()
                self._auto_timer = None
        except Exception:
            pass


class _HomePanel(wx.Panel):
    def __init__(self, parent, name):
        super().__init__(parent, name=name)
        self.name = name
        self.type = "home_timeline"
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.list = widgets.list(self, _("Author"), _("Post"), _("Date"), style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.list.set_windows_size(0, 120)
        self.list.set_windows_size(1, 360)
        self.list.set_windows_size(2, 150)
        self.list.set_size()
        sizer.Add(self.list.list, 1, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(sizer)


class ATProtoSocialFollowingTimelinePanel(ATProtoSocialHomeTimelinePanel):
    """Following-only timeline (reverse-chronological)."""

    def __init__(self, parent, name: str, session):
        super().__init__(parent, name, session)
        self.type = "following_timeline"
        # Make sure the underlying wx panel also reflects this type
        try:
            self.buffer.type = "following_timeline"
        except Exception:
            pass

    def start_stream(self, mandatory=False, play_sound=True):
        try:
            count = self.session.settings["general"]["max_posts_per_call"] or 40
        except Exception:
            count = 40
        try:
            api = self.session._ensure_client()
            # Use plain dict params to ensure algorithm is passed regardless of SDK models version
            res = api.app.bsky.feed.get_timeline({"limit": count, "algorithm": "reverse-chronological"})
            feed = getattr(res, "feed", [])
            self.cursor = getattr(res, "cursor", None)
            self.items = []
            for it in feed:
                post = getattr(it, "post", None)
                if not post:
                    continue
                record = getattr(post, "record", None)
                author = getattr(post, "author", None)
                text = getattr(record, "text", "") if record else ""
                handle = getattr(author, "handle", "") if author else ""
                indexed_at = getattr(post, "indexed_at", None)
                self.items.append({
                    "uri": getattr(post, "uri", ""),
                    "author": handle,
                    "text": text,
                    "indexed_at": indexed_at,
                })
            self._render_list(replace=True)
            return len(self.items)
        except Exception:
            log.exception("Failed to load Bluesky following timeline")
            self.buffer.list.clear()
            self.buffer.list.insert_item(False, _("Error"), _("Could not load timeline."), "")
            return 0
