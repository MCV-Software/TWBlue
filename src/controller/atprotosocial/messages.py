from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

# fromapprove.controller.mastodon import messages as mastodon_messages # Example, if adapting
fromapprove.translation import translate as _

if TYPE_CHECKING:
    fromapprove.sessions.atprotosocial.session import Session as ATProtoSocialSession # Adjusted import

logger = logging.getLogger(__name__)

# This file would typically contain functions to generate complex message bodies or
# interactive components for ATProtoSocial, similar to how it might be done for Mastodon.
# Since ATProtoSocial's interactive features (beyond basic posts) are still evolving
# or client-dependent (like polls), this might be less complex initially.

# Example: If ATProtoSocial develops a standard for "cards" or interactive messages,
# functions to create those would go here. For now, we can imagine placeholders.

def format_welcome_message(session: ATProtoSocialSession) -> dict[str, Any]:
    """
    Generates a welcome message for a new ATProtoSocial session.
    This is just a placeholder and example.
    """
    # user_profile = session.util.get_own_profile_info() # Assuming this method exists and is async or cached
    # handle = user_profile.get("handle", _("your ATProtoSocial account")) if user_profile else _("your ATProtoSocial account")
    handle = session.util.get_own_username() or _("your ATProtoSocial account")


    return {
        "text": _("Welcome to Approve for ATProtoSocial! Your account {handle} is connected.").format(handle=handle),
        # "blocks": [ # If ATProtoSocial supports a block kit like Slack or Discord
        #     {
        #         "type": "section",
        #         "text": {
        #             "type": "mrkdwn", # Or ATProtoSocial's equivalent
        #             "text": _("Welcome to Approve for ATProtoSocial! Your account *{handle}* is connected.").format(handle=handle)
        #         }
        #     },
        #     {
        #         "type": "actions",
        #         "elements": [
        #             {
        #                 "type": "button",
        #                 "text": {"type": "plain_text", "text": _("Post your first Skeet")},
        #                 "action_id": "atprotosocial_compose_new_post" # Example action ID
        #             }
        #         ]
        #     }
        # ]
    }

def format_error_message(error_description: str, details: str | None = None) -> dict[str, Any]:
    """
    Generates a standardized error message.
    """
    message = {"text": f":warning: Error: {error_description}"} # Basic text message
    # if details:
    #     message["blocks"] = [
    #         {
    #             "type": "section",
    #             "text": {"type": "mrkdwn", "text": f":warning: *Error:* {error_description}\n{details}"}
    #         }
    #     ]
    return message

# More functions could be added here as ATProtoSocial's capabilities become clearer
# or as specific formatting needs for Approve arise. For example:
# - Formatting a post for display with all its embeds and cards.
# - Generating help messages specific to ATProtoSocial features.
# - Creating interactive messages for polls (if supported via some convention).

# Example of adapting a function that might exist in mastodon_messages:
# def build_post_summary_message(session: ATProtoSocialSession, post_uri: str, post_content: dict) -> dict[str, Any]:
#     """
#     Builds a summary message for an ATProtoSocial post.
#     """
#     author_handle = post_content.get("author", {}).get("handle", "Unknown user")
#     text_preview = post_content.get("text", "")[:100] # First 100 chars of text
#     # url = session.get_message_url(post_uri) # Assuming this method exists
#     url = f"https://bsky.app/profile/{author_handle}/post/{post_uri.split('/')[-1]}" # Construct a URL

#     return {
#         "text": _("Post by {author_handle}: {text_preview}... ({url})").format(
#             author_handle=author_handle, text_preview=text_preview, url=url
#         ),
#         # Potentially with "blocks" for richer formatting if the platform supports it
#     }

logger.info("ATProtoSocial messages module loaded (placeholders).")
