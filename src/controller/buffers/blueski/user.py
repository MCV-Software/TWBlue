# -*- coding: utf-8 -*-
import logging
import output
from .base import BaseBuffer
from wxUI.buffers.blueski import panels as BlueskiPanels
from sessions.blueski import compose

log = logging.getLogger("controller.buffers.blueski.user")

class UserBuffer(BaseBuffer):
    def __init__(self, *args, **kwargs):
        # We need compose_user for this buffer
        kwargs["compose_func"] = "compose_user"
        super(UserBuffer, self).__init__(*args, **kwargs)
        self.type = "user"
        self.next_cursor = None
        self.sound = "new_event.ogg"
        
    def create_buffer(self, parent, name):
        self.buffer = BlueskiPanels.UserPanel(parent, name)
        self.buffer.session = self.session

    def start_stream(self, mandatory=False, play_sound=True):
        api_method = self.kwargs.get("api_method")
        if not api_method: return 0
        
        count = self.get_max_items()
        actor = (
            self.kwargs.get("actor")
            or self.kwargs.get("did")
            or self.kwargs.get("handle")
            or self.kwargs.get("id")
        )

        try:
            if api_method in ("get_followers", "get_follows"):
                res = getattr(self.session, api_method)(actor=actor, limit=count)
            else:
                res = getattr(self.session, api_method)(limit=count)
            items = self._hydrate_profiles(res.get("items", []) or [])
            self.next_cursor = res.get("cursor")
            return self.process_items(items, play_sound)
        except Exception as e:
            log.error("Error fetching user list for %s: %s", self.name, e)
            return 0

    def get_more_items(self):
        api_method = self.kwargs.get("api_method")
        if not api_method or not self.next_cursor:
            return

        count = self.get_max_items()
        actor = (
            self.kwargs.get("actor")
            or self.kwargs.get("did")
            or self.kwargs.get("handle")
            or self.kwargs.get("id")
        )
        try:
            if api_method in ("get_followers", "get_follows"):
                res = getattr(self.session, api_method)(actor=actor, limit=count, cursor=self.next_cursor)
            else:
                res = getattr(self.session, api_method)(limit=count, cursor=self.next_cursor)
            items = self._hydrate_profiles(res.get("items", []) or [])
            self.next_cursor = res.get("cursor")
            added = self.process_items(items, play_sound=False)
            if added:
                output.speak(_(u"%s items retrieved") % (str(added)), True)
        except Exception as e:
            log.error("Error fetching more user list items for %s: %s", self.name, e)

    def _hydrate_profiles(self, items):
        if not items:
            return []

        def g(obj, key, default=None):
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)

        def resolve_profile(obj):
            if g(obj, "handle") or g(obj, "did"):
                return obj
            for key in ("subject", "actor", "profile", "user"):
                nested = g(obj, key)
                if nested and (g(nested, "handle") or g(nested, "did")):
                    return nested
            return obj

        actors = []
        for item in items:
            profile = resolve_profile(item)
            did = g(profile, "did")
            handle = g(profile, "handle")
            if did:
                actors.append(did)
            elif handle:
                actors.append(handle)

        if not actors:
            return items

        profiles = []
        if actors and hasattr(self.session, "get_profiles"):
            try:
                res = self.session.get_profiles(actors)
                profiles = res.get("items", []) or []
            except Exception:
                profiles = []
        # If batch profiles lack counts, hydrate with detailed profiles.
        if hasattr(self.session, "get_profile"):
            def counts_missing(profile_obj):
                p1 = g(profile_obj, "followersCount", None)
                p2 = g(profile_obj, "followsCount", None)
                p3 = g(profile_obj, "postsCount", None)
                if p1 is None and p2 is None and p3 is None:
                    return True
                return (p1 or 0) == 0 and (p2 or 0) == 0 and (p3 or 0) == 0

            if not profiles:
                for actor in actors:
                    try:
                        p = self.session.get_profile(actor)
                        if p:
                            profiles.append(p)
                    except Exception:
                        pass
            else:
                for idx, p in enumerate(profiles):
                    if counts_missing(p):
                        did = g(p, "did") or g(p, "handle")
                        if not did:
                            continue
                        try:
                            detailed = self.session.get_profile(did)
                            if detailed:
                                profiles[idx] = detailed
                        except Exception:
                            pass

        profile_map = {}
        for p in profiles:
            did = g(p, "did")
            handle = g(p, "handle")
            if did:
                profile_map[did] = p
            if handle and handle not in profile_map:
                profile_map[handle] = p

        def needs_replace(item, profile):
            if profile is None:
                return False
            base = resolve_profile(item)
            f1 = g(base, "followersCount", None)
            f2 = g(base, "followsCount", None)
            f3 = g(base, "postsCount", None)
            p1 = g(profile, "followersCount", None)
            p2 = g(profile, "followsCount", None)
            p3 = g(profile, "postsCount", None)
            if f1 is None and f2 is None and f3 is None:
                return True
            if (f1 or 0) == 0 and (f2 or 0) == 0 and (f3 or 0) == 0:
                return (p1 or 0) != 0 or (p2 or 0) != 0 or (p3 or 0) != 0
            return False

        enriched = []
        for item in items:
            base = resolve_profile(item)
            did = g(base, "did")
            handle = g(base, "handle")
            profile = profile_map.get(did) or profile_map.get(handle)
            if needs_replace(item, profile):
                enriched.append(profile)
            else:
                enriched.append(item)
        return enriched

class FollowersBuffer(UserBuffer):
    def __init__(self, *args, **kwargs):
        kwargs["api_method"] = "get_followers"
        super(FollowersBuffer, self).__init__(*args, **kwargs)
        self.sound = "update_followers.ogg"

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
            key = self.kwargs.get("actor") or self.kwargs.get("handle") or self.kwargs.get("id")
            timelines = self.session.settings["other_buffers"].get("followers_timelines") or []
            if isinstance(timelines, str):
                timelines = [t for t in timelines.split(",") if t]
            if key in timelines:
                timelines.remove(key)
                self.session.settings["other_buffers"]["followers_timelines"] = timelines
                self.session.settings.write()
        except Exception as e:
            log.error("Error updating Bluesky followers timelines settings: %s", e)
        return True

class FollowingBuffer(UserBuffer):
    def __init__(self, *args, **kwargs):
        kwargs["api_method"] = "get_follows"
        super(FollowingBuffer, self).__init__(*args, **kwargs)
        self.sound = "update_followers.ogg"

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
            key = self.kwargs.get("actor") or self.kwargs.get("handle") or self.kwargs.get("id")
            timelines = self.session.settings["other_buffers"].get("following_timelines") or []
            if isinstance(timelines, str):
                timelines = [t for t in timelines.split(",") if t]
            if key in timelines:
                timelines.remove(key)
                self.session.settings["other_buffers"]["following_timelines"] = timelines
                self.session.settings.write()
        except Exception as e:
            log.error("Error updating Bluesky following timelines settings: %s", e)
        return True

class BlocksBuffer(UserBuffer):
    def __init__(self, *args, **kwargs):
        kwargs["api_method"] = "get_blocks"
        super(BlocksBuffer, self).__init__(*args, **kwargs)


class PostUserListBuffer(UserBuffer):
    def __init__(self, *args, **kwargs):
        self.post_uri = kwargs.get("post_uri")
        self.api_method = kwargs.get("api_method")
        super(PostUserListBuffer, self).__init__(*args, **kwargs)
        self.type = "post_user_list"

    def start_stream(self, mandatory=False, play_sound=True):
        if not self.api_method or not self.post_uri:
            return 0
        count = self.get_max_items()
        try:
            res = getattr(self.session, self.api_method)(self.post_uri, limit=count)
            items = res.get("items", [])
            self.next_cursor = res.get("cursor")
            return self.process_items(items, play_sound)
        except Exception as e:
            log.error("Error fetching post user list for %s: %s", self.name, e)
            return 0

    def get_more_items(self):
        if not self.api_method or not self.post_uri or not self.next_cursor:
            return
        count = self.get_max_items()
        try:
            res = getattr(self.session, self.api_method)(self.post_uri, limit=count, cursor=self.next_cursor)
            items = res.get("items", [])
            self.next_cursor = res.get("cursor")
            added = self.process_items(items, play_sound=False)
            if added:
                output.speak(_(u"%s items retrieved") % (str(added)), True)
        except Exception as e:
            log.error("Error fetching more post user list items for %s: %s", self.name, e)

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
        return True
