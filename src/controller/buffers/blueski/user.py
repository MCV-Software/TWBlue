# -*- coding: utf-8 -*-
import logging
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
        
    def create_buffer(self, parent, name):
        self.buffer = BlueskiPanels.UserPanel(parent, name)
        self.buffer.session = self.session

    def start_stream(self, mandatory=False, play_sound=True):
        api_method = self.kwargs.get("api_method")
        if not api_method: return 0
        
        count = self.session.settings["general"].get("max_posts_per_call", 50)
        actor = (
            self.kwargs.get("actor")
            or self.kwargs.get("did")
            or self.kwargs.get("handle")
            or self.kwargs.get("id")
        )
        
        try:
            # We call the method in session. API methods return {"items": [...], "cursor": ...}
            if api_method in ("get_followers", "get_follows"):
                res = getattr(self.session, api_method)(actor=actor, limit=count)
            else:
                res = getattr(self.session, api_method)(limit=count)
            items = res.get("items", [])
            
            # Clear existing items for these lists to start fresh? 
            # Or append? Standard lists in TWBlue usually append.
            # But followers/blocks are often full-sync or large jumps.
            # For now, append like timelines.
            
            return self.process_items(items, play_sound)
        except Exception:
            log.exception(f"Error fetching user list for {self.name}")
            return 0

class FollowersBuffer(UserBuffer):
    def __init__(self, *args, **kwargs):
        kwargs["api_method"] = "get_followers"
        super(FollowersBuffer, self).__init__(*args, **kwargs)

class FollowingBuffer(UserBuffer):
    def __init__(self, *args, **kwargs):
        kwargs["api_method"] = "get_follows"
        super(FollowingBuffer, self).__init__(*args, **kwargs)

class BlocksBuffer(UserBuffer):
    def __init__(self, *args, **kwargs):
        kwargs["api_method"] = "get_blocks"
        super(BlocksBuffer, self).__init__(*args, **kwargs)
