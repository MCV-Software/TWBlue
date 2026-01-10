from __future__ import annotations

import logging
from typing import Any

# Translation function is provided globally by TWBlue's language handler (_)

logger = logging.getLogger(__name__)

# This file would typically contain functions to generate complex message bodies or
# interactive components for Blueski, similar to how it might be done for Mastodon.
# Since Blueski's interactive features (beyond basic posts) are still evolving
# or client-dependent (like polls), this might be less complex initially.

# Example: If Blueski develops a standard for "cards" or interactive messages,
# functions to create those would go here. For now, we can imagine placeholders.

def format_welcome_message(session: Any) -> dict[str, Any]:
    """
    Generates a welcome message for a new Blueski session.
    This is just a placeholder and example.
    """
    # user_profile = session.util.get_own_profile_info() # Assuming this method exists and is async or cached
    # handle = user_profile.get("handle", _("your Blueski account")) if user_profile else _("your Blueski account")
    # Expect session to expose username via db/settings
    handle = (getattr(session, "db", {}).get("user_name")
              or getattr(getattr(session, "settings", {}), "get", lambda *_: {})("blueski").get("handle")
              or _("your Bluesky account"))


    return {
        "text": _("Welcome to Approve for Blueski! Your account {handle} is connected.").format(handle=handle),
        # "blocks": [ # If Blueski supports a block kit like Slack or Discord
        #     {
        #         "type": "section",
        #         "text": {
        #             "type": "mrkdwn", # Or Blueski's equivalent
        #             "text": _("Welcome to Approve for Blueski! Your account *{handle}* is connected.").format(handle=handle)
        #         }
        #     },
        #     {
        #         "type": "actions",
        #         "elements": [
        #             {
        #                 "type": "button",
        #                 "text": {"type": "plain_text", "text": _("Post your first Skeet")},
        #                 "action_id": "blueski_compose_new_post" # Example action ID
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

# More functions could be added here as Blueski's capabilities become clearer
# or as specific formatting needs for Approve arise. For example:
# - Formatting a post for display with all its embeds and cards.
# - Generating help messages specific to Blueski features.
# - Creating interactive messages for polls (if supported via some convention).

# Example of adapting a function that might exist in mastodon_messages:
# def build_post_summary_message(session: BlueskiSession, post_uri: str, post_content: dict) -> dict[str, Any]:
#     """
#     Builds a summary message for an Blueski post.
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

logger.info("Blueski messages module loaded (placeholders).")
