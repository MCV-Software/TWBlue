from __future__ import annotations

import logging
import wx
import asyncio
import output
from mysc.thread_utils import call_threaded
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
        # Home (Following-only timeline - reverse-chronological)
        pub.sendMessage(
            "createBuffer",
            buffer_type="following_timeline",
            session_type="blueski",
            buffer_title=_("Home"),
            parent_tab=root_position,
            start=False,
            kwargs=dict(parent=controller.view.nb, name="following_timeline", session=session)
        )
        # Mentions (replies, mentions, quotes)
        pub.sendMessage(
            "createBuffer",
            buffer_type="MentionsBuffer",
            session_type="blueski",
            buffer_title=_("Mentions"),
            parent_tab=root_position,
            start=False,
            kwargs=dict(parent=controller.view.nb, name="mentions", session=session)
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
        # Sent posts
        pub.sendMessage(
            "createBuffer",
            buffer_type="SentBuffer",
            session_type="blueski",
            buffer_title=_("Sent"),
            parent_tab=root_position,
            start=False,
            kwargs=dict(parent=controller.view.nb, name="sent", session=session)
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
        # Followings (Users you follow)
        pub.sendMessage(
            "createBuffer",
            buffer_type="FollowingBuffer",
            session_type="blueski",
            buffer_title=_("Followings"),
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

        # Timelines container
        pub.sendMessage(
            "createBuffer",
            buffer_type="EmptyBuffer",
            session_type="base",
            buffer_title=_("Timelines"),
            parent_tab=root_position,
            start=False,
            kwargs=dict(parent=controller.view.nb, name="timelines", account=name)
        )
        timelines_position = controller.view.search("timelines", name)

        # Saved user timelines
        try:
            timelines = session.settings["other_buffers"].get("timelines")
            if timelines is None:
                timelines = []
            if isinstance(timelines, str):
                timelines = [t for t in timelines.split(",") if t]
            for actor in timelines:
                handle = actor
                try:
                    if isinstance(actor, str) and actor.startswith("did:"):
                        profile = session.get_profile(actor)
                        if profile:
                            def g(obj, key, default=None):
                                if isinstance(obj, dict):
                                    return obj.get(key, default)
                                return getattr(obj, key, default)
                            handle = g(profile, "handle") or actor
                except Exception:
                    handle = actor
                title = _("Timeline for {user}").format(user=handle)
                pub.sendMessage(
                    "createBuffer",
                    buffer_type="UserTimeline",
                    session_type="blueski",
                    buffer_title=title,
                    parent_tab=timelines_position,
                    start=False,
                    kwargs=dict(parent=controller.view.nb, name=f"{handle}-timeline", session=session, actor=actor, handle=handle)
                )
        except Exception:
            logger.exception("Failed to restore Bluesky timeline buffers")

        # Saved followers/following timelines
        try:
            followers = session.settings["other_buffers"].get("followers_timelines")
            if followers is None:
                followers = []
            if isinstance(followers, str):
                followers = [t for t in followers.split(",") if t]
            for actor in followers:
                handle = actor
                try:
                    if isinstance(actor, str) and actor.startswith("did:"):
                        profile = session.get_profile(actor)
                        if profile:
                            def g(obj, key, default=None):
                                if isinstance(obj, dict):
                                    return obj.get(key, default)
                                return getattr(obj, key, default)
                            handle = g(profile, "handle") or actor
                except Exception:
                    handle = actor
                title = _("Followers for {user}").format(user=handle)
                pub.sendMessage(
                    "createBuffer",
                    buffer_type="FollowersBuffer",
                    session_type="blueski",
                    buffer_title=title,
                    parent_tab=timelines_position,
                    start=False,
                    kwargs=dict(parent=controller.view.nb, name=f"{handle}-followers", session=session, actor=actor, handle=handle)
                )
        except Exception:
            logger.exception("Failed to restore Bluesky followers buffers")

        try:
            following = session.settings["other_buffers"].get("following_timelines")
            if following is None:
                following = []
            if isinstance(following, str):
                following = [t for t in following.split(",") if t]
            for actor in following:
                handle = actor
                try:
                    if isinstance(actor, str) and actor.startswith("did:"):
                        profile = session.get_profile(actor)
                        if profile:
                            def g(obj, key, default=None):
                                if isinstance(obj, dict):
                                    return obj.get(key, default)
                                return getattr(obj, key, default)
                            handle = g(profile, "handle") or actor
                except Exception:
                    handle = actor
                title = _("Following for {user}").format(user=handle)
                pub.sendMessage(
                    "createBuffer",
                    buffer_type="FollowingBuffer",
                    session_type="blueski",
                    buffer_title=title,
                    parent_tab=timelines_position,
                    start=False,
                    kwargs=dict(parent=controller.view.nb, name=f"{handle}-following", session=session, actor=actor, handle=handle)
                )
        except Exception:
            logger.exception("Failed to restore Bluesky following buffers")

        # Start the background poller for real-time-like updates
        try:
            session.start_streaming()
        except Exception:
            logger.exception("Failed to start Bluesky streaming for session %s", name)

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
        handle = None
        display_name = None
        if hasattr(buffer, "get_selected_item_author_details"):
            details = buffer.get_selected_item_author_details()
            if details:
                handle = details.get("handle")
        if not handle:
            def g(obj, key, default=None):
                if isinstance(obj, dict):
                    return obj.get(key, default)
                return getattr(obj, key, default)
            author = g(item, "author") or g(g(item, "post"), "author")
            if author:
                handle = g(author, "handle")
                display_name = g(author, "displayName") or g(author, "display_name")
        label = handle or display_name or _("Unknown")
        title = _("Conversation with {0}").format(label)
        
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

    def open_timeline(self, controller, buffer, default="posts"):
        if not hasattr(buffer, "get_item"):
            return
        item = buffer.get_item()
        if not item:
            output.speak(_("No user selected."), True)
            return

        def g(obj, key, default=None):
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)

        users = []
        handle = None
        if hasattr(buffer, "get_selected_item_author_details"):
            details = buffer.get_selected_item_author_details()
            if details:
                handle = details.get("handle") or details.get("did")
        if not handle:
            if g(item, "handle") or g(item, "did"):
                handle = g(item, "handle") or g(item, "did")
            else:
                author = g(item, "author") or g(g(item, "post"), "author")
                if author:
                    handle = g(author, "handle") or g(author, "did")

        if not handle:
            output.speak(_("No user selected."), True)
            return
        users.append(handle)

        # Add mentioned users if available (facets)
        record = g(g(item, "post"), "record") or g(item, "record")
        facets = g(record, "facets", []) if record else []
        handle_cache = {}

        def resolve_handle(did):
            if did in handle_cache:
                return handle_cache[did]
            try:
                profile = buffer.session.get_profile(did)
                if profile:
                    h = g(profile, "handle")
                    if h:
                        handle_cache[did] = h
                        return h
            except Exception:
                pass
            return None

        self_did = buffer.session.db.get("user_id")
        for facet in facets or []:
            features = g(facet, "features", []) or []
            for feat in features:
                ftype = g(feat, "$type") or g(feat, "py_type") or ""
                if "facet#mention" in ftype:
                    did = g(feat, "did")
                    if not did or did == self_did:
                        continue
                    h = resolve_handle(did)
                    if h and h not in users:
                        users.append(h)

        from wxUI.dialogs.mastodon import userTimeline as userTimelineDialog
        dlg = userTimelineDialog.UserTimeline(users=users, default=default)
        try:
            if hasattr(dlg, "autocompletion"):
                dlg.autocompletion.Enable(False)
        except Exception:
            pass
        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return

        action = dlg.get_action()
        user = dlg.get_user().strip() or handle
        dlg.Destroy()

        if user.startswith("@"):
            user = user[1:]
        user_payload = {"handle": user}
        if action == "posts":
            result = self.open_user_timeline(main_controller=controller, session=buffer.session, user_payload=user_payload)
        elif action == "followers":
            result = self.open_followers_timeline(main_controller=controller, session=buffer.session, user_payload=user_payload)
        elif action == "following":
            result = self.open_following_timeline(main_controller=controller, session=buffer.session, user_payload=user_payload)
        else:
            return

        if asyncio.iscoroutine(result):
            call_threaded(asyncio.run, result)

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

    def open_user_timeline(self, main_controller, session, user_payload=None):
        """Open posts timeline for a user (Alt+Win+I)."""
        actor, handle = self._resolve_actor(session, user_payload)
        if not actor:
            output.speak(_("No user selected."), True)
            return

        actor, handle = self._resolve_actor(session, {"did": actor, "handle": handle})
        if not handle:
            handle = actor

        account_name = session.get_name()
        list_name = f"{handle}-timeline"
        if main_controller.search_buffer(list_name, account_name):
            index = main_controller.view.search(list_name, account_name)
            if index is not None:
                main_controller.view.change_buffer(index)
            return

        title = _("Timeline for {user}").format(user=handle)
        from pubsub import pub
        pub.sendMessage(
            "createBuffer",
            buffer_type="UserTimeline",
            session_type="blueski",
            buffer_title=title,
            parent_tab=main_controller.view.search("timelines", account_name),
            start=True,
            kwargs=dict(parent=main_controller.view.nb, name=list_name, session=session, actor=actor, handle=handle)
        )
        try:
            timelines = session.settings["other_buffers"].get("timelines")
            if timelines is None:
                timelines = []
            if isinstance(timelines, str):
                timelines = [t for t in timelines.split(",") if t]
            key = actor or handle
            if key in timelines:
                from wxUI import commonMessageDialogs
                commonMessageDialogs.timeline_exist()
                return
            if key:
                timelines.append(key)
                session.settings["other_buffers"]["timelines"] = timelines
                session.settings.write()
        except Exception:
            logger.exception("Failed to persist Bluesky timeline buffer")

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
        if isinstance(actor, str):
            actor = actor.strip()
            if actor.startswith("@"):
                actor = actor[1:]
        if isinstance(handle, str):
            handle = handle.strip()
            if handle.startswith("@"):
                handle = handle[1:]
        # Resolve handle -> DID when possible, and keep handle for titles
        try:
            if isinstance(actor, str) and not actor.startswith("did:"):
                profile = session.get_profile(actor)
                if profile:
                    did = g(profile, "did")
                    if did:
                        actor = did
                    if not handle:
                        handle = g(profile, "handle")
        except Exception:
            pass

        if not actor:
            actor = session.db.get("user_id") or session.db.get("user_name")
            handle = session.db.get("user_name") or actor

        if not handle and isinstance(actor, str):
            try:
                if actor.startswith("did:"):
                    profile = session.get_profile(actor)
                    if profile:
                        handle = g(profile, "handle")
            except Exception:
                pass

        return actor, handle

    def _open_user_list(self, main_controller, session, actor, handle, list_type):
        account_name = session.get_name()
        if not handle:
            handle = actor
        own_actor = session.db.get("user_id") or session.db.get("user_name")
        own_handle = session.db.get("user_name")
        if actor == own_actor or (own_handle and actor == own_handle) or (handle and own_handle and handle == own_handle):
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

        settings_key = "followers_timelines" if list_type == "followers" else "following_timelines"
        try:
            stored = session.settings["other_buffers"].get(settings_key)
            if stored is None:
                stored = []
            if isinstance(stored, str):
                stored = [t for t in stored.split(",") if t]
            key = actor or handle
            if key in stored:
                from wxUI import commonMessageDialogs
                commonMessageDialogs.timeline_exist()
                return
        except Exception:
            stored = None

        title = _("Followers for {user}").format(user=handle) if list_type == "followers" else _("Following for {user}").format(user=handle)
        from pubsub import pub
        pub.sendMessage(
            "createBuffer",
            buffer_type="FollowersBuffer" if list_type == "followers" else "FollowingBuffer",
            session_type="blueski",
            buffer_title=title,
            parent_tab=main_controller.view.search("timelines", account_name),
            start=True,
            kwargs=dict(parent=main_controller.view.nb, name=list_name, session=session, actor=actor, handle=handle)
        )
        try:
            if stored is None:
                stored = session.settings["other_buffers"].get(settings_key) or []
                if isinstance(stored, str):
                    stored = [t for t in stored.split(",") if t]
            key = actor or handle
            if key:
                stored.append(key)
                session.settings["other_buffers"][settings_key] = stored
                session.settings.write()
        except Exception:
            logger.exception("Failed to persist Bluesky %s buffer", list_type)

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

    def search(self, controller, session):
        """Open search dialog and create search buffer for results."""
        dlg = wx.TextEntryDialog(
            controller.view,
            _("Enter search term:"),
            _("Search Bluesky")
        )
        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return

        query = dlg.GetValue().strip()
        dlg.Destroy()

        if not query:
            return

        # Create unique buffer name for this search
        buffer_name = f"search_{query[:20]}"
        account_name = session.get_name()

        # Check if buffer already exists
        existing = controller.search_buffer(buffer_name, account_name)
        if existing:
            # Navigate to existing buffer
            index = controller.view.search(buffer_name, account_name)
            if index is not None:
                controller.view.change_buffer(index)
                # Refresh search
                existing.search_query = query
                existing.start_stream(mandatory=True, play_sound=False)
            return

        # Create new search buffer
        title = _("Search: {query}").format(query=query)
        from pubsub import pub
        pub.sendMessage(
            "createBuffer",
            buffer_type="SearchBuffer",
            session_type="blueski",
            buffer_title=title,
            parent_tab=controller.view.search(account_name, account_name),
            start=True,
            kwargs=dict(
                parent=controller.view.nb,
                name=buffer_name,
                session=session,
                query=query
            )
        )
