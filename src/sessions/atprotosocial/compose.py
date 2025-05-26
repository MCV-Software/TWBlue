from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

fromapprove.translation import translate as _

if TYPE_CHECKING:
    fromapprove.sessions.atprotosocial.session import Session as ATProtoSocialSession

logger = logging.getLogger(__name__)


class ATProtoSocialCompose:
    # Maximum number of characters allowed in a post on ATProtoSocial (Bluesky uses graphemes, not codepoints)
    # Bluesky's limit is 300 graphemes. This might need adjustment based on how Python handles graphemes.
    MAX_CHARS = 300 # Defined by app.bsky.feed.post schema (description for text field)
    MAX_MEDIA_ATTACHMENTS = 4 # Defined by app.bsky.embed.images schema (maxItems for images array)
    MAX_LANGUAGES = 3 # Defined by app.bsky.feed.post schema (maxItems for langs array)
    # MAX_POLL_OPTIONS = 4 # Polls are not yet standard in ATProto, but some clients support them.
    # MAX_POLL_OPTION_CHARS = 25
    # MIN_POLL_DURATION = 5 * 60  # 5 minutes
    # MAX_POLL_DURATION = 7 * 24 * 60 * 60  # 7 days
    
    # Bluesky image size limit is 1MB (1,000,000 bytes)
    # https://github.com/bluesky-social/social-app/blob/main/src/lib/constants.ts#L28
    MAX_IMAGE_SIZE_BYTES = 1_000_000 


    def __init__(self, session: ATProtoSocialSession) -> None:
        self.session = session
        self.supported_media_types: list[str] = ["image/jpeg", "image/png"]
        self.max_image_size_bytes: int = self.MAX_IMAGE_SIZE_BYTES


    def get_panel_configuration(self) -> dict[str, Any]:
        """Returns configuration for the compose panel specific to ATProtoSocial."""
        return {
            "max_chars": self.MAX_CHARS,
            "max_media_attachments": self.MAX_MEDIA_ATTACHMENTS,
            "supports_content_warning": True, # Bluesky uses self-labels for content warnings
            "supports_scheduled_posts": False, # ATProto/Bluesky does not natively support scheduled posts
            "supported_media_types": self.supported_media_types,
            "max_media_size_bytes": self.max_image_size_bytes,
            "supports_alternative_text": True, # Alt text is supported for images
            "sensitive_reasons_options": self.session.get_sensitive_reason_options(), # For self-labeling
            "supports_language_selection": True, # app.bsky.feed.post supports 'langs' field
            "max_languages": self.MAX_LANGUAGES,
            "supports_quoting": True, # Bluesky supports quoting via app.bsky.embed.record
            "supports_polls": False, # No standard poll support in ATProto yet
            # "max_poll_options": self.MAX_POLL_OPTIONS,
            # "max_poll_option_chars": self.MAX_POLL_OPTION_CHARS,
            # "min_poll_duration": self.MIN_POLL_DURATION,
            # "max_poll_duration": self.MAX_POLL_DURATION,
        }

    async def get_quote_text(self, message_id: str, url: str) -> str | None:
        """
        Generates text to be added to the compose box when quoting an ATProtoSocial post.
        For Bluesky, the actual quote is an embed. This text is typically appended by the user.
        `message_id` here is the AT-URI of the post to be quoted.
        `url` is the web URL of the post.
        """
        # The actual embedding of a quote is handled in session.send_message by passing quote_uri.
        # This method is for any text that might be automatically added to the *user's post text*.
        # Often, users just add the link manually, or clients might add "QT: [link]".
        # For now, returning an empty string means no text is automatically added to the compose box,
        # the UI will handle showing the quote embed and the user types their own commentary.
        # Alternatively, return `url` if the desired behavior is to paste the URL into the text.
        
        # Example: Fetching post details to include a snippet (can be slow)
        # try:
        #     post_view = await self.session.util.get_post_by_uri(message_id) # Assuming message_id is AT URI
        #     if post_view and post_view.author and post_view.record:
        #         author_handle = post_view.author.handle
        #         text_snippet = str(post_view.record.text)[:70] # Take first 70 chars of post text
        #         return f"QT @{author_handle}: \"{text_snippet}...\"\n{url}\n"
        # except Exception as e:
        #     logger.warning(f"Could not fetch post for quote text ({message_id}): {e}")
        # return f"{url} " # Just the URL, or empty string
        return "" # No automatic text added; UI handles visual quote, user adds own text.


    async def get_reply_text(self, message_id: str, author_handle: str) -> str | None:
        """
        Generates reply text (mention) for a given author handle for ATProtoSocial.
        """
        # TODO: Confirm if any specific prefix is needed beyond the mention.
        # Bluesky handles mentions with "@handle.example.com"
        if not author_handle.startswith("@"):
            return f"@{author_handle} "
        return f"{author_handle} "


    # Any other ATProtoSocial specific compose methods would go here.
    # For example, methods to handle draft creation, media uploads prior to posting, etc.
    # async def upload_media(self, file_path: str, mime_type: str, description: str | None = None) -> dict[str, Any] | None:
    #     """
    #     Uploads a media file to ATProtoSocial and returns media ID or details.
    #     This would use the atproto client's blob upload.
    #     """
    #     # try:
    #     #     # client = self.session.util.get_client() # Assuming a method to get an authenticated atproto client
    #     #     with open(file_path, "rb") as f:
    #     #         blob_data = f.read()
    #     #     # response = await client.com.atproto.repo.upload_blob(blob_data, mime_type=mime_type)
    #     #     # return {"id": response.blob.ref, "url": response.blob.cid, "description": description} # Example structure
    #     #     logger.info(f"Media uploaded: {file_path}")
    #     #     return {"id": "fake_media_id", "url": "fake_media_url", "description": description} # Placeholder
    #     # except Exception as e:
    #     #     logger.error(f"Failed to upload media to ATProtoSocial: {e}")
    #     #     return None
    #     pass

    def get_text_formatting_rules(self) -> dict[str, Any]:
        """
        Returns text formatting rules for ATProtoSocial.
        Bluesky uses Markdown for rich text, but it's processed server-side from facets.
        Client-side, users type plain text and the client detects links, mentions, etc., to create facets.
        """
        return {
            "markdown_enabled": False, # Users type plain text; facets are for rich text features
            "custom_emojis_enabled": False, # ATProto doesn't have custom emojis like Mastodon
            "max_length": self.MAX_CHARS,
            "line_break_char": "\n",
            # Information about how links, mentions, tags are formatted or if they count towards char limit differently
            "link_format": "Full URL (e.g., https://example.com)", # Links are typically full URLs
            "mention_format": "@handle.bsky.social",
            "tag_format": "#tag (becomes a facet link)", # Hashtags are detected and become links
        }

    def is_media_type_supported(self, mime_type: str) -> bool:
        """Checks if a given MIME type is supported for upload."""
        # TODO: Use actual supported types from `self.supported_media_types`
        return mime_type.lower() in self.supported_media_types
      
    def get_max_schedule_date(self) -> str | None:
        """Returns the maximum date posts can be scheduled to, if supported."""
        # ATProtoSocial does not natively support scheduled posts.
        return None

    def get_poll_configuration(self) -> dict[str, Any] | None:
        """Returns configuration for polls, if supported."""
        # Polls are not a standard part of ATProto yet.
        # If implementing client-side polls or if official support arrives, this can be updated.
        # return {
        #     "max_options": self.MAX_POLL_OPTIONS,
        #     "max_option_chars": self.MAX_POLL_OPTION_CHARS,
        #     "min_duration_seconds": self.MIN_POLL_DURATION,
        #     "max_duration_seconds": self.MAX_POLL_DURATION,
        #     "default_duration_seconds": 24 * 60 * 60,  # 1 day
        # }
        return None
