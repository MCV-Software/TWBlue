# -*- coding: utf-8 -*-
import wx
import asyncio
import logging
from pubsub import pub

from approve.translation import translate as _
from approve.notifications import NotificationError
from multiplatform_widgets import widgets # Assuming this provides a generic list control

logger = logging.getLogger(__name__)

# Attempt to import a base panel if available, otherwise wx.Panel
try:
    from ..mastodon.base import basePanel as BaseTimelinePanel # If a suitable base exists
except ImportError:
    logger.warning("Mastodon basePanel not found, using wx.Panel as base for ATProtoSocial panels.")
    class BaseTimelinePanel(wx.Panel): # Minimal fallback
        def __init__(self, parent, name=""):
            super().__init__(parent, name=name)
            # Derived classes should create self.list (widgets.list)
            self.list = None # Must be initialized by subclass
            self.session = None # Must be set by subclass or via a method
            self.account = "" # Must be set
            self.name = name # Buffer name/type
            self.viewer_states = {} # For like/repost URIs

        def get_selected_item_id(self):
            if self.list and self.list.get_selected_count() > 0:
                idx = self.list.get_selected()
                # Assuming item data (URI) is stored using SetItemData or similar
                # This needs to be robust based on how items are actually added.
                # For now, let's assume we might store URI in a parallel list or directly.
            # This was a placeholder. Correct implementation relies on GetItemData if SetItemData was used.
            # If item_uris list is maintained parallel to the list control items:
            # if hasattr(self, "item_uris") and self.item_uris and idx < len(self.item_uris):
            #    return self.item_uris[idx]
            # However, using GetItemData is generally cleaner if URIs are stored there.
            # This method is overridden in ATProtoSocialUserTimelinePanel to use GetItemData.
            pass # Base implementation might not be suitable if not overridden.
            return None

        def get_selected_item_author_details(self):
        """Retrieves author details for the selected item from the message cache."""
        selected_item_uri = self.get_selected_item_id() # Relies on overridden get_selected_item_id
        if selected_item_uri and self.session and hasattr(self.session, "message_cache"):
            item_data = self.session.message_cache.get(selected_item_uri)
            #     if item_data and isinstance(item_data, dict):
                author_dict = item_data.get("author")
                if isinstance(author_dict, dict):
                    return author_dict
        logger.debug(f"BaseTimelinePanel: Could not get author details for {selected_item_uri}. Cache entry: {self.session.message_cache.get(selected_item_uri) if self.session and hasattr(self.session, 'message_cache') else 'N/A'}")
            return None

        def get_selected_item_summary_for_quote(self):
        """Generates a summary string for quoting the selected post."""
        selected_item_uri = self.get_selected_item_id()
        if selected_item_uri and self.session and hasattr(self.session, "message_cache"):
            item_data = self.session.message_cache.get(selected_item_uri)
            if item_data and isinstance(item_data, dict):
                record = item_data.get("record") # This is the Main post record dict/object
                author_info = item_data.get("author", {})

                author_handle = author_info.get("handle", "user")
                text_content = getattr(record, 'text', '') if not isinstance(record, dict) else record.get('text', '')
                text_snippet = (text_content[:70] + "...") if len(text_content) > 73 else text_content
                # Try to get web URL for context as well
                web_url = self.get_selected_item_web_url() or selected_item_uri
                return f"QT @{author_handle}: \"{text_snippet}\"\n({web_url})"
        return _("Quoting post...") # Fallback

        def get_selected_item_web_url(self):
        # This method should be overridden by specific panel types (like ATProtoSocialUserTimelinePanel)
        # as URL structure is platform-dependent.
        item_uri = self.get_selected_item_id()
        if item_uri:
            return f"Web URL for: {item_uri}" # Generic placeholder
            return ""

        def store_item_viewer_state(self, item_uri: str, key: str, value: Any):
            if item_uri not in self.viewer_states:
                self.viewer_states[item_uri] = {}
            self.viewer_states[item_uri][key] = value

        def get_item_viewer_state(self, item_uri: str, key: str) -> Any | None:
            return self.viewer_states.get(item_uri, {}).get(key)

        def set_focus_in_list(self):
            if self.list:
                self.list.list.SetFocus()


class ATProtoSocialUserTimelinePanel(BaseTimelinePanel):
    def __init__(self, parent, name: str, session, target_user_did: str, target_user_handle: str):
        super().__init__(parent, name=name)
        self.session = session
        self.account = session.label # Or session.uid / session.get_name()
        self.target_user_did = target_user_did
        self.target_user_handle = target_user_handle
        self.type = "user_timeline" # Buffer type identifier

        self.item_uris = [] # To store AT URIs of posts, parallel to list items
        self.cursor = None      # For pagination to load older posts
        self.newest_item_timestamp = None # For fetching newer posts (not directly used by Bluesky cursor pagination for "new")

        self._setup_ui()

        # Initial load is now typically triggered by mainController after buffer creation
        # wx.CallAfter(asyncio.create_task, self.load_initial_posts())


    def _setup_ui(self):
        self.list = widgets.list(self, _("Author"), _("Post Content"), _("Date"), style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_VIRTUAL)
        # Set column widths as appropriate
        self.list.set_windows_size(0, 120)  # Author
        self.list.set_windows_size(1, 350)  # Post Content (main part)
        self.list.set_windows_size(2, 150)  # Date
        self.list.set_size()

        # Bind list events if needed (e.g., item selection, activation)
        # self.list.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_item_activated)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.list.list, 1, wx.EXPAND | wx.ALL, 0) # List takes most space
        self.SetSizer(sizer)
        self.Layout()

    async def load_initial_posts(self, limit: int = 20):
        """Loads the initial set of posts for the user's timeline."""
        logger.info(f"ATProtoSocialUserTimelinePanel: Loading initial posts for {self.target_user_handle} ({self.target_user_did})")
        if not self.session or not self.session.is_ready():
            logger.warning("Session not ready, cannot load posts.")
            # Optionally display a message in the panel
            return
        try:
            # filter_type="posts_no_replies" or "posts_with_replies" or "posts_and_author_threads"
            # "posts_and_author_threads" is good for profile view to see everything
            fetched_data = await self.session.fetch_user_timeline(
                user_did=self.target_user_did,
                limit=limit,
                new_only=True, # To get newest first
                filter_type="posts_and_author_threads"
            )
            # fetch_user_timeline returns (processed_ids, next_cursor)
            # The processed_ids are already in message_cache.
            # We need to update the list control.
            if fetched_data:
                post_uris, self.cursor = fetched_data
                self.item_uris = post_uris # Store URIs for get_selected_item_id
                self.update_list_ctrl()
            else:
                self.list.list.DeleteAllItems() # Clear if no data
                self.list.list.InsertItem(0, _("No posts found."))

        except NotificationError as e:
            logger.error(f"NotificationError loading posts for {self.target_user_handle}: {e.message}")
            self.list.list.InsertItem(0, _("Error: ") + e.message)
        except Exception as e:
            logger.error(f"Error loading posts for {self.target_user_handle}: {e}", exc_info=True)
            self.list.list.InsertItem(0, _("An unexpected error occurred loading posts."))


    async def load_more_posts(self, limit: int = 20):
        """Loads older posts for the user's timeline using the current cursor."""
        logger.info(f"ATProtoSocialUserTimelinePanel: Loading more posts for {self.target_user_handle}, cursor: {self.cursor}")
        if not self.session or not self.session.is_ready() or not self.cursor:
            logger.warning(f"Session not ready or no cursor, cannot load more posts. Cursor: {self.cursor}")
            if not self.cursor:
                 self.list.list.InsertItem(self.list.list.GetItemCount(), _("No more posts to load."))
            return
        try:
            fetched_data = await self.session.fetch_user_timeline(
                user_did=self.target_user_did,
                limit=limit,
                cursor=self.cursor,
                new_only=False, # Fetching older items
                filter_type="posts_and_author_threads"
            )
            if fetched_data:
                new_post_uris, self.cursor = fetched_data
                if new_post_uris:
                    self.item_uris.extend(new_post_uris) # Add to existing URIs
                    self.update_list_ctrl(append=True) # Append new items
                else:
                    self.list.list.InsertItem(self.list.list.GetItemCount(), _("No more posts found."))
                    self.cursor = None # No more items to load
            else:
                self.list.list.InsertItem(self.list.list.GetItemCount(), _("Failed to load more posts or no more posts."))
                self.cursor = None # Stop further attempts if API returns no data structure

        except NotificationError as e:
            logger.error(f"NotificationError loading more posts for {self.target_user_handle}: {e.message}")
            self.list.list.InsertItem(self.list.list.GetItemCount(), _("Error: ") + e.message)
        except Exception as e:
            logger.error(f"Error loading more posts for {self.target_user_handle}: {e}", exc_info=True)
            self.list.list.InsertItem(self.list.list.GetItemCount(), _("An unexpected error occurred."))


    def update_list_ctrl(self, append: bool = False):
        """Populates or updates the list control with cached post data."""
        if not append:
            self.list.list.DeleteAllItems()
            current_uris_to_display = self.item_uris
        else: # Appending, so only add new URIs
            # This assumes self.item_uris has already been extended with new URIs
            # And we need to find which ones are truly new to the list control items
            # A simpler append strategy is just to add all from the new batch.
            # For now, if append is true, this method isn't directly called with new_only=True logic from session.
            # This method is mostly for full refresh or initial population.
            # The `order_buffer` in session.py handles adding to `self.item_uris`.
            # This method should just render what's in self.item_uris.
            # Let's simplify: this method always redraws based on self.item_uris.
            # If appending, the caller (load_more_posts) should have extended self.item_uris.
             pass # No, if appending, we add items, don't delete all. This logic needs care.

        if not append:
             self.list.list.DeleteAllItems()

        start_index = 0
        if append:
            start_index = self.list.list.GetItemCount() # Add after existing items

        for i, post_uri in enumerate(self.item_uris[start_index:] if append else self.item_uris):
            post_data = self.session.message_cache.get(post_uri)
            if post_data and isinstance(post_data, dict):
                display_string = self.session.compose_panel.compose_post_for_display(post_data)
                # Split display string for columns (simplified)
                lines = display_string.split('\n', 2)
                author_line = lines[0]
                content_line = lines[1] if len(lines) > 1 else ""
                # Date is part of author_line, this is a simplification.
                # A proper list control might need custom rendering or more structured data.

                # For a virtual list, we'd use self.list.list.SetItemCount(len(self.item_uris))
                # and implement OnGetItemText. For now, direct insertion:
                actual_index = start_index + i
                self.list.list.InsertItem(actual_index, author_line) # Column 0: Author + Timestamp
                self.list.list.SetItem(actual_index, 1, content_line) # Column 1: Main content
                self.list.list.SetItem(actual_index, 2, "") # Column 2: Date (already in header)
                self.list.list.SetItemData(actual_index, post_uri) # Store URI for retrieval
            else:
                logger.warning(f"Post data for URI {post_uri} not found in cache or invalid format.")
                self.list.list.InsertItem(start_index + i, post_uri)
                self.list.list.SetItem(start_index + i, 1, _("Error: Post data missing."))

        if not self.item_uris and not append:
            self.list.list.InsertItem(0, _("No posts to display."))

    # --- Item Interaction Methods ---
    # These are now part of BaseTimelinePanel and inherited
    # get_selected_item_id() -> Returns item URI from self.item_uris
    # get_selected_item_author_details() -> Returns author dict from message_cache
    # get_selected_item_summary_for_quote() -> Returns "QT @author: snippet..." from message_cache
    # get_selected_item_web_url() -> Constructs bsky.app URL for the post
    # store_item_viewer_state(item_uri, key, value) -> Stores in self.viewer_states
    # get_item_viewer_state(item_uri, key) -> Retrieves from self.viewer_states

    # Overriding from BaseTimelinePanel to use SetItemData for URI storage directly
    def get_selected_item_id(self):
        if self.list and self.list.get_selected_count() > 0:
            idx = self.list.get_selected()
            return self.list.list.GetItemData(idx) # Assumes URI was stored with SetItemData
        return None

    def get_selected_item_web_url(self):
        item_uri = self.get_selected_item_id()
        if item_uri and self.session:
            # Attempt to get handle from cached author data if available, otherwise use DID from URI
            post_data = self.session.message_cache.get(item_uri)
            author_handle_or_did = item_uri.split('/')[2] # Extract DID from at://<did>/...
            if post_data and isinstance(post_data, dict):
                author_info = post_data.get("author")
                if author_info and isinstance(author_info, dict) and author_info.get("handle"):
                    author_handle_or_did = author_info.get("handle")

            rkey = item_uri.split('/')[-1]
            return f"https://bsky.app/profile/{author_handle_or_did}/post/{rkey}"
        return ""


class ATProtoSocialHomeTimelinePanel(ATProtoSocialUserTimelinePanel):
    def __init__(self, parent, name: str, session):
        super().__init__(parent, name, session,
                         target_user_did=session.util.get_own_did() or "N/A",
                         target_user_handle=session.util.get_own_username() or "N/A")
        self.type = "home_timeline"

    async def load_initial_posts(self, limit: int = 20):
        """Loads the initial set of posts for the home timeline."""
        logger.info(f"ATProtoSocialHomeTimelinePanel: Loading initial posts for home timeline for {self.session.label}")
        if not self.session or not self.session.is_ready():
            logger.warning("Session not ready for home timeline.")
            return
        try:
            # The session's fetch_home_timeline updates self.session.home_timeline_buffer and self.session.home_timeline_cursor
            # It returns (processed_ids, next_cursor)
            processed_ids, _ = await self.session.fetch_home_timeline(limit=limit, new_only=True)

            if processed_ids:
                self.item_uris = list(self.session.home_timeline_buffer) # Reflect the session buffer
                self.update_list_ctrl()
            else:
                self.list.list.DeleteAllItems()
                self.list.list.InsertItem(0, _("Home timeline is empty or failed to load."))
        except Exception as e:
            logger.error(f"Error loading home timeline: {e}", exc_info=True)
            if self.list.list: self.list.list.InsertItem(0, _("Error loading home timeline."))

    async def load_more_posts(self, limit: int = 20):
        """Loads older posts for the home timeline using the session's cursor."""
        logger.info(f"ATProtoSocialHomeTimelinePanel: Loading more posts, cursor: {self.session.home_timeline_cursor}")
        if not self.session or not self.session.is_ready():
            logger.warning("Session not ready, cannot load more posts for home timeline.")
            return
        if not self.session.home_timeline_cursor:
            if self.list.list: self.list.list.InsertItem(self.list.list.GetItemCount(), _("No more posts."))
            return

        try:
            new_post_uris, _ = await self.session.fetch_home_timeline(
                cursor=self.session.home_timeline_cursor,
                limit=limit,
                new_only=False
            )
            if new_post_uris:
                # self.item_uris is now just a reflection of session.home_timeline_buffer
                self.item_uris = list(self.session.home_timeline_buffer)
                self.update_list_ctrl() # Redraw the list with the full buffer
            else:
                if self.list.list: self.list.list.InsertItem(self.list.list.GetItemCount(), _("No more posts found."))
                self.session.home_timeline_cursor = None
        except Exception as e:
            logger.error(f"Error loading more for home timeline: {e}", exc_info=True)
            if self.list.list: self.list.list.InsertItem(self.list.list.GetItemCount(), _("Error loading more posts."))


class ATProtoSocialNotificationPanel(BaseTimelinePanel):
    def __init__(self, parent, name: str, session):
        super().__init__(parent, name=name)
        self.session = session
        self.account = session.label
        self.type = "notifications"
        self.item_uris = [] # Stores notification URIs or unique IDs
        self.cursor = None
        self._setup_ui()
        # Initial load handled by session.fetch_notifications -> send_notification_to_channel
        # This panel should listen to pubsub or have a method to add notifications.
        # For now, it's a static list that needs manual refresh.
        pub.subscribe(self.on_new_notification_processed, f"approve.notification_processed.{self.session.uid}")


    def _setup_ui(self):
        # Simplified list for notifications: Author, Action, Snippet/Link, Date
        self.list = widgets.list(self, _("Author"), _("Action"), _("Details"), _("Date"), style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_VIRTUAL)
        self.list.set_windows_size(0, 100)
        self.list.set_windows_size(1, 250)
        self.list.set_windows_size(2, 150)
        self.list.set_windows_size(3, 120)
        self.list.set_size()
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.list.list, 1, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(sizer)
        self.Layout()
        wx.CallAfter(asyncio.create_task, self.load_initial_notifications())


    async def load_initial_notifications(self, limit: int = 30):
        logger.info(f"ATProtoSocialNotificationPanel: Loading initial notifications for {self.session.label}")
        if not self.session or not self.session.is_ready(): return
        try:
            # fetch_notifications in session.py handles sending to channel, not directly populating a list here.
            # This panel needs to be populated by notifications received by send_notification_to_channel.
            # For a poll-based refresh:
            self.cursor = await self.session.fetch_notifications(limit=limit, cursor=None) # Returns next cursor
            # The actual display items are added via pubsub from session's notification handlers
            # So, this load_initial_notifications mainly serves to trigger the fetch.
            # The list will be populated by on_new_notification_processed.
            # If no items appear, it means they were all read or no new ones.
            if not self.list.list.GetItemCount():
                 # If fetch_notifications itself doesn't add to list (only via pubsub),
                 # and no pubsub messages came through for unread items, this will be shown.
                 # If fetch_notifications is expected to return items directly for initial load,
                 # this logic would be different. For now, assuming pubsub populates.
                 self.list.list.InsertItem(0, _("No new unread notifications found or failed to load initial set."))
            elif self.list.list.GetItemText(0).startswith(_("No new unread notifications")): # If only placeholder is there
                pass # Keep placeholder until real notif comes via pubsub

        except Exception as e:
            logger.error(f"Error in NotificationPanel load_initial_notifications/refresh: {e}", exc_info=True)
            if self.list.list and self.list.list.GetItemCount() == 0:
                self.list.list.InsertItem(0, _("Error loading notifications."))

    async def load_more_notifications(self, limit: int = 20):
        """Fetches older notifications using the current cursor."""
        logger.info(f"ATProtoSocialNotificationPanel: Loading more notifications for {self.session.label}, cursor: {self.cursor}")
        if not self.session or not self.session.is_ready():
            logger.warning("Session not ready, cannot load more notifications.")
            return
        if not self.cursor:
            logger.info("No older notifications cursor available.")
            if self.list.list: self.list.list.InsertItem(self.list.list.GetItemCount(), _("No more older notifications."))
            return

        try:
            # This fetch will send items via pubsub if they are "new" in the context of this fetch.
            # The panel's on_new_notification_processed will then add them.
            # We need to ensure that fetch_notifications correctly handles pagination for older items.
            # The session's fetch_notifications should ideally return the list of processed items too for direct handling here.
            # For now, we rely on it sending via pubsub and updating self.cursor.

            # Make 'fetch_notifications' return the items directly for "load more" scenarios
            # to avoid complex pubsub interaction for prepending vs appending.
            # This requires a change in session.fetch_notifications or a new method.
            # Let's assume session.fetch_notifications can be used for this for now and it returns items.

            # Conceptual: if session.fetch_notifications returned items directly:
            # items, next_cursor = await self.session.fetch_notifications(cursor=self.cursor, limit=limit, fetch_mode="older")
            # if items:
            #    for notif_obj in reversed(items): # If fetch_notifications returns newest first from the page
            #        self._add_notification_to_list(notif_obj, prepend=False) # Append older items
            #    self.cursor = next_cursor
            # else:
            #    self.list.list.InsertItem(self.list.list.GetItemCount(), _("No more older notifications found."))
            #    self.cursor = None

            # Current session.fetch_notifications sends via pubsub. This is not ideal for "load more".
            # For now, "load more" on notifications will just re-trigger a general refresh.
            # A proper "load older" requires session.fetch_notifications to support fetching older pages
            # and this panel to append them.
            output.speak(_("Refreshing recent notifications. True 'load older' for notifications is not yet fully implemented."), True)
            await self.refresh_notifications(limit=limit)


        except Exception as e:
            logger.error(f"Error loading more notifications: {e}", exc_info=True)
            if self.list.list: self.list.list.InsertItem(self.list.list.GetItemCount(), _("Error loading more notifications."))


    def on_new_notification_processed(self, notification_obj: Any):
        """Handles new notification object from pubsub, adds to list control."""
        # This needs to be called via wx.CallAfter if pubsub is from another thread
        # For now, assuming it's called on main thread or handled by pubsub config.

        # Convert Notification object to a dictionary suitable for compose_notification_for_display
        # This assumes notification_obj is an instance of approve.notifications.Notification
        notif_dict_for_display = {
            "title": notification_obj.title,
            "body": notification_obj.body,
            "author_name": notification_obj.author_name,
            "timestamp_dt": datetime.fromtimestamp(notification_obj.timestamp) if notification_obj.timestamp else None,
            "kind": notification_obj.kind.value # Pass the string value of the enum
            # Add any other fields that compose_notification_for_display might use
        }

        display_string = self.session.compose_panel.compose_notification_for_display(notif_dict_for_display)

        # For a simple list, we might just display the string.
        # If the list has columns, we need to parse `display_string` or have `compose_notification_for_display` return parts.
        # For now, let's assume a single main column for the formatted string, and author for the first.
        # This panel's list setup: _("Author"), _("Action"), _("Details"), _("Date")

        author_display = notification_obj.author_name or _("System")
        # The `display_string` from `compose_notification_for_display` usually has timestamp and title.
        # We need to adapt how this is split into columns or simplify the columns.
        # Let's try putting the main part of the composed string in "Action" and snippet in "Details".

        parts = display_string.split('\n', 1) # Split by first newline if any
        main_action_line = parts[0]
        details_line = parts[1] if len(parts) > 1 else (notification_obj.body or "")

        timestamp_str = ""
        if notification_obj.timestamp:
             timestamp_str = datetime.fromtimestamp(notification_obj.timestamp).strftime("%I:%M %p %b %d")


        # Prepend to list
        # Columns: Author, Action (title from compose), Details (body snippet from compose), Date
        idx = self.list.list.InsertItem(0, author_display)
        self.list.list.SetItem(idx, 1, main_action_line)
        self.list.list.SetItem(idx, 2, (details_line[:75] + "...") if len(details_line) > 78 else details_line)
        self.list.list.SetItem(idx, 3, timestamp_str) # Date string from notification object

        # Store a unique ID for the notification if available (e.g., its URI or a generated one)
        # This helps if we need to interact with it (e.g., mark as read, navigate to source)
        unique_id = notification_obj.message_id or notification_obj.url or str(notification_obj.timestamp) # Fallback ID
        self.list.list.SetItemData(idx, unique_id)

        if self.list.list.GetItemCount() > 0:
            # Remove placeholder "No unread notifications..." if it exists and isn't the item we just added
            # This check needs to be more robust if the placeholder is generic.
            first_item_text = self.list.list.GetItemText(0) if self.list.list.GetItemCount() == 1 else self.list.list.GetItemText(1) # Check previous first item if count > 1
            if first_item_text.startswith(_("No unread notifications")) and self.list.list.GetItemCount() > 1:
                 # Find and delete the placeholder; it's safer to check by a specific marker or ensure it's always at index 0 when list is empty
                 for i in range(self.list.list.GetItemCount()):
                     if self.list.list.GetItemText(i).startswith(_("No unread notifications")):
                         self.list.list.DeleteItem(i)
                         break
            elif self.list.list.GetItemText(0).startswith(_("No unread notifications")) and self.list.list.GetItemCount() == 1 and unique_id != self.list.list.GetItemData(0):
                 # This case can happen if the placeholder was the only item, and we added a new one.
                 # However, the InsertItem(0,...) already shifted it. This logic is tricky.
                 # A better way: if list was empty and had placeholder, clear it BEFORE inserting new.
                 pass


    def UnbindPubSub(self): # Call this on panel close
        if hasattr(self, 'session') and self.session: # Ensure session exists before trying to get uid
            pub.unsubscribe(self.on_new_notification_processed, f"approve.notification_processed.{self.session.uid}")
        super().Destroy()

    def get_selected_item_id(self): # Returns Notification URI or URL stored with item
        if self.list and self.list.get_selected_count() > 0:
            idx = self.list.get_selected()
            return self.list.list.GetItemData(idx)
        return None

    def get_selected_item_web_url(self): # Attempt to return a web URL if stored, or construct one
        item_identifier = self.get_selected_item_id() # This might be a post URI, like URI, or follow URI
        if item_identifier and item_identifier.startswith("at://"):
            # This is a generic AT URI, try to make a bsky.app link if it's a post.
            # More specific handling might be needed depending on what ID is stored.
            try:
                # Example: at://did:plc:xyz/app.bsky.feed.post/3k අඩුk අඩුj අඩු
                parts = item_identifier.replace("at://", "").split("/")
                if len(parts) == 3 and parts[1] == "app.bsky.feed.post":
                    did_or_handle = parts[0]
                    rkey = parts[2]
                    # Try to resolve DID to handle for a nicer URL if possible (complex here)
                    return f"https://bsky.app/profile/{did_or_handle}/post/{rkey}"
                elif len(parts) == 3 and parts[1] == "app.bsky.actor.profile": # Link to profile
                    did_or_handle = parts[0]
                    return f"https://bsky.app/profile/{did_or_handle}"
            except Exception as e:
                logger.debug(f"Could not parse AT URI {item_identifier} for web URL: {e}")
        elif item_identifier and item_identifier.startswith("http"): # Already a web URL
            return item_identifier
        return item_identifier # Fallback to returning the ID itself


class ATProtoSocialUserListPanel(BaseTimelinePanel):
    def __init__(self, parent, name: str, session, list_type: str, target_user_did: str, target_user_handle: str | None = None):
        super().__init__(parent, name=name)
        self.session = session
        self.account = session.label
        self.list_type = list_type
        self.target_user_did = target_user_did
        self.target_user_handle = target_user_handle or target_user_did
        self.type = f"user_list_{list_type}"

        self.user_list_data = []
        self.cursor = None

        self._setup_ui()
        wx.CallAfter(asyncio.create_task, self.load_initial_users())

    def _setup_ui(self):
        self.list = widgets.list(self, _("Display Name"), _("Handle"), _("Bio"), style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_VIRTUAL)
        self.list.set_windows_size(0, 150)
        self.list.set_windows_size(1, 150)
        self.list.set_windows_size(2, 300)
        self.list.set_size()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.list.list, 1, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(sizer)
        self.Layout()

    async def load_initial_users(self, limit: int = 30):
        logger.info(f"ATProtoSocialUserListPanel: Loading initial users for {self.list_type} of {self.target_user_handle or self.target_user_did}")
        if not self.session or not self.session.is_ready():
            logger.warning(f"Session not ready, cannot load {self.list_type}.")
            return
        try:
            # Using the controller.userList function for paginated fetching directly
            # This requires access to mainController or passing it down.
            # For simplicity, let's assume a helper on session that calls the controller.userList function.
            # Or, we can make this panel call a new session method that wraps this.
            # For now, let's assume session has a method like `get_paginated_user_list`.
            # This method needs to exist on the session:
            # async def get_paginated_user_list(self, list_type, identifier, limit, cursor) -> tuple[list, str|None]:
            #    from controller.atprotosocial import userList as atpUserListCtrl # Keep import local
            #    return await atpUserListCtrl.get_user_list_paginated(self, list_type, identifier, limit, cursor)

            # Always call the session method now
            users, self.cursor = await self.session.get_paginated_user_list(
                list_type=self.list_type,
                identifier=self.target_user_did,
                limit=limit,
                cursor=None
            )

            if users:
                self.user_list_data = users
                self.update_list_ctrl()
            else:
                self.list.list.DeleteAllItems()
                self.list.list.InsertItem(0, _("No users found in this list."))

        except Exception as e:
            logger.error(f"Error loading {self.list_type} for {self.target_user_handle}: {e}", exc_info=True)
            self.list.list.InsertItem(0, _("Error loading user list."))


    async def load_more_users(self, limit: int = 30):
        logger.info(f"ATProtoSocialUserListPanel: Loading more users for {self.list_type} of {self.target_user_handle or self.target_user_did}, cursor: {self.cursor}")
        if not self.session or not self.session.is_ready():
            logger.warning(f"Session not ready, cannot load more {self.list_type}.")
            return
        if not self.cursor: # No cursor means no more pages or initial load failed to get one
            logger.info(f"No cursor available for {self.list_type} of {self.target_user_handle or self.target_user_did}, assuming no more items.")
            # self.list.list.InsertItem(self.list.list.GetItemCount(), _("No more users to load.")) # Avoid duplicate messages if already shown
            return

        try:
            new_users, next_cursor = await self.session.get_paginated_user_list(
                list_type=self.list_type,
                identifier=self.target_user_did,
                limit=limit,
                cursor=self.cursor
            )

            self.cursor = next_cursor # Update cursor regardless of whether new_users were found

            if new_users:
                self.user_list_data.extend(new_users)
                self.update_list_ctrl(append=True)
                logger.info(f"Loaded {len(new_users)} more users for {self.list_type} of {self.target_user_handle or self.target_user_did}.")
            else:
                logger.info(f"No more users found for {self.list_type} of {self.target_user_handle or self.target_user_did} with cursor {self.cursor}.")
                # self.list.list.InsertItem(self.list.list.GetItemCount(), _("No more users found.")) # Message can be optional
        except NotificationError as e: # Catch errors from session.get_paginated_user_list
            logger.error(f"NotificationError loading more {self.list_type} for {self.target_user_handle}: {e.message}", exc_info=True)
            if self.list.list: self.list.list.InsertItem(self.list.list.GetItemCount(), _("Error: ") + e.message)
        except Exception as e:
            logger.error(f"Error loading more {self.list_type} for {self.target_user_handle}: {e}", exc_info=True)
            if self.list.list: self.list.list.InsertItem(self.list.list.GetItemCount(), _("An unexpected error occurred while loading more users."))

    def update_list_ctrl(self, append: bool = False):
        """Populates or updates the list control with user data."""
        if not append:
            self.list.list.DeleteAllItems()

        start_index = 0
        if append:
            start_index = self.list.list.GetItemCount()
            items_to_add = self.user_list_data[start_index:]
        else:
            items_to_add = self.user_list_data

        for i, user_data in enumerate(items_to_add):
            if not isinstance(user_data, dict): continue # Should be formatted dicts

            display_name = user_data.get("displayName", "")
            handle = user_data.get("handle", "")
            description = user_data.get("description", "")

            actual_index = start_index + i
            self.list.list.InsertItem(actual_index, display_name)
            self.list.list.SetItem(actual_index, 1, f"@{handle}")
            self.list.list.SetItem(actual_index, 2, description.replace("\n", " ")) # Show bio on one line
            self.list.list.SetItemData(actual_index, user_data.get("did")) # Store DID for actions

        if not self.user_list_data and not append:
            self.list.list.InsertItem(0, _("This list is empty."))

    # Override item interaction methods if the data stored/retrieved needs different handling
    def get_selected_item_id(self): # Returns DID for users
        if self.list and self.list.get_selected_count() > 0:
            idx = self.list.get_selected()
            return self.list.list.GetItemData(idx) # DID was stored here
        return None

    def get_selected_item_author_details(self): # For a user list, the "author" is the user item itself
        selected_did = self.get_selected_item_id()
        if selected_did:
            # Find the user_data dict in self.user_list_data
            for user_data_item in self.user_list_data:
                if user_data_item.get("did") == selected_did:
                    return user_data_item # Return the whole dict, mainController.user_details can use it
        return None

    def get_selected_item_summary_for_quote(self): # Not applicable for a list of users
        return ""

    def get_selected_item_web_url(self): # Construct profile URL
        selected_did = self.get_selected_item_id()
        if selected_did:
            # Find handle from self.user_list_data
            for user_data_item in self.user_list_data:
                if user_data_item.get("did") == selected_did:
                    handle = user_data_item.get("handle")
                    if handle: return f"https://bsky.app/profile/{handle}"
            return f"https://bsky.app/profile/{selected_did}" # Fallback to DID
        return ""
