from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, AsyncGenerator

fromapprove.translation import translate as _
# fromapprove.controller.mastodon import userList as mastodon_user_list # If adapting

if TYPE_CHECKING:
    fromapprove.sessions.atprotosocial.session import Session as ATProtoSocialSession # Adjusted
    # Define a type for what a user entry in a list might look like for ATProtoSocial
    ATProtoSocialUserListItem = dict[str, Any] # e.g. {"did": "...", "handle": "...", "displayName": "..."}

logger = logging.getLogger(__name__)

# This file is responsible for fetching and managing lists of users from ATProtoSocial.
# Examples include:
# - Followers of a user
# - Users a user is following
# - Users who liked or reposted a post
# - Users in a specific list or feed (if ATProtoSocial supports user lists like Twitter/Mastodon)
# - Search results for users

# The structure will likely involve:
# - A base class or functions for paginating through user lists from the ATProtoSocial API.
# - Specific functions for each type of user list.
# - Formatting ATProtoSocial user data into a consistent structure for UI display.

async def fetch_followers(
    session: ATProtoSocialSession,
    user_id: str, # DID of the user whose followers to fetch
    limit: int = 20,
    cursor: str | None = None
) -> AsyncGenerator[ATProtoSocialUserListItem, None]:
    """
    Asynchronously fetches a list of followers for a given ATProtoSocial user.
    user_id is the DID of the target user.
    Yields user data dictionaries.
    """
    # client = await session.util._get_client() # Get authenticated client
    # if not client:
    #     logger.warning(f"ATProtoSocial client not available for fetching followers of {user_id}.")
    #     return

    # current_cursor = cursor
    # try:
    #     while True:
    #         # response = await client.app.bsky.graph.get_followers(
    #         #     models.AppBskyGraphGetFollowers.Params(
    #         #         actor=user_id,
    #         #         limit=min(limit, 100), # ATProto API might have its own max limit per request (e.g. 100)
    #         #         cursor=current_cursor
    #         #     )
    #         # )
    #         # if not response or not response.followers:
    #         #     break
            
    #         # for user_profile_view in response.followers:
    #         #     yield session.util._format_profile_data(user_profile_view) # Use a utility to standardize format

    #         # current_cursor = response.cursor
    #         # if not current_cursor or len(response.followers) < limit : # Or however the API indicates end of list
    #         #     break
            
    #         # This is a placeholder loop for demonstration
    #         if current_cursor == "simulated_end_cursor": break # Stop after one simulated page
    #         for i in range(limit):
    #             if current_cursor and int(current_cursor) + i >= 25: # Simulate total 25 followers
    #                 current_cursor = "simulated_end_cursor"
    #                 break
    #             yield {
    #                 "did": f"did:plc:follower{i + (int(current_cursor) if current_cursor else 0)}",
    #                 "handle": f"follower{i + (int(current_cursor) if current_cursor else 0)}.bsky.social",
    #                 "displayName": f"Follower {i + (int(current_cursor) if current_cursor else 0)}",
    #                 "avatar": None # Placeholder
    #             }
    #         if not current_cursor: current_cursor = str(limit) # Simulate next cursor
    #         elif current_cursor != "simulated_end_cursor": current_cursor = str(int(current_cursor) + limit)


    """
    if not session.is_ready():
        logger.warning(f"Cannot fetch followers for {user_id}: ATProtoSocial session not ready.")
        # yield {} # Stop iteration if not ready
        return
        
    try:
        followers_data = await session.util.get_followers(user_did=user_id, limit=limit, cursor=cursor)
        if followers_data:
            users, _ = followers_data # We'll return the cursor separately via the calling HTTP handler
            for user_profile_view in users:
                yield session.util._format_profile_data(user_profile_view)
        else:
            logger.info(f"No followers data returned for user {user_id}.")
            
    except Exception as e:
        logger.error(f"Error in fetch_followers for ATProtoSocial user {user_id}: {e}", exc_info=True)
        # Depending on desired error handling, could raise or yield an error marker


async def fetch_following(
    session: ATProtoSocialSession,
    user_id: str, # DID of the user whose followed accounts to fetch
    limit: int = 20,
    cursor: str | None = None
) -> AsyncGenerator[ATProtoSocialUserListItem, None]:
    """
    Asynchronously fetches a list of users followed by a given ATProtoSocial user.
    Yields user data dictionaries.
    """
    if not session.is_ready():
        logger.warning(f"Cannot fetch following for {user_id}: ATProtoSocial session not ready.")
        return

    try:
        following_data = await session.util.get_following(user_did=user_id, limit=limit, cursor=cursor)
        if following_data:
            users, _ = following_data
            for user_profile_view in users:
                yield session.util._format_profile_data(user_profile_view)
        else:
            logger.info(f"No following data returned for user {user_id}.")
            
    except Exception as e:
        logger.error(f"Error in fetch_following for ATProtoSocial user {user_id}: {e}", exc_info=True)


async def search_users(
    session: ATProtoSocialSession,
    query: str,
    limit: int = 20,
    cursor: str | None = None 
) -> AsyncGenerator[ATProtoSocialUserListItem, None]:
    """
    Searches for users on ATProtoSocial based on a query string.
    Yields user data dictionaries.
    """
    if not session.is_ready():
        logger.warning(f"Cannot search users for '{query}': ATProtoSocial session not ready.")
        return

    try:
        search_data = await session.util.search_users(term=query, limit=limit, cursor=cursor)
        if search_data:
            users, _ = search_data
            for user_profile_view in users:
                yield session.util._format_profile_data(user_profile_view)
        else:
            logger.info(f"No users found for search term '{query}'.")
            
    except Exception as e:
        logger.error(f"Error in search_users for ATProtoSocial query '{query}': {e}", exc_info=True)

# This function is designed to be called by an API endpoint that returns JSON
async def get_user_list_paginated(
    session: ATProtoSocialSession,
    list_type: str, # "followers", "following", "search"
    identifier: str, # User DID for followers/following, or search query for search
    limit: int = 20,
    cursor: str | None = None
) -> tuple[list[ATProtoSocialUserListItem], str | None]:
    """
    Fetches a paginated list of users (followers, following, or search results)
    and returns the list and the next cursor.
    """
    users_list: list[ATProtoSocialUserListItem] = []
    next_cursor: str | None = None

    if not session.is_ready():
        logger.warning(f"Cannot fetch user list '{list_type}': ATProtoSocial session not ready.")
        return [], None

    try:
        if list_type == "followers":
            data = await session.util.get_followers(user_did=identifier, limit=limit, cursor=cursor)
            if data: users_list = [session.util._format_profile_data(u) for u in data[0]]; next_cursor = data[1]
        elif list_type == "following":
            data = await session.util.get_following(user_did=identifier, limit=limit, cursor=cursor)
            if data: users_list = [session.util._format_profile_data(u) for u in data[0]]; next_cursor = data[1]
        elif list_type == "search_users":
            data = await session.util.search_users(term=identifier, limit=limit, cursor=cursor)
            if data: users_list = [session.util._format_profile_data(u) for u in data[0]]; next_cursor = data[1]
        else:
            logger.error(f"Unknown list_type: {list_type}")
            return [], None
            
    except Exception as e:
        logger.error(f"Error fetching paginated user list '{list_type}' for '{identifier}': {e}", exc_info=True)
        # Optionally re-raise or return empty with no cursor to indicate error
        return [], None 
        
    return users_list, next_cursor


async def get_user_profile_details(session: ATProtoSocialSession, user_ident: str) -> ATProtoSocialUserListItem | None:
    """
    Fetches detailed profile information for a user by DID or handle.
    Returns a dictionary of formatted profile data, or None if not found/error.
    """
    if not session.is_ready():
        logger.warning(f"Cannot get profile for {user_ident}: ATProtoSocial session not ready.")
        return None
    
    try:
        profile_view_detailed = await session.util.get_user_profile(user_ident=user_ident)
        if profile_view_detailed:
            return session.util._format_profile_data(profile_view_detailed)
        else:
            logger.info(f"No profile data found for user {user_ident}.")
            return None
    except Exception as e:
        logger.error(f"Error in get_user_profile_details for {user_ident}: {e}", exc_info=True)
        return None


# Other list types could include:
# - fetch_likers(session, post_uri, limit, cursor) # Needs app.bsky.feed.getLikes
# - fetch_reposters(session, post_uri, limit, cursor)
# - fetch_muted_users(session, limit, cursor)
# - fetch_blocked_users(session, limit, cursor)

# The UI part of Approve that displays user lists would call these functions.
# Each function needs to handle pagination as provided by the ATProto API (usually cursor-based).

logger.info("ATProtoSocial userList module loaded (placeholders).")
