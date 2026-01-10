from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

fromapprove.translation import translate as _

if TYPE_CHECKING:
    fromapprove.sessions.blueski.session import Session as BlueskiSession

logger = logging.getLogger(__name__)


class BlueskiTemplates:
    def __init__(self, session: BlueskiSession) -> None:
        self.session = session

    def get_template_data(self, template_name: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Returns data required for rendering a specific template for Blueski.
        This method would populate template variables based on the template name and context.
        """
        base_data = {
            "session_kind": self.session.kind,
            "session_label": self.session.label,
            "user_id": self.session.user_id,
            # Add any other common data needed by Blueski templates
        }
        if context:
            base_data.update(context)

        # TODO: Implement specific data fetching for different Blueski templates
        # Example:
        # if template_name == "profile_summary.html":
        #     # profile_info = await self.session.util.get_my_profile_info() # Assuming such a method exists
        #     # base_data["profile"] = profile_info
        #     base_data["profile"] = {"display_name": "User", "handle": "user.bsky.social"} # Placeholder
        # elif template_name == "post_details.html":
        #     # post_id = context.get("post_id")
        #     # post_details = await self.session.util.get_post_by_id(post_id)
        #     # base_data["post"] = post_details
        #     base_data["post"] = {"text": "A sample post", "author_handle": "author.bsky.social"} # Placeholder

        return base_data

    def get_message_card_template(self) -> str:
        """Returns the path to the message card template for Blueski."""
        # This template would define how a single Blueski post (or other message type)
        # is rendered in a list (e.g., in a timeline or search results).
        # return "sessions/blueski/cards/message.html" # Example path
        return "sessions/generic/cards/message_generic.html" # Placeholder, use generic if no specific yet

    def get_notification_template_map(self) -> dict[str, str]:
        """
        Returns a map of Blueski notification types to their respective template paths.
        """
        # TODO: Define templates for different Blueski notification types
        # (e.g., mention, reply, new follower, like, repost).
        # The keys should match the notification types used internally by Approve
        # when processing Blueski events.
        # Example:
        # return {
        #     "mention": "sessions/blueski/notifications/mention.html",
        #     "reply": "sessions/blueski/notifications/reply.html",
        #     "follow": "sessions/blueski/notifications/follow.html",
        #     "like": "sessions/blueski/notifications/like.html", # Bluesky uses 'like'
        #     "repost": "sessions/blueski/notifications/repost.html", # Bluesky uses 'repost'
        #     # ... other notification types
        # }
        # Using generic templates as placeholders:
        return {
            "mention": "sessions/generic/notifications/mention.html",
            "reply": "sessions/generic/notifications/reply.html",
            "follow": "sessions/generic/notifications/follow.html",
            "like": "sessions/generic/notifications/favourite.html", # Map to favourite if generic expects that
            "repost": "sessions/generic/notifications/reblog.html", # Map to reblog if generic expects that
        }

    def get_settings_template(self) -> str | None:
        """Returns the path to the settings template for Blueski, if any."""
        # This template would be used to render Blueski-specific settings in the UI.
        # return "sessions/blueski/settings.html"
        return "sessions/generic/settings_auth_password.html" # If using simple handle/password auth

    def get_user_action_templates(self) -> dict[str, str] | None:
        """
        Returns a map of user action identifiers to their template paths for Blueski.
        User actions are typically buttons or forms displayed on a user's profile.
        """
        # TODO: Define templates for Blueski user actions
        # Example:
        # return {
        #     "view_profile_on_bsky": "sessions/blueski/actions/view_profile_button.html",
        #     "send_direct_message": "sessions/blueski/actions/send_dm_form.html", # If DMs are supported
        # }
        return None # Placeholder

    def get_user_list_action_templates(self) -> dict[str, str] | None:
        """
        Returns a map of user list action identifiers to their template paths for Blueski.
        These actions might appear on lists of users (e.g., followers, following).
        """
        # TODO: Define templates for Blueski user list actions
        # Example:
        # return {
        #     "follow_all_visible": "sessions/blueski/list_actions/follow_all_button.html",
        # }
        return None # Placeholder

    # Add any other template-related helper methods specific to Blueski.
    # For example, methods to get templates for specific types of content (images, polls)
    # if they need special rendering.

    def get_template_for_message_type(self, message_type: str) -> str | None:
        """
        Returns a specific template path for a given message type (e.g., post, reply, quote).
        This can be useful if different types of messages need distinct rendering beyond the standard card.
        """
        # TODO: Define specific templates if Blueski messages have varied structures
        # that require different display logic.
        # if message_type == "quote_post":
        #    return "sessions/blueski/cards/quote_post.html"
        return None # Default to standard message card if not specified
