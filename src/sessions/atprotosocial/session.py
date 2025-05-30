from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import wx # For dialogs
from tornado.ioloop import IOLoop

from atproto import AsyncClient, Client # Bluesky SDK
from atproto.xrpc_client.models.common import XrpcError # For error handling

fromapprove import channels, constants, util
fromapprove.approval import ApprovalAPI, ApprovalResult
fromapprove.config import Config, config, ConfigurableValue # Import ConfigurableValue properly
fromapprove.notifications import Notification, NotificationError, NotificationKind
fromapprove.reporting import Reporter, ReportingDecision, ReportingReasons
fromapprove.sessions.atprotosocial import compose as atprotosocial_compose
fromapprove.sessions.atprotosocial import streaming as atprotosocial_streaming
fromapprove.sessions.atprotosocial import templates as atprotosocial_templates
fromapprove.sessions.atprotosocial import utils as atprotosocial_utils
fromapprove.sessions.base import baseSession
fromapprove.translation import translate as _
fromapprove.util import GenerateID

if TYPE_CHECKING:
    fromapprove.channels import Channel
    fromapprove.notifications import NotificationData
    fromapprove.reporting import ReportData
    fromapprove.sessions.atprotosocial.compose import ATProtoSocialCompose
    fromapprove.sessions.atprotosocial.streaming import ATProtoSocialStreaming
    fromapprove.sessions.atprotosocial.templates import ATProtoSocialTemplates
    fromapprove.sessions.atprotosocial.utils import ATProtoSocialUtils

logger = logging.getLogger(__name__)


class Session(baseSession):
    KIND = "atprotosocial"
    LABEL = "ATProtoSocial"
    HAS_SETTINGS = True
    CAN_APPROVE = True
    CAN_REPORT = True
    CAN_STREAM = True

    _client: AsyncClient | None = None # Authenticated ATProto client
    _compose_panel: ATProtoSocialCompose | None = None
    _streaming_manager: ATProtoSocialStreaming | None = None
    _templates: ATProtoSocialTemplates | None = None
    _util: ATProtoSocialUtils | None = None

    # Define ConfigurableValues for ATProtoSocial
    handle = ConfigurableValue("handle", "")
    app_password = ConfigurableValue("app_password", "", is_secret=True) # Mark as secret
    did = ConfigurableValue("did", "", is_readonly=True) # Read-only, stored after login


    def __init__(self, approval_api: ApprovalAPI, user_id: str, channel_id: str) -> None:
        super().__init__(approval_api, user_id, channel_id)
        self.client: AsyncClient | None = None # Renamed from _client to avoid conflict with base class
        self._load_session_from_db()

        # Timeline specific attributes
        self.home_timeline_buffer: list[str] = [] # Stores AT URIs of posts in home timeline
        self.home_timeline_cursor: str | None = None
        # self.user_posts_buffer: list[str] = [] # For viewing a specific user's posts - managed by UI context
        # self.user_posts_cursor: str | None = None
        # self.message_cache is inherited from baseSession for storing post details

    async def login(self, handle: str, app_password: str) -> bool:
        """Logs into ATProtoSocial using handle and app password."""
        logger.info(f"ATProtoSocial: Attempting login for handle {handle}")
        try:
            # Ensure util is initialized so it can also store DID/handle
            _ = self.util

            temp_client = AsyncClient()
            profile = await temp_client.login(handle, app_password)
            if profile and profile.access_jwt and profile.did and profile.handle:
                self.client = temp_client # Assign the successfully logged-in client

                self.db["access_jwt"] = profile.access_jwt
                self.db["refresh_jwt"] = profile.refresh_jwt
                self.db["did"] = profile.did
                self.db["handle"] = profile.handle
                await self.save_db()

                # Update util with new DID and handle
                if self._util:
                    self._util._own_did = profile.did
                    self._util._own_handle = profile.handle

                # Update config store as well
                await config.sessions.atprotosocial[self.user_id].handle.set(profile.handle)
                await config.sessions.atprotosocial[self.user_id].app_password.set(app_password) # Store the password used for login
                await config.sessions.atprotosocial[self.user_id].did.set(profile.did)

                logger.info(f"ATProtoSocial: Login successful for {handle}. DID: {profile.did}")
                await self.notify_session_ready()
                return True
            else:
                logger.error(f"ATProtoSocial: Login failed for {handle} - profile data missing.")
                self.client = None
                return False
        except XrpcError as e:
            logger.error(f"ATProtoSocial: Login failed for {handle} (XrpcError): {e.error} - {e.message}")
            self.client = None
            # Specific error for invalid credentials if possible
            if e.error == 'AuthenticationFailed' or e.error == 'InvalidRequest' and 'password' in str(e.message).lower():
                 # This is a guess, actual error might differ. Need to check Bluesky SDK specifics.
                raise NotificationError(_("Invalid handle or app password.")) from e
            raise NotificationError(_("Login failed: {error} - {message}").format(error=e.error, message=e.message or "Protocol error")) from e
        except Exception as e:
            logger.error(f"ATProtoSocial: Login failed for {handle} (Exception): {e}", exc_info=True)
            self.client = None
            raise NotificationError(_("An unexpected error occurred during login: {error}").format(error=str(e))) from e

    def _load_session_from_db(self) -> None:
        """Loads session details from DB and attempts to initialize the client."""
        access_jwt = self.db.get("access_jwt")
        handle = self.db.get("handle") # Or get from config: self.config_get("handle")

        if access_jwt and handle:
            logger.info(f"ATProtoSocial: Found existing session for {handle} in DB. Initializing client.")
            # Create a new client instance and load session.
            # The atproto SDK's AsyncClient doesn't have a simple "load_session" from individual tokens.
            # It re-logins or expects a full session object from client.export_session_string()
            # For simplicity here, we'll rely on re-login if needed or assume test_connection handles it.
            # A more robust way would be to use client.resume_session(profile_dict_from_db) if available
            # or store the output of client.export_session_string() and client = AsyncClient.import_session_string(...)

            # For now, we won't auto-resume here but rely on start() or is_ready() to trigger login/test.
            # self.client = AsyncClient() # Create a placeholder client
            # TODO: Properly resume session with SDK if possible without re-login.
            # One way: if we have refreshJwt, we could try to refresh the session.
            # For now, is_ready() will be false and start() will attempt login if needed.
            logger.debug(f"ATProtoSocial: Session for {handle} loaded. Further checks in is_ready/start.")
        else:
            logger.info("ATProtoSocial: No existing session found in DB.")


    async def authorise(self) -> bool:
        """Prompts the user for Bluesky handle and app password and attempts to log in."""
        if not wx.GetApp(): # Ensure wx App exists
            logger.error("ATProtoSocial: wx.App not available for dialogs.")
            self.send_text_notification(
                title=_("ATProtoSocial Authentication Error"),
                message=_("Cannot display login dialogs. Please check application logs.")
            )
            return False

        handle_dialog = wx.TextEntryDialog(
            None,
            _("Enter your Bluesky handle (e.g., username.bsky.social):"),
            _("Bluesky Login"),
            self.config_get("handle") or "" # Pre-fill with saved handle if any
        )
        if handle_dialog.ShowModal() == wx.ID_OK:
            handle = handle_dialog.GetValue()
            handle_dialog.Destroy()

            password_dialog = wx.PasswordEntryDialog(
                None,
                _("Enter your Bluesky App Password (generate one in Bluesky settings):"),
                _("Bluesky Login")
            )
            if password_dialog.ShowModal() == wx.ID_OK:
                app_password = password_dialog.GetValue()
                password_dialog.Destroy()

                try:
                    if await self.login(handle, app_password):
                        wx.MessageBox(_("Successfully logged into Bluesky!"), _("Login Success"), wx.OK | wx.ICON_INFORMATION)
                        return True
                    else:
                        # Login method now raises NotificationError, so this part might not be reached
                        # if error handling is done via exceptions.
                        wx.MessageBox(_("Login failed. Please check your handle and app password."), _("Login Failed"), wx.OK | wx.ICON_ERROR)
                        return False
                except NotificationError as e: # Catch errors from login()
                    wx.MessageBox(str(e), _("Login Failed"), wx.OK | wx.ICON_ERROR)
                    return False
                except Exception as e:
                    logger.error(f"ATProtoSocial: Unexpected error during authorise: {e}", exc_info=True)
                    wx.MessageBox(_("An unexpected error occurred: {error}").format(error=str(e)), _("Login Error"), wx.OK | wx.ICON_ERROR)
                    return False
            else:
                password_dialog.Destroy()
                return False # User cancelled password dialog
        else:
            handle_dialog.Destroy()
            return False # User cancelled handle dialog
        return False


    async def _ensure_dependencies_ready(self) -> None:
        """Ensure all dependencies are ready to be used."""
        # This could check if the atproto library is installed, though get_dependencies handles that.
        # More relevant here: ensuring the client is authenticated if credentials exist.
        if not self.is_ready():
            logger.info("ATProtoSocial: Session not ready, attempting to re-establish from config.")
            handle = self.config_get("handle")
            app_password = self.config_get("app_password") # This might be empty if not re-saved

            # Try to login if we have handle and app_password from config
            if handle and app_password:
                try:
                    await self.login(handle, app_password)
                except NotificationError: # Login failed, don't bubble up here
                    logger.warning(f"ATProtoSocial: Auto-login attempt failed for {handle} during ensure_dependencies_ready.")
                    pass # is_ready() will remain false
            elif handle and not app_password:
                logger.info(f"ATProtoSocial: Handle {handle} found but no app password. Manual authorization needed.")
            else:
                logger.info("ATProtoSocial: No credentials in config to attempt auto-login.")


    @property
    def active(self) -> bool:
        return self.is_ready()

    @property
    def kind(self) -> str:
        return self.KIND

    @property
    def label(self) -> str:
        return self.LABEL

    @property
    def has_settings(self) -> bool:
        return self.HAS_SETTINGS

    @property
    def can_approve(self) -> bool:
        return self.CAN_APPROVE

    @property
    def can_report(self) -> bool:
        return self.CAN_REPORT

    @property
    def can_stream(self) -> bool:
        return self.CAN_STREAM

    @property
    def util(self) -> ATProtoSocialUtils:
        if not self._util:
            self._util = atprotosocial_utils.ATProtoSocialUtils(self)
        return self._util

    @property
    def templates(self) -> ATProtoSocialTemplates:
        if not self._templates:
            self._templates = atprotosocial_templates.ATProtoSocialTemplates(self)
        return self._templates

    @property
    def compose_panel(self) -> ATProtoSocialCompose:
        if not self._compose_panel:
            self._compose_panel = atprotosocial_compose.ATProtoSocialCompose(self)
        return self._compose_panel

    @property
    def streaming_manager(self) -> ATProtoSocialStreaming:
        if not self._streaming_manager:
            # TODO: Ensure that this is initialized correctly, potentially with a stream_type
            self._streaming_manager = atprotosocial_streaming.ATProtoSocialStreaming(self, "user") # Placeholder stream_type
        return self._streaming_manager

    async def start(self) -> None:
        logger.info(f"Starting ATProtoSocial session for user {self.user_id}")
        await self._ensure_dependencies_ready() # This will attempt login if needed

        if self.is_ready():
            # Fetch initial home timeline
            try:
                await self.fetch_home_timeline(limit=20, new_only=True) # Fetch newest items
            except NotificationError as e:
                logger.error(f"ATProtoSocial: Failed to fetch initial home timeline: {e}")
                # Non-fatal, session can still start

            if self.can_stream:
                # TODO: Initialize and start streaming if applicable
                # self.streaming_manager.start_streaming(self.handle_streaming_event)
                logger.info(f"ATProtoSocial session for {self.user_id} started. Streaming setup placeholder.")
        elif not self.is_ready():
            logger.warning(f"ATProtoSocial session for {self.user_id} could not be started: not ready (login may have failed or is needed).")


    async def stop(self) -> None:
        logger.info(f"Stopping ATProtoSocial session for user {self.user_id}")
        if self._streaming_manager and self._streaming_manager.is_alive():
            await self._streaming_manager.stop_streaming()
        if self.client:
            # ATProto AsyncClient doesn't have an explicit close/logout that clears local session.
            # We just nullify it on our end.
            self.client = None
        logger.info(f"ATProtoSocial session for {self.user_id} stopped.")

    async def send_message(
        self,
        message: str,
        files: list[str] | None = None, # List of file paths
        reply_to: str | None = None, # AT URI of the post being replied to
        cw_text: str | None = None, # Content warning text
        is_sensitive: bool = False, # General sensitivity flag
        **kwargs: Any, # For additional params like quote_uri, langs, media_alt_texts
    ) -> str | None: # Returns the AT URI of the new post, or None on failure
        """Sends a message (post/skeet) to ATProtoSocial."""
        if not self.is_ready():
            logger.error(f"ATProtoSocial session for {self.user_id} is not ready. Cannot send message.")
            raise NotificationError(_("Session is not active. Please log in or check your connection."))

        logger.debug(
            f"Sending message for ATProtoSocial session {self.user_id}: text='{message}', files={files}, reply_to='{reply_to}', cw_text='{cw_text}', sensitive={is_sensitive}, kwargs={kwargs}"
        )

        media_blobs_for_post = [] # Will hold list of dicts: {"blob_ref": BlobRef, "alt_text": "..."}

        # Media upload handling
        if files:
            # kwargs might contain 'media_alt_texts' as a list parallel to 'files'
            media_alt_texts = kwargs.get("media_alt_texts", [])
            if not isinstance(media_alt_texts, list) or len(media_alt_texts) != len(files):
                media_alt_texts = [""] * len(files) # Default to empty alt text if not provided correctly

            for i, file_path in enumerate(files):
                try:
                    # Determine mime_type (simplified, real app might use python-magic or similar)
                    # For now, rely on file extension.
                    # TODO: More robust MIME type detection
                    ext = file_path.split('.')[-1].lower()
                    mime_type = {
                        'jpg': 'image/jpeg',
                        'jpeg': 'image/jpeg',
                        'png': 'image/png',
                        # 'gif': 'image/gif', # ATProto current primary support is jpeg/png
                    }.get(ext)

                    if not mime_type:
                        logger.warning(f"Unsupported file type for {file_path}, skipping.")
                        # Optionally, notify user about skipped file
                        self.send_text_notification(
                            title=_("Unsupported File Skipped"),
                            message=_("File {filename} has an unsupported type and was not attached.").format(filename=file_path.split('/')[-1])
                        )
                        continue

                    alt_text = media_alt_texts[i]
                    # upload_media returns a dict like {"blob_ref": BlobRef, "alt_text": "..."} or None
                    media_blob_info = await self.util.upload_media(file_path, mime_type, alt_text=alt_text)
                    if media_blob_info:
                        media_blobs_for_post.append(media_blob_info)
                    else:
                        # Notify user about failed upload for this specific file
                        self.send_text_notification(
                            title=_("Media Upload Failed"),
                            message=_("Failed to upload {filename}. It will not be attached.").format(filename=file_path.split('/')[-1])
                        )
                except Exception as e:
                    logger.error(f"Error uploading file {file_path}: {e}", exc_info=True)
                    self.send_text_notification(
                        title=_("Media Upload Error"),
                        message=_("An error occurred while uploading {filename}: {error}").format(filename=file_path.split('/')[-1], error=str(e))
                    )
                    # Depending on policy, either continue without this file or fail the whole post
                    # For now, continue and try to post without this file.

        # Extract other relevant parameters from kwargs
        quote_uri = kwargs.get("quote_uri") # AT URI of the post to quote
        langs = kwargs.get("langs") # List of language codes, e.g., ['en', 'ja']
        if langs and not isinstance(langs, list):
            logger.warning(f"Invalid 'langs' format: {langs}. Expected list of strings. Ignoring.")
            langs = None

        tags = kwargs.get("tags") # List of hashtags (without '#')
        if tags and not isinstance(tags, list):
            logger.warning(f"Invalid 'tags' format: {tags}. Expected list of strings. Ignoring.")
            tags = None

        try:
            # Call the util method to actually create the post
            # self.util.post_status expects media_ids to be the list of blob dicts from upload_media
            post_uri = await self.util.post_status(
                text=message,
                media_ids=media_blobs_for_post if media_blobs_for_post else None,
                reply_to_uri=reply_to,
                quote_uri=quote_uri,
                cw_text=cw_text,
                is_sensitive=is_sensitive,
                langs=langs,
                tags=tags,
                # Any other specific params for Bluesky can be passed via kwargs if post_status handles them
            )

            if post_uri:
                logger.info(f"Message posted successfully to ATProtoSocial. URI: {post_uri}")
                return post_uri
            else:
                # This case should ideally be covered by post_status raising an error,
                # but as a fallback if it returns None on failure without raising:
                logger.error("Failed to post message to ATProtoSocial, post_status returned None.")
                raise NotificationError(_("Failed to send post. The server did not confirm the post creation."))

        except NotificationError: # Re-raise known errors
            raise
        except Exception as e: # Catch unexpected errors from post_status or here
            logger.error(f"An unexpected error occurred in send_message for ATProtoSocial: {e}", exc_info=True)
            raise NotificationError(_("An unexpected error occurred while sending the post: {error}").format(error=str(e)))


    async def delete_message(self, message_id: str) -> None:
        # TODO: Implement deleting message for ATProtoSocial
        logger.debug(
            f"Deleting message for ATProtoSocial session {self.user_id}: {message_id}"
        )
        # await self.util.delete_status(message_id)

    async def get_message_url(self, message_id: str, context: str | None = None) -> str:
        # message_id here is expected to be the rkey of the post
        # TODO: Confirm if self.util.get_own_username() is populated correctly before this call
        own_handle = self.util.get_own_username() or self.db.get("handle", "unknown.bsky.social")
        # Ensure message_id is just the rkey, not the full AT URI.
        # If it's a full URI, extract rkey. This logic might need refinement based on what `message_id` contains.
        if message_id.startswith("at://"):
            message_id = message_id.split("/")[-1]

        return f"https://bsky.app/profile/{own_handle}/post/{message_id}"


    async def approve_message(self, notification_data: NotificationData) -> ApprovalResult:
        # TODO: Implement message approval for ATProtoSocial
        logger.debug(
            f"Approving message for ATProtoSocial session {self.user_id}: {notification_data['id']}"
        )
        # This is a placeholder implementation
        # await self.util.authorize_follow_request(notification_data["account"]["id"])
        return ApprovalResult.APPROVED

    async def reject_message(self, notification_data: NotificationData) -> ApprovalResult:
        # TODO: Implement message rejection for ATProtoSocial
        logger.debug(
            f"Rejecting message for ATProtoSocial session {self.user_id}: {notification_data['id']}"
        )
        # This is a placeholder implementation
        # await self.util.reject_follow_request(notification_data["account"]["id"])
        return ApprovalResult.REJECTED

    async def report_message(self, report_data: ReportData) -> ReportingDecision:
        # TODO: Implement message reporting for ATProtoSocial
        logger.debug(
            f"Reporting message for ATProtoSocial session {self.user_id}: {report_data['message_id']}"
        )
        # This is a placeholder implementation
        # await self.util.report_status(
        #     status_id=report_data["message_id"],
        #     account_id=report_data["message_author_id"],
        #     reason=report_data["reason"],
        # )
        return ReportingDecision.REPORTED

    @classmethod
    def get_configurable_values(cls) -> dict[str, ConfigurableValue]:
        """Returns all configurable values for ATProtoSocial."""
        return {
            "handle": cls.handle,
            "app_password": cls.app_password, # Write-only through auth/settings UI
            "did": cls.did, # Read-only, set after login
        }

    @classmethod
    def get_configurable_values_for_user(cls, user_id: str) -> dict[str, Any]:
        """Returns current configuration for a specific user."""
        user_config = config.sessions.atprotosocial[user_id]
        return {
            "handle": user_config.handle.get(),
            "app_password": "",  # Never return stored password
            "did": user_config.did.get(),
        }

    @classmethod
    def validate_config(cls, cfg: Config) -> None: # cfg is actually ConfigSectionProxy for the user
        """Validates ATProtoSocial configuration for a user."""
        # This is called when settings are saved.
        # `handle` and `app_password` are primary credentials.
        # `did` is derived, so no need to validate its presence here as essential for saving.
        if not cfg.handle.get():
            raise ValueError(_("Bluesky handle is required."))
        if not cfg.app_password.get(): # This might be an issue if password is not re-typed on every save
            # Consider if validation is only for initial setup or if password must always be re-entered on save.
            # For now, assume if a handle exists, a password was once entered.
            # If DID exists, it means login was successful at some point.
            pass # Allowing save without re-entering password if handle exists. Test_connection is key.
        logger.info(f"ATProtoSocial configuration validation for user: {cfg._user_id} passed (basic checks).")


    @classmethod
    async def generate_oauth_url(cls, channel_id: str, user_id: str, redirect_uri: str) -> str | None:
        # ATProtoSocial does not use OAuth2 for user login in the typical 3rd party app sense.
        # App Passwords are used instead. So, this method is not applicable.
        return None

    @classmethod
    async def finish_oauth_authentication(
        cls,
        channel_id: str,
        user_id: str,
        redirect_uri: str,
        code: str | None = None,
        error: str | None = None,
        error_description: str | None = None,
    ) -> None:
        # TODO: Implement OAuth finish authentication for ATProtoSocial if applicable
        pass

    @classmethod
    def get_settings_inputs(
        cls, user_id: str | None = None, current_config: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        # TODO: Define settings inputs for ATProtoSocial
        # This is a placeholder implementation
        # Example:
        # return [
        #     {
        #         "type": "text",
        #         "name": "api_base_url",
        #         "label": _("API Base URL"),
        #         "value": current_config.get("api_base_url", "https://bsky.social"),
        #         "required": True,
        #     },
        #     {
        #         "type": "password",
        #         "name": "access_token", # This should probably be app_password or similar for Bluesky
        #         "label": _("Access Token / App Password"),
        #         "value": current_config.get("access_token", ""),
        #         "required": True,
        #     },
        # ]
        return []

    @classmethod
    def get_user_actions(cls) -> list[dict[str, Any]]:
        """Defines user-specific actions available for ATProtoSocial profiles."""
        # These actions are typically displayed on a user's profile in the UI.
        # 'id' is used to map to the handler in controller/handler.py
        # 'action_type': 'api_call' (calls handle_user_command), 'link' (opens URL)
        # 'payload_params': list of params from user context to include in payload to handle_user_command
        # 'requires_target_user_did': True if the action needs a target user's DID

        # Note: Current Approve UI might not distinguish visibility based on context (e.g., don't show "Follow" if already following).
        # This logic would typically reside in the UI or be supplemented by viewer state from profile data.

        actions = [
            {
                "id": "atp_view_profile_web", # Unique ID
                "label": _("View Profile on Web"),
                "icon": "external-link-alt",
                "action_type": "link", # Opens a URL
                "url_template": "https://bsky.app/profile/{target_user_handle}", # {target_user_handle} will be replaced
                "requires_target_user_did": False, # Needs handle, but can be derived from DID
                "requires_target_user_handle": True,
            },
            {
                "id": "atp_follow_user",
                "label": _("Follow User"),
                "icon": "user-plus",
                "action_type": "api_call",
                "api_command": "follow_user", # Command for handle_user_command
                "requires_target_user_did": True,
                "confirmation_required": False,
            },
            {
                "id": "atp_unfollow_user",
                "label": _("Unfollow User"),
                "icon": "user-minus",
                "action_type": "api_call",
                "api_command": "unfollow_user",
                "requires_target_user_did": True,
                "confirmation_required": True,
                "confirmation_message": _("Are you sure you want to unfollow this user?"),
            },
            {
                "id": "atp_mute_user",
                "label": _("Mute User"),
                "icon": "volume-mute",
                "action_type": "api_call",
                "api_command": "mute_user",
                "requires_target_user_did": True,
            },
            {
                "id": "atp_unmute_user",
                "label": _("Unmute User"),
                "icon": "volume-up",
                "action_type": "api_call",
                "api_command": "unmute_user",
                "requires_target_user_did": True,
            },
            {
                "id": "atp_block_user",
                "label": _("Block User"),
                "icon": "user-slash", # Or "ban"
                "action_type": "api_call",
                "api_command": "block_user",
                "requires_target_user_did": True,
                "confirmation_required": True,
                "confirmation_message": _("Are you sure you want to block this user? They will not be able to interact with you, and you will not see their content."),
            },
            {
                "id": "atp_unblock_user", # This might be handled by UI if block status is known
                "label": _("Unblock User"),
                "icon": "user-check", # Or "undo"
                "action_type": "api_call",
                "api_command": "unblock_user",
                "requires_target_user_did": True,
                 # No confirmation usually for unblock, but can be added
            },
            # Example: Action to fetch user's feed (handled by UI navigation, not typically a button here)
            # {
            #     "id": "atp_view_user_feed",
            #     "label": _("View User's Posts"),
            #     "icon": "list-alt",
            #     "action_type": "ui_navigation", # Special type for UI to handle
            #     "target_view": "user_feed",
            #     "requires_target_user_did": True,
            # },
        ]
        return actions

    @classmethod
    def get_user_list_actions(cls) -> list[dict[str, Any]]:
        # TODO: Define user list actions for ATProtoSocial
        return []

    def get_reporter(self) -> Reporter | None:
        # TODO: Implement if ATProtoSocial has specific reporting capabilities
        # that differ from the base implementation
        return super().get_reporter()

    def is_ready(self) -> bool:
        """Checks if the session is properly configured and authenticated."""
        # A more robust check would be to see if self.client.me is not None or similar SDK check
        # For example: return self.client is not None and self.client.me is not None (after client.get_session() or login)
        # For now, check if essential details are in DB, implying a successful login occurred.
        return bool(self.db.get("access_jwt") and self.db.get("did") and self.db.get("handle"))


    async def _get_user_id_from_username(self, username: str) -> str | None: # username is handle
        # TODO: Implement handle to DID resolution if needed for general use.
        # client = await self.util._get_client() # Ensure client is available
        # if client:
        #     try:
        #         profile = await client.app.bsky.actor.get_profile({'actor': username})
        #         return profile.did
        #     except Exception:
        #         return None
        return None

    async def _get_username_from_user_id(self, user_id: str) -> str | None: # user_id is DID
        # TODO: Implement user ID to username resolution if needed more broadly.
        # For now, profile data usually contains the handle.
        if not self.is_ready() or not self.client:
            return None
        try:
            profile = await self.client.app.bsky.actor.get_profile(models.AppBskyActorGetProfile.Params(actor=user_id))
            return profile.handle if profile else None
        except Exception:
            return None

    # --- Notification Handling ---

    async def _handle_like_notification(self, notification_item: utils.ATNotification) -> None:
        author = notification_item.author
        post_uri = notification_item.uri # URI of the like record itself
        subject_uri = notification_item.reasonSubject # URI of the post that was liked

        title = _("{author_name} liked your post").format(author_name=author.displayName or author.handle)
        body = "" # Could fetch post content for body if desired, but title is often enough for likes

        # Try to get the URL of the liked post
        url = None
        if subject_uri:
            try:
                # Assuming subject_uri is the AT URI of the post.
                # We need its rkey and author handle to build a bsky.app URL.
                # This is complex if we don't have the post details already.
                # For simplicity, make the notification URL point to the liker's profile or the like record.
                # A better UX might involve fetching the post to link to it directly.
                url = await self.get_message_url(message_id=subject_uri, context="notification_like_subject")
            except Exception as e:
                logger.warning(f"Could not generate URL for liked post {subject_uri}: {e}")
                url = f"https://bsky.app/profile/{author.handle}" # Fallback to liker's profile

        await self.send_notification_to_channel(
            kind=NotificationKind.FAVOURITE, # Maps to 'like'
            title=title,
            body=body,
            url=url,
            author_name=author.displayName or author.handle,
            author_id=author.did,
            author_avatar_url=author.avatar,
            timestamp=util.parse_iso_datetime(notification_item.indexedAt),
            message_id=post_uri, # ID of the like notification/record itself
            original_message_id=subject_uri, # ID of the liked post
            # original_message_author_id: self.util.get_own_did(), # The user receiving the like
            # original_message_author_username: self.util.get_own_username(),
        )

    async def _handle_repost_notification(self, notification_item: utils.ATNotification) -> None:
        author = notification_item.author
        repost_uri = notification_item.uri # URI of the repost record
        subject_uri = notification_item.reasonSubject # URI of the original post that was reposted

        title = _("{author_name} reposted your post").format(author_name=author.displayName or author.handle)
        body = "" # Could fetch original post content for body
        url = None
        if subject_uri:
            try:
                url = await self.get_message_url(message_id=subject_uri, context="notification_repost_subject")
            except Exception as e:
                logger.warning(f"Could not generate URL for reposted post {subject_uri}: {e}")
                url = f"https://bsky.app/profile/{author.handle}" # Fallback to reposter's profile


        await self.send_notification_to_channel(
            kind=NotificationKind.REBLOG, # Maps to 'repost'
            title=title,
            body=body,
            url=url,
            author_name=author.displayName or author.handle,
            author_id=author.did,
            author_avatar_url=author.avatar,
            timestamp=util.parse_iso_datetime(notification_item.indexedAt),
            message_id=repost_uri,
            original_message_id=subject_uri,
        )

    async def _handle_follow_notification(self, notification_item: utils.ATNotification) -> None:
        author = notification_item.author
        follow_uri = notification_item.uri # URI of the follow record

        title = _("{author_name} followed you").format(author_name=author.displayName or author.handle)
        url = f"https://bsky.app/profile/{author.handle}" # Link to follower's profile

        await self.send_notification_to_channel(
            kind=NotificationKind.FOLLOW,
            title=title,
            body=None, # No body needed for follow
            url=url,
            author_name=author.displayName or author.handle,
            author_id=author.did,
            author_avatar_url=author.avatar,
            timestamp=util.parse_iso_datetime(notification_item.indexedAt), # type: ignore[attr-defined]
            message_id=follow_uri,
        )

    async def _handle_mention_notification(self, notification_item: utils.ATNotification) -> None:
        author = notification_item.author
        post_record = notification_item.record # This is the app.bsky.feed.post record
        post_uri = notification_item.uri # URI of the post containing the mention

        title = _("New mention from {author_name}").format(author_name=author.displayName or author.handle)
        body = getattr(post_record, 'text', '') if post_record else ''
        url = None
        if post_uri:
            try:
                url = await self.get_message_url(message_id=post_uri, context="notification_mention")
            except Exception as e:
                 logger.warning(f"Could not generate URL for mention post {post_uri}: {e}")
                 url = f"https://bsky.app/profile/{author.handle}"


        await self.send_notification_to_channel( # type: ignore[attr-defined]
            kind=NotificationKind.MENTION, # type: ignore[attr-defined]
            title=title,
            body=body,
            url=url,
            author_name=author.displayName or author.handle,
            author_id=author.did,
            author_avatar_url=author.avatar,
            timestamp=util.parse_iso_datetime(notification_item.indexedAt), # type: ignore[attr-defined]
            message_id=post_uri,
            original_message_id=post_uri, # The mention is in this post
        )

    async def _handle_reply_notification(self, notification_item: utils.ATNotification) -> None:
        author = notification_item.author
        post_record = notification_item.record # The app.bsky.feed.post record (the reply post)
        reply_post_uri = notification_item.uri # URI of the reply post

        # The subject of the reply notification is the user's original post that was replied to.
        # notification_item.reasonSubject might be null if the reply is to a post that was deleted
        # or if the notification structure is different. The reply record itself contains parent/root.
        replied_to_post_uri = getattr(post_record.reply, 'parent', {}).get('uri') if post_record and hasattr(post_record, 'reply') and hasattr(post_record.reply, 'parent') and hasattr(post_record.reply.parent, 'uri') else None


        title = _("{author_name} replied to your post").format(author_name=author.displayName or author.handle)
        body = getattr(post_record, 'text', '') if post_record else ''
        url = None
        if reply_post_uri: # Link to the reply itself
            try:
                url = await self.get_message_url(message_id=reply_post_uri, context="notification_reply")
            except Exception as e:
                 logger.warning(f"Could not generate URL for reply post {reply_post_uri}: {e}")
                 url = f"https://bsky.app/profile/{author.handle}"


        await self.send_notification_to_channel( # type: ignore[attr-defined]
            kind=NotificationKind.REPLY, # type: ignore[attr-defined]
            title=title,
            body=body,
            url=url,
            author_name=author.displayName or author.handle,
            author_id=author.did,
            author_avatar_url=author.avatar,
            timestamp=util.parse_iso_datetime(notification_item.indexedAt), # type: ignore[attr-defined]
            message_id=reply_post_uri,
            original_message_id=replied_to_post_uri, # The post that was replied to
        )

    async def _handle_quote_notification(self, notification_item: utils.ATNotification) -> None:
        author = notification_item.author
        post_record = notification_item.record # The app.bsky.feed.post record (the post that quotes)
        quoting_post_uri = notification_item.uri # URI of the post that contains the quote

        # The subject of the quote notification is the user's original post that was quoted.
        quoted_post_uri = notification_item.reasonSubject

        title = _("{author_name} quoted your post").format(author_name=author.displayName or author.handle)
        body = getattr(post_record, 'text', '') if post_record else '' # Text of the quoting post
        url = None
        if quoting_post_uri: # Link to the quoting post
            try:
                url = await self.get_message_url(message_id=quoting_post_uri, context="notification_quote")
            except Exception as e:
                 logger.warning(f"Could not generate URL for quoting post {quoting_post_uri}: {e}")
                 url = f"https://bsky.app/profile/{author.handle}"


        await self.send_notification_to_channel( # type: ignore[attr-defined]
            kind=NotificationKind.QUOTE, # Assuming a QUOTE kind exists or map to MENTION/custom  # type: ignore[attr-defined]
            title=title,
            body=body,
            url=url,
            author_name=author.displayName or author.handle,
            author_id=author.did,
            author_avatar_url=author.avatar,
            timestamp=util.parse_iso_datetime(notification_item.indexedAt), # type: ignore[attr-defined]
            message_id=quoting_post_uri,
            original_message_id=quoted_post_uri, # The post that was quoted
        )

    def _get_notification_handler_map(self) -> dict[str, Any]: # type: ignore[type-arg]
        """Maps ATProto notification reasons to handler methods."""
        return {
            "like": self._handle_like_notification,
            "repost": self._handle_repost_notification,
            "follow": self._handle_follow_notification,
            "mention": self._handle_mention_notification,
            "reply": self._handle_reply_notification,
            "quote": self._handle_quote_notification,
        }

    async def fetch_notifications(self, cursor: str | None = None, limit: int = 20) -> str | None:
        """
        Fetches notifications from ATProtoSocial and processes them.
        Returns the cursor for the next page, or None if no more notifications.
        """
        if not self.is_ready():
            logger.warning("Cannot fetch notifications: session not ready.")
            return None

        try:
            logger.info(f"Fetching ATProtoSocial notifications with cursor: {cursor}")
            notifications_tuple = await self.util.get_notifications(limit=limit, cursor=cursor)
            if not notifications_tuple:
                logger.info("No notifications returned from util.get_notifications.")
                return None

            raw_notifications, next_cursor = notifications_tuple

            if not raw_notifications:
                logger.info("No new notifications found.")
                # Consider updating last seen timestamp here if all caught up.
                # await self.mark_notifications_as_seen()
                return next_cursor # Return cursor even if no new items, could be end of list

            handler_map = self._get_notification_handler_map()
            processed_count = 0
            for item in raw_notifications:
                # item is models.AppBskyNotificationListNotifications.Notification
                if not item.isRead: # Process only unread notifications for UI to avoid duplicates if polling
                                    # However, for initial sync, we might want to process some read ones too.
                                    # For now, let's assume we process and then it's up to UI to display "unread" state.
                                    # The `mark_notifications_as_seen` would be key.
                    handler = handler_map.get(item.reason)
                    if handler:
                        try:
                            await handler(item)
                            processed_count +=1
                        except Exception as e:
                            logger.error(f"Error handling notification type {item.reason} (URI: {item.uri}): {e}", exc_info=True)
                    else:
                        logger.warning(f"No handler for ATProtoSocial notification reason: {item.reason}")

            logger.info(f"Processed {processed_count} ATProtoSocial notifications.")

            # TODO: Implement marking notifications as seen.
            # This should probably be done after a short delay or user action.
            # If all fetched notifications were processed, and it was a full page,
            # we might consider calling client.app.bsky.notification.update_seen()
            # await self.mark_notifications_as_seen() # Be careful not to do this too aggressively
        # If not item.isRead: # Only mark seen if we actually processed unread items.
        #    if processed_count > 0 and (len(raw_notifications) < limit or not next_cursor) : # If we are at the "end" of unread.
        #       await self.mark_notifications_as_seen()


            return next_cursor
        except NotificationError as e: # Errors from util.get_notifications
            logger.error(f"Failed to fetch notifications: {e.message}")
            self.send_text_notification(title=_("Notification Error"), message=str(e))
            return cursor # Return original cursor on error to retry later
        except Exception as e:
            logger.error(f"Unexpected error fetching notifications: {e}", exc_info=True)
            self.send_text_notification(title=_("Notification Error"), message=_("An unexpected error occurred while fetching notifications."))
            return cursor


    async def mark_notifications_as_seen(self, seen_at: str | None = None) -> None:
        """Marks notifications as seen up to a certain timestamp."""
        if not self.is_ready() or not self.client:
            logger.warning("Cannot mark notifications as seen: client not ready.")
            return

        try:
            # seen_at should be an ISO 8601 timestamp. If None, defaults to now.
            # from atproto_client.models import get_or_create, ids, string_to_datetime # SDK specific import
            # if not seen_at:
            #    seen_at = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            # await self.client.app.bsky.notification.update_seen({'seenAt': seen_at})
            # For now, using a placeholder as direct update_seen might need specific datetime string.
            # The SDK client might have a helper for current time in correct format.
            await self.client.app.bsky.notification.update_seen() # SDK might default seenAt to now
            logger.info("Marked ATProtoSocial notifications as seen.")
        except Exception as e:
            logger.error(f"Error marking notifications as seen: {e}", exc_info=True)


    async def handle_streaming_event(self, event_type: str, data: Any) -> None: # data type is ATNotification or similar
        """
        Handles incoming notification events from a streaming connection.
        `event_type` would be something like 'mention', 'like', etc.
        `data` should be the ATProtoSocial notification model object.
        """
        logger.debug(f"ATProtoSocial: Received streaming event: {event_type} with data: {data}")
        handler = self._get_notification_handler_map().get(event_type)
        if handler:
            try:
                # Assuming 'data' is already in the format of models.AppBskyNotificationListNotifications.Notification
                # If not, it needs to be transformed here.
                await handler(data)
            except Exception as e:
                logger.error(f"Error handling streamed notification type {event_type}: {e}", exc_info=True)
        else:
            logger.warning(f"No handler for ATProtoSocial streamed event type: {event_type}")


    def get_sensitive_reason_options(self) -> dict[str, str] | None:
        # TODO: If ATProtoSocial supports reasons for marking content sensitive, define them here
        return None

    # --- Timeline Fetching and Processing ---

    async def fetch_home_timeline(self, cursor: str | None = None, limit: int = 20, new_only: bool = False) -> tuple[list[str], str | None]:
        """Fetches the home timeline (following) and processes it."""
        if not self.is_ready():
            logger.warning("Cannot fetch home timeline: session not ready.")
            raise NotificationError(_("Session is not active. Please log in or check your connection."))

        logger.info(f"Fetching home timeline with cursor: {cursor}, limit: {limit}, new_only: {new_only}")
        try:
            timeline_data = await self.util.get_timeline(algorithm=None, limit=limit, cursor=cursor)
            if not timeline_data:
                logger.info("No home timeline data returned from util.")
                return [], cursor # Return current cursor if no data

            feed_view_posts, next_cursor = timeline_data
            processed_ids = await self.order_buffer(
                items=feed_view_posts,
                new_only=new_only,
                buffer_name="home_timeline_buffer"
            )

            if new_only and next_cursor: # For fetching newest, cursor logic might differ or not be used this way
                self.home_timeline_cursor = next_cursor # Bluesky cursors are typically for older items
            elif not new_only : # Fetching older items
                 self.home_timeline_cursor = next_cursor

            logger.info(f"Fetched {len(processed_ids)} items for home timeline. Next cursor: {self.home_timeline_cursor}")
            return processed_ids, self.home_timeline_cursor
        except NotificationError: # Re-raise critical errors
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching home timeline: {e}", exc_info=True)
            raise NotificationError(_("An error occurred while fetching your home timeline."))


    async def fetch_user_timeline(self, user_did: str, cursor: str | None = None, limit: int = 20, new_only: bool = False, filter_type: str = "posts_with_replies") -> tuple[list[str], str | None]:
        """Fetches a specific user's timeline and processes it."""
        if not self.is_ready():
            logger.warning(f"Cannot fetch user timeline for {user_did}: session not ready.")
            raise NotificationError(_("Session is not active. Please log in or check your connection."))

        logger.info(f"Fetching user timeline for {user_did} with cursor: {cursor}, filter: {filter_type}")
        try:
            feed_data = await self.util.get_author_feed(actor_did=user_did, limit=limit, cursor=cursor, filter=filter_type)
            if not feed_data:
                logger.info(f"No feed data returned for user {user_did}.")
                return [], cursor

            feed_view_posts, next_cursor = feed_data
            # For user timelines, we might not store them in a persistent session buffer like home_timeline_buffer,
            # but rather just process them into message_cache for direct display or a temporary view buffer.
            # For now, let's use a generic buffer name or imply it's for message_cache population.
            processed_ids = await self.order_buffer(
                items=feed_view_posts,
                new_only=new_only, # This might be always False or True depending on how user timeline view works
                buffer_name=f"user_timeline_{user_did}" # Example of a dynamic buffer name, though not stored on session directly
            )
            logger.info(f"Fetched {len(processed_ids)} items for user {user_did} timeline. Next cursor: {next_cursor}")
            return processed_ids, next_cursor
        except NotificationError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching user timeline for {user_did}: {e}", exc_info=True)
            raise NotificationError(_("An error occurred while fetching the user's timeline."))


    async def order_buffer(self, items: list[utils.models.AppBskyFeedDefs.FeedViewPost], new_only: bool = True, buffer_name: str = "home_timeline_buffer", **kwargs) -> list[str]: # type: ignore
        """Processes and orders items (FeedViewPost) into the specified buffer and message_cache."""
        if not isinstance(items, list):
            logger.warning(f"order_buffer received non-list items: {type(items)}. Skipping.")
            return []

        added_ids: list[str] = []
        target_buffer_list: list[str] | None = getattr(self, buffer_name, None)

        # If buffer_name is dynamic (e.g. user timelines), target_buffer_list might be None.
        # In such cases, items are added to message_cache, and added_ids are returned for direct use.
        # If it's a well-known buffer like home_timeline_buffer, it's updated.

        for item in items:
            if not isinstance(item, utils.models.AppBskyFeedDefs.FeedViewPost):
                logger.warning(f"Skipping non-FeedViewPost item in order_buffer: {item}")
                continue

            post_view = item.post
            if not post_view or not post_view.uri:
                logger.warning(f"FeedViewPost item missing post view or URI: {item}")
                continue

            post_uri = post_view.uri

            # Cache the main post
            # self.util._format_post_data can convert PostView to a dict if needed by message_cache
            # For now, assume message_cache can store the PostView model directly or its dict representation
            formatted_post_data = self.util._format_post_data(post_view) # Ensure this returns a dict
            self.message_cache[post_uri] = formatted_post_data

            # Handle replies - cache parent/root if present and not already cached
            if item.reply:
                if item.reply.parent and item.reply.parent.uri not in self.message_cache:
                    self.message_cache[item.reply.parent.uri] = self.util._format_post_data(item.reply.parent) # type: ignore
                if item.reply.root and item.reply.root.uri not in self.message_cache:
                     self.message_cache[item.reply.root.uri] = self.util._format_post_data(item.reply.root) # type: ignore


            # Handle reposts - the item.post is the original post.
            # The item.reason (if ReasonRepost) indicates it's a repost.
            # The UI needs to use this context when rendering item.post.uri from the timeline.
            # For simplicity, the buffer stores the URI of the original post.
            # If a more complex object is needed in the buffer, this is where to construct it.
            # For example: {"type": "repost", "reposter": item.reason.by.handle, "post_uri": post_uri, "repost_time": item.reason.indexedAt}

            if target_buffer_list is not None:
                if post_uri not in target_buffer_list: # Avoid duplicates in the list itself
                    if new_only: # Add to the start (newer items)
                        target_buffer_list.insert(0, post_uri)
                    else: # Add to the end (older items)
                        target_buffer_list.append(post_uri)
            added_ids.append(post_uri)

        if target_buffer_list is not None: # Trim if necessary (e.g. keep last N items)
            max_buffer_size = constants.MAX_BUFFER_SIZE # From fromapprove import constants
            if len(target_buffer_list) > max_buffer_size:
                if new_only: # Trim from the end (oldest)
                    setattr(self, buffer_name, target_buffer_list[:max_buffer_size])
                else: # Trim from the start (newest - less common for this kind of buffer)
                    setattr(self, buffer_name, target_buffer_list[-max_buffer_size:])

        self.cleanup_message_cache(buffers_to_check=[buffer_name] if target_buffer_list is not None else [])
        return added_ids


    async def check_buffers(self, post_data: utils.ATPost | dict[str, Any]) -> None: # type: ignore
        """
        Adds a newly created post (by the current user) to relevant buffers,
        primarily self.posts_buffer and self.message_cache.
        `post_data` is the PostView model or its dict representation of the new post.
        """
        if not post_data:
            return

        post_uri = None
        formatted_data = {}

        if isinstance(post_data, utils.models.AppBskyFeedDefs.PostView):
            post_uri = post_data.uri
            formatted_data = self.util._format_post_data(post_data)
        elif isinstance(post_data, dict) and "uri" in post_data: # Assuming it's already formatted
            post_uri = post_data["uri"]
            formatted_data = post_data
        else:
            logger.warning(f"check_buffers received unexpected post_data type: {type(post_data)}")
            return

        if not post_uri or not formatted_data:
            logger.error("Could not process post_data in check_buffers: URI or data missing.")
            return

        # Add to message_cache
        self.message_cache[post_uri] = formatted_data

        # Add to user's own posts buffer (self.posts_buffer is from baseSession)
        if post_uri not in self.posts_buffer:
            self.posts_buffer.insert(0, post_uri) # Add to the beginning (newest)
            if len(self.posts_buffer) > constants.MAX_BUFFER_SIZE:
                self.posts_buffer = self.posts_buffer[:constants.MAX_BUFFER_SIZE]

        # A user's own new post might appear on their home timeline if they follow themselves
        # or if the timeline algorithm includes own posts.
        # For now, explicitly adding to home_timeline_buffer if not present.
        # Some UIs might prefer not to duplicate, relying on separate "My Posts" view.
        # if post_uri not in self.home_timeline_buffer:
        #    self.home_timeline_buffer.insert(0, post_uri)
        #    if len(self.home_timeline_buffer) > constants.MAX_BUFFER_SIZE:
        #        self.home_timeline_buffer = self.home_timeline_buffer[:constants.MAX_BUFFER_SIZE]

        self.cleanup_message_cache(buffers_to_check=["posts_buffer", "home_timeline_buffer"])
        logger.debug(f"Added new post {post_uri} to relevant buffers.")

    # --- User List Fetching Wrapper ---
    async def get_paginated_user_list(
        self,
        list_type: str, # "followers", "following", "search_users" (though search might be handled differently)
        identifier: str, # User DID for followers/following, or search term
        limit: int,
        cursor: str | None
    ) -> tuple[list[dict[str,Any]], str | None]: # Returns (list_of_formatted_user_dicts, next_cursor)
        """
        Wrapper to call the user list fetching functions from controller.userList.
        This helps keep panel logic cleaner by calling a session method.
        """
        from controller.atprotosocial import userList as atpUserListCtrl # Local import

        # Ensure the util methods used by get_user_list_paginated are available and client is ready
        if not self.is_ready() or not self.util:
            logger.warning(f"Session not ready for get_paginated_user_list (type: {list_type})")
            return [], None

        try:
            # get_user_list_paginated is expected to return formatted dicts and a cursor
            users_list, next_cursor = await atpUserListCtrl.get_user_list_paginated(
                session=self, # Pass self (the session instance)
                list_type=list_type,
                identifier=identifier,
                limit=limit,
                cursor=cursor
            )
            return users_list, next_cursor
        except Exception as e:
            logger.error(f"Error in session.get_paginated_user_list for {list_type} of {identifier}: {e}", exc_info=True)
            raise NotificationError(_("Failed to load user list: {error}").format(error=str(e)))


    def get_reporting_reasons(self) -> ReportingReasons | None:
        # TODO: Define specific reporting reasons for ATProtoSocial if they differ from generic ones
        # This could involve fetching categories from ATProtoSocial's API or defining a static list.
        # Example:
        # return ReportingReasons(
        #     categories={
        #         "spam": _("Spam"),
        #         "illegal": _("Illegal Content"),
        #         "harassment": _("Harassment"),
        #         # ... other ATProtoSocial specific categories
        #     },
        #     default_text_reason_required=True,
        # )
        return None

    @classmethod
    def get_config_description(cls) -> str | None:
        # TODO: Provide a description for the ATProtoSocial configuration section
        return _(
            "Configure your ATProtoSocial (Bluesky) account. You'll need your user handle (e.g., @username.bsky.social) and an App Password."
        )

    @classmethod
    def is_suitable_for_channel(cls, channel: Channel) -> bool:
        # TODO: Determine if this session type is suitable for the given channel.
        # For now, assuming it's suitable for any channel.
        return True

    @classmethod
    def get_dependencies(cls) -> list[str]:
        # TODO: List any Python package dependencies required for this session type.
        # Example: return ["atproto"]
        return ["atproto"]

    @classmethod
    def get_logo_path(cls) -> str | None:
        # TODO: Provide path to a logo for ATProtoSocial, e.g., "static/img/atprotosocial_logo.svg"
        return "static/img/bluesky_logo.svg" # Assuming a logo file will be added here

    @classmethod
    def get_auth_type(cls) -> str:
        # TODO: Specify the authentication type. "password" for user/pass (or handle/app_password), "oauth" for OAuth2
        return "password" # Bluesky typically uses handle and app password

    @classmethod
    def get_auth_inputs(cls, user_id: str | None = None, current_config: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Defines inputs required for ATProtoSocial authentication (handle and app password)."""
        cfg = current_config or {}
        return [
            {
                "type": "text",
                "name": "handle",
                "label": _("Bluesky Handle (e.g., @username.bsky.social or username.bsky.social)"),
                "value": cfg.get("handle", ""),
                "required": True,
            },
            {
                "type": "password",
                "name": "app_password",
                "label": _("App Password (generate one in Bluesky settings)"),
                "value": "",  # Never pre-fill password
                "required": True,
            },
        ]


    @classmethod
    async def test_connection(cls, settings: dict[str, Any]) -> tuple[bool, str]:
        """Tests connection to ATProtoSocial using provided handle and app password."""
        handle = settings.get("handle")
        app_password = settings.get("app_password")

        if not handle or not app_password:
            return False, _("Handle and App Password are required.")

        try:
            # Use a temporary client for testing to not interfere with any existing session client
            temp_client = AsyncClient()
            logger.info(f"ATProtoSocial: Testing connection for handle {handle}...")
            profile = await temp_client.login(handle, app_password)
            if profile and profile.did:
                logger.info(f"ATProtoSocial: Connection test successful for {handle}. DID: {profile.did}")
                return True, _("Successfully connected and authenticated with Bluesky.")
            else:
                logger.warning(f"ATProtoSocial: Connection test for {handle} returned no profile data.")
                return False, _("Authentication succeeded but no profile data was returned.")
        except XrpcError as e:
            logger.error(f"ATProtoSocial: Connection test failed for handle {handle} (XrpcError): {e.error} - {e.message}")
            error_msg = f"{e.error or 'Error'}: {e.message or 'Failed to connect'}"
            return False, _("Connection failed: {error_details}").format(error_details=error_msg)
        except Exception as e:
            logger.error(f"ATProtoSocial: Connection test failed for handle {handle} (Exception): {e}", exc_info=True)
            return False, _("An unexpected error occurred: {error}").format(error=str(e))


    async def send_notification(
        self,
        kind: NotificationKind,
        title: str,
        body: str | None = None,
        url: str | None = None,
        buttons: list[dict[str, str]] | None = None,
        image_url: str | None = None,
        message_id: str | None = None,
        original_message_id: str | None = None,
        original_message_author_id: str | None = None,
        original_message_author_username: str | None = None,
        original_message_url: str | None = None,
        timestamp: float | None = None,
        **kwargs: Any,
    ) -> None:
        """Sends a notification through the configured channel."""
        # This method is usually handled by the baseSession, but can be overridden
        # if ATProtoSocial has a special way of handling notifications or needs more context.
        # For now, let the base class handle it.
        await super().send_notification(
            kind=kind,
            title=title,
            body=body,
            url=url,
            buttons=buttons,
            image_url=image_url,
            message_id=message_id,
            original_message_id=original_message_id,
            original_message_author_id=original_message_author_id,
            original_message_author_username=original_message_author_username,
            original_message_url=original_message_url,
            timestamp=timestamp,
            **kwargs,
        )
