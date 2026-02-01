# -*- coding: utf-8 -*-
import logging
import wx
import output
import sound
import config
import widgetUtils
from pubsub import pub
from controller.buffers.base import base
from controller.blueski import messages as blueski_messages
from sessions.blueski import compose
from wxUI.buffers.blueski import panels as BlueskiPanels

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
        self.sound = sound
        
        # Initialize DB list if needed
        if self.name not in self.session.db:
            self.session.db[self.name] = []
            
        self.bind_events()

    def create_buffer(self, parent, name):
        # Default to HomePanel, can be overridden
        self.buffer = BlueskiPanels.HomePanel(parent, name, account=self.account)
        self.buffer.session = self.session

    def bind_events(self):
        # Bind essential events
        widgetUtils.connect_event(self.buffer.list.list, widgetUtils.KEYPRESS, self.get_event)
        
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
             
    def on_post(self, evt):
        from wxUI.dialogs.blueski import postDialogs
        dlg = postDialogs.Post(caption=_("New Post"))
        if dlg.ShowModal() == wx.ID_OK:
            text, files, cw, langs = dlg.get_payload()
            self.session.send_message(message=text, files=files, cw_text=cw, langs=langs)
            output.speak(_("Sending..."))
        dlg.Destroy()

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

        from wxUI.dialogs.blueski import postDialogs
        dlg = postDialogs.Post(caption=_("Reply"), text=initial_text)
        if dlg.ShowModal() == wx.ID_OK:
             text, files, cw, langs = dlg.get_payload()
             self.session.send_message(message=text, files=files, reply_to=uri, reply_to_cid=reply_cid, cw_text=cw, langs=langs)
             output.speak(_("Sending reply..."))
             if getattr(self, "type", "") == "conversation":
                 try:
                     self.start_stream(mandatory=True, play_sound=False)
                 except Exception:
                     pass
        dlg.Destroy()

    def on_repost(self, evt):
        self.share_item(confirm=True)

    def share_item(self, confirm=False, *args, **kwargs):
        item = self.get_item()
        if not item: return
        uri = item.get("uri") if isinstance(item, dict) else getattr(item, "uri", None)
        
        if confirm:
             if wx.MessageBox(_("Repost this?"), _("Confirm"), wx.YES_NO | wx.ICON_QUESTION) != wx.YES:
                  return

        self.session.repost(uri)
        output.speak(_("Reposted."))

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
                self.buffer.list.list.SetItem(index, 1, post_data[1])  # Text (with ♥ indicator)
                self.buffer.list.list.SetItem(index, 2, post_data[2])  # Date
                # Note: compose_post returns 4 items but list only has 3 columns
        except Exception:
            log.exception("Error refreshing list item after like")
        
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

         if self.showing == False:
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
                             output.speak(_("Message sent."), True)
                        except:
                             log.exception("Error sending Bluesky DM (invisible)")
                             output.speak(_("Failed to send message."), True)
              dlg.Destroy()
              return

         # If showing, we'll just open the chat buffer for now as it's more structured
         self.view_chat_with_user(did, handle)

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
        except Exception:
            log.exception("Error opening Bluesky post viewer")

    def url_(self, *args, **kwargs):
        self.url()


    def url(self, *args, **kwargs):
        item = self.get_item()
        if not item: return

        import webbrowser
        
        def g(obj, key, default=None):
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)

        uri = g(item, "uri")
        author = g(item, "author") or g(g(item, "post"), "author")
        handle = g(author, "handle")

        if uri and handle:
            # URI format: at://did:plc:xxx/app.bsky.feed.post/rkey
            if "app.bsky.feed.post" in uri:
                rkey = uri.split("/")[-1]
                url = f"https://bsky.app/profile/{handle}/post/{rkey}"
                webbrowser.open(url)
                return
            elif "app.bsky.feed.like" in uri:
                 # It's a like notification, try to get the subject
                 subject = g(item, "subject")
                 subject_uri = g(subject, "uri") if subject else None
                 if subject_uri:
                      rkey = subject_uri.split("/")[-1]
                      # We might not have the handle of the post author here easily if it's not in the notification
                      # But let's try...
                      # Actually, notification items usually have enough info or we can't deep direct link easily without fetching.
                      # For now, let's just open the profile of the liker
                      pass
                      
        # Fallback to profile
        if handle:
             url = f"https://bsky.app/profile/{handle}"
             webbrowser.open(url)
             return

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
        
    def share_item(self, *args, **kwargs):
        self.on_repost(None)
        
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
             except Exception:
                 log.exception("Error deleting Bluesky post")
                 output.speak(_("Could not delete."), True)


    def audio(self, *args, **kwargs):
        output.speak(_("Audio playback not supported for Bluesky yet."))
        
    # Helper to map standard keys if they don't invoke the methods above via get_event
    # But usually get_event is enough.
    
    # Also implement "view_item" if standard keymap uses it
    def get_formatted_message(self):
         return self.compose_function(self.get_item(), self.session.db, self.session.settings, self.session.settings["general"].get("relative_times", False), self.session.settings["general"].get("show_screen_names", False))[1]

    def get_message(self):
         item = self.get_item()
         if item is None:
              return
         # Use the compose function to get the full formatted text
         # Bluesky compose returns [user, text, date, source]
         composed = self.compose_function(item, self.session.db, self.session.settings, self.session.settings["general"].get("relative_times", False), self.session.settings["general"].get("show_screen_names", False))
         # Join them for a full readout similar to Mastodon's template render
         return " ".join(composed)

    def view_conversation(self, *args, **kwargs):
         item = self.get_item()
         if not item: return
         
         uri = item.get("uri") if isinstance(item, dict) else getattr(item, "uri", None)
         if not uri: return
         
         import application
         controller = application.app.controller
         
         handle = "Unknown"
         if isinstance(item, dict):
             handle = item.get("author", {}).get("handle", "Unknown")
         else:
             handle = getattr(getattr(item, "author", None), "handle", "Unknown")
             
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
    
    def process_items(self, items, play_sound=True):
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
             
        return len(new_items)

    def save_positions(self):
        try:
            self.session.db[self.name+"_pos"] = self.buffer.list.get_selected()
        except: pass

    def remove_buffer(self, force=False):
        if self.type in ("conversation", "chat_messages") or self.name.lower().startswith("conversation"):
            try:
                self.session.db.pop(self.name, None)
            except Exception:
                pass
            return True
        return False

