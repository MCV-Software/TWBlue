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
            items = res.get("items", [])
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
            items = res.get("items", [])
            self.next_cursor = res.get("cursor")
            added = self.process_items(items, play_sound=False)
            if added:
                output.speak(_(u"%s items retrieved") % (str(added)), True)
        except Exception as e:
            log.error("Error fetching more user list items for %s: %s", self.name, e)

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
