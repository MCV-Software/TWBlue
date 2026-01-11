from __future__ import annotations

import logging
import wx
import output
from wxUI.dialogs.blueski.showUserProfile import ShowUserProfileDialog
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
        if createAccounts:
            from pubsub import pub
            pub.sendMessage("core.create_account", name=name, session_id=session.session_id, logged=session.logged)
        
        if not session.logged:
            logger.debug(f"Session {session.session_id} is not logged in, skipping timeline buffer creation.")
            return
        if name not in controller.accounts:
            controller.accounts.append(name)

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
        # Notifications
        pub.sendMessage(
            "createBuffer",
            buffer_type="notifications",
            session_type="blueski",
            buffer_title=_("Notifications"),
            parent_tab=root_position,
            start=False,
            kwargs=dict(parent=controller.view.nb, name="notifications", session=session)
        )
        # Likes
        pub.sendMessage(
            "createBuffer",
            buffer_type="likes",
            session_type="blueski",
            buffer_title=_("Likes"),
            parent_tab=root_position,
            start=False,
            kwargs=dict(parent=controller.view.nb, name="likes", session=session)
        )
        # Followers
        pub.sendMessage(
            "createBuffer",
            buffer_type="FollowersBuffer",
            session_type="blueski",
            buffer_title=_("Followers"),
            parent_tab=root_position,
            start=False,
            kwargs=dict(parent=controller.view.nb, name="followers", session=session)
        )
        # Following (Users)
        pub.sendMessage(
            "createBuffer",
            buffer_type="FollowingBuffer",
            session_type="blueski",
            buffer_title=_("Following (Users)"),
            parent_tab=root_position,
            start=False,
            kwargs=dict(parent=controller.view.nb, name="following", session=session)
        )
        # Blocks
        pub.sendMessage(
            "createBuffer",
            buffer_type="BlocksBuffer",
            session_type="blueski",
            buffer_title=_("Blocked Users"),
            parent_tab=root_position,
            start=False,
            kwargs=dict(parent=controller.view.nb, name="blocked", session=session)
        )
        # Chats
        pub.sendMessage(
            "createBuffer",
            buffer_type="ConversationListBuffer",
            session_type="blueski",
            buffer_title=_("Chats"),
            parent_tab=root_position,
            start=False,
            kwargs=dict(parent=controller.view.nb, name="direct_messages", session=session)
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

    def user_details(self, buffer):
        """Show user profile dialog for the selected user/post."""
        session = getattr(buffer, "session", None)
        if not session:
            output.speak(_("No active session to view user details."), True)
            return

        item = buffer.get_item() if hasattr(buffer, "get_item") else None
        if not item:
            output.speak(_("No user selected or identified to view details."), True)
            return

        def g(obj, key, default=None):
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)

        user_ident = None

        # If we're in a user list, the item itself is the user profile dict/model.
        if g(item, "did") or g(item, "handle"):
            user_ident = g(item, "did") or g(item, "handle")
        else:
            author = g(item, "author")
            if not author:
                post = g(item, "post") or g(item, "record")
                author = g(post, "author") if post else None
            if author:
                user_ident = g(author, "did") or g(author, "handle")

        if not user_ident:
            output.speak(_("No user selected or identified to view details."), True)
            return

        parent = getattr(buffer, "buffer", None) or wx.GetApp().GetTopWindow()
        dialog = ShowUserProfileDialog(parent, session, user_ident)
        dialog.ShowModal()
        dialog.Destroy()

    async def handle_action(self, action_name: str, user_id: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        logger.debug("handle_action stub: %s %s %s", action_name, user_id, payload)
        return None

    async def handle_message_command(self, command: str, user_id: str, message_id: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        logger.debug("handle_message_command stub: %s %s %s %s", command, user_id, message_id, payload)
        return None

    async def handle_user_command(self, command: str, user_id: str, target_user_id: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        logger.debug("handle_user_command stub: %s %s %s %s", command, user_id, target_user_id, payload)
        return None

    def add_to_favourites(self, buffer):
        """Standard action for Alt+Win+F"""
        if hasattr(buffer, "add_to_favorites"):
            buffer.add_to_favorites()
        elif hasattr(buffer, "on_like"):
             # Fallback
             buffer.on_like(None)
    
    def remove_from_favourites(self, buffer):
        """Standard action for Alt+Shift+Win+F"""
        if hasattr(buffer, "remove_from_favorites"):
            buffer.remove_from_favorites()
        elif hasattr(buffer, "on_like"):
            buffer.on_like(None)
            
    def follow(self, buffer):
        """Standard action for Ctrl+Win+S"""
        session = getattr(buffer, "session", None)
        if not session:
            output.speak(_("No active session."), True)
            return

        def g(obj, key, default=None):
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)

        user_ident = None
        item = buffer.get_item() if hasattr(buffer, "get_item") else None
        if item:
            if g(item, "handle") or g(item, "did"):
                user_ident = g(item, "handle") or g(item, "did")
            else:
                author = g(item, "author")
                if not author:
                    post = g(item, "post") or g(item, "record")
                    author = g(post, "author") if post else None
                if author:
                    user_ident = g(author, "handle") or g(author, "did")

        users = [user_ident] if user_ident else []
        from controller.blueski import userActions as user_actions_controller
        user_actions_controller.userActions(session, users)

    def open_conversation(self, controller, buffer):
        """Standard action for Control+Win+C"""
        item = buffer.get_item()
        if not item:
            return

        uri = None
        if hasattr(buffer, "get_selected_item_id"):
            uri = buffer.get_selected_item_id()
        if not uri:
            uri = getattr(item, "uri", None) or (item.get("post", {}).get("uri") if isinstance(item, dict) else None)
        if not uri: return
        
        # Buffer Title
        author = getattr(item, "author", None) or (item.get("post", {}).get("author") if isinstance(item, dict) else None)
        handle = getattr(author, "handle", "unknown") if author else "unknown"
        title = _("Conversation with {0}").format(handle)
        
        from pubsub import pub
        pub.sendMessage(
            "createBuffer",
            buffer_type="conversation",
            session_type="blueski",
            buffer_title=title,
            parent_tab=controller.view.search(buffer.session.get_name(), buffer.session.get_name()) if hasattr(buffer.session, "get_name") else None,
            start=True,
            kwargs=dict(parent=controller.view.nb, name=title, session=buffer.session, uri=uri)
        )

    def open_followers_timeline(self, main_controller, session, user_payload=None):
        actor, handle = self._resolve_actor(session, user_payload)
        if not actor:
            output.speak(_("No user selected."), True)
            return
        self._open_user_list(main_controller, session, actor, handle, list_type="followers")

    def open_following_timeline(self, main_controller, session, user_payload=None):
        actor, handle = self._resolve_actor(session, user_payload)
        if not actor:
            output.speak(_("No user selected."), True)
            return
        self._open_user_list(main_controller, session, actor, handle, list_type="following")

    def _resolve_actor(self, session, user_payload):
        def g(obj, key, default=None):
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)

        actor = None
        handle = None
        if user_payload:
            actor = g(user_payload, "did") or g(user_payload, "handle")
            handle = g(user_payload, "handle") or g(user_payload, "did")
        if not actor:
            actor = session.db.get("user_id") or session.db.get("user_name")
            handle = session.db.get("user_name") or actor
        return actor, handle

    def _open_user_list(self, main_controller, session, actor, handle, list_type):
        account_name = session.get_name()
        own_actor = session.db.get("user_id") or session.db.get("user_name")
        own_handle = session.db.get("user_name")
        if actor == own_actor or (own_handle and actor == own_handle):
            name = "followers" if list_type == "followers" else "following"
            index = main_controller.view.search(name, account_name)
            if index is not None:
                main_controller.view.change_buffer(index)
                return

        list_name = f"{handle}-{list_type}"
        if main_controller.search_buffer(list_name, account_name):
            index = main_controller.view.search(list_name, account_name)
            if index is not None:
                main_controller.view.change_buffer(index)
            return

        title = _("Followers for {user}").format(user=handle) if list_type == "followers" else _("Following for {user}").format(user=handle)
        from pubsub import pub
        pub.sendMessage(
            "createBuffer",
            buffer_type="FollowersBuffer" if list_type == "followers" else "FollowingBuffer",
            session_type="blueski",
            buffer_title=title,
            parent_tab=main_controller.view.search(account_name, account_name),
            start=True,
            kwargs=dict(parent=main_controller.view.nb, name=list_name, session=session, actor=actor)
        )

    def delete(self, buffer, controller):
        """Standard action for delete key / menu item"""
        item = buffer.get_item()
        if not item: return
        
        uri = getattr(item, "uri", None) or (item.get("post", {}).get("uri") if isinstance(item, dict) else None)
        if not uri: return
        
        import wx
        if wx.MessageBox(_("Are you sure you want to delete this post?"), _("Delete post"), wx.YES_NO | wx.ICON_QUESTION) == wx.YES:
            if buffer.session.delete_post(uri):
                import output
                output.speak(_("Post deleted."))
                # Refresh buffer
                if hasattr(buffer, "start_stream"):
                    buffer.start_stream(mandatory=True, play_sound=False)
            else:
                import output
                output.speak(_("Failed to delete post."))
