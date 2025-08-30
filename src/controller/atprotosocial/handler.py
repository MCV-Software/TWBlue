from __future__ import annotations

import logging
from typing import Any
import languageHandler  # Ensure _() injection

logger = logging.getLogger(__name__)


class Handler:
    """Handler for Bluesky integration: creates minimal buffers."""

    def __init__(self):
        super().__init__()
        self.menus = dict(
            compose="&Post",
        )
        self.item_menu = "&Post"

    def create_buffers(self, session, createAccounts=True, controller=None):
        name = session.get_name()
        controller.accounts.append(name)
        if createAccounts:
            from pubsub import pub
            pub.sendMessage("core.create_account", name=name, session_id=session.session_id, logged=True)
        root_position = controller.view.search(name, name)
        # Home timeline only for now
        from pubsub import pub
        pub.sendMessage(
            "createBuffer",
            buffer_type="home_timeline",
            session_type="atprotosocial",
            buffer_title=_("Home"),
            parent_tab=root_position,
            start=True,
            kwargs=dict(parent=controller.view.nb, name="home_timeline", session=session)
        )
        # Following-only timeline (reverse-chronological)
        pub.sendMessage(
            "createBuffer",
            buffer_type="following_timeline",
            session_type="atprotosocial",
            buffer_title=_("Following"),
            parent_tab=root_position,
            start=False,
            kwargs=dict(parent=controller.view.nb, name="following_timeline", session=session)
        )

    def start_buffer(self, controller, buffer):
        """Start a newly created Bluesky buffer."""
        try:
            if hasattr(buffer, "start_stream"):
                buffer.start_stream(mandatory=True, play_sound=False)
            # Enable periodic auto-refresh to simulate real-time updates
            if hasattr(buffer, "enable_auto_refresh"):
                buffer.enable_auto_refresh()
        finally:
            # Ensure we won't try to start it again
            try:
                buffer.needs_init = False
            except Exception:
                pass

    async def handle_action(self, action_name: str, user_id: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        logger.debug("handle_action stub: %s %s %s", action_name, user_id, payload)
        return None

    async def handle_message_command(self, command: str, user_id: str, message_id: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        logger.debug("handle_message_command stub: %s %s %s %s", command, user_id, message_id, payload)
        return None

    async def handle_user_command(self, command: str, user_id: str, target_user_id: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        logger.debug("handle_user_command stub: %s %s %s %s", command, user_id, target_user_id, payload)
        return None
