from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

fromapprove.controller.base import BaseHandler
fromapprove.sessions import SessionStoreInterface

if TYPE_CHECKING:
    fromapprove.config import Config
    fromapprove.sessions.atprotosocial.session import Session as ATProtoSocialSession

logger = logging.getLogger(__name__)


class Handler(BaseHandler):
    SESSION_KIND = "atprotosocial"

    def __init__(self, session_store: SessionStoreInterface, config: Config) -> None:
        super().__init__(session_store, config)
        self.main_controller = wx.GetApp().mainController # Get a reference to the mainController
        # Define menu labels specific to ATProtoSocial
        self.menus = {
            "menubar_item": _("&Post"),  # Top-level menu for posting actions
            "compose": _("&New Post"),   # New post/skeet
            "share": _("&Repost"),       # Equivalent of Boost/Retweet
            "fav": _("&Like"),           # Equivalent of Favorite
            "unfav": _("&Unlike"),
            # "dm": None,  # Disable Direct Message if not applicable
            # Add other menu items that need relabeling or enabling/disabling
        }
        # self.item_menu is another attribute used in mainController.update_menus
        # It seems to be the label for the second main menu (originally "&Tweet")
        self.item_menu = _("&Post") # Changes the top-level "Tweet" menu label to "Post"

    def _get_session(self, user_id: str) -> ATProtoSocialSession:
        session = self.session_store.get_session_by_user_id(user_id, self.SESSION_KIND)
        if not session:
            # It's possible the session is still being created, especially during initial setup.
            # Try to get it from the global sessions store if it was just added.
            from sessions import sessions as global_sessions
            if user_id in global_sessions and global_sessions[user_id].KIND == self.SESSION_KIND:
                return global_sessions[user_id] # type: ignore[return-value]
            raise ValueError(f"No ATProtoSocial session found for user {user_id}")
        return session # type: ignore[return-value] # We are checking kind

    def create_buffers(self, user_id: str) -> None:
        """Creates the default set of buffers for an ATProtoSocial session."""
        session = self._get_session(user_id)
        if not session:
            logger.error(f"Cannot create buffers for ATProtoSocial user {user_id}: session not found.")
            return

        logger.info(f"Creating default buffers for ATProtoSocial user {user_id} ({session.label})")

        # Home Timeline Buffer
        self.main_controller.add_buffer(
            buffer_type="home_timeline", # Generic type, panel will adapt based on session kind
            user_id=user_id,
            name=_("{label} Home").format(label=session.label),
            session_kind=self.SESSION_KIND
        )

        # Notifications Buffer
        self.main_controller.add_buffer(
            buffer_type="notifications", # Generic type
            user_id=user_id,
            name=_("{label} Notifications").format(label=session.label),
            session_kind=self.SESSION_KIND
        )

        # Own Posts (Profile) Buffer - using "user_posts" which is often generic
        # self.main_controller.add_buffer(
        #     buffer_type="user_posts",
        #     user_id=user_id, # User whose posts to show (self in this case)
        #     target_user_id=session.util.get_own_did(), # Pass own DID as target
        #     name=_("{label} My Posts").format(label=session.label),
        #     session_kind=self.SESSION_KIND
        # )
        # Mentions buffer might be part of notifications or a separate stream/filter later.

        # Ensure these buffers are shown if it's a new setup
        # This part might be handled by mainController.add_buffer or session startup logic
        # For now, just creating them. The UI should make them visible.

    # --- Action Handlers (called by mainController based on menu interactions) ---

    async def repost_item(self, session: ATProtoSocialSession, item_uri: str) -> dict[str, Any]:
        """Handles reposting an item."""
        if not session.is_ready():
            return {"status": "error", "message": _("Session not ready.")}
        try:
            success = await session.util.repost_post(item_uri) # Assuming repost_post in utils
            if success:
                return {"status": "success", "message": _("Post reposted successfully.")}
            else:
                return {"status": "error", "message": _("Failed to repost post.")}
        except NotificationError as e:
            return {"status": "error", "message": e.message}
        except Exception as e:
            logger.error(f"Error reposting item {item_uri}: {e}", exc_info=True)
            return {"status": "error", "message": _("An unexpected error occurred while reposting.")}

    async def like_item(self, session: ATProtoSocialSession, item_uri: str) -> dict[str, Any]:
        """Handles liking an item."""
        if not session.is_ready():
            return {"status": "error", "message": _("Session not ready.")}
        try:
            like_uri = await session.util.like_post(item_uri) # Assuming like_post in utils
            if like_uri:
                return {"status": "success", "message": _("Post liked successfully."), "like_uri": like_uri}
            else:
                return {"status": "error", "message": _("Failed to like post.")}
        except NotificationError as e:
            return {"status": "error", "message": e.message}
        except Exception as e:
            logger.error(f"Error liking item {item_uri}: {e}", exc_info=True)
            return {"status": "error", "message": _("An unexpected error occurred while liking the post.")}

    async def unlike_item(self, session: ATProtoSocialSession, like_uri: str) -> dict[str, Any]: # like_uri is the URI of the like record
        """Handles unliking an item."""
        if not session.is_ready():
            return {"status": "error", "message": _("Session not ready.")}
        try:
            # Unlike typically requires the URI of the like record itself, not the post.
            # The UI or calling context needs to store this (e.g. from viewer_state of the post).
            success = await session.util.delete_like(like_uri) # Assuming delete_like in utils
            if success:
                return {"status": "success", "message": _("Like removed successfully.")}
            else:
                return {"status": "error", "message": _("Failed to remove like.")}
        except NotificationError as e:
            return {"status": "error", "message": e.message}
        except Exception as e:
            logger.error(f"Error unliking item with like URI {like_uri}: {e}", exc_info=True)
            return {"status": "error", "message": _("An unexpected error occurred while unliking.")}


    async def handle_action(self, action_name: str, user_id: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        """Handles actions specific to ATProtoSocial integration."""
        logger.debug(
            f"Handling ATProtoSocial action '{action_name}' for user {user_id} with payload: {payload}"
        )
        # session = self._get_session(user_id)

        # TODO: Implement action handlers based on ATProtoSocial's capabilities
        # Example:
        # if action_name == "get_profile_info":
        #     # profile_data = await session.util.get_profile_info(payload.get("handle"))
        #     # return {"profile": profile_data}
        # elif action_name == "follow_user":
        #     # await session.util.follow_user(payload.get("user_id_to_follow"))
        #     # return {"status": "success", "message": "User followed"}
        # else:
        #     logger.warning(f"Unknown ATProtoSocial action: {action_name}")
        #     return {"error": f"Unknown action: {action_name}"}
        return None # Placeholder

    async def handle_message_command(
        self, command: str, user_id: str, message_id: str, payload: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Handles commands related to specific messages for ATProtoSocial."""
        logger.debug(
            f"Handling ATProtoSocial message command '{command}' for user {user_id}, message {message_id} with payload: {payload}"
        )
        # session = self._get_session(user_id)

        # TODO: Implement message command handlers
        # Example:
        # if command == "get_post_details":
        #     # post_details = await session.util.get_post_by_id(message_id)
        #     # return {"details": post_details}
        # elif command == "like_post":
        #     # await session.util.like_post(message_id)
        #     # return {"status": "success", "message": "Post liked"}
        # else:
        #     logger.warning(f"Unknown ATProtoSocial message command: {command}")
        #     return {"error": f"Unknown message command: {command}"}
        return None # Placeholder

fromapprove.translation import translate as _ # For user-facing messages

    async def handle_user_command(
        self, command: str, user_id: str, target_user_id: str, payload: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Handles commands related to specific users for ATProtoSocial."""
        logger.debug(
            f"Handling ATProtoSocial user command '{command}' for user {user_id}, target user {target_user_id} with payload: {payload}"
        )
        session = self._get_session(user_id)
        if not session.is_ready():
            return {"status": "error", "message": _("ATProtoSocial session is not active or authenticated.")}

        # target_user_id is expected to be the DID of the user to act upon.
        if not target_user_id:
            return {"status": "error", "message": _("Target user DID not provided.")}

        success = False
        message = _("Action could not be completed.") # Default error message

        try:
            if command == "follow_user":
                success = await session.util.follow_user(target_user_id)
                message = _("User followed successfully.") if success else _("Failed to follow user.")
            elif command == "unfollow_user":
                success = await session.util.unfollow_user(target_user_id)
                message = _("User unfollowed successfully.") if success else _("Failed to unfollow user.")
            elif command == "mute_user":
                success = await session.util.mute_user(target_user_id)
                message = _("User muted successfully.") if success else _("Failed to mute user.")
            elif command == "unmute_user":
                success = await session.util.unmute_user(target_user_id)
                message = _("User unmuted successfully.") if success else _("Failed to unmute user.")
            elif command == "block_user":
                block_uri = await session.util.block_user(target_user_id) # Returns URI or None
                success = bool(block_uri)
                message = _("User blocked successfully.") if success else _("Failed to block user.")
            elif command == "unblock_user":
                success = await session.util.unblock_user(target_user_id)
                message = _("User unblocked successfully.") if success else _("Failed to unblock user, or user was not blocked.")
            else:
                logger.warning(f"Unknown ATProtoSocial user command: {command}")
                return {"status": "error", "message": _("Unknown action: {command}").format(command=command)}

            return {"status": "success" if success else "error", "message": message}

        except NotificationError as e: # Catch specific errors raised from utils
            logger.error(f"ATProtoSocial user command '{command}' failed for target {target_user_id}: {e.message}")
            return {"status": "error", "message": e.message}
        except Exception as e:
            logger.error(f"Unexpected error during ATProtoSocial user command '{command}' for target {target_user_id}: {e}", exc_info=True)
            return {"status": "error", "message": _("An unexpected server error occurred.")}

    # --- UI Related Action Handlers (called by mainController) ---

    async def user_details(self, buffer: Any) -> None: # buffer is typically a timeline panel
        """Shows user profile details for the selected user in the buffer."""
        session = buffer.session
        if not session or session.KIND != self.SESSION_KIND or not session.is_ready():
            output.speak(_("Active ATProtoSocial session not found or not ready."), True)
            return

        user_ident = None
        if hasattr(buffer, "get_selected_item_author_details"): # Method in panel to get author of selected post
            author_details = buffer.get_selected_item_author_details()
            if author_details and isinstance(author_details, dict):
                user_ident = author_details.get("did") or author_details.get("handle")

        if not user_ident:
            # Fallback or if no item selected, prompt for user
            # For now, just inform user if no selection. A dialog prompt could be added.
            output.speak(_("Please select an item or user to view details."), True)
            # TODO: Add wx.TextEntryDialog to ask for user handle/DID if none selected
            return

        try:
            profile_data = await session.util.get_user_profile(user_ident)
            if profile_data:
                # Example: from src.wxUI.dialogs.mastodon.showUserProfile import UserProfileDialog
                # For ATProtoSocial, we use the new dialog:
                from wxUI.dialogs.atprotosocial.showUserProfile import ShowUserProfileDialog
                # Ensure main_controller.view is the correct parent (main frame)
                dialog = ShowUserProfileDialog(parent=self.main_controller.view, session=session, user_identifier=user_ident)
                dialog.ShowModal() # Show as modal dialog
                dialog.Destroy()
            else:
                output.speak(_("Could not fetch profile for {user_ident}.").format(user_ident=user_ident), True)
        except Exception as e:
            logger.error(f"Error fetching/displaying profile for {user_ident}: {e}", exc_info=True)
            output.speak(_("Error displaying profile: {error}").format(error=str(e)), True)


    async def open_user_timeline(self, main_controller: Any, session: ATProtoSocialSession, user_payload: Any | None) -> None:
        """Opens a new buffer for a specific user's posts."""
        user_ident = None
        if isinstance(user_payload, dict): # Assuming user_payload is a dict from get_selected_item_author_details
            user_ident = user_payload.get("did") or user_payload.get("handle")
        elif isinstance(user_payload, str): # Direct DID or Handle string
            user_ident = user_payload

        if not user_ident: # Prompt if not found
            dialog = wx.TextEntryDialog(main_controller.view, _("Enter user DID or handle:"), _("View User Timeline"))
            if dialog.ShowModal() == wx.ID_OK:
                user_ident = dialog.GetValue()
            dialog.Destroy()
            if not user_ident:
                return

        # Fetch profile to get canonical handle/DID for buffer name, and to ensure user exists
        try:
            profile = await session.util.get_user_profile(user_ident)
            if not profile:
                output.speak(_("User {user_ident} not found.").format(user_ident=user_ident), True)
                return

            buffer_name = _("{user_handle}'s Posts").format(user_handle=profile.handle)
            buffer_id = f"atp_user_feed_{profile.did}" # Unique ID for the buffer

            # Check if buffer already exists
            # existing_buffer = main_controller.search_buffer_by_id_or_properties(id=buffer_id) # Hypothetical method
            # For now, assume it might create duplicates if not handled by add_buffer logic

            main_controller.add_buffer(
                buffer_type="user_timeline", # This type will need a corresponding panel
                user_id=session.uid, # The session user_id
                name=buffer_name,
                session_kind=self.SESSION_KIND,
                target_user_did=profile.did, # Store target DID for the panel to use
                target_user_handle=profile.handle
            )
        except Exception as e:
            logger.error(f"Error opening user timeline for {user_ident}: {e}", exc_info=True)
            output.speak(_("Failed to open user timeline: {error}").format(error=str(e)), True)


    async def open_followers_timeline(self, main_controller: Any, session: ATProtoSocialSession, user_payload: Any | None) -> None:
        """Opens a new buffer for a user's followers."""
        user_ident = None
        if isinstance(user_payload, dict):
            user_ident = user_payload.get("did") or user_payload.get("handle")
        elif isinstance(user_payload, str):
            user_ident = user_payload

        if not user_ident:
            dialog = wx.TextEntryDialog(main_controller.view, _("Enter user DID or handle to view followers:"), _("View Followers"))
            if dialog.ShowModal() == wx.ID_OK:
                user_ident = dialog.GetValue()
            dialog.Destroy()
            if not user_ident:
                return

        try:
            profile = await session.util.get_user_profile(user_ident) # Ensure user exists, get DID
            if not profile:
                output.speak(_("User {user_ident} not found.").format(user_ident=user_ident), True)
                return

            buffer_name = _("Followers of {user_handle}").format(user_handle=profile.handle)
            main_controller.add_buffer(
                buffer_type="user_list_followers", # Needs specific panel type
                user_id=session.uid,
                name=buffer_name,
                session_kind=self.SESSION_KIND,
                target_user_did=profile.did
            )
        except Exception as e:
            logger.error(f"Error opening followers list for {user_ident}: {e}", exc_info=True)
            output.speak(_("Failed to open followers list: {error}").format(error=str(e)), True)


    async def open_following_timeline(self, main_controller: Any, session: ATProtoSocialSession, user_payload: Any | None) -> None:
        """Opens a new buffer for users a user is following."""
        user_ident = None
        if isinstance(user_payload, dict):
            user_ident = user_payload.get("did") or user_payload.get("handle")
        elif isinstance(user_payload, str):
            user_ident = user_payload

        if not user_ident:
            dialog = wx.TextEntryDialog(main_controller.view, _("Enter user DID or handle to view their following list:"), _("View Following"))
            if dialog.ShowModal() == wx.ID_OK:
                user_ident = dialog.GetValue()
            dialog.Destroy()
            if not user_ident:
                return

        try:
            profile = await session.util.get_user_profile(user_ident) # Ensure user exists, get DID
            if not profile:
                output.speak(_("User {user_ident} not found.").format(user_ident=user_ident), True)
                return

            buffer_name = _("Following by {user_handle}").format(user_handle=profile.handle)
            main_controller.add_buffer(
                buffer_type="user_list_following", # Needs specific panel type
                user_id=session.uid,
                name=buffer_name,
                session_kind=self.SESSION_KIND,
                target_user_did=profile.did
            )
        except Exception as e:
            logger.error(f"Error opening following list for {user_ident}: {e}", exc_info=True)
            output.speak(_("Failed to open following list: {error}").format(error=str(e)), True)


    async def get_settings_inputs(self, user_id: str | None = None) -> list[dict[str, Any]]:
        """Returns settings inputs for ATProtoSocial, potentially user-specific."""
        # This typically delegates to the Session class's method
        fromapprove.sessions.atprotosocial.session import Session as ATProtoSocialSession

        current_config = {}
        if user_id:
            # Fetch existing config for the user if available to pre-fill values
            # This part depends on how config is stored and accessed.
            # For example, if Session class has a method to get its current config:
            try:
                session = self._get_session(user_id)
                current_config = session.get_configurable_values_for_user(user_id)
            except ValueError: # No session means no specific config yet for this user
                pass
            except Exception as e:
                logger.error(f"Error fetching current ATProtoSocial config for user {user_id}: {e}")


        return ATProtoSocialSession.get_settings_inputs(user_id=user_id, current_config=current_config)

    async def update_settings(self, user_id: str, settings_data: dict[str, Any]) -> dict[str, Any]:
        """Updates settings for ATProtoSocial for a given user."""
        logger.info(f"Updating ATProtoSocial settings for user {user_id}")

        # This is a simplified example. In a real scenario, you'd validate `settings_data`
        # and then update the configuration, possibly re-initializing the session or
        # informing it of the changes.

        # config_manager = self.config.sessions.atprotosocial[user_id]
        # for key, value in settings_data.items():
        #     if hasattr(config_manager, key):
        #         await config_manager[key].set(value)
        #     else:
        #         logger.warning(f"Attempted to set unknown ATProtoSocial setting '{key}' for user {user_id}")

        # # Optionally, re-initialize or notify the session if it's active
        # try:
        #     session = self._get_session(user_id)
        #     await session.stop() # Stop if it might be using old settings
        #     # Re-fetch config for the session or update it directly
        #     # session.api_base_url = settings_data.get("api_base_url", session.api_base_url)
        #     # session.access_token = settings_data.get("access_token", session.access_token)
        #     if session.active: # Or based on some logic if it should auto-restart
        #         await session.start()
        #     logger.info(f"Successfully updated and re-initialized ATProtoSocial session for user {user_id}")
        # except ValueError:
        #     logger.info(f"ATProtoSocial session for user {user_id} not found or not active, settings saved but session not restarted.")
        # except Exception as e:
        #     logger.error(f"Error re-initializing ATProtoSocial session for user {user_id} after settings update: {e}")
        #     return {"status": "error", "message": f"Settings saved, but failed to restart session: {e}"}

        # For now, just a placeholder response
        return {"status": "success", "message": "ATProtoSocial settings updated (implementation pending)."}

    @classmethod
    def get_auth_inputs(cls, user_id: str | None = None) -> list[dict[str, Any]]:
        fromapprove.sessions.atprotosocial.session import Session as ATProtoSocialSession
        # current_config = {} # fetch if needed
        return ATProtoSocialSession.get_auth_inputs(user_id=user_id) # current_config=current_config

    @classmethod
    async def test_connection(cls, settings: dict[str, Any]) -> tuple[bool, str]:
        fromapprove.sessions.atprotosocial.session import Session as ATProtoSocialSession
        return await ATProtoSocialSession.test_connection(settings)

    @classmethod
    def get_user_actions(cls) -> list[dict[str, Any]]:
        fromapprove.sessions.atprotosocial.session import Session as ATProtoSocialSession
        return ATProtoSocialSession.get_user_actions()

    @classmethod
    def get_user_list_actions(cls) -> list[dict[str, Any]]:
        fromapprove.sessions.atprotosocial.session import Session as ATProtoSocialSession
        return ATProtoSocialSession.get_user_list_actions()

    @classmethod
    def get_config_description(cls) -> str | None:
        fromapprove.sessions.atprotosocial.session import Session as ATProtoSocialSession
        return ATProtoSocialSession.get_config_description()

    @classmethod
    def get_auth_type(cls) -> str:
        fromapprove.sessions.atprotosocial.session import Session as ATProtoSocialSession
        return ATProtoSocialSession.get_auth_type()

    @classmethod
    def get_logo_path(cls) -> str | None:
        fromapprove.sessions.atprotosocial.session import Session as ATProtoSocialSession
        return ATProtoSocialSession.get_logo_path()

    @classmethod
    def get_session_kind(cls) -> str:
        return cls.SESSION_KIND

    @classmethod
    def get_dependencies(cls) -> list[str]:
        fromapprove.sessions.atprotosocial.session import Session as ATProtoSocialSession
        return ATProtoSocialSession.get_dependencies()
