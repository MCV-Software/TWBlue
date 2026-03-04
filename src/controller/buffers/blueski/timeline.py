# -*- coding: utf-8 -*-
import logging
import output
from .base import BaseBuffer
from wxUI.buffers.blueski import panels as BlueskiPanels

log = logging.getLogger("controller.buffers.blueski.timeline")


class HomeTimeline(BaseBuffer):
    """Discover feed buffer."""

    def __init__(self, *args, **kwargs):
        super(HomeTimeline, self).__init__(*args, **kwargs)
        self.type = "home_timeline"
        self.feed_uri = None
        self.next_cursor = None
        self.sound = "tweet_received.ogg"

    def create_buffer(self, parent, name):
        self.buffer = BlueskiPanels.HomePanel(parent, name)
        self.buffer.session = self.session

    def start_stream(self, mandatory=False, play_sound=True):
        count = self.get_max_items()
        api = self.session._ensure_client()
        if not self.feed_uri:
            self.feed_uri = self._resolve_discover_feed(api)
        try:
            if self.feed_uri:
                res = api.app.bsky.feed.get_feed({"feed": self.feed_uri, "limit": count})
            else:
                res = api.app.bsky.feed.get_timeline({"limit": count})
            items = list(getattr(res, "feed", []))
            self.next_cursor = getattr(res, "cursor", None)
        except Exception as e:
            log.error("Error fetching home timeline: %s", e)
            return 0
        return self.process_items(items, play_sound)

    def get_more_items(self):
        if not self.next_cursor:
            return
        count = self.get_max_items()
        api = self.session._ensure_client()
        try:
            if self.feed_uri:
                res = api.app.bsky.feed.get_feed({"feed": self.feed_uri, "limit": count, "cursor": self.next_cursor})
            else:
                res = api.app.bsky.feed.get_timeline({"limit": count, "cursor": self.next_cursor})
            items = list(getattr(res, "feed", []))
            self.next_cursor = getattr(res, "cursor", None)
            added = self.process_items(items, play_sound=False)
            if added:
                output.speak(_(u"%s items retrieved") % added, True)
        except Exception as e:
            log.error("Error fetching more home timeline: %s", e)

    def _resolve_discover_feed(self, api):
        cached = self.session.db.get("discover_feed_uri")
        if cached:
            return cached
        try:
            res = api.app.bsky.feed.get_suggested_feeds({"limit": 50})
            for feed in getattr(res, "feeds", []):
                dn = getattr(feed, "displayName", "") or getattr(feed, "display_name", "")
                if "discover" in dn.lower():
                    uri = getattr(feed, "uri", "")
                    self.session.db["discover_feed_uri"] = uri
                    return uri
        except Exception:
            pass
        return None


class FollowingTimeline(BaseBuffer):
    """Following-only timeline (reverse-chronological)."""

    def __init__(self, *args, **kwargs):
        super(FollowingTimeline, self).__init__(*args, **kwargs)
        self.type = "following_timeline"
        self.next_cursor = None
        self.sound = "tweet_received.ogg"

    def create_buffer(self, parent, name):
        self.buffer = BlueskiPanels.HomePanel(parent, name)
        self.buffer.session = self.session

    def start_stream(self, mandatory=False, play_sound=True):
        count = self.get_max_items()
        api = self.session._ensure_client()
        try:
            res = api.app.bsky.feed.get_timeline({"limit": count, "algorithm": "reverse-chronological"})
            items = list(getattr(res, "feed", []))
            self.next_cursor = getattr(res, "cursor", None)
        except Exception as e:
            log.error("Error fetching following timeline: %s", e)
            return 0
        return self.process_items(items, play_sound)

    def get_more_items(self):
        if not self.next_cursor:
            return
        count = self.get_max_items()
        api = self.session._ensure_client()
        try:
            res = api.app.bsky.feed.get_timeline({"limit": count, "algorithm": "reverse-chronological", "cursor": self.next_cursor})
            items = list(getattr(res, "feed", []))
            self.next_cursor = getattr(res, "cursor", None)
            added = self.process_items(items, play_sound=False)
            if added:
                output.speak(_(u"%s items retrieved") % added, True)
        except Exception as e:
            log.error("Error fetching more following timeline: %s", e)


class NotificationBuffer(BaseBuffer):
    """Notifications buffer."""

    def __init__(self, *args, **kwargs):
        kwargs["compose_func"] = "compose_notification"
        super(NotificationBuffer, self).__init__(*args, **kwargs)
        self.type = "notifications"
        self.sound = "notification_received.ogg"
        self.next_cursor = None

    def create_buffer(self, parent, name):
        self.buffer = BlueskiPanels.NotificationPanel(parent, name)
        self.buffer.session = self.session

    def _hydrate_notifications(self, notifications):
        """Fetch subject post text for like/repost notifications."""
        if not notifications:
            return notifications

        def g(obj, key, default=None):
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)

        # Collect URIs for likes/reposts that need subject post text
        uris_to_fetch = []
        for notif in notifications:
            reason = g(notif, "reason", "")
            if reason in ("like", "repost"):
                reason_subject = g(notif, "reasonSubject") or g(notif, "reason_subject")
                if reason_subject and isinstance(reason_subject, str):
                    uris_to_fetch.append(reason_subject)

        if not uris_to_fetch:
            return notifications

        # Fetch posts in batch
        posts_map = {}
        try:
            api = self.session._ensure_client()
            if api and uris_to_fetch:
                # getPosts accepts up to 25 URIs at a time
                for i in range(0, len(uris_to_fetch), 25):
                    batch = uris_to_fetch[i:i+25]
                    res = api.app.bsky.feed.get_posts({"uris": batch})
                    for post in getattr(res, "posts", []):
                        uri = g(post, "uri")
                        if uri:
                            record = g(post, "record", {})
                            text = g(record, "text", "")
                            posts_map[uri] = text
        except Exception as e:
            log.error("Error fetching subject posts for notifications: %s", e)

        # Attach subject post text to notifications
        enriched = []
        for notif in notifications:
            reason = g(notif, "reason", "")
            if reason in ("like", "repost"):
                reason_subject = g(notif, "reasonSubject") or g(notif, "reason_subject")
                if reason_subject and reason_subject in posts_map:
                    # Create a modified notification with subject post text
                    if isinstance(notif, dict):
                        notif = dict(notif)
                        notif["_subject_text"] = posts_map[reason_subject]
                    else:
                        # For ATProto model objects, add as attribute
                        try:
                            notif._subject_text = posts_map[reason_subject]
                        except AttributeError:
                            pass
            enriched.append(notif)

        return enriched

    def start_stream(self, mandatory=False, play_sound=True):
        count = self.get_max_items()
        api = self.session._ensure_client()
        if not api:
            return 0
        try:
            res = api.app.bsky.notification.list_notifications({"limit": count})
            notifications = list(getattr(res, "notifications", []))
            self.next_cursor = getattr(res, "cursor", None)
            if not notifications:
                return 0
            notifications = self._hydrate_notifications(notifications)
            return self.process_items(notifications, play_sound)
        except Exception as e:
            log.error("Error fetching notifications: %s", e)
            return 0

    def get_more_items(self):
        if not self.next_cursor:
            return
        count = self.get_max_items()
        api = self.session._ensure_client()
        if not api:
            return
        try:
            res = api.app.bsky.notification.list_notifications({"limit": count, "cursor": self.next_cursor})
            notifications = list(getattr(res, "notifications", []))
            self.next_cursor = getattr(res, "cursor", None)
            notifications = self._hydrate_notifications(notifications)
            added = self.process_items(notifications, play_sound=False)
            if added:
                output.speak(_(u"%s items retrieved") % added, True)
        except Exception as e:
            log.error("Error fetching more notifications: %s", e)

    def add_new_item(self, notification):
        notifications = self._hydrate_notifications([notification])
        return self.process_items(notifications, play_sound=True)


class Conversation(BaseBuffer):
    """Thread/conversation view."""

    def __init__(self, *args, **kwargs):
        super(Conversation, self).__init__(*args, **kwargs)
        self.type = "conversation"
        self.root_uri = kwargs.get("uri")
        self.sound = "search_updated.ogg"

    def create_buffer(self, parent, name):
        self.buffer = BlueskiPanels.HomePanel(parent, name)
        self.buffer.session = self.session

    def start_stream(self, mandatory=False, play_sound=True):
        if not self.root_uri:
            return 0
        api = self.session._ensure_client()
        try:
            res = api.app.bsky.feed.get_post_thread({"uri": self.root_uri, "depth": 100, "parentHeight": 100})
            thread = getattr(res, "thread", None)
            if not thread:
                return 0

            def g(obj, key, default=None):
                return obj.get(key, default) if isinstance(obj, dict) else getattr(obj, key, default)

            final_items = []
            # Add ancestors
            ancestors = []
            parent = g(thread, "parent")
            while parent:
                ppost = g(parent, "post")
                if ppost:
                    ancestors.insert(0, ppost)
                parent = g(parent, "parent")
            final_items.extend(ancestors)

            # Traverse thread
            def traverse(node):
                if not node:
                    return
                post = g(node, "post")
                if post:
                    final_items.append(post)
                for r in (g(node, "replies") or []):
                    traverse(r)

            traverse(thread)
            self.session.db[self.name] = []
            self.buffer.list.clear()
            # Don't use process_items() because it applies reverse logic.
            # Conversations should always be chronological (oldest first).
            return self._add_items_chronological(final_items, play_sound)
        except Exception as e:
            log.error("Error fetching thread: %s", e)
            return 0

    def _add_items_chronological(self, items, play_sound=True):
        """Add items in chronological order (oldest first) without reverse logic."""
        if not items:
            return 0

        safe = True
        relative_times = self.session.settings["general"].get("relative_times", False)
        show_screen_names = self.session.settings["general"].get("show_screen_names", False)

        for item in items:
            self.session.db[self.name].append(item)
            post = self.compose_function(item, self.session.db, self.session.settings,
                                         relative_times=relative_times,
                                         show_screen_names=show_screen_names,
                                         safe=safe)
            self.buffer.list.insert_item(False, *post)

        # Select the root post (first item after ancestors, or just the first)
        total = self.buffer.list.get_count()
        if total > 0:
            self.buffer.list.select_item(0)

        if play_sound and self.sound and not self.session.settings["sound"]["session_mute"]:
            self.session.sound.play(self.sound)

        return len(items)


class LikesBuffer(BaseBuffer):
    """User's liked posts."""

    def __init__(self, *args, **kwargs):
        super(LikesBuffer, self).__init__(*args, **kwargs)
        self.type = "likes"
        self.next_cursor = None
        self.sound = "favourite.ogg"

    def create_buffer(self, parent, name):
        self.buffer = BlueskiPanels.HomePanel(parent, name)
        self.buffer.session = self.session

    def start_stream(self, mandatory=False, play_sound=True):
        count = self.get_max_items()
        api = self.session._ensure_client()
        try:
            res = api.app.bsky.feed.get_actor_likes({"actor": api.me.did, "limit": count})
            items = list(getattr(res, "feed", None) or getattr(res, "items", None) or [])
            self.next_cursor = getattr(res, "cursor", None)
        except Exception as e:
            log.error("Error fetching likes: %s", e)
            return 0
        return self.process_items(items, play_sound)

    def get_more_items(self):
        if not self.next_cursor:
            return
        count = self.get_max_items()
        api = self.session._ensure_client()
        if not api:
            return
        try:
            res = api.app.bsky.feed.get_actor_likes({"actor": api.me.did, "limit": count, "cursor": self.next_cursor})
            items = list(getattr(res, "feed", None) or getattr(res, "items", None) or [])
            self.next_cursor = getattr(res, "cursor", None)
            added = self.process_items(items, play_sound=False)
            if added:
                output.speak(_(u"%s items retrieved") % added, True)
        except Exception as e:
            log.error("Error fetching more likes: %s", e)


class MentionsBuffer(BaseBuffer):
    """Mentions, replies and quotes."""

    def __init__(self, *args, **kwargs):
        kwargs["compose_func"] = "compose_notification"
        super(MentionsBuffer, self).__init__(*args, **kwargs)
        self.type = "mentions"
        self.sound = "mention_received.ogg"
        self.next_cursor = None

    def create_buffer(self, parent, name):
        self.buffer = BlueskiPanels.NotificationPanel(parent, name)
        self.buffer.session = self.session

    def start_stream(self, mandatory=False, play_sound=True):
        count = self.get_max_items()
        api = self.session._ensure_client()
        if not api:
            return 0
        try:
            res = api.app.bsky.notification.list_notifications({"limit": count})
            notifications = getattr(res, "notifications", [])
            self.next_cursor = getattr(res, "cursor", None)
            mentions = [n for n in notifications if getattr(n, "reason", "") in ("mention", "reply", "quote")]
            if not mentions:
                return 0
            return self.process_items(mentions, play_sound)
        except Exception as e:
            log.error("Error fetching mentions: %s", e)
            return 0

    def get_more_items(self):
        if not self.next_cursor:
            return
        count = self.get_max_items()
        api = self.session._ensure_client()
        if not api:
            return
        try:
            res = api.app.bsky.notification.list_notifications({"limit": count, "cursor": self.next_cursor})
            notifications = getattr(res, "notifications", [])
            self.next_cursor = getattr(res, "cursor", None)
            mentions = [n for n in notifications if getattr(n, "reason", "") in ("mention", "reply", "quote")]
            if mentions:
                added = self.process_items(mentions, play_sound=False)
                if added:
                    output.speak(_(u"%s items retrieved") % added, True)
        except Exception as e:
            log.error("Error fetching more mentions: %s", e)

    def add_new_item(self, notification):
        if getattr(notification, "reason", "") in ("mention", "reply", "quote"):
            return self.process_items([notification], play_sound=True)
        return 0


class SentBuffer(BaseBuffer):
    """User's sent posts."""

    def __init__(self, *args, **kwargs):
        super(SentBuffer, self).__init__(*args, **kwargs)
        self.type = "sent"
        self.next_cursor = None

    def create_buffer(self, parent, name):
        self.buffer = BlueskiPanels.HomePanel(parent, name)
        self.buffer.session = self.session

    def start_stream(self, mandatory=False, play_sound=True):
        count = self.get_max_items()
        api = self.session._ensure_client()
        if not api or not api.me:
            return 0
        try:
            res = api.app.bsky.feed.get_author_feed({"actor": api.me.did, "limit": count, "filter": "posts_no_replies"})
            items = list(getattr(res, "feed", []))
            self.next_cursor = getattr(res, "cursor", None)
            if not items:
                return 0
            return self.process_items(items, play_sound)
        except Exception as e:
            log.error("Error fetching sent posts: %s", e)
            return 0

    def get_more_items(self):
        if not self.next_cursor:
            return
        count = self.get_max_items()
        api = self.session._ensure_client()
        if not api or not api.me:
            return
        try:
            res = api.app.bsky.feed.get_author_feed({"actor": api.me.did, "limit": count, "filter": "posts_no_replies", "cursor": self.next_cursor})
            items = list(getattr(res, "feed", []))
            self.next_cursor = getattr(res, "cursor", None)
            added = self.process_items(items, play_sound=False)
            if added:
                output.speak(_(u"%s items retrieved") % added, True)
        except Exception as e:
            log.error("Error fetching more sent posts: %s", e)


class UserTimeline(BaseBuffer):
    """Timeline for a specific user."""

    def __init__(self, *args, **kwargs):
        self.actor = kwargs.get("actor")
        self.handle = kwargs.get("handle")
        super(UserTimeline, self).__init__(*args, **kwargs)
        self.type = "user_timeline"
        self.next_cursor = None
        self._resolved_actor = None
        self.sound = "tweet_timeline.ogg"

    def create_buffer(self, parent, name):
        self.buffer = BlueskiPanels.HomePanel(parent, name)
        self.buffer.session = self.session

    def start_stream(self, mandatory=False, play_sound=True):
        if not self.actor:
            return 0
        count = self.get_max_items()
        actor = self.actor.strip().lstrip("@") if isinstance(self.actor, str) else self.actor
        api = self.session._ensure_client()
        if not api:
            return 0
        try:
            if isinstance(actor, str) and not actor.startswith("did:"):
                profile = self.session.get_profile(actor)
                if profile:
                    did = profile.get("did") if isinstance(profile, dict) else getattr(profile, "did", None)
                    if did:
                        actor = did
            self._resolved_actor = actor
            res = api.app.bsky.feed.get_author_feed({"actor": actor, "limit": count})
            items = list(getattr(res, "feed", []) or [])
            self.next_cursor = getattr(res, "cursor", None)
        except Exception as e:
            log.error("Error fetching user timeline: %s", e)
            return 0
        return self.process_items(items, play_sound)

    def get_more_items(self):
        if not self.next_cursor or not self._resolved_actor:
            return
        count = self.get_max_items()
        api = self.session._ensure_client()
        if not api:
            return
        try:
            res = api.app.bsky.feed.get_author_feed({"actor": self._resolved_actor, "limit": count, "cursor": self.next_cursor})
            items = list(getattr(res, "feed", []) or [])
            self.next_cursor = getattr(res, "cursor", None)
            added = self.process_items(items, play_sound=False)
            if added:
                output.speak(_(u"%s items retrieved") % added, True)
        except Exception as e:
            log.error("Error fetching more user timeline: %s", e)

    def remove_buffer(self, force=False):
        if not force:
            from wxUI import commonMessageDialogs
            import widgetUtils
            if commonMessageDialogs.remove_buffer() != widgetUtils.YES:
                return False
        self.session.db.pop(self.name, None)
        timelines = self.session.settings["other_buffers"].get("timelines") or []
        if isinstance(timelines, str):
            timelines = [t for t in timelines.split(",") if t]
        for key in (self.actor or "", self.handle or ""):
            if key in timelines:
                timelines.remove(key)
        self.session.settings["other_buffers"]["timelines"] = timelines
        self.session.settings.write()
        return True


class SearchBuffer(BaseBuffer):
    """Search results buffer."""

    def __init__(self, *args, **kwargs):
        self.search_query = kwargs.pop("query", "")
        super(SearchBuffer, self).__init__(*args, **kwargs)
        self.type = "search"
        self.next_cursor = None
        self.sound = "search_updated.ogg"

    def create_buffer(self, parent, name):
        self.buffer = BlueskiPanels.HomePanel(parent, name)
        self.buffer.session = self.session

    def start_stream(self, mandatory=False, play_sound=True):
        if not self.search_query:
            return 0
        count = self.get_max_items()
        api = self.session._ensure_client()
        if not api:
            return 0
        try:
            res = api.app.bsky.feed.search_posts({"q": self.search_query, "limit": count})
            posts = list(getattr(res, "posts", []))
            self.next_cursor = getattr(res, "cursor", None)
            if not posts:
                return 0
            self.session.db[self.name] = []
            self.buffer.list.clear()
            return self.process_items(posts, play_sound)
        except Exception as e:
            log.error("Error searching posts: %s", e)
            return 0

    def get_more_items(self):
        if not self.next_cursor or not self.search_query:
            return
        count = self.get_max_items()
        api = self.session._ensure_client()
        if not api:
            return
        try:
            res = api.app.bsky.feed.search_posts({"q": self.search_query, "limit": count, "cursor": self.next_cursor})
            posts = list(getattr(res, "posts", []))
            self.next_cursor = getattr(res, "cursor", None)
            added = self.process_items(posts, play_sound=False)
            if added:
                output.speak(_(u"%s items retrieved") % added, True)
        except Exception as e:
            log.error("Error fetching more search results: %s", e)

    def remove_buffer(self, force=False):
        if not force:
            from wxUI import commonMessageDialogs
            import widgetUtils
            if commonMessageDialogs.remove_buffer() != widgetUtils.YES:
                return False
        self.session.db.pop(self.name, None)
        searches = self.session.settings["other_buffers"].get("searches") or []
        if isinstance(searches, str):
            searches = [s for s in searches.split(",") if s]
        if self.search_query in searches:
            searches.remove(self.search_query)
            self.session.settings["other_buffers"]["searches"] = searches
            self.session.settings.write()
        return True
