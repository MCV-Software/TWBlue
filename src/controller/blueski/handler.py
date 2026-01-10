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
        # Discover/home timeline
        from pubsub import pub
        pub.sendMessage(
            "createBuffer",
            buffer_type="home_timeline",
            session_type="blueski",
            buffer_title=_("Discover"),
            parent_tab=root_position,
            start=True,
            kwargs=dict(parent=controller.view.nb, name="home_timeline", session=session)
        )
        # Following-only timeline (reverse-chronological)
        pub.sendMessage(
            "createBuffer",
            buffer_type="following_timeline",
            session_type="blueski",
            buffer_title=_("Following (Chronological)"),
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

    def account_settings(self, buffer, controller):
        """Open a minimal account settings dialog for Bluesky."""
        try:
            current_mode = None
            try:
                current_mode = buffer.session.settings["general"].get("boost_mode")
            except Exception:
                current_mode = None
            ask_default = True if current_mode in (None, "ask") else False

            from wxUI.dialogs.blueski.configuration import AccountSettingsDialog
            dlg = AccountSettingsDialog(controller.view, ask_before_boost=ask_default)
            resp = dlg.ShowModal()
            if resp == wx.ID_OK:
                vals = dlg.get_values()
                boost_mode = "ask" if vals.get("ask_before_boost") else "direct"
                try:
                    buffer.session.settings["general"]["boost_mode"] = boost_mode
                    buffer.session.settings.write()
                except Exception:
                    logger.exception("Failed to persist Bluesky boost_mode setting")
            dlg.Destroy()
        except Exception:
            logger.exception("Error opening Bluesky account settings dialog")

    async def handle_action(self, action_name: str, user_id: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        logger.debug("handle_action stub: %s %s %s", action_name, user_id, payload)
        return None

    async def handle_message_command(self, command: str, user_id: str, message_id: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        logger.debug("handle_message_command stub: %s %s %s %s", command, user_id, message_id, payload)
        return None

    async def handle_user_command(self, command: str, user_id: str, target_user_id: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        logger.debug("handle_user_command stub: %s %s %s %s", command, user_id, target_user_id, payload)
        return None
