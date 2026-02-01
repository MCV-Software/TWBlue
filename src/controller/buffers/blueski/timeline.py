# -*- coding: utf-8 -*-
import logging
import output
from .base import BaseBuffer
from wxUI.buffers.blueski import panels as BlueskiPanels
from pubsub import pub

log = logging.getLogger("controller.buffers.blueski.timeline")

class HomeTimeline(BaseBuffer):
    def __init__(self, *args, **kwargs):
        super(HomeTimeline, self).__init__(*args, **kwargs)
        self.type = "home_timeline"
        self.feed_uri = None
        self.next_cursor = None

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
            self.next_cursor = getattr(res, "cursor", None)

        except Exception:
            log.exception("Failed to fetch home timeline")
            return 0

        return self.process_items(items, play_sound)

    def get_more_items(self):
        if not self.next_cursor:
            return
        count = 50
        try:
            count = self.session.settings["general"].get("max_posts_per_call", 50)
        except:
            pass
        api = self.session._ensure_client()
        try:
            if self.feed_uri:
                res = api.app.bsky.feed.get_feed({"feed": self.feed_uri, "limit": count, "cursor": self.next_cursor})
            else:
                res = api.app.bsky.feed.get_timeline({"limit": count, "cursor": self.next_cursor})
            feed = getattr(res, "feed", [])
            items = list(feed)
            self.next_cursor = getattr(res, "cursor", None)
            added = self.process_items(items, play_sound=False)
            if added:
                output.speak(_(u"%s items retrieved") % (str(added)), True)
        except Exception:
            log.exception("Error fetching more home timeline items")

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
        self.next_cursor = None

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
             self.next_cursor = getattr(res, "cursor", None)
         except Exception:
             log.exception("Error fetching following timeline")
             return 0

         return self.process_items(items, play_sound)

    def get_more_items(self):
        if not self.next_cursor:
            return
        count = 50
        try:
            count = self.session.settings["general"].get("max_posts_per_call", 50)
        except:
            pass
        api = self.session._ensure_client()
        try:
            res = api.app.bsky.feed.get_timeline({"limit": count, "algorithm": "reverse-chronological", "cursor": self.next_cursor})
            feed = getattr(res, "feed", [])
            items = list(feed)
            self.next_cursor = getattr(res, "cursor", None)
            added = self.process_items(items, play_sound=False)
            if added:
                output.speak(_(u"%s items retrieved") % (str(added)), True)
        except Exception:
            log.exception("Error fetching more following timeline items")

class NotificationBuffer(BaseBuffer):
    def __init__(self, *args, **kwargs):
        # Override compose_func before calling super().__init__
        kwargs["compose_func"] = "compose_notification"
        super(NotificationBuffer, self).__init__(*args, **kwargs)
        self.type = "notifications"
        self.sound = "notification_received.ogg"
        self.next_cursor = None

    def create_buffer(self, parent, name):
        self.buffer = BlueskiPanels.NotificationPanel(parent, name)
        self.buffer.session = self.session

    def start_stream(self, mandatory=False, play_sound=True):
        count = 50
        try:
            count = self.session.settings["general"].get("max_posts_per_call", 50)
        except Exception:
            pass

        api = self.session._ensure_client()
        if not api:
            return 0

        try:
            res = api.app.bsky.notification.list_notifications({"limit": count})
            notifications = getattr(res, "notifications", [])
            self.next_cursor = getattr(res, "cursor", None)
            if not notifications:
                return 0

            # Process notifications using the notification compose function
            return self.process_items(list(notifications), play_sound)

        except Exception:
            log.exception("Error fetching Bluesky notifications")
            return 0

    def get_more_items(self):
        if not self.next_cursor:
            return
        count = 50
        try:
            count = self.session.settings["general"].get("max_posts_per_call", 50)
        except:
            pass
        api = self.session._ensure_client()
        if not api:
            return
        try:
            res = api.app.bsky.notification.list_notifications({"limit": count, "cursor": self.next_cursor})
            notifications = getattr(res, "notifications", [])
            self.next_cursor = getattr(res, "cursor", None)
            added = self.process_items(list(notifications), play_sound=False)
            if added:
                output.speak(_(u"%s items retrieved") % (str(added)), True)
        except Exception:
            log.exception("Error fetching more notifications")

    def add_new_item(self, notification):
        """Add a single new notification from streaming/polling."""
        return self.process_items([notification], play_sound=True)

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

            def g(obj, key, default=None):
                if isinstance(obj, dict):
                    return obj.get(key, default)
                return getattr(obj, key, default)

            thread = getattr(res, "thread", None) or (res.get("thread") if isinstance(res, dict) else None)
            if not thread:
                return 0

            final_items = []

            # Add parent chain (oldest to newest) if available
            ancestors = []
            parent = g(thread, "parent")
            while parent:
                ppost = g(parent, "post")
                if ppost:
                    ancestors.insert(0, ppost)
                parent = g(parent, "parent")
            final_items.extend(ancestors)

            def traverse(node):
                if not node:
                    return
                post = g(node, "post")
                if post:
                    final_items.append(post)
                replies = g(node, "replies") or []
                for r in replies:
                    traverse(r)

            traverse(thread)
            
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
        self.next_cursor = None

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
            self.next_cursor = getattr(res, "cursor", None)
        except Exception:
            log.exception("Error fetching likes")
            return 0

        return self.process_items(list(items), play_sound)

    def get_more_items(self):
        if not self.next_cursor:
            return
        count = 50
        try:
            count = self.session.settings["general"].get("max_posts_per_call", 50)
        except:
            pass
        api = self.session._ensure_client()
        if not api:
            return
        try:
            res = api.app.bsky.feed.get_actor_likes({"actor": api.me.did, "limit": count, "cursor": self.next_cursor})
            items = getattr(res, "feed", None) or getattr(res, "items", None) or []
            self.next_cursor = getattr(res, "cursor", None)
            added = self.process_items(list(items), play_sound=False)
            if added:
                output.speak(_(u"%s items retrieved") % (str(added)), True)
        except Exception:
            log.exception("Error fetching more likes")


class MentionsBuffer(BaseBuffer):
    """Buffer for mentions and replies to the current user."""

    def __init__(self, *args, **kwargs):
        # Use notification compose function since mentions come from notifications
        kwargs["compose_func"] = "compose_notification"
        super(MentionsBuffer, self).__init__(*args, **kwargs)
        self.type = "mentions"
        self.sound = "mention_received.ogg"
        self.next_cursor = None

    def create_buffer(self, parent, name):
        self.buffer = BlueskiPanels.NotificationPanel(parent, name)
        self.buffer.session = self.session

    def start_stream(self, mandatory=False, play_sound=True):
        count = 50
        try:
            count = self.session.settings["general"].get("max_posts_per_call", 50)
        except Exception:
            pass

        api = self.session._ensure_client()
        if not api:
            return 0

        try:
            res = api.app.bsky.notification.list_notifications({"limit": count})
            notifications = getattr(res, "notifications", [])
            self.next_cursor = getattr(res, "cursor", None)
            if not notifications:
                return 0

            # Filter only mentions and replies
            mentions = [
                n for n in notifications
                if getattr(n, "reason", "") in ("mention", "reply", "quote")
            ]

            if not mentions:
                return 0

            return self.process_items(mentions, play_sound)

        except Exception:
            log.exception("Error fetching Bluesky mentions")
            return 0

    def get_more_items(self):
        if not self.next_cursor:
            return
        count = 50
        try:
            count = self.session.settings["general"].get("max_posts_per_call", 50)
        except:
            pass
        api = self.session._ensure_client()
        if not api:
            return
        try:
            res = api.app.bsky.notification.list_notifications({"limit": count, "cursor": self.next_cursor})
            notifications = getattr(res, "notifications", [])
            self.next_cursor = getattr(res, "cursor", None)
            # Filter only mentions and replies
            mentions = [
                n for n in notifications
                if getattr(n, "reason", "") in ("mention", "reply", "quote")
            ]
            if mentions:
                added = self.process_items(mentions, play_sound=False)
                if added:
                    output.speak(_(u"%s items retrieved") % (str(added)), True)
        except Exception:
            log.exception("Error fetching more mentions")

    def add_new_item(self, notification):
        """Add a single new mention from streaming/polling."""
        reason = getattr(notification, "reason", "")
        if reason in ("mention", "reply", "quote"):
            return self.process_items([notification], play_sound=True)
        return 0


class SentBuffer(BaseBuffer):
    """Buffer for posts sent by the current user."""

    def __init__(self, *args, **kwargs):
        super(SentBuffer, self).__init__(*args, **kwargs)
        self.type = "sent"
        self.next_cursor = None

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
        if not api or not api.me:
            return 0

        try:
            # Get author's own posts (excluding replies)
            res = api.app.bsky.feed.get_author_feed({
                "actor": api.me.did,
                "limit": count,
                "filter": "posts_no_replies"
            })
            items = getattr(res, "feed", [])
            self.next_cursor = getattr(res, "cursor", None)

            if not items:
                return 0

            return self.process_items(list(items), play_sound)

        except Exception:
            log.exception("Error fetching sent posts")
            return 0

    def get_more_items(self):
        if not self.next_cursor:
            return
        count = 50
        try:
            count = self.session.settings["general"].get("max_posts_per_call", 50)
        except:
            pass
        api = self.session._ensure_client()
        if not api or not api.me:
            return
        try:
            res = api.app.bsky.feed.get_author_feed({
                "actor": api.me.did,
                "limit": count,
                "filter": "posts_no_replies",
                "cursor": self.next_cursor
            })
            items = getattr(res, "feed", [])
            self.next_cursor = getattr(res, "cursor", None)
            added = self.process_items(list(items), play_sound=False)
            if added:
                output.speak(_(u"%s items retrieved") % (str(added)), True)
        except Exception:
            log.exception("Error fetching more sent posts")


class UserTimeline(BaseBuffer):
    """Buffer for posts by a specific user."""

    def __init__(self, *args, **kwargs):
        self.actor = kwargs.get("actor")
        self.handle = kwargs.get("handle")
        super(UserTimeline, self).__init__(*args, **kwargs)
        self.type = "user_timeline"
        self.next_cursor = None
        self._resolved_actor = None

    def create_buffer(self, parent, name):
        self.buffer = BlueskiPanels.HomePanel(parent, name)
        self.buffer.session = self.session

    def start_stream(self, mandatory=False, play_sound=True):
        if not self.actor:
            return 0

        count = 50
        try:
            count = self.session.settings["general"].get("max_posts_per_call", 50)
        except Exception:
            pass

        actor = self.actor
        if isinstance(actor, str):
            actor = actor.strip()
            if actor.startswith("@"):
                actor = actor[1:]

        api = self.session._ensure_client()
        if not api:
            return 0

        try:
            if isinstance(actor, str) and not actor.startswith("did:"):
                try:
                    profile = self.session.get_profile(actor)
                    if profile:
                        def g(obj, key, default=None):
                            if isinstance(obj, dict):
                                return obj.get(key, default)
                            return getattr(obj, key, default)
                        did = g(profile, "did")
                        if did:
                            actor = did
                except Exception:
                    pass
            self._resolved_actor = actor
            res = api.app.bsky.feed.get_author_feed({
                "actor": actor,
                "limit": count,
            })
            items = getattr(res, "feed", []) or []
            self.next_cursor = getattr(res, "cursor", None)
        except Exception:
            log.exception("Error fetching user timeline")
            return 0

        return self.process_items(list(items), play_sound)

    def get_more_items(self):
        if not self.next_cursor or not self._resolved_actor:
            return
        count = 50
        try:
            count = self.session.settings["general"].get("max_posts_per_call", 50)
        except:
            pass
        api = self.session._ensure_client()
        if not api:
            return
        try:
            res = api.app.bsky.feed.get_author_feed({
                "actor": self._resolved_actor,
                "limit": count,
                "cursor": self.next_cursor
            })
            items = getattr(res, "feed", []) or []
            self.next_cursor = getattr(res, "cursor", None)
            added = self.process_items(list(items), play_sound=False)
            if added:
                output.speak(_(u"%s items retrieved") % (str(added)), True)
        except Exception:
            log.exception("Error fetching more user timeline items")

    def remove_buffer(self, force=False):
        if not force:
            from wxUI import commonMessageDialogs
            import widgetUtils
            dlg = commonMessageDialogs.remove_buffer()
            if dlg != widgetUtils.YES:
                return False
        try:
            self.session.db.pop(self.name, None)
        except Exception:
            pass
        try:
            timelines = self.session.settings["other_buffers"].get("timelines")
            if timelines is None:
                timelines = []
            if isinstance(timelines, str):
                timelines = [t for t in timelines.split(",") if t]
            actor = self.actor or ""
            handle = self.handle or ""
            for key in (actor, handle):
                if key in timelines:
                    timelines.remove(key)
            self.session.settings["other_buffers"]["timelines"] = timelines
            self.session.settings.write()
        except Exception:
            log.exception("Error updating Bluesky timelines settings")
        return True


class SearchBuffer(BaseBuffer):
    """Buffer for search results (posts)."""

    def __init__(self, *args, **kwargs):
        self.search_query = kwargs.pop("query", "")
        super(SearchBuffer, self).__init__(*args, **kwargs)
        self.type = "search"
        self.next_cursor = None

    def create_buffer(self, parent, name):
        self.buffer = BlueskiPanels.HomePanel(parent, name)
        self.buffer.session = self.session

    def start_stream(self, mandatory=False, play_sound=True):
        if not self.search_query:
            return 0

        count = 50
        try:
            count = self.session.settings["general"].get("max_posts_per_call", 50)
        except Exception:
            pass

        api = self.session._ensure_client()
        if not api:
            return 0

        try:
            # Search posts
            res = api.app.bsky.feed.search_posts({
                "q": self.search_query,
                "limit": count
            })
            posts = getattr(res, "posts", [])
            self.next_cursor = getattr(res, "cursor", None)

            if not posts:
                return 0

            # Clear existing results for new search
            self.session.db[self.name] = []
            self.buffer.list.clear()

            return self.process_items(list(posts), play_sound)

        except Exception:
            log.exception("Error searching Bluesky posts")
            return 0

    def get_more_items(self):
        if not self.next_cursor or not self.search_query:
            return
        count = 50
        try:
            count = self.session.settings["general"].get("max_posts_per_call", 50)
        except:
            pass
        api = self.session._ensure_client()
        if not api:
            return
        try:
            res = api.app.bsky.feed.search_posts({
                "q": self.search_query,
                "limit": count,
                "cursor": self.next_cursor
            })
            posts = getattr(res, "posts", [])
            self.next_cursor = getattr(res, "cursor", None)
            added = self.process_items(list(posts), play_sound=False)
            if added:
                output.speak(_(u"%s items retrieved") % (str(added)), True)
        except Exception:
            log.exception("Error fetching more search results")

    def remove_buffer(self, force=False):
        """Search buffers can always be removed."""
        if not force:
            from wxUI import commonMessageDialogs
            import widgetUtils
            dlg = commonMessageDialogs.remove_buffer()
            if dlg != widgetUtils.YES:
                return False
        try:
            self.session.db.pop(self.name, None)
        except Exception:
            pass
        # Also remove from saved searches
        try:
            searches = self.session.settings["other_buffers"].get("searches")
            if searches:
                if isinstance(searches, str):
                    searches = [s for s in searches.split(",") if s]
                if self.search_query in searches:
                    searches.remove(self.search_query)
                    self.session.settings["other_buffers"]["searches"] = searches
                    self.session.settings.write()
        except Exception:
            log.exception("Error updating saved searches")
        return True
