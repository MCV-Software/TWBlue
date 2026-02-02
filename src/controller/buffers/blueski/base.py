# -*- coding: utf-8 -*-
import logging
import wx
import arrow
import output
import sound
import config
import widgetUtils
import languageHandler
from pubsub import pub
from controller.buffers.base import base
from controller.blueski import messages as blueski_messages
from sessions.blueski import compose, utils, templates
from mysc.thread_utils import call_threaded
from wxUI.buffers.blueski import panels as BlueskiPanels
from wxUI import commonMessageDialogs
from wxUI.dialogs.blueski import menus

log = logging.getLogger("controller.buffers.blueski.base")

class BaseBuffer(base.Buffer):
    def __init__(self, parent=None, name=None, session=None, *args, **kwargs):
        # Adapt params to BaseBuffer
        # BaseBuffer expects (parent, function, name, sessionObject, account)
        function = "timeline" # Dummy
        sessionObject = session
        account = session.get_name() if session else "Unknown"
        
        super(BaseBuffer, self).__init__(parent, function, name=name, sessionObject=sessionObject, account=account, *args, **kwargs)
        
        self.session = sessionObject
        self.account = account
        self.name = name
        self.create_buffer(parent, name)
        self.buffer.account = account
        self.invisible = True
        compose_func = kwargs.get("compose_func", "compose_post")
        self.compose_function = getattr(compose, compose_func)
        self.sound = kwargs.get("sound", None)
        
        # Initialize DB list if needed
        if self.name not in self.session.db:
            self.session.db[self.name] = []

        self.bind_events()

    def get_max_items(self):
        """Get max items per call from settings."""
        return self.session.settings["general"]["max_posts_per_call"]

    def create_buffer(self, parent, name):
        # Default to HomePanel, can be overridden
        self.buffer = BlueskiPanels.HomePanel(parent, name, account=self.account)
        self.buffer.session = self.session

    def bind_events(self):
        # Bind essential events
        log.debug("Binding events for buffer %s" % self.name)
        self.buffer.set_focus_function(self.onFocus)
        widgetUtils.connect_event(self.buffer.list.list, widgetUtils.KEYPRESS, self.get_event)
        widgetUtils.connect_event(self.buffer.list.list, wx.EVT_LIST_ITEM_RIGHT_CLICK, self.show_menu)
        widgetUtils.connect_event(self.buffer.list.list, wx.EVT_LIST_KEY_DOWN, self.show_menu_by_key)

        # Buttons
        if hasattr(self.buffer, "post"):
             self.buffer.post.Bind(wx.EVT_BUTTON, self.on_post)
        if hasattr(self.buffer, "reply"):
             self.buffer.reply.Bind(wx.EVT_BUTTON, self.on_reply)
        if hasattr(self.buffer, "repost"):
             self.buffer.repost.Bind(wx.EVT_BUTTON, self.on_repost)
        if hasattr(self.buffer, "like"):
             self.buffer.like.Bind(wx.EVT_BUTTON, self.on_like)
        if hasattr(self.buffer, "dm"):
             self.buffer.dm.Bind(wx.EVT_BUTTON, self.on_dm)
        if hasattr(self.buffer, "actions"):
             self.buffer.actions.Bind(wx.EVT_BUTTON, self.user_actions)

    def get_buffer_name(self):
        """Get human-readable buffer name."""
        basic_buffers = dict(
            home_timeline=_("Home"),
            notifications=_("Notifications"),
            mentions=_("Mentions"),
            sent=_("Sent"),
            likes=_("Likes"),
            chats=_("Chats"),
        )
        if self.name in basic_buffers:
            return basic_buffers[self.name]
        if hasattr(self, "username"):
            if "timeline" in self.name.lower():
                return _("{username}'s timeline").format(username=self.username)
            if "followers" in self.name.lower():
                return _("{username}'s followers").format(username=self.username)
            if "following" in self.name.lower():
                return _("{username}'s following").format(username=self.username)
        return self.name

    def onFocus(self, *args, **kwargs):
        """Handle focus event for accessibility features."""
        post = self.get_item()
        if not post:
            return

        # Update relative time display
        if self.session.settings["general"].get("relative_times", False):
            try:
                index = self.buffer.list.get_selected()
                if index < 0:
                    return

                def g(obj, key, default=None):
                    if isinstance(obj, dict):
                        return obj.get(key, default)
                    return getattr(obj, key, default)

                actual_post = g(post, "post", post)
                indexed_at = g(actual_post, "indexed_at", "") or g(actual_post, "indexedAt", "")
                if indexed_at:
                    original_date = arrow.get(indexed_at)
                    ts = original_date.humanize(locale=languageHandler.curLang[:2])
                    self.buffer.list.list.SetItem(index, 2, ts)
            except Exception as e:
                log.error("Error updating relative time on focus: %s", e)

        # Read long posts in GUI
        if config.app["app-settings"].get("read_long_posts_in_gui", False) and self.buffer.list.list.HasFocus():
            wx.CallLater(40, output.speak, self.get_message(), interrupt=True)

        # Audio/video indicator sound
        if self.session.settings["sound"].get("indicate_audio", False) and utils.is_audio_or_video(post):
            self.session.sound.play("audio.ogg")

        # Image indicator sound
        if self.session.settings["sound"].get("indicate_img", False) and utils.is_image(post):
            self.session.sound.play("image.ogg")

    def auto_read(self, number_of_items):
        """Automatically read new items for accessibility."""
        if number_of_items == 0:
            return
        if self.name in self.session.settings["other_buffers"].get("muted_buffers", []):
            return
        if self.session.settings["sound"].get("session_mute", False):
            return
        if self.name not in self.session.settings["other_buffers"].get("autoread_buffers", []):
            return

        safe = True
        relative_times = self.session.settings["general"].get("relative_times", False)
        show_screen_names = self.session.settings["general"].get("show_screen_names", False)

        if number_of_items == 1:
            if self.session.settings["general"].get("reverse_timelines", False):
                post = self.session.db[self.name][0]
            else:
                post = self.session.db[self.name][-1]
            output.speak(_("New post in {0}").format(self.get_buffer_name()))
            output.speak(" ".join(self.compose_function(post, self.session.db, self.session.settings, relative_times, show_screen_names, safe=safe)))
        elif number_of_items > 1:
            output.speak(_("{0} new posts in {1}.").format(number_of_items, self.get_buffer_name()))

    def show_menu(self, ev, pos=0, *args, **kwargs):
        """Show context menu for current item."""
        if self.buffer.list.get_count() == 0:
            return
        menu = menus.baseMenu()
        widgetUtils.connect_event(menu, widgetUtils.MENU, self.reply, menuitem=menu.reply)
        widgetUtils.connect_event(menu, widgetUtils.MENU, self.share_item, menuitem=menu.repost)
        if hasattr(menu, "quote"):
            widgetUtils.connect_event(menu, widgetUtils.MENU, self.quote, menuitem=menu.quote)
        widgetUtils.connect_event(menu, widgetUtils.MENU, self.add_to_favorites, menuitem=menu.like)
        widgetUtils.connect_event(menu, widgetUtils.MENU, self.user_actions, menuitem=menu.userActions)
        widgetUtils.connect_event(menu, widgetUtils.MENU, self.url_, menuitem=menu.openUrl)
        if hasattr(menu, "openInBrowser"):
            widgetUtils.connect_event(menu, widgetUtils.MENU, self.open_in_browser, menuitem=menu.openInBrowser)
        widgetUtils.connect_event(menu, widgetUtils.MENU, self.view, menuitem=menu.view)
        widgetUtils.connect_event(menu, widgetUtils.MENU, self.copy, menuitem=menu.copy)
        widgetUtils.connect_event(menu, widgetUtils.MENU, self.destroy_status, menuitem=menu.remove)
        if pos != 0:
            self.buffer.PopupMenu(menu, pos)
        else:
            self.buffer.PopupMenu(menu, self.buffer.list.list.GetPosition())

    def show_menu_by_key(self, ev):
        """Show context menu when pressing menu key."""
        if self.buffer.list.get_count() == 0:
            return
        if ev.GetKeyCode() == wx.WXK_WINDOWS_MENU:
            self.show_menu(widgetUtils.MENU, pos=self.buffer.list.list.GetPosition())

    def copy(self, *args, **kwargs):
        """Copy post to clipboard."""
        pub.sendMessage("execute-action", action="copy_to_clipboard")

    def on_post(self, evt):
        dlg = blueski_messages.post(session=self.session, title=_("New Post"), caption=_("New Post"))
        if dlg.message.ShowModal() == wx.ID_OK:
            text, files, cw, langs = dlg.get_data()
            self._send_post_async(
                text=text,
                files=files,
                cw_text=cw,
                langs=langs,
                success_message=_("Sent."),
                error_message=_("An error occurred while posting."),
                sound="tweet_send.ogg",
                refresh_args=(False, False),
            )
        dlg.message.Destroy()

    def on_reply(self, evt):
        item = self.get_item()
        if not item: return
        
        # item is a feed object or dict. 
        # We need its URI.
        uri = self.get_selected_item_id()
        if not uri:
            uri = item.get("uri") if isinstance(item, dict) else getattr(item, "uri", None)
        reply_cid = self.get_selected_item_cid()
        # Attempt to get CID if present for consistency, though send_message handles it

        def g(obj, key, default=None):
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)

        author = g(item, "author")
        if not author:
            post = g(item, "post") or g(item, "record")
            author = g(post, "author") if post else None
        handle = g(author, "handle", "")
        initial_text = f"@{handle} " if handle and not handle.startswith("@") else (f"{handle} " if handle else "")

        dlg = blueski_messages.post(session=self.session, title=_("Reply"), caption=_("Reply"), text=initial_text)
        if dlg.message.ShowModal() == wx.ID_OK:
             text, files, cw, langs = dlg.get_data()
             refresh_args = (True, False) if getattr(self, "type", "") == "conversation" else None
             self._send_post_async(
                 text=text,
                 files=files,
                 cw_text=cw,
                 langs=langs,
                 reply_to=uri,
                 reply_to_cid=reply_cid,
                 success_message=_("Reply sent."),
                 error_message=_("An error occurred while replying."),
                 sound="reply_send.ogg",
                 refresh_args=refresh_args,
             )
        dlg.message.Destroy()

    def _send_post_async(
        self,
        *,
        text,
        files,
        cw_text,
        langs,
        reply_to=None,
        reply_to_cid=None,
        success_message="",
        error_message="",
        sound=None,
        refresh_args=None,
    ):
        if not text and not files:
            return

        def do_send():
            try:
                uri_resp = self.session.send_message(
                    message=text,
                    files=files,
                    reply_to=reply_to,
                    reply_to_cid=reply_to_cid,
                    cw_text=cw_text,
                    langs=langs,
                )
                if uri_resp:
                    if sound:
                        wx.CallAfter(self.session.sound.play, sound)
                    if success_message:
                        wx.CallAfter(output.speak, success_message)
                    if refresh_args and hasattr(self, "start_stream"):
                        try:
                            wx.CallAfter(self.start_stream, *refresh_args)
                        except Exception:
                            pass
                else:
                    wx.CallAfter(output.speak, _("Failed to send post."), True)
            except Exception:
                log.exception("Error sending Bluesky post")
                if error_message:
                    wx.CallAfter(output.speak, error_message, True)
                else:
                    wx.CallAfter(output.speak, _("An error occurred while posting."), True)

        call_threaded(do_send)

    def on_repost(self, evt):
        self.share_item()

    def share_item(self, event=None, item=None, *args, **kwargs):
        if item is None:
            item = self.get_item()
        if not item:
            return

        def g(obj, key, default=None):
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)

        # Get the URI for reposting
        uri = g(item, "uri") or g(g(item, "post"), "uri")
        cid = g(item, "cid") or g(g(item, "post"), "cid")
        if not uri:
            output.speak(_("Could not find post to repost."), True)
            return

        # Check boost_mode setting
        boost_mode = self.session.settings["general"].get("boost_mode", "ask")
        if boost_mode == "ask":
            from wxUI.dialogs.blueski.postDialogs import repost_question
            answer = repost_question()
            if answer == 1:
                self._direct_repost(uri)
            elif answer == 2:
                self.quote(item=item)
        else:
            self._direct_repost(uri)

    def _direct_repost(self, uri):
        try:
            self.session.repost(uri)
            self.session.sound.play("retweet_send.ogg")
            output.speak(_("Reposted."))
        except Exception as e:
            log.error("Error reposting: %s", e)
            output.speak(_("Failed to repost."), True)

    def quote(self, event=None, item=None, *args, **kwargs):
        if item is None:
            item = self.get_item()
        if not item:
            return

        def g(obj, key, default=None):
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)

        uri = g(item, "uri") or g(g(item, "post"), "uri")
        if not uri:
            output.speak(_("Could not find post to quote."), True)
            return

        title = _("Quote post")
        caption = _("Write your comment here")
        dlg = blueski_messages.post(session=self.session, title=title, caption=caption)
        if dlg.message.ShowModal() == wx.ID_OK:
            text, files, cw, langs = dlg.get_data()
            if text or files:
                def do_quote():
                    try:
                        result = self.session.send_message(
                            message=text,
                            files=files,
                            cw_text=cw,
                            langs=langs,
                            quote_uri=uri,
                        )
                        if result:
                            wx.CallAfter(self.session.sound.play, "retweet_send.ogg")
                            wx.CallAfter(output.speak, _("Quote posted."))
                        else:
                            wx.CallAfter(output.speak, _("Failed to post quote."), True)
                    except Exception as e:
                        log.error("Error posting quote: %s", e)
                        wx.CallAfter(output.speak, _("Failed to post quote."), True)
                call_threaded(do_quote)
        dlg.message.Destroy()

    def on_like(self, evt):
        self.toggle_favorite(confirm=False)

    def toggle_favorite(self, confirm=False, *args, **kwargs):
        item = self.get_item()
        if not item: 
            output.speak(_("No item to like."), True)
            return
        
        def g(obj, key, default=None):
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)
        
        uri = g(item, "uri")
        if not uri:
            post = g(item, "post") or g(item, "record")
            uri = g(post, "uri") if post else None
        
        if not uri:
            output.speak(_("Could not find post identifier."), True)
            return
        
        if confirm:
             if wx.MessageBox(_("Like this post?"), _("Confirm"), wx.YES_NO | wx.ICON_QUESTION) != wx.YES:
                  return

        # Check if already liked
        viewer = g(item, "viewer")
        already_liked = g(viewer, "like") if viewer else None
        
        if already_liked:
            output.speak(_("Already liked."), True)
            return

        # Perform the like
        like_uri = self.session.like(uri)
        if not like_uri:
            output.speak(_("Failed to like post."), True)
            return

        self.session.sound.play("favourite.ogg")
        output.speak(_("Liked."))
        
        # Update the viewer state in the item
        if isinstance(item, dict):
            if "viewer" not in item:
                item["viewer"] = {}
            item["viewer"]["like"] = like_uri
        else:
            # For SDK models, create or update viewer
            if not hasattr(item, "viewer") or item.viewer is None:
                # Create a simple object to hold the like state
                class Viewer:
                    def __init__(self):
                        self.like = None
                item.viewer = Viewer()
            item.viewer.like = like_uri
        
        # Refresh the displayed item in the list
        try:
            index = self.buffer.list.get_selected()
            if index > -1:
                # Recompose and update the list item
                safe = True
                relative_times = self.session.settings["general"].get("relative_times", False)
                show_screen_names = self.session.settings["general"].get("show_screen_names", False)
                post_data = self.compose_function(item, self.session.db, self.session.settings, 
                                                   relative_times=relative_times, 
                                                   show_screen_names=show_screen_names, 
                                                   safe=safe)
                
                # Update the item in place (only 3 columns: Author, Post, Date)
                self.buffer.list.list.SetItem(index, 0, post_data[0])  # Author
                self.buffer.list.list.SetItem(index, 1, post_data[1])  # Text
                self.buffer.list.list.SetItem(index, 2, post_data[2])  # Date
                # Note: compose_post returns 4 items but list only has 3 columns
        except Exception as e:
            log.error("Error refreshing list item after like: %s", e)
        
    def add_to_favorites(self, *args, **kwargs):
        self.toggle_favorite(confirm=False)
        
    def remove_from_favorites(self, *args, **kwargs):
        # We need unlike support in session
        pass
             
    def on_dm(self, evt):
        self.send_message()

    def send_message(self, *args, **kwargs):
         # Global shortcut for DM
         item = self.get_item()
         if not item:
              output.speak(_("No user selected to message."), True)
              return
         
         author = getattr(item, "author", None) or (item.get("post", {}).get("author") if isinstance(item, dict) else None)
         if not author:
              # Try item itself if it's a user object (UserBuffer)
              author = item
         
         did = getattr(author, "did", None) or author.get("did")
         handle = getattr(author, "handle", "unknown") or (author.get("handle") if isinstance(author, dict) else "unknown")

         if not did:
              return

         # Show simple text entry dialog for sending DM
         dlg = wx.TextEntryDialog(None, _("Message to {0}:").format(handle), _("Send Message"))
         if dlg.ShowModal() == wx.ID_OK:
             text = dlg.GetValue()
             if text:
                 try:
                     api = self.session._ensure_client()
                     dm_client = api.with_bsky_chat_proxy()
                     # Get or create conversation
                     res = dm_client.chat.bsky.convo.get_convo_for_members({"members": [did]})
                     convo_id = res.convo.id
                     self.session.send_chat_message(convo_id, text)
                     self.session.sound.play("dm_sent.ogg")
                     output.speak(_("Message sent."), True)
                 except Exception as e:
                     log.error("Error sending Bluesky DM: %s", e)
                     output.speak(_("Failed to send message."), True)
         dlg.Destroy()

    def view(self, *args, **kwargs):
        self.view_item()

    def view_item(self, item=None):
        if item is None:
            item = self.get_item()
        if not item:
            return
        if not blueski_messages.has_post_data(item):
            pub.sendMessage("execute-action", action="user_details")
            return
        try:
            blueski_messages.viewPost(self.session, item)
        except Exception as e:
            log.error("Error opening Bluesky post viewer: %s", e)

    def url_(self, *args, **kwargs):
        self.url()

    def url(self, announce=True, item=None, *args, **kwargs):
        """Open URLs found in the post content."""
        if item is None:
            item = self.get_item()
        if not item:
            return

        import webbrowser
        from wxUI.dialogs import urlList

        urls = utils.find_urls(item)
        url = ""
        if len(urls) == 1:
            url = urls[0]
        elif len(urls) > 1:
            urls_list = urlList.urlList()
            urls_list.populate_list(urls)
            if urls_list.get_response() == widgetUtils.OK:
                url = urls_list.get_string()
            if hasattr(urls_list, "destroy"):
                urls_list.destroy()
        if url != '':
            if announce:
                output.speak(_(u"Opening URL..."), True)
            webbrowser.open_new_tab(url)

    def user_actions(self, *args, **kwargs):
        pub.sendMessage("execute-action", action="follow")

    def view_chat_with_user(self, did, handle):
        try:
             api = self.session._ensure_client()
             res = api.chat.bsky.convo.get_convo_for_members({"members": [did]})
             convo_id = res.convo.id
             
             import application
             title = _("Chat: {0}").format(handle)
             application.app.controller.create_buffer(
                 buffer_type="chat_messages",
                 session_type="blueski",
                 buffer_title=title,
                 kwargs={"session": self.session, "convo_id": convo_id, "name": title},
                 start=True
             )
        except:
             output.speak(_("Could not open chat."), True)

    def block_user(self, *args, **kwargs):
        item = self.get_item()
        if not item: return
        author = getattr(item, "author", None) or (item.get("post", {}).get("author") if isinstance(item, dict) else item)
        did = getattr(author, "did", None) or (author.get("did") if isinstance(author, dict) else None)
        handle = getattr(author, "handle", "unknown") or (author.get("handle") if isinstance(author, dict) else "unknown")
        
        if wx.MessageBox(_("Are you sure you want to block {0}?").format(handle), _("Block"), wx.YES_NO | wx.ICON_WARNING) == wx.YES:
             if self.session.block_user(did):
                  output.speak(_("User blocked."))
             else:
                  output.speak(_("Failed to block user."))

    def unblock_user(self, *args, **kwargs):
         # Unblocking usually needs the block record URI. 
         # In a UserBuffer (Blocks), it might be present.
         item = self.get_item()
         if not item: return
         
         # Check if item itself is a block record or user object with viewer.blocking
         block_uri = None
         if isinstance(item, dict):
              block_uri = item.get("viewer", {}).get("blocking")
         else:
              viewer = getattr(item, "viewer", None)
              block_uri = getattr(viewer, "blocking", None) if viewer else None
         
         if not block_uri:
              output.speak(_("Could not find block information for this user."), True)
              return
              
         if self.session.unblock_user(block_uri):
              output.speak(_("User unblocked."))
         else:
              output.speak(_("Failed to unblock user."))
        
    def put_items_on_list(self, number_of_items):
        list_to_use = self.session.db[self.name]
        count = self.buffer.list.get_count()
        reverse = False
        try:
             reverse = self.session.settings["general"].get("reverse_timelines", False)
        except: pass

        if number_of_items == 0:
            return

        safe = True
        relative_times = self.session.settings["general"].get("relative_times", False)
        show_screen_names = self.session.settings["general"].get("show_screen_names", False)

        if count == 0:
            for i in list_to_use:
                post = self.compose_function(i, self.session.db, self.session.settings, relative_times=relative_times, show_screen_names=show_screen_names, safe=safe)
                self.buffer.list.insert_item(False, *post)
            # Set selection
            total = self.buffer.list.get_count()
            if total > 0:
                if not reverse:
                    self.buffer.list.select_item(total - 1) # Bottom
                else:
                    self.buffer.list.select_item(0) # Top

        elif count > 0 and number_of_items > 0:
             if not reverse:
                 items = list_to_use[:number_of_items] # If we prepended items for normal (oldest first) timeline... wait.
                 # Standard flow: "New items" come from API.
                 # If standard timeline (oldest at top, newest at bottom): new items appended to DB.
                 # UI: append to bottom.
                 items = list_to_use[len(list_to_use)-number_of_items:]
                 for i in items:
                     post = self.compose_function(i, self.session.db, self.session.settings, relative_times=relative_times, show_screen_names=show_screen_names, safe=safe)
                     self.buffer.list.insert_item(False, *post)
             else:
                 # Reverse timeline (Newest at top).
                 # New items appended to DB? Or inserted at 0?
                 # Mastodon BaseBuffer:
                 # if reverse_timelines == False: items_db.insert(0, i) (Wait, insert at 0?)
                 # Actually let's look at `get_more_items` in Mastodon BaseBuffer again.
                 # "if self.session.settings["general"]["reverse_timelines"] == False: items_db.insert(0, i)"
                 # This means for standard timeline, new items (newer time) go to index 0?
                 # No, standard timeline usually has oldest at top. Retrieve "more items" usually means "newer items" or "older items" depending on context (streaming vs styling).

                 # Let's trust that we just need to insert based on how we updated DB in start_stream.

                 # For now, simplistic approach:
                 items = list_to_use[0:number_of_items] # Assuming we inserted at 0 in DB
                 # items.reverse() if needed?
                 for i in items:
                     post = self.compose_function(i, self.session.db, self.session.settings, relative_times=relative_times, show_screen_names=show_screen_names, safe=safe)
                     self.buffer.list.insert_item(True, *post) # Insert at 0 (True)

    def reply(self, *args, **kwargs):
        self.on_reply(None)

    def post_status(self, *args, **kwargs):
        self.on_post(None)

    def destroy_status(self, *args, **kwargs):
         # Delete post
        item = self.get_item()
        if not item: return
        uri = self.get_selected_item_id()
        if not uri:
            if isinstance(item, dict):
                uri = item.get("uri") or item.get("post", {}).get("uri")
            else:
                post = getattr(item, "post", None)
                uri = getattr(item, "uri", None) or getattr(post, "uri", None)
        if not uri:
            output.speak(_("Could not find the post identifier."), True)
            return
        
        # Check if author is self
        # Implementation depends on parsing URI or checking active user DID vs author DID
        # For now, just try and handle error
        if wx.MessageBox(_("Delete this post?"), _("Confirm"), wx.YES_NO | wx.ICON_QUESTION) == wx.YES:
             try:
                 ok = self.session.delete_post(uri)
                 if not ok:
                     output.speak(_("Could not delete."), True)
                     return
                 index = self.buffer.list.get_selected()
                 if index > -1 and self.session.db.get(self.name):
                     try:
                         self.session.db[self.name].pop(index)
                     except Exception:
                         pass
                     try:
                         self.buffer.list.remove_item(index)
                     except Exception:
                         pass
                 output.speak(_("Deleted."))
             except Exception as e:
                 log.error("Error deleting Bluesky post: %s", e)
                 output.speak(_("Could not delete."), True)


    def audio(self, event=None, item=None, *args, **kwargs):
        """Play audio/video from the current post."""
        if sound.URLPlayer.player.is_playing():
            return sound.URLPlayer.stop_audio()
        if item is None:
            item = self.get_item()
        if not item:
            return
        urls = utils.get_media_urls(item)
        if not urls:
            output.speak(_("This post has no playable media."), True)
            return
        url = ""
        if len(urls) == 1:
            url = urls[0]
        elif len(urls) > 1:
            from wxUI.dialogs import urlList
            urls_list = urlList.urlList()
            urls_list.populate_list(urls)
            if urls_list.get_response() == widgetUtils.OK:
                url = urls_list.get_string()
            if hasattr(urls_list, "destroy"):
                urls_list.destroy()
        if url:
            sound.URLPlayer.play(url, self.session.settings["sound"]["volume"])

    def ocr_image(self, *args, **kwargs):
        """Perform OCR on images in the current post."""
        post = self.get_item()
        if not post:
            return

        image_list = utils.get_image_urls(post)
        if not image_list:
            return

        if len(image_list) > 1:
            from wxUI.dialogs import urlList
            labels = [_("Picture {0}").format(i + 1) for i in range(len(image_list))]
            dialog = urlList.urlList(title=_("Select the picture"))
            dialog.populate_list(labels)
            if dialog.get_response() != widgetUtils.OK:
                return
            img = image_list[dialog.get_item()]
        else:
            img = image_list[0]

        url = img.get("url")
        if not url:
            return

        from extra import ocr as ocr_module
        api = ocr_module.OCRSpace.OCRSpaceAPI()
        try:
            text = api.OCR_URL(url)
        except ocr_module.OCRSpace.APIError:
            output.speak(_("Unable to extract text"), True)
            return
        except Exception as e:
            log.error("OCR error: %s", e)
            output.speak(_("Unable to extract text"), True)
            return

        viewer = blueski_messages.text(title=_("OCR Result"), text=text["ParsedText"])
        viewer.message.ShowModal()
        viewer.message.Destroy()
    
    # Also implement "view_item" if standard keymap uses it
    def get_formatted_message(self):
         return self.compose_function(self.get_item(), self.session.db, self.session.settings, self.session.settings["general"].get("relative_times", False), self.session.settings["general"].get("show_screen_names", False))[1]

    def get_message(self):
         item = self.get_item()
         if item is None:
              return
         relative_times = self.session.settings["general"].get("relative_times", False)
         offset_hours = 0
         if isinstance(self.session.db, dict):
             offset_hours = self.session.db.get("utc_offset", 0) or 0
         template_settings = self.session.settings.get("templates", {})
         try:
             if self.type == "notifications":
                 template = template_settings.get("notification", "$display_name $text, $date")
                 post_template = template_settings.get("post", "$display_name, $safe_text $date.")
                 return templates.render_notification(item, template, post_template, self.session.settings, relative_times, offset_hours)
             if self.type in ("user", "post_user_list"):
                 template = template_settings.get("person", "$display_name (@$screen_name). $followers followers, $following following, $posts posts.")
                 return templates.render_user(item, template, self.session.settings, relative_times, offset_hours)
             template = template_settings.get("post", "$display_name, $safe_text $date.")
             return templates.render_post(item, template, self.session.settings, relative_times, offset_hours)
         except Exception:
             # Fallback to compose if any template render fails.
             composed = self.compose_function(
                 item,
                 self.session.db,
                 self.session.settings,
                 relative_times,
                 self.session.settings["general"].get("show_screen_names", False),
             )
             return " ".join(composed)

    def view_conversation(self, *args, **kwargs):
         item = self.get_item()
         if not item: return
         
         uri = item.get("uri") if isinstance(item, dict) else getattr(item, "uri", None)
         if not uri: return
         
         import application
         controller = application.app.controller
         
         details = self.get_selected_item_author_details()
         handle = "Unknown"
         if details:
             handle = details.get("handle") or "Unknown"
         title = _("Conversation: {0}").format(handle)
         
         controller.create_buffer(
             buffer_type="conversation",
             session_type="blueski",
             buffer_title=title,
             kwargs={"session": self.session, "uri": uri, "name": title},
             start=True
         )
     
    def get_item(self):
         index = self.buffer.list.get_selected()
         if index > -1 and self.session.db.get(self.name) is not None:
              # Logic implies DB order matches UI order
              return self.session.db[self.name][index]

    def get_selected_item_id(self):
         item = self.get_item()
         if not item:
             return None

         if isinstance(item, dict):
             uri = item.get("uri")
             if uri:
                 return uri
             post = item.get("post") or item.get("record")
             if isinstance(post, dict):
                 return post.get("uri")
             return getattr(post, "uri", None)

         return getattr(item, "uri", None) or getattr(getattr(item, "post", None), "uri", None)

    def get_selected_item_cid(self):
         item = self.get_item()
         if not item:
             return None

         if isinstance(item, dict):
             cid = item.get("cid")
             if cid:
                 return cid
             post = item.get("post") or item.get("record")
             if isinstance(post, dict):
                 return post.get("cid")
             return getattr(post, "cid", None)

         return getattr(item, "cid", None) or getattr(getattr(item, "post", None), "cid", None)

    def get_selected_item_author_details(self):
        item = self.get_item()
        if not item:
            return None

        def g(obj, key, default=None):
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)

        author = None
        if g(item, "did") or g(item, "handle"):
            author = item
        else:
            author = g(item, "author")
            if not author:
                post = g(item, "post") or g(item, "record")
                author = g(post, "author") if post else None

        if not author:
            return None

        return {
            "did": g(author, "did"),
            "handle": g(author, "handle"),
        }
    
    def process_items(self, items, play_sound=True, avoid_autoreading=False):
        """
        Process list of items (FeedViewPost objects), update DB, and update UI.
        Returns number of new items.
        """
        if not items:
            return 0
            
        # Identify new items
        new_items = []
        current_uris = set()
        # Create a set of keys from existing db to check duplicates
        def get_key(it):
            if isinstance(it, dict):
                post = it.get("post")
                if isinstance(post, dict) and post.get("uri"):
                    return post.get("uri")
                if it.get("uri"):
                    return it.get("uri")
                if it.get("id"):
                    return it.get("id")
                if it.get("did"):
                    return it.get("did")
                if it.get("handle"):
                    return it.get("handle")
                author = it.get("author")
                if isinstance(author, dict):
                    return author.get("did") or author.get("handle")
                return None
            post = getattr(it, "post", None)
            if post is not None:
                return getattr(post, "uri", None)
            for attr in ("uri", "id", "did", "handle"):
                val = getattr(it, attr, None)
                if val:
                    return val
            author = getattr(it, "author", None)
            if author is not None:
                return getattr(author, "did", None) or getattr(author, "handle", None)
            return None

        for item in self.session.db[self.name]:
            key = get_key(item)
            if key:
                current_uris.add(key)
            
        for item in items:
            key = get_key(item)
            if key:
                if key in current_uris:
                    continue
                current_uris.add(key)
            new_items.append(item)
                
        if not new_items:
            return 0
            
        # Add to DB
        # Reverse timeline setting
        reverse = False
        try: reverse = self.session.settings["general"].get("reverse_timelines", False)
        except: pass
        
        # If reverse (newest at top), we insert new items at index 0?
        # Typically API returns newest first.
        # If DB is [Newest ... Oldest] (Reverse order)
        # Then we insert new items at 0.
        # If DB is [Oldest ... Newest] (Normal order)
        # Then we append new items at end.
        
        # But traditionally APIs return [Newest ... Oldest].
        # So 'items' list is [Newest ... Oldest].
        
        if reverse: # Newest at top
            # DB: [Newest (Index 0) ... Oldest]
            # We want to insert 'new_items' at 0.
            # But 'new_items' are also [Newest...Oldest]
            # So duplicates check handled.
            # We insert the whole block at 0?
            for it in reversed(new_items): # Insert oldest of new first, so newest ends up at 0
                 self.session.db[self.name].insert(0, it)
        else: # Oldest at top
            # DB: [Oldest ... Newest]
            # APIs return [Newest ... Oldest]
            # We want to append them.
            # So we append reversed(new_items)?
            for it in reversed(new_items):
                self.session.db[self.name].append(it)
                
        # Update UI
        self.put_items_on_list(len(new_items))
        
        # Play sound
        if play_sound and self.sound and not self.session.settings["sound"]["session_mute"]:
             self.session.sound.play(self.sound)

        # Auto-read for accessibility
        if not avoid_autoreading and len(new_items) > 0:
            self.auto_read(len(new_items))

        return len(new_items)

    def add_new_item(self, item):
        """Add a single new item from streaming."""
        safe = True
        relative_times = self.session.settings["general"].get("relative_times", False)
        show_screen_names = self.session.settings["general"].get("show_screen_names", False)
        post = self.compose_function(item, self.session.db, self.session.settings, relative_times, show_screen_names, safe=safe)

        if self.session.settings["general"].get("reverse_timelines", False):
            self.buffer.list.insert_item(True, *post)
            self.session.db[self.name].insert(0, item)
        else:
            self.buffer.list.insert_item(False, *post)
            self.session.db[self.name].append(item)

        # Auto-read single item
        if self.name in self.session.settings["other_buffers"].get("autoread_buffers", []) and \
           self.name not in self.session.settings["other_buffers"].get("muted_buffers", []) and \
           not self.session.settings["sound"].get("session_mute", False):
            output.speak(" ".join(post[:2]),
                        speech=self.session.settings["reporting"].get("speech_reporting", True),
                        braille=self.session.settings["reporting"].get("braille_reporting", True))

    def update_item(self, item, position):
        """Update an existing item at the specified position."""
        safe = True
        relative_times = self.session.settings["general"].get("relative_times", False)
        show_screen_names = self.session.settings["general"].get("show_screen_names", False)
        post = self.compose_function(item, self.session.db, self.session.settings, relative_times, show_screen_names, safe=safe)
        self.buffer.list.list.SetItem(position, 1, post[1])

    def open_in_browser(self, *args, **kwargs):
        """Open the current post in web browser."""
        item = self.get_item()
        if not item:
            return

        import webbrowser

        def g(obj, key, default=None):
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)

        uri = g(item, "uri") or g(g(item, "post"), "uri")
        author = g(item, "author") or g(g(item, "post"), "author")
        handle = g(author, "handle")

        if uri and handle:
            if "app.bsky.feed.post" in uri:
                rkey = uri.split("/")[-1]
                url = f"https://bsky.app/profile/{handle}/post/{rkey}"
                output.speak(_("Opening item in web browser..."))
                webbrowser.open(url)
                return

        # Fallback to profile
        if handle:
            url = f"https://bsky.app/profile/{handle}"
            output.speak(_("Opening item in web browser..."))
            webbrowser.open(url)

    def save_positions(self):
        try:
            self.session.db[self.name+"_pos"] = self.buffer.list.get_selected()
        except: pass

    def clear_list(self):
        dlg = commonMessageDialogs.clear_list()
        if dlg == widgetUtils.YES:
            self.session.db[self.name] = []
            self.buffer.list.clear()

    def remove_buffer(self, force=False):
        if self.type in ("conversation", "chat_messages") or self.name.lower().startswith("conversation"):
            if not force:
                dlg = commonMessageDialogs.remove_buffer()
                if dlg != widgetUtils.YES:
                    return False
            try:
                self.session.db.pop(self.name, None)
            except Exception:
                pass
            return True
        return False

