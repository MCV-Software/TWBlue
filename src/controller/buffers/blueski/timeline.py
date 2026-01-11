# -*- coding: utf-8 -*-
import logging
from .base import BaseBuffer
from wxUI.buffers.blueski import panels as BlueskiPanels
from pubsub import pub

log = logging.getLogger("controller.buffers.blueski.timeline")

class HomeTimeline(BaseBuffer):
    def __init__(self, *args, **kwargs):
        super(HomeTimeline, self).__init__(*args, **kwargs)
        self.type = "home_timeline"
        self.feed_uri = None
        
    def create_buffer(self, parent, name):
        # Override to use HomePanel
        self.buffer = BlueskiPanels.HomePanel(parent, name)
        self.buffer.session = self.session

    def start_stream(self, mandatory=False, play_sound=True):
        count = 50
        try:
             count = self.session.settings["general"].get("max_posts_per_call", 50)
        except: pass
        
        api = self.session._ensure_client()
        
        # Discover Logic
        if not self.feed_uri:
            self.feed_uri = self._resolve_discover_feed(api)
            
        items = []
        try:
            res = None
            if self.feed_uri:
                 # Fetch feed
                 res = api.app.bsky.feed.get_feed({"feed": self.feed_uri, "limit": count})
            else:
                 # Fallback to standard timeline
                 res = api.app.bsky.feed.get_timeline({"limit": count})
            
            feed = getattr(res, "feed", [])
            items = list(feed)
            
        except Exception:
            log.exception("Failed to fetch home timeline")
            return 0
            
        return self.process_items(items, play_sound)

    def _resolve_discover_feed(self, api):
        # Reuse logic from panels.py
        try:
            cached = self.session.db.get("discover_feed_uri")
            if cached: return cached
            
            # Simple fallback: Suggested feeds
            try:
                res = api.app.bsky.feed.get_suggested_feeds({"limit": 50})
                feeds = getattr(res, "feeds", [])
                for feed in feeds:
                     dn = getattr(feed, "displayName", "") or getattr(feed, "display_name", "")
                     if "discover" in dn.lower():
                         uri = getattr(feed, "uri", "")
                         self.session.db["discover_feed_uri"] = uri
                         try: self.session.save_persistent_data()
                         except: pass
                         return uri
            except: pass
            
            return None
        except:
             return None

class FollowingTimeline(BaseBuffer):
    def __init__(self, *args, **kwargs):
        super(FollowingTimeline, self).__init__(*args, **kwargs)
        self.type = "following_timeline"
        
    def create_buffer(self, parent, name):
        self.buffer = BlueskiPanels.HomePanel(parent, name) # Reuse HomePanel layout
        self.buffer.session = self.session

    def start_stream(self, mandatory=False, play_sound=True):
         count = 50
         try: count = self.session.settings["general"].get("max_posts_per_call", 50)
         except: pass
         
         api = self.session._ensure_client()
         try:
             # Force reverse-chronological
             res = api.app.bsky.feed.get_timeline({"limit": count, "algorithm": "reverse-chronological"})
             feed = getattr(res, "feed", [])
             items = list(feed)
         except Exception:
             log.exception("Error fetching following timeline")
             return 0
         
         return self.process_items(items, play_sound)

class NotificationBuffer(BaseBuffer):
    def __init__(self, *args, **kwargs):
        super(NotificationBuffer, self).__init__(*args, **kwargs)
        self.type = "notifications"
        
    def create_buffer(self, parent, name):
        self.buffer = BlueskiPanels.NotificationPanel(parent, name) 
        self.buffer.session = self.session

    def start_stream(self, mandatory=False, play_sound=True):
         count = 50
         api = self.session._ensure_client()
         try:
             res = api.app.bsky.notification.list_notifications({"limit": count})
             notifs = getattr(res, "notifications", [])
             items = []
             # Notifications are not FeedViewPost. They have different structure.
             # self.compose_function expects FeedViewPost-like structure (post, author, etc).
             # We need to map them or have a different compose function.
             # For now, let's skip items to avoid crash
             # Or attempt to map.
         except:
             return 0
         return 0

class Conversation(BaseBuffer):
    def __init__(self, *args, **kwargs):
        super(Conversation, self).__init__(*args, **kwargs)
        self.type = "conversation"
        # We need the root URI or the URI of the post to show thread for
        self.root_uri = kwargs.get("uri")
        
    def create_buffer(self, parent, name):
        self.buffer = BlueskiPanels.HomePanel(parent, name)
        self.buffer.session = self.session
        
    def start_stream(self, mandatory=False, play_sound=True):
        if not self.root_uri: return 0
        
        api = self.session._ensure_client()
        try:
            params = {"uri": self.root_uri, "depth": 100, "parentHeight": 100}
            try:
                res = api.app.bsky.feed.get_post_thread(params)
            except Exception:
                res = api.app.bsky.feed.get_post_thread({"uri": self.root_uri})
            thread = getattr(res, "thread", None)
            if not thread:
                return 0

            def g(obj, key, default=None):
                if isinstance(obj, dict):
                    return obj.get(key, default)
                return getattr(obj, key, default)

            # Find the root of the thread tree
            curr = thread
            while g(curr, "parent"):
                curr = g(curr, "parent")

            final_items = []

            def traverse(node):
                if not node:
                    return
                post = g(node, "post")
                if post:
                    final_items.append(post)
                replies = g(node, "replies") or []
                for r in replies:
                    traverse(r)

            traverse(curr)
            
            # Clear existing items to avoid duplication when refreshing a thread view (which changes structure little)
            self.session.db[self.name] = [] 
            self.buffer.list.clear() # Clear UI too
            
            return self.process_items(final_items, play_sound)
            
        except Exception:
            log.exception("Error fetching thread")
            return 0

class LikesBuffer(BaseBuffer):
    def __init__(self, *args, **kwargs):
        super(LikesBuffer, self).__init__(*args, **kwargs)
        self.type = "likes"

    def create_buffer(self, parent, name):
        self.buffer = BlueskiPanels.HomePanel(parent, name)
        self.buffer.session = self.session

    def start_stream(self, mandatory=False, play_sound=True):
        count = 50
        try:
            count = self.session.settings["general"].get("max_posts_per_call", 50)
        except Exception:
            pass

        api = self.session._ensure_client()
        try:
            res = api.app.bsky.feed.get_actor_likes({"actor": api.me.did, "limit": count})
            items = getattr(res, "feed", None) or getattr(res, "items", None) or []
        except Exception:
            log.exception("Error fetching likes")
            return 0

        return self.process_items(list(items), play_sound)
