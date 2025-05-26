from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from atproto import AsyncClient # Removed Client as AsyncClient is used
from atproto.exceptions import AtProtocolError, NetworkError, RequestException # Specific exceptions
from atproto.xrpc_client import models
from atproto.lexicon import models as lexicon_models # For lexicon definitions like com.atproto.moderation.defs
from atproto.xrpc_client.models import ids # For collection IDs like ids.AppBskyFeedPost


fromapprove.util import GenerateID, get_http_client, httpx_max_retries_hook
fromapprove.translation import translate as _
fromapprove.notifications import NotificationError


if TYPE_CHECKING:
    fromapprove.sessions.atprotosocial.session import Session as ATProtoSocialSession
    # Define common type aliases if needed
    ATUserProfile = models.AppBskyActorDefs.ProfileViewDetailed
    ATPost = models.AppBskyFeedDefs.PostView
    ATNotification = models.AppBskyNotificationListNotifications.Notification # Item in notification list
    # StrongRef might be models.ComAtprotoRepoStrongRef.Main or similar


logger = logging.getLogger(__name__)


class ATProtoSocialUtils:
    def __init__(self, session: ATProtoSocialSession) -> None:
        self.session = session
        # _own_did and _own_handle are now set by Session.login upon successful authentication
        # and directly on the util instance.
        self._own_did: str | None = self.session.db.get("did") or self.session.config_get("did")
        self._own_handle: str | None = self.session.db.get("handle") or self.session.config_get("handle")

    # --- Client Initialization and Management ---
    
    async def _get_client(self) -> AsyncClient | None:
        """Returns the authenticated ATProto AsyncClient from the session."""
        if self.session.client and self.session.is_ready(): # is_ready checks if client is authenticated
            # Ensure internal DID/handle are in sync if possible, though session.login should handle this.
            if not self._own_did and self.session.client.me:
                 self._own_did = self.session.client.me.did
            if not self._own_handle and self.session.client.me:
                 self._own_handle = self.session.client.me.handle
            return self.session.client
        
        logger.warning("ATProtoSocialUtils: Client not available or not authenticated.")
        # Optionally, try to trigger re-authentication if appropriate,
        # but generally, the caller should ensure session is ready.
        # For example, by calling session.start() or session.authorise()
        # if await self.session.authorise(): # This could trigger UI prompts, be careful
        #    return self.session.client
        return None

    async def get_own_profile_info(self) -> ATUserProfile | None:
        """Retrieves the authenticated user's profile information."""
        client = await self._get_client()
        if not client or not self.get_own_did(): # Use getter for _own_did
            logger.warning("ATProtoSocial client not available or user DID not known.")
            return None
        try:
            # client.me should be populated after login by the SDK
            if client.me: # client.me is ProfileViewDetailed after login
                # To get the most detailed, up-to-date profile:
                response = await client.app.bsky.actor.get_profile(models.AppBskyActorGetProfile.Params(actor=self.get_own_did()))
                if isinstance(response, models.AppBskyActorDefs.ProfileViewDetailed):
                    return response # This is already the correct type
                else: # Should not happen if DID is correct
                    logger.error(f"Unexpected response type from get_profile: {type(response)}")
                    return None
            else: # Fallback if client.me is somehow not populated
                 logger.info("client.me not populated, attempting get_profile for own DID.")
                 response = await client.app.bsky.actor.get_profile(models.AppBskyActorGetProfile.Params(actor=self.get_own_did()))
                 if isinstance(response, models.AppBskyActorDefs.ProfileViewDetailed):
                    return response
                 return None
        except AtProtocolError as e:
            logger.error(f"Error fetching own ATProtoSocial profile: {e}")
            return None

    def get_own_did(self) -> str | None:
        """Returns the authenticated user's DID."""
        if not self._own_did: # If not set during init (e.g. session not fully loaded yet)
            self._own_did = self.session.db.get("did") or self.session.config_get("did")
        
        # Fallback: try to get from client if it's alive and has .me property
        if not self._own_did and self.session.client and self.session.client.me:
            self._own_did = self.session.client.me.did
        return self._own_did

    def get_own_username(self) -> str | None: # "username" here means handle
        """Returns the authenticated user's handle."""
        if not self._own_handle:
             self._own_handle = self.session.db.get("handle") or self.session.config_get("handle")

        if not self._own_handle and self.session.client and self.session.client.me:
            self._own_handle = self.session.client.me.handle
        return self._own_handle


    # --- Post / Status Operations ---

    async def post_status(
        self,
        text: str,
        media_ids: list[str] | None = None, # Here media_ids would be blob refs from upload_media
        reply_to_uri: str | None = None, # ATURI of the post being replied to
        quote_uri: str | None = None, # ATURI of the post being quoted
        cw_text: str | None = None, # For content warning (labels)
        is_sensitive: bool = False, # General sensitivity flag
        langs: list[str] | None = None, # List of language codes e.g. ['en', 'ja']
        tags: list[str] | None = None, # Hashtags
        **kwargs: Any
    ) -> str | None: # Returns the ATURI of the new post, or None on failure
        """
        Posts a status (skeet) to ATProtoSocial.
        Handles text, images, replies, quotes, and content warnings (labels).
        """
        client = await self._get_client()
        if not client:
            logger.error("ATProtoSocial client not available for posting.")
            raise NotificationError(_("Not connected to ATProtoSocial. Please check your connection settings or log in."))

        if not self.get_own_did():
            logger.error("Cannot post status: User DID not available.")
            raise NotificationError(_("User identity not found. Cannot create post."))

        try:
            # Prepare core post record
            post_record_data = {'text': text, 'created_at': client.get_current_time_iso()} # SDK handles datetime format
            
            if langs:
                post_record_data['langs'] = langs
            
            # Facets (mentions, links, tags) should be processed before other embeds
            # as they are part of the main post record.
            facets = await self._extract_facets(text, tags) # Pass client for potential resolutions
            if facets:
                post_record_data['facets'] = facets

            # Embeds: images, quote posts, external links
            # Note: Bluesky typically allows one main embed type (images OR record OR external)
            embed_to_add: models.AppBskyFeedPost.Embed | None = None

            # Embeds: images, quote posts, external links
            # ATProto allows one main embed type: app.bsky.embed.images, app.bsky.embed.record (quote/post embed), 
            # or app.bsky.embed.external.
            # Priority: 1. Quote, 2. Images. External embeds are not handled in this example.
            # If both quote and images are provided, quote takes precedence.

            embed_to_add: models.AppBskyFeedPost.Embed | None = None

            if quote_uri:
                logger.info(f"Attempting to add quote embed for URI: {quote_uri}")
                quoted_post_strong_ref = await self._get_strong_ref_for_uri(quote_uri)
                if quoted_post_strong_ref:
                    embed_to_add = models.AppBskyEmbedRecord.Main(record=quoted_post_strong_ref)
                    if media_ids:
                        logger.warning(f"Quote URI provided ({quote_uri}), images will be ignored due to embed priority.")
                else:
                    logger.warning(f"Could not create strong reference for quote URI: {quote_uri}. Quote will be omitted.")
            
            # Handle media attachments (images) only if no quote embed was successfully created
            if not embed_to_add and media_ids:
                logger.info(f"Attempting to add image embed with {len(media_ids)} media items.")
                images_for_embed = []
                for media_info in media_ids: 
                    if isinstance(media_info, dict) and media_info.get("blob_ref"):
                        images_for_embed.append(
                            models.AppBskyEmbedImages.Image(
                                image=media_info["blob_ref"], # This should be a BlobRef instance
                                alt=media_info.get("alt_text", "")
                            )
                        )
                if images_for_embed:
                    embed_to_add = models.AppBskyEmbedImages.Main(images=images_for_embed)
            
            if embed_to_add:
                post_record_data['embed'] = embed_to_add

            # Handle replies
            if reply_to_uri:
                parent_strong_ref = await self._get_strong_ref_for_uri(reply_to_uri)
                if parent_strong_ref:
                    # Determine root. If parent is also a reply, its root should be used.
                    # This requires fetching the parent post and checking its .reply.root
                    # For simplicity now, assume direct parent is root, or parent_strong_ref itself is enough.
                    # A robust solution fetches parent post: parent_post_details = await client.app.bsky.feed.get_posts([reply_to_uri])
                    # then uses parent_post_details.posts[0].record.reply.root if present.
                    # Placeholder: use parent as root for now
                    post_record_data['reply'] = models.AppBskyFeedPost.ReplyRef(
                        root=parent_strong_ref, # Simplified: SDK might need full root post ref
                        parent=parent_strong_ref
                    )
                else:
                    logger.warning(f"Could not create strong reference for reply URI: {reply_to_uri}. Reply info will be omitted.")


            # Handle content warnings (labels)
            # Bluesky uses self-labeling.
            post_labels: list[models.ComAtprotoLabelDefs.SelfLabel] = []
            if cw_text: # Custom label for "content warning" text itself
                # Ensure cw_text is not too long for a label value (max 64 chars for label value, but this is for the *value*, not a predefined category)
                # Using a generic "!warn" or a custom scheme like "cw:..."
                # The SDK might have specific ways to add !warn or other standard labels.
                # For a simple text CW, it's often just part of the text or a client-side convention.
                # If mapping to official labels:
                post_labels.append(models.ComAtprotoLabelDefs.SelfLabel(val="!warn")) # Generic warning
                # Or if cw_text is a specific category that maps to a label:
                # post_labels.append(models.ComAtprotoLabelDefs.SelfLabel(val=cw_text)) # if cw_text is like "nudity"
            if is_sensitive and not any(l.val == "!warn" for l in post_labels): # Add generic !warn if sensitive and not already added by cw_text
                 post_labels.append(models.ComAtprotoLabelDefs.SelfLabel(val="!warn"))
            
            if post_labels:
                 post_record_data['labels'] = models.ComAtprotoLabelDefs.SelfLabels(values=post_labels)
            
            # Create the post record object
            final_post_record = models.AppBskyFeedPost.Main(**post_record_data)

            response = await client.com.atproto.repo.create_record(
                models.ComAtprotoRepoCreateRecord.Input(
                    repo=self.get_own_did(), # Must be own DID
                    collection=ids.AppBskyFeedPost, # e.g., "app.bsky.feed.post"
                    record=final_post_record,
                )
            )
            logger.info(f"Successfully posted to ATProtoSocial. URI: {response.uri}")
            return response.uri 
        except AtProtocolError as e:
            logger.error(f"Error posting status to ATProtoSocial: {e.error} - {e.message}", exc_info=True)
            raise NotificationError(_("Failed to post: {error} - {message}").format(error=e.error or "Error", message=e.message or "Protocol error")) from e
        except Exception as e: # Catch any other unexpected errors
            logger.error(f"Unexpected error posting status to ATProtoSocial: {e}", exc_info=True)
            raise NotificationError(_("An unexpected error occurred while posting: {error}").format(error=str(e))) from e


    async def delete_status(self, post_uri: str) -> bool:
        """Deletes a status (post) given its AT URI."""
        client = await self._get_client()
        if not client:
            logger.error("ATProtoSocial client not available for deleting post.")
            return False
        if not self.get_own_did():
            logger.error("Cannot delete status: User DID not available.")
            return False
            
        try:
            # Extract rkey from URI. URI format: at://<did>/<collection>/<rkey>
            uri_parts = post_uri.replace("at://", "").split("/")
            if len(uri_parts) != 3:
                logger.error(f"Invalid AT URI format for deletion: {post_uri}")
                return False
            # repo_did = uri_parts[0] # Should match self.get_own_did()
            collection = uri_parts[1]
            rkey = uri_parts[2]

            if collection != ids.AppBskyFeedPost: # Ensure it's the correct collection
                logger.error(f"Attempting to delete from incorrect collection '{collection}'. Expected '{ids.AppBskyFeedPost}'.")
                return False

            await client.com.atproto.repo.delete_record(
                models.ComAtprotoRepoDeleteRecord.Input(
                    repo=self.get_own_did(), # Must be own DID
                    collection=collection,
                    rkey=rkey,
                )
            )
            logger.info(f"Successfully deleted post {post_uri} from ATProtoSocial.")
            return True
        except AtProtocolError as e:
            logger.error(f"Error deleting post {post_uri} from ATProtoSocial: {e.error} - {e.message}")
        except Exception as e:
            logger.error(f"Unexpected error deleting post {post_uri}: {e}", exc_info=True)
        return False


    async def upload_media(self, file_path: str, mime_type: str, alt_text: str | None = None) -> dict[str, Any] | None:
        """
        Uploads media (image) to ATProtoSocial.
        Returns a dictionary containing the SDK's BlobRef object and alt_text, or None on failure.
        """
        client = await self._get_client()
        if not client:
            logger.error("ATProtoSocial client not available for media upload.")
            return None
        try:
            with open(file_path, "rb") as f:
                image_data = f.read()
            
            # The SDK's upload_blob takes bytes directly.
            response = await client.com.atproto.repo.upload_blob(image_data, mime_type=mime_type) 
            if response and response.blob:
                logger.info(f"Media uploaded successfully: {file_path}, Blob CID: {response.blob.cid}")
                # Return the actual blob object from the SDK, as it's needed for post creation.
                return {
                    "blob_ref": response.blob, # This is models.ComAtprotoRepoStrongRef.Blob
                    "alt_text": alt_text or "",
                }
            else:
                logger.error(f"Media upload failed for {file_path}, no blob in response.")
                return None
        except AtProtocolError as e:
            logger.error(f"Error uploading media {file_path} to ATProtoSocial: {e.error} - {e.message}", exc_info=True)
        except Exception as e:
            logger.error(f"Unexpected error uploading media {file_path}: {e}", exc_info=True)
        return None


    # --- User Profile and Interaction ---

    async def get_profile_by_handle(self, handle: str) -> ATUserProfile | None:
        """Fetches a user's profile by their handle."""
        client = await self._get_client()
        if not client: return None
        try:
            response = await client.app.bsky.actor.get_profile(models.AppBskyActorGetProfile.Params(actor=handle))
            if isinstance(response, models.AppBskyActorDefs.ProfileViewDetailed):
                return response
            return None # Should not happen if handle is valid
        except AtProtocolError as e:
            logger.error(f"Error fetching profile for {handle}: {e.error} - {e.message}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching profile for {handle}: {e}", exc_info=True)
            return None


    async def follow_user(self, user_did: str) -> bool:
        """Follows a user by their DID."""
        client = await self._get_client()
        if not client: return False
        if not self.get_own_did():
            logger.error("Cannot follow user: Own DID not available.")
            return False
            
        try:
            await client.com.atproto.repo.create_record(
                models.ComAtprotoRepoCreateRecord.Input(
                    repo=self.get_own_did(),
                    collection=ids.AppBskyGraphFollow, # "app.bsky.graph.follow"
                    record=models.AppBskyGraphFollow.Main(subject=user_did, created_at=client.get_current_time_iso()),
                )
            )
            logger.info(f"Successfully followed user {user_did}.")
            return True
        except AtProtocolError as e:
            logger.error(f"Error following user {user_did}: {e.error} - {e.message}")
        except Exception as e:
            logger.error(f"Unexpected error following user {user_did}: {e}", exc_info=True)
        return False


    async def unfollow_user(self, user_did: str) -> bool:
        """Unfollows a user by their DID. Requires finding the follow record's URI (rkey)."""
        client = await self._get_client()
        if not client: return False
        if not self.get_own_did():
            logger.error("Cannot unfollow user: Own DID not available.")
            return False

        try:
            # Find the URI of the follow record. This is the tricky part.
            # We need the rkey of the follow record.
            follow_rkey = await self._find_follow_record_rkey(user_did)
            if not follow_rkey:
                logger.warning(f"Could not find follow record for user {user_did} to unfollow.")
                return False
            
            await client.com.atproto.repo.delete_record(
                models.ComAtprotoRepoDeleteRecord.Input(
                    repo=self.get_own_did(),
                    collection=ids.AppBskyGraphFollow,
                    rkey=follow_rkey,
                )
            )
            logger.info(f"Successfully unfollowed user {user_did}.")
            return True
        except AtProtocolError as e:
            logger.error(f"Error unfollowing user {user_did}: {e.error} - {e.message}")
        except Exception as e:
            logger.error(f"Unexpected error unfollowing user {user_did}: {e}", exc_info=True)
        return False

        
    # --- Notifications and Timelines (Illustrative - actual implementation is complex) ---

    async def get_notifications(self, limit: int = 20, cursor: str | None = None) -> tuple[list[ATNotification], str | None] | None:
        """Fetches notifications for the authenticated user. Returns (notifications, cursor) or None."""
        client = await self._get_client()
        if not client: return None
        try:
            response = await client.app.bsky.notification.list_notifications(
               models.AppBskyNotificationListNotifications.Params(limit=limit, cursor=cursor)
            )
            # No need to format further if ATNotification type hint is used and callers expect SDK models
            return response.notifications, response.cursor
        except AtProtocolError as e:
            logger.error(f"Error fetching notifications: {e.error} - {e.message}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching notifications: {e}", exc_info=True)
            return None


    async def get_timeline(self, algorithm: str | None = None, limit: int = 20, cursor: str | None = None) -> tuple[list[models.AppBskyFeedDefs.FeedViewPost], str | None] | None:
        """
        Fetches a timeline (feed) for the authenticated user.
        Returns (feed_items, cursor) or None.
        'algorithm' can be None for default "Following" or a custom feed URI (at://did/app.bsky.feed.generator/uri).
        """
        client = await self._get_client()
        if not client: return None
        try:
            params = models.AppBskyFeedGetTimeline.Params(limit=limit, cursor=cursor)
            if algorithm: # Only add algorithm if it's specified, SDK might default to 'following'
                params.algorithm = algorithm
                
            response = await client.app.bsky.feed.get_timeline(params)
            # response.feed is a list of FeedViewPost items
            return response.feed, response.cursor
        except AtProtocolError as e:
            logger.error(f"Error fetching timeline (algorithm: {algorithm}): {e.error} - {e.message}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching timeline (algorithm: {algorithm}): {e}", exc_info=True)
            return None


    async def get_author_feed(self, actor_did: str, limit: int = 20, cursor: str | None = None, filter: str = "posts_with_replies") -> tuple[list[models.AppBskyFeedDefs.FeedViewPost], str | None] | None:
        """
        Fetches a specific user's timeline (feed).
        Returns (feed_items, cursor) or None.
        filter can be: "posts_with_replies", "posts_no_replies", "posts_with_media".
        The default "posts_with_replies" includes user's posts and their replies.
        To get only original posts (no replies): "posts_no_replies".
        To get posts and reposts: This is not a direct filter in getAuthorFeed. Reposts are part of the feed if the PDS includes them.
        The `filter` parameter in `getAuthorFeed` is actually `filter: Literal['posts_with_replies', 'posts_no_replies', 'posts_and_author_threads', 'posts_with_media']`
        Let's use a sensible default or make it configurable if needed by the session.
        For "posts and reposts", you typically just get the author feed and it includes reposts.
        """
        client = await self._get_client()
        if not client: return None
        try:
            # Ensure filter is a valid choice for the SDK if it uses an Enum or Literal
            # For this example, we assume the string is passed directly.
            # Valid filters are 'posts_with_replies', 'posts_no_replies', 'posts_and_author_threads', 'posts_with_media'.
            # Defaulting to 'posts_and_author_threads' to include posts, replies, and reposts by the author.
            # Actually, getAuthorFeed's `filter` param does not directly control inclusion of reposts in a way that
            # "posts_and_reposts" would imply. Reposts by the author of things *they reposted* are part of their feed.
            # A common default is 'posts_with_replies'. If we want to see their reposts, that's typically included by default.
            
            current_filter_value = filter
            if current_filter_value not in ['posts_with_replies', 'posts_no_replies', 'posts_and_author_threads', 'posts_with_media']:
                logger.warning(f"Invalid filter '{current_filter_value}' for getAuthorFeed. Defaulting to 'posts_with_replies'.")
                current_filter_value = 'posts_with_replies'


            params = models.AppBskyFeedGetAuthorFeed.Params(actor=actor_did, limit=limit, cursor=cursor, filter=current_filter_value)
            response = await client.app.bsky.feed.get_author_feed(params)
            return response.feed, response.cursor
        except AtProtocolError as e:
            logger.error(f"Error fetching author feed for {actor_did}: {e.error} - {e.message}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching author feed for {actor_did}: {e}", exc_info=True)
            return None

    async def get_user_profile(self, user_ident: str) -> ATUserProfile | None:
        """Fetches a detailed user profile by DID or handle."""
        client = await self._get_client()
        if not client:
            logger.error(f"Cannot get profile for {user_ident}: ATProto client not available.")
            return None
        try:
            response = await client.app.bsky.actor.get_profile(models.AppBskyActorGetProfile.Params(actor=user_ident))
            if isinstance(response, models.AppBskyActorDefs.ProfileViewDetailed):
                return response
            logger.error(f"Unexpected response type when fetching profile for {user_ident}: {type(response)}")
            return None
        except AtProtocolError as e:
            logger.error(f"Error fetching profile for {user_ident}: {e.error} - {e.message}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching profile for {user_ident}: {e}", exc_info=True)
            return None


    async def get_followers(self, user_did: str, limit: int = 30, cursor: str | None = None) -> tuple[list[models.AppBskyActorDefs.ProfileView], str | None] | None:
        """Fetches followers for a given user DID."""
        client = await self._get_client()
        if not client:
            logger.error(f"Cannot get followers for {user_did}: ATProto client not available.")
            return None
        try:
            response = await client.app.bsky.graph.get_followers(
                models.AppBskyGraphGetFollowers.Params(actor=user_did, limit=limit, cursor=cursor)
            )
            return response.followers, response.cursor
        except AtProtocolError as e:
            logger.error(f"Error fetching followers for {user_did}: {e.error} - {e.message}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching followers for {user_did}: {e}", exc_info=True)
            return None

    async def get_following(self, user_did: str, limit: int = 30, cursor: str | None = None) -> tuple[list[models.AppBskyActorDefs.ProfileView], str | None] | None:
        """Fetches accounts followed by a given user DID."""
        client = await self._get_client()
        if not client:
            logger.error(f"Cannot get following for {user_did}: ATProto client not available.")
            return None
        try:
            response = await client.app.bsky.graph.get_follows( # Correct endpoint is get_follows
                models.AppBskyGraphGetFollows.Params(actor=user_did, limit=limit, cursor=cursor)
            )
            return response.follows, response.cursor
        except AtProtocolError as e:
            logger.error(f"Error fetching accounts followed by {user_did}: {e.error} - {e.message}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching accounts followed by {user_did}: {e}", exc_info=True)
            return None

    async def search_users(self, term: str, limit: int = 20, cursor: str | None = None) -> tuple[list[models.AppBskyActorDefs.ProfileView], str | None] | None:
        """Searches for users based on a term."""
        client = await self._get_client()
        if not client:
            logger.error(f"Cannot search users for '{term}': ATProto client not available.")
            return None
        try:
            response = await client.app.bsky.actor.search_actors(
                models.AppBskyActorSearchActors.Params(term=term, limit=limit, cursor=cursor)
            )
            return response.actors, response.cursor
        except AtProtocolError as e:
            logger.error(f"Error searching users for '{term}': {e.error} - {e.message}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error searching users for '{term}': {e}", exc_info=True)
            return None


    async def mute_user(self, user_did: str) -> bool:
        """Mutes a user by their DID."""
        client = await self._get_client()
        if not client: 
            logger.error("Cannot mute user: ATProto client not available.")
            return False
        try:
            await client.app.bsky.graph.mute_actor(models.AppBskyGraphMuteActor.Input(actor=user_did))
            logger.info(f"Successfully muted user {user_did}.")
            return True
        except AtProtocolError as e:
            # Check if already muted - SDK might throw specific error or general one.
            # For now, log and return False. A more specific error could be returned to UI.
            logger.error(f"Error muting user {user_did}: {e.error} - {e.message}")
        except Exception as e:
            logger.error(f"Unexpected error muting user {user_did}: {e}", exc_info=True)
        return False

    async def unmute_user(self, user_did: str) -> bool:
        """Unmutes a user by their DID."""
        client = await self._get_client()
        if not client: 
            logger.error("Cannot unmute user: ATProto client not available.")
            return False
        try:
            await client.app.bsky.graph.unmute_actor(models.AppBskyGraphUnmuteActor.Input(actor=user_did))
            logger.info(f"Successfully unmuted user {user_did}.")
            return True
        except AtProtocolError as e:
            # Check if already unmuted / not muted.
            logger.error(f"Error unmuting user {user_did}: {e.error} - {e.message}")
        except Exception as e:
            logger.error(f"Unexpected error unmuting user {user_did}: {e}", exc_info=True)
        return False

    async def block_user(self, user_did: str) -> str | None:
        """
        Blocks a user by their DID.
        Returns the AT URI of the block record on success, None on failure.
        """
        client = await self._get_client()
        if not client: 
            logger.error("Cannot block user: ATProto client not available.")
            return None
        if not self.get_own_did():
            logger.error("Cannot block user: Own DID not available.")
            return None
            
        try:
            response = await client.com.atproto.repo.create_record(
                models.ComAtprotoRepoCreateRecord.Input(
                    repo=self.get_own_did(),
                    collection=ids.AppBskyGraphBlock, # "app.bsky.graph.block"
                    record=models.AppBskyGraphBlock.Main(subject=user_did, created_at=client.get_current_time_iso()),
                )
            )
            logger.info(f"Successfully blocked user {user_did}. Block record URI: {response.uri}")
            return response.uri
        except AtProtocolError as e:
            # Handle specific errors, e.g., if user is already blocked.
            # The SDK might raise an error like "already exists" or a generic one.
            logger.error(f"Error blocking user {user_did}: {e.error} - {e.message}")
        except Exception as e:
            logger.error(f"Unexpected error blocking user {user_did}: {e}", exc_info=True)
        return None

    async def _find_block_record_rkey(self, target_did: str) -> str | None:
        """Helper to find the rkey of a block record for a given target DID."""
        client = await self._get_client()
        own_did = self.get_own_did()
        if not client or not own_did: return None
        
        cursor = None
        try:
            while True:
                response = await client.com.atproto.repo.list_records(
                    models.ComAtprotoRepoListRecords.Params(
                        repo=own_did,
                        collection=ids.AppBskyGraphBlock, 
                        limit=100, 
                        cursor=cursor,
                    )
                )
                if not response or not response.records:
                    break 
                
                for record_item in response.records:
                    if record_item.value and isinstance(record_item.value, models.AppBskyGraphBlock.Main):
                        if record_item.value.subject == target_did:
                            return record_item.uri.split("/")[-1] # Extract rkey from URI
                
                cursor = response.cursor
                if not cursor:
                    break
            logger.info(f"No active block record found for user {target_did} by {own_did}.")
            return None 
        except AtProtocolError as e:
            logger.error(f"Error listing block records for {own_did} to find {target_did}: {e.error} - {e.message}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error finding block rkey for {target_did}: {e}", exc_info=True)
            return None

    async def repost_post(self, post_uri: str, post_cid: str | None = None) -> str | None:
        """Creates a repost for a given post URI and CID. Returns URI of the repost record or None."""
        client = await self._get_client()
        if not client or not self.get_own_did():
            logger.error("Cannot repost: client or own DID not available.")
            return None
        
        if not post_cid: # If CID is not provided, try to get it
            strong_ref = await self._get_strong_ref_for_uri(post_uri)
            if not strong_ref:
                logger.error(f"Could not get strong reference for post {post_uri} to repost.")
                return None
            post_cid = strong_ref.cid # type: ignore

        try:
            response = await client.com.atproto.repo.create_record(
                models.ComAtprotoRepoCreateRecord.Input(
                    repo=self.get_own_did(),
                    collection=ids.AppBskyFeedRepost,
                    record=models.AppBskyFeedRepost.Main(
                        subject=models.ComAtprotoRepoStrongRef.Main(uri=post_uri, cid=post_cid),
                        createdAt=client.get_current_time_iso()
                    )
                )
            )
            logger.info(f"Successfully reposted {post_uri}. Repost URI: {response.uri}")
            return response.uri
        except AtProtocolError as e:
            logger.error(f"Error reposting {post_uri}: {e.error} - {e.message}")
            # Consider raising NotificationError for specific, user-understandable errors
            if "already exists" in str(e.message).lower() or "duplicate" in str(e.message).lower():
                 raise NotificationError(_("You have already reposted this post.")) from e
        except Exception as e:
            logger.error(f"Unexpected error reposting {post_uri}: {e}", exc_info=True)
        return None

    async def like_post(self, post_uri: str, post_cid: str | None = None) -> str | None:
        """Likes a given post URI and CID. Returns URI of the like record or None."""
        client = await self._get_client()
        if not client or not self.get_own_did():
            logger.error("Cannot like post: client or own DID not available.")
            return None

        if not post_cid: # If CID is not provided, try to get it
            strong_ref = await self._get_strong_ref_for_uri(post_uri)
            if not strong_ref:
                logger.error(f"Could not get strong reference for post {post_uri} to like.")
                return None
            post_cid = strong_ref.cid # type: ignore

        try:
            response = await client.com.atproto.repo.create_record(
                models.ComAtprotoRepoCreateRecord.Input(
                    repo=self.get_own_did(),
                    collection=ids.AppBskyFeedLike,
                    record=models.AppBskyFeedLike.Main(
                        subject=models.ComAtprotoRepoStrongRef.Main(uri=post_uri, cid=post_cid),
                        createdAt=client.get_current_time_iso()
                    )
                )
            )
            logger.info(f"Successfully liked {post_uri}. Like URI: {response.uri}")
            return response.uri
        except AtProtocolError as e:
            logger.error(f"Error liking {post_uri}: {e.error} - {e.message}")
            if "already exists" in str(e.message).lower() or "duplicate" in str(e.message).lower():
                 raise NotificationError(_("You have already liked this post.")) from e
        except Exception as e:
            logger.error(f"Unexpected error liking {post_uri}: {e}", exc_info=True)
        return None

    async def delete_like(self, like_uri: str) -> bool:
        """Deletes a like given the URI of the like record itself."""
        client = await self._get_client()
        if not client or not self.get_own_did():
            logger.error("Cannot delete like: client or own DID not available.")
            return False
        
        try:
            # Extract rkey from like_uri
            # Format: at://<did>/app.bsky.feed.like/<rkey>
            uri_parts = like_uri.replace("at://", "").split("/")
            if len(uri_parts) != 3 or uri_parts[1] != ids.AppBskyFeedLike:
                logger.error(f"Invalid like URI format for deletion: {like_uri}")
                return False
            
            rkey = uri_parts[2]
            
            await client.com.atproto.repo.delete_record(
                models.ComAtprotoRepoDeleteRecord.Input(
                    repo=self.get_own_did(),
                    collection=ids.AppBskyFeedLike,
                    rkey=rkey
                )
            )
            logger.info(f"Successfully deleted like {like_uri}.")
            return True
        except AtProtocolError as e:
            logger.error(f"Error deleting like {like_uri}: {e.error} - {e.message}")
            # Could check for "not found" type errors if user tries to unlike something not liked
        except Exception as e:
            logger.error(f"Unexpected error deleting like {like_uri}: {e}", exc_info=True)
        return False

    async def repost_post(self, post_uri: str, post_cid: str | None = None) -> str | None:
        """Creates a repost for a given post URI and CID. Returns URI of the repost record or None."""
        client = await self._get_client()
        if not client or not self.get_own_did():
            logger.error("Cannot repost: client or own DID not available.")
            # raise NotificationError(_("Session not ready. Please log in.")) # Alternative
            return None
        
        if not post_cid: # If CID is not provided, try to get it from the URI
            strong_ref_to_post = await self._get_strong_ref_for_uri(post_uri)
            if not strong_ref_to_post:
                logger.error(f"Could not get strong reference for post {post_uri} to repost it.")
                raise NotificationError(_("Could not find the post to repost."))
            post_cid = strong_ref_to_post.cid # type: ignore # SDK uses .cid

        try:
            response = await client.com.atproto.repo.create_record(
                models.ComAtprotoRepoCreateRecord.Input(
                    repo=self.get_own_did(), # Must be own DID
                    collection=ids.AppBskyFeedRepost,
                    record=models.AppBskyFeedRepost.Main(
                        subject=models.ComAtprotoRepoStrongRef.Main(uri=post_uri, cid=post_cid),
                        createdAt=client.get_current_time_iso() # SDK helper for current time
                    )
                )
            )
            logger.info(f"Successfully reposted {post_uri}. Repost URI: {response.uri}")
            return response.uri
        except AtProtocolError as e:
            logger.error(f"Error reposting {post_uri}: {e.error} - {e.message}")
            if e.error == "DuplicateRecord": # Or similar error code for existing repost
                 raise NotificationError(_("You have already reposted this post.")) from e
            raise NotificationError(_("Failed to repost: {error}").format(error=e.message or e.error)) from e
        except Exception as e:
            logger.error(f"Unexpected error reposting {post_uri}: {e}", exc_info=True)
            raise NotificationError(_("An unexpected error occurred while reposting."))


    async def like_post(self, post_uri: str, post_cid: str | None = None) -> str | None:
        """Likes a given post URI and CID. Returns URI of the like record or None."""
        client = await self._get_client()
        if not client or not self.get_own_did():
            logger.error("Cannot like post: client or own DID not available.")
            return None # Or raise NotificationError

        if not post_cid: # If CID is not provided, try to get it from the URI
            strong_ref_to_post = await self._get_strong_ref_for_uri(post_uri)
            if not strong_ref_to_post:
                logger.error(f"Could not get strong reference for post {post_uri} to like it.")
                raise NotificationError(_("Could not find the post to like."))
            post_cid = strong_ref_to_post.cid # type: ignore

        try:
            response = await client.com.atproto.repo.create_record(
                models.ComAtprotoRepoCreateRecord.Input(
                    repo=self.get_own_did(),
                    collection=ids.AppBskyFeedLike, # "app.bsky.feed.like"
                    record=models.AppBskyFeedLike.Main(
                        subject=models.ComAtprotoRepoStrongRef.Main(uri=post_uri, cid=post_cid),
                        createdAt=client.get_current_time_iso()
                    )
                )
            )
            logger.info(f"Successfully liked {post_uri}. Like URI: {response.uri}")
            return response.uri
        except AtProtocolError as e:
            logger.error(f"Error liking {post_uri}: {e.error} - {e.message}")
            if e.error == "DuplicateRecord": # Or similar error code for existing like
                 raise NotificationError(_("You have already liked this post.")) from e
            raise NotificationError(_("Failed to like post: {error}").format(error=e.message or e.error)) from e
        except Exception as e:
            logger.error(f"Unexpected error liking {post_uri}: {e}", exc_info=True)
            raise NotificationError(_("An unexpected error occurred while liking the post."))


    async def delete_like(self, like_uri: str) -> bool:
        """Deletes a like given the URI of the like record itself."""
        client = await self._get_client()
        if not client or not self.get_own_did():
            logger.error("Cannot delete like: client or own DID not available.")
            return False
        
        try:
            # Extract rkey from like_uri
            # Format: at://<did>/app.bsky.feed.like/<rkey>
            uri_parts = like_uri.replace("at://", "").split("/")
            if len(uri_parts) != 3 or uri_parts[1] != ids.AppBskyFeedLike: # Check collection is correct
                logger.error(f"Invalid like URI format for deletion: {like_uri}")
                return False # Or raise error
            
            # own_did_from_uri = uri_parts[0] # This should match self.get_own_did()
            # if own_did_from_uri != self.get_own_did():
            #    logger.error(f"Attempting to delete a like not owned by the current user: {like_uri}")
            #    return False

            rkey = uri_parts[2]
            
            await client.com.atproto.repo.delete_record(
                models.ComAtprotoRepoDeleteRecord.Input(
                    repo=self.get_own_did(), # Must be own DID
                    collection=ids.AppBskyFeedLike,
                    rkey=rkey
                )
            )
            logger.info(f"Successfully deleted like {like_uri}.")
            return True
        except AtProtocolError as e:
            logger.error(f"Error deleting like {like_uri}: {e.error} - {e.message}")
            # If error indicates "not found", it means it was already unliked or never existed.
            # We could return True for idempotency or False for strict "did I delete it now?"
            # For now, let's return False on any API error.
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting like {like_uri}: {e}", exc_info=True)
            return False


    async def unblock_user(self, user_did: str) -> bool:
        """Unblocks a user by their DID. Requires finding the block record's rkey."""
        client = await self._get_client()
        if not client: 
            logger.error("Cannot unblock user: ATProto client not available.")
            return False
        if not self.get_own_did():
            logger.error("Cannot unblock user: Own DID not available.")
            return False

        try:
            block_rkey = await self._find_block_record_rkey(user_did)
            if not block_rkey:
                logger.warning(f"Could not find block record for user {user_did} to unblock. User might not be blocked.")
                # Depending on desired UX, this could be True (idempotency) or False (strict "not found")
                return False 
            
            await client.com.atproto.repo.delete_record(
                models.ComAtprotoRepoDeleteRecord.Input(
                    repo=self.get_own_did(),
                    collection=ids.AppBskyGraphBlock,
                    rkey=block_rkey,
                )
            )
            logger.info(f"Successfully unblocked user {user_did}.")
            return True
        except AtProtocolError as e:
            logger.error(f"Error unblocking user {user_did}: {e.error} - {e.message}")
        except Exception as e:
            logger.error(f"Unexpected error unblocking user {user_did}: {e}", exc_info=True)
        return False

        
    # --- Helper Methods for Formatting and URI/DID manipulation ---

    def _format_profile_data(self, profile_model: models.AppBskyActorDefs.ProfileViewDetailed | models.AppBskyActorDefs.ProfileView | models.AppBskyActorDefs.ProfileViewBasic) -> dict[str, Any]:
        """Converts an ATProto profile model to a standardized dictionary for Approve internal use if needed."""
        # This is an example if Approve needs its own dict format instead of using SDK models directly.
        # For now, many methods return SDK models directly (ATUserProfile, ATPost types).
        return {
            "did": profile_model.did,
            "handle": profile_model.handle,
            "displayName": getattr(profile_model, 'displayName', None) or profile_model.handle,
            "description": getattr(profile_model, 'description', None),
            "avatar": getattr(profile_model, 'avatar', None),
            "banner": getattr(profile_model, 'banner', None) if hasattr(profile_model, 'banner') else None,
            "followersCount": getattr(profile_model, 'followersCount', 0) if hasattr(profile_model, 'followersCount') else None,
            "followsCount": getattr(profile_model, 'followsCount', 0) if hasattr(profile_model, 'followsCount') else None,
            "postsCount": getattr(profile_model, 'postsCount', 0) if hasattr(profile_model, 'postsCount') else None,
            "indexedAt": getattr(profile_model, 'indexedAt', None), # For ProfileView, not Basic
            "labels": getattr(profile_model, 'labels', []), # For ProfileView, not Basic
            "viewer": getattr(profile_model, 'viewer', None), # For ProfileView, not Basic (viewer state like muted/following)
        }

    def _format_post_data(self, post_view_model: models.AppBskyFeedDefs.PostView) -> dict[str, Any]:
        """Converts an ATProto PostView model to a standardized dictionary if needed."""
        # record_data = post_view_model.record # This is the actual app.bsky.feed.post record
        # if not isinstance(record_data, models.AppBskyFeedPost.Main()): # Check it's the expected type
        #    logger.warning(f"Post record is not of type Main, actual: {type(record_data)}")
        #    text_content = "Unsupported post record type"
        # else:
        #    text_content = record_data.text
        
        return {
            "uri": post_view_model.uri,
            "cid": post_view_model.cid,
            "author": self._format_profile_data(post_view_model.author) if post_view_model.author else None,
            "record": post_view_model.record, # Keep the raw record for full data
            # "text": text_content, # Extracted text
            "embed": post_view_model.embed, # Raw embed
            "replyCount": post_view_model.replyCount if post_view_model.replyCount is not None else 0,
            "repostCount": post_view_model.repostCount if post_view_model.repostCount is not None else 0,
            "likeCount": post_view_model.likeCount if post_view_model.likeCount is not None else 0,
            "indexedAt": post_view_model.indexedAt,
            "labels": post_view_model.labels or [],
            "viewer": post_view_model.viewer, # Viewer state (e.g. like URI, repost URI)
        }

    def _format_notification_data(self, notification_model: ATNotification) -> dict[str,Any]:
        # This is an example if Approve needs its own dict format.
        return {
            "uri": notification_model.uri,
            "cid": notification_model.cid,
            "author": self._format_profile_data(notification_model.author) if notification_model.author else None,
            "reason": notification_model.reason, # e.g., "like", "repost", "follow", "mention", "reply", "quote"
            "reasonSubject": notification_model.reasonSubject, # AT URI of the subject of the notification (e.g. URI of the like record)
            "record": notification_model.record, # The record that actioned this notification (e.g. the like record itself)
            "isRead": notification_model.isRead,
            "indexedAt": notification_model.indexedAt,
            "labels": notification_model.labels or [],
        }

    async def _get_strong_ref_for_uri(self, at_uri: str) -> models.ComAtprotoRepoStrongRef.Main | None:
        """
        Given an AT URI, describe the record to get its CID and create a strong reference.
        This is needed for replies, quotes, etc.
        Alternatively, SDK's client.com.atproto.repo.create_strong_ref can be used if available.
        """
        client = await self._get_client()
        if not client: return None
        try:
            # URI format: at://<did>/<collection>/<rkey>
            parts = at_uri.replace("at://", "").split("/")
            if len(parts) != 3:
                logger.error(f"Invalid AT URI for strong ref: {at_uri}")
                return None
            
            repo_did, collection, rkey = parts
            
            # This is one way to get the CID if not already known.
            # If the CID is known, models.ComAtprotoRepoStrongRef.Main(uri=at_uri, cid=known_cid) is simpler.
            # However, for replies/quotes, the record must exist and be resolvable.
            described_record = await client.com.atproto.repo.describe_record(
               models.ComAtprotoRepoDescribeRecord.Params(repo=repo_did, collection=collection, rkey=rkey)
            )
            if described_record and described_record.cid:
                return models.ComAtprotoRepoStrongRef.Main(uri=described_record.uri, cid=described_record.cid)
            else:
                logger.error(f"Could not describe record for URI {at_uri} to create strong ref.")
                return None
        except AtProtocolError as e:
            logger.error(f"Could not get strong reference for URI {at_uri}: {e.error} - {e.message}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting strong ref for {at_uri}: {e}", exc_info=True)
            return None


    async def _find_follow_record_rkey(self, target_did: str) -> str | None:
        """Helper to find the rkey of a follow record for a given target DID."""
        client = await self._get_client()
        own_did = self.get_own_did()
        if not client or not own_did: return None
        
        cursor = None
        try:
            while True:
                response = await client.com.atproto.repo.list_records(
                    models.ComAtprotoRepoListRecords.Params(
                        repo=own_did,
                        collection=ids.AppBskyGraphFollow, # "app.bsky.graph.follow"
                        limit=100, 
                        cursor=cursor,
                    )
                )
                if not response or not response.records:
                    break 
                
                for record_item in response.records:
                    # record_item.value is the actual follow record (AppBskyGraphFollow.Main)
                    if record_item.value and isinstance(record_item.value, models.AppBskyGraphFollow.Main):
                        if record_item.value.subject == target_did:
                            # The rkey is part of the URI: at://<did>/app.bsky.graph.follow/<rkey>
                            return record_item.uri.split("/")[-1]
                
                cursor = response.cursor
                if not cursor:
                    break
            return None # Follow record not found
        except AtProtocolError as e:
            logger.error(f"Error listing follow records for {own_did} to find {target_did}: {e.error} - {e.message}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error finding follow rkey for {target_did}: {e}", exc_info=True)
            return None


    async def _extract_facets(self, text: str, tags: list[str] | None = None) -> list[models.AppBskyRichtextFacet.Main] | None:
        """
        Detects mentions, links, and tags in text and creates facet objects.
        Uses the atproto SDK's `detect_facets` via the client if available and resolves mentions.
        """
        client = await self._get_client()
        if not client:
            logger.warning("Cannot extract facets: ATProto client not available.")
            return None

        try:
            # The SDK's detect_facets is a utility function, not a client method.
            # from atproto. conhecido.facets import detect_facets # Path may vary
            # For now, assume a simplified version or that client might expose it.
            # A full implementation needs to handle byte offsets correctly.
            # This is a complex part of posting.
            
            # Placeholder for actual facet detection logic.
            # This would involve regex for mentions (@handle.bsky.social), links (http://...), and tags (#tag).
            # For mentions, DIDs need to be resolved. For links, URI needs to be validated.
            # Example (very simplified, not for production):
            # facets = []
            # import re
            # # Mentions
            # for match in re.finditer(r'@([a-zA-Z0-9.-]+)', text):
            #     handle = match.group(1)
            #     try:
            #         # profile = await client.app.bsky.actor.get_profile(models.AppBskyActorGetProfile.Params(actor=handle)) # This is a network call per mention!
            #         # if profile:
            #         #    facets.append(models.AppBskyRichtextFacet.Main(
            #         #        index=models.AppBskyRichtextFacet.ByteSlice(byteStart=match.start(), byteEnd=match.end()),
            #         #        features=[models.AppBskyRichtextFacet.Mention(did=profile.did)]
            #         #    ))
            #         pass # Proper implementation needed
            #     except Exception: # Handle resolution failure
            #         logger.warning(f"Could not resolve DID for mention @{handle}")
            # # Links
            # # Tags
            # if tags:
            #    for tag in tags:
            #        # find occurrences of #tag in text and add facet
            #        pass
            
            # If the SDK has a robust way to do this (even if it's a static method you import) use it.
            # e.g. from atproto. अमीर_text import RichText
            # rt = RichText(text)
            # await rt.resolve_facets(client) # if it needs async client for resolution
            # return rt.facets

            logger.debug("Facet extraction is currently a placeholder and may not correctly identify all rich text features.")
            return None
        except Exception as e:
            logger.error(f"Error during facet extraction: {e}", exc_info=True)
            return None


    async def report_post(self, post_uri: str, reason_type: str, reason_text: str | None = None) -> bool:
        """
        Reports a post (skeet) to the PDS/moderation service.
        reason_type should be one of com.atproto.moderation.defs#reasonType
        (e.g., lexicon_models.COM_ATPROTO_MODERATION_DEFS_REASONSPAM -> "com.atproto.moderation.defs#reasonSpam")
        """
        client = await self._get_client()
        if not client:
            logger.error("ATProtoSocial client not available for reporting.")
            return False
        
        try:
            # We need a strong reference to the post being reported.
            subject_strong_ref = await self._get_strong_ref_for_uri(post_uri)
            if not subject_strong_ref:
                logger.error(f"Could not get strong reference for post URI {post_uri} to report.")
                return False

            # The 'subject' for reporting a record is ComAtprotoRepoStrongRef.Main
            report_subject = models.ComAtprotoRepoStrongRef.Main(uri=subject_strong_ref.uri, cid=subject_strong_ref.cid)
            
            # For reporting an account, it would be ComAtprotoAdminDefs.RepoRef(did=...)

            await client.com.atproto.moderation.create_report(
                models.ComAtprotoModerationCreateReport.Input(
                    reasonType=reason_type, # e.g. lexicon_models.COM_ATPROTO_MODERATION_DEFS_REASONSPAM
                    reason=reason_text if reason_text else None,
                    subject=report_subject 
                )
            )
            logger.info(f"Successfully reported post {post_uri} for reason {reason_type}.")
            return True
        except AtProtocolError as e:
            logger.error(f"Error reporting post {post_uri}: {e.error} - {e.message}", exc_info=True)
        except Exception as e:
            logger.error(f"Unexpected error reporting post {post_uri}: {e}", exc_info=True)
        return False


    def is_mention_of_me(self, post_data: models.AppBskyFeedPost.Main | dict) -> bool:
        """
        Checks if a post record (not post view) mentions the authenticated user.
        This requires parsing facets from the post's record.
        `post_data` should be the `record` field of a `PostView` or a `FeedViewPost`.
        """
        my_did = self.get_own_did()
        if not my_did:
            return False
        
        facets_to_check = None
        if isinstance(post_data, models.AppBskyFeedPost.Main):
            facets_to_check = post_data.facets
        elif isinstance(post_data, dict) and 'facets' in post_data: # If raw dict from JSON
            # Need to parse dict facets into SDK models or handle dict structure
            # This simplified check assumes facets are already models.AppBskyRichtextFacet.Main objects
            # For robustness, parse dict to models.AppBskyRichtextFacet.Main if necessary.
            facets_to_check = post_data['facets']


        if not facets_to_check:
            return False
        
        for facet_item_model in facets_to_check:
            # Ensure facet_item_model is the correct SDK model type if it came from dict
            if isinstance(facet_item_model, models.AppBskyRichtextFacet.Main):
                for feature in facet_item_model.features:
                    if isinstance(feature, models.AppBskyRichtextFacet.Mention) and feature.did == my_did:
                        return True
            # Add handling for dict-based facet items if not pre-parsed
            elif isinstance(facet_item_model, dict) and 'features' in facet_item_model:
                 for feature_dict in facet_item_model['features']:
                     if isinstance(feature_dict, dict) and feature_dict.get('$type') == ids.AppBskyRichtextFacetMention and feature_dict.get('did') == my_did:
                         return True
        return False

    # Add more utility functions as needed, e.g., for specific API calls, data transformations, etc.
