# -*- coding: utf-8 -*-
import logging
import wx
import widgetUtils
import output
from .base import BaseBuffer
from controller.blueski import messages as blueski_messages
from wxUI.buffers.blueski import panels as BlueskiPanels
from sessions.blueski import compose
from mysc.thread_utils import call_threaded

log = logging.getLogger("controller.buffers.blueski.chat")

class ConversationListBuffer(BaseBuffer):
    """Buffer for listing conversations, similar to Mastodon's ConversationListBuffer."""

    def __init__(self, *args, **kwargs):
        kwargs["compose_func"] = "compose_convo"
        super(ConversationListBuffer, self).__init__(*args, **kwargs)
        self.type = "chat"
        self.sound = "dm_received.ogg"

    def create_buffer(self, parent, name):
        self.buffer = BlueskiPanels.ChatPanel(parent, name)
        self.buffer.session = self.session

    def bind_events(self):
        """Bind events like Mastodon's ConversationListBuffer."""
        self.buffer.set_focus_function(self.onFocus)
        widgetUtils.connect_event(self.buffer.list.list, widgetUtils.KEYPRESS, self.get_event)
        widgetUtils.connect_event(self.buffer.list.list, wx.EVT_LIST_ITEM_RIGHT_CLICK, self.show_menu)
        widgetUtils.connect_event(self.buffer.list.list, wx.EVT_LIST_KEY_DOWN, self.show_menu_by_key)
        # Buttons
        if hasattr(self.buffer, "post"):
            widgetUtils.connect_event(self.buffer, widgetUtils.BUTTON_PRESSED, self.on_post, self.buffer.post)
        if hasattr(self.buffer, "reply"):
            widgetUtils.connect_event(self.buffer, widgetUtils.BUTTON_PRESSED, self.reply, self.buffer.reply)
        if hasattr(self.buffer, "new_chat"):
            widgetUtils.connect_event(self.buffer, widgetUtils.BUTTON_PRESSED, self.on_new_chat, self.buffer.new_chat)

    def get_item(self):
        """Get the last message from the selected conversation (like Mastodon)."""
        index = self.buffer.list.get_selected()
        if index > -1 and self.session.db.get(self.name) is not None and len(self.session.db[self.name]) > index:
            convo = self.session.db[self.name][index]
            # Return lastMessage for compatibility with item-based operations
            last_msg = getattr(convo, "lastMessage", None) or (convo.get("lastMessage") if isinstance(convo, dict) else None)
            return last_msg
        return None

    def get_conversation(self):
        """Get the full conversation object."""
        index = self.buffer.list.get_selected()
        if index > -1 and self.session.db.get(self.name) is not None and len(self.session.db[self.name]) > index:
            return self.session.db[self.name][index]
        return None

    def get_convo_id(self, conversation):
        """Extract conversation ID from a conversation object, handling different field names."""
        if not conversation:
            return None
        # Try different possible field names for the conversation ID
        for attr in ("id", "convo_id", "convoId"):
            val = getattr(conversation, attr, None)
            if val:
                return val
            if isinstance(conversation, dict) and attr in conversation:
                return conversation[attr]
        return None

    def _get_members_key(self, conversation):
        """Fallback key when convo id is missing: stable member DID list."""
        members = getattr(conversation, "members", None) or (conversation.get("members") if isinstance(conversation, dict) else None) or []
        dids = []
        for m in members:
            did = getattr(m, "did", None) or (m.get("did") if isinstance(m, dict) else None)
            if did:
                dids.append(did)
        if not dids:
            return None
        dids.sort()
        return tuple(dids)

    def _get_last_message_key(self, conversation):
        """Key for detecting conversation updates based on last message."""
        last_msg = getattr(conversation, "lastMessage", None) or (conversation.get("lastMessage") if isinstance(conversation, dict) else None)
        if not last_msg:
            return None

        def g(obj, key, default=None):
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)

        for attr in ("id", "messageId", "message_id", "msgId", "msg_id", "cid", "rev"):
            val = g(last_msg, attr)
            if val:
                return val

        nested = g(last_msg, "message") or g(last_msg, "record")
        if nested:
            for attr in ("id", "messageId", "message_id", "msgId", "msg_id", "cid", "rev"):
                val = g(nested, attr)
                if val:
                    return val

        sent_at = g(last_msg, "sentAt") or g(last_msg, "sent_at") or g(last_msg, "createdAt") or g(last_msg, "created_at")
        sender = g(last_msg, "sender") or (g(nested, "sender") if nested else {}) or {}
        sender_did = g(sender, "did")
        text = g(last_msg, "text") or (g(nested, "text") if nested else None)
        if sent_at or sender_did or text:
            return (sent_at, sender_did, text)
        return None

    def get_formatted_message(self):
        """Return last message text for current conversation."""
        conversation = self.get_conversation()
        if not conversation:
            return None
        return self.compose_function(
            conversation,
            self.session.db,
            self.session.settings,
            self.session.settings["general"].get("relative_times", False),
            self.session.settings["general"].get("show_screen_names", False),
        )[1]

    def get_message(self):
        """Return a readable summary for the selected conversation."""
        conversation = self.get_conversation()
        if not conversation:
            return None
        composed = self.compose_function(
            conversation,
            self.session.db,
            self.session.settings,
            self.session.settings["general"].get("relative_times", False),
            self.session.settings["general"].get("show_screen_names", False),
        )
        return " ".join(composed)

    def on_new_chat(self, *args, **kwargs):
        """Start a new conversation by entering a handle."""
        dlg = wx.TextEntryDialog(None, _("Enter the handle of the user (e.g., user.bsky.social):"), _("New Chat"))
        if dlg.ShowModal() == wx.ID_OK:
            handle = dlg.GetValue().strip()
            if handle:
                if handle.startswith("@"):
                    handle = handle[1:]
                def do_create():
                    try:
                        # Resolve handle to DID
                        profile = self.session.get_profile(handle)
                        if not profile:
                            wx.CallAfter(output.speak, _("User not found."), True)
                            return
                        did = getattr(profile, "did", None) or (profile.get("did") if isinstance(profile, dict) else None)
                        if not did:
                            wx.CallAfter(output.speak, _("Could not get user ID."), True)
                            return
                        # Get or create conversation
                        convo = self.session.get_or_create_convo([did])
                        if not convo:
                            wx.CallAfter(output.speak, _("Could not create conversation."), True)
                            return
                        convo_id = self.get_convo_id(convo)
                        user_handle = getattr(profile, "handle", None) or (profile.get("handle") if isinstance(profile, dict) else None) or handle
                        title = _("Chat: {0}").format(user_handle)
                        # Create the buffer under direct_messages node
                        wx.CallAfter(self._create_chat_buffer, self.controller, title, convo_id)
                        # Refresh conversation list
                        wx.CallAfter(self.start_stream, True, False)
                    except Exception:
                        log.exception("Error creating new conversation")
                        wx.CallAfter(output.speak, _("Error creating conversation."), True)
                call_threaded(do_create)
        dlg.Destroy()

    def start_stream(self, mandatory=False, play_sound=True, avoid_autoreading=False):
        count = self.get_max_items()
        try:
            res = self.session.list_convos(limit=count)
            items = res.get("items", [])
            return self._merge_conversations(items, play_sound, avoid_autoreading=avoid_autoreading)
        except Exception:
            log.exception("Error fetching conversations")
            output.speak(_("Error loading conversations."), True)
            return 0

    def _merge_conversations(self, items, play_sound=True, avoid_autoreading=False):
        """Merge conversation list, updating items without duplicating or re-alerting."""
        if self.session.db.get(self.name) is None:
            self.session.db[self.name] = []

        # Track current selection to restore after refresh
        selected_key = None
        current_convo = self.get_conversation()
        if current_convo:
            selected_key = self.get_convo_id(current_convo) or self._get_members_key(current_convo)

        existing = {}
        existing_last = {}
        for convo in self.session.db[self.name]:
            key = self.get_convo_id(convo) or self._get_members_key(convo)
            if key is None:
                continue
            existing[key] = convo
            existing_last[key] = self._get_last_message_key(convo)

        new_db = []
        new_count = 0
        first_load = len(self.session.db[self.name]) == 0
        for convo in items:
            key = self.get_convo_id(convo) or self._get_members_key(convo)
            new_db.append(convo)
            if key is None:
                if first_load:
                    new_count += 1
                continue
            if key not in existing:
                new_count += 1
                continue
            if self._get_last_message_key(convo) != existing_last.get(key):
                new_count += 1

        # Replace DB with latest ordered list from API
        self.session.db[self.name] = new_db

        # Rebuild list UI to keep ordering consistent with API
        self.buffer.list.clear()
        safe = True
        relative_times = self.session.settings["general"].get("relative_times", False)
        show_screen_names = self.session.settings["general"].get("show_screen_names", False)
        for convo in new_db:
            row = self.compose_function(convo, self.session.db, self.session.settings, relative_times, show_screen_names, safe=safe)
            self.buffer.list.insert_item(False, *row)

        # Restore selection if possible
        if selected_key is not None:
            for idx, convo in enumerate(new_db):
                key = self.get_convo_id(convo) or self._get_members_key(convo)
                if key == selected_key:
                    self.buffer.list.select_item(idx)
                    break

        # Sound and auto-read only when something actually changed
        if new_count > 0:
            if play_sound and self.sound and not self.session.settings["sound"].get("session_mute", False):
                self.session.sound.play(self.sound)
            if not avoid_autoreading:
                self.auto_read(new_count)

        return new_count

    def fav(self):
        pass

    def unfav(self):
        pass

    def can_share(self):
        return False

    def url(self, *args, **kwargs):
        """Enter key opens the chat conversation buffer."""
        self.view_chat()

    def send_message(self, *args, **kwargs):
        """Global DM shortcut - reply to conversation."""
        return self.reply()

    def reply(self, *args, **kwargs):
        """Reply to the selected conversation (like Mastodon)."""
        conversation = self.get_conversation()
        if not conversation:
            output.speak(_("No conversation selected."), True)
            return

        convo_id = self.get_convo_id(conversation)
        if not convo_id:
            log.error("Could not get conversation ID from conversation object")
            output.speak(_("Could not identify conversation."), True)
            return

        # Get participants for title
        members = getattr(conversation, "members", []) or (conversation.get("members", []) if isinstance(conversation, dict) else [])
        user_did = self.session.db.get("user_id")
        others = [m for m in members if (getattr(m, "did", None) or (m.get("did") if isinstance(m, dict) else None)) != user_did]
        if not others:
            others = members

        if others:
            first_user = others[0]
            username = getattr(first_user, "handle", None) or (first_user.get("handle") if isinstance(first_user, dict) else None) or "unknown"
        else:
            username = "unknown"

        title = _("Conversation with {0}").format(username)
        caption = _("Write your message here")
        initial_text = "@{} ".format(username)

        post = blueski_messages.post(session=self.session, title=title, caption=caption, text=initial_text)
        if post.message.ShowModal() == wx.ID_OK:
            text, files, cw_text, langs = post.get_data()
            if text:
                def do_send():
                    try:
                        self.session.send_chat_message(convo_id, text)
                        wx.CallAfter(self.session.sound.play, "dm_sent.ogg")
                        wx.CallAfter(output.speak, _("Message sent."))
                        wx.CallAfter(self.start_stream, True, False)
                    except Exception:
                        log.exception("Error sending message")
                        wx.CallAfter(output.speak, _("Failed to send message."), True)
                call_threaded(do_send)
        if hasattr(post.message, "Destroy"):
            post.message.Destroy()

    def view_chat(self):
        """Open the conversation in a separate buffer (nested under Chats node)."""
        conversation = self.get_conversation()
        if not conversation:
            output.speak(_("No conversation selected."), True)
            return

        convo_id = self.get_convo_id(conversation)
        if not convo_id:
            log.error("Could not get conversation ID from conversation object: %r", conversation)
            output.speak(_("Could not identify conversation."), True)
            return

        # Determine participants names for title
        members = getattr(conversation, "members", []) or (conversation.get("members", []) if isinstance(conversation, dict) else [])
        user_did = self.session.db.get("user_id")
        others = [m for m in members if (getattr(m, "did", None) or (m.get("did") if isinstance(m, dict) else None)) != user_did]
        if not others:
            others = members
        names = ", ".join([getattr(m, "handle", None) or (m.get("handle") if isinstance(m, dict) else None) or "unknown" for m in others])

        title = _("Chat: {0}").format(names)

        self._create_chat_buffer(self.controller, title, convo_id)

    def _create_chat_buffer(self, controller, title, convo_id):
        """Create a chat buffer under the direct_messages node, avoiding duplicates."""
        account_name = self.session.get_name()

        # Avoid duplicates: if buffer already exists, navigate to it
        existing = controller.search_buffer(title, account_name)
        if existing:
            index = controller.view.search(title, account_name)
            if index is not None:
                controller.view.change_buffer(index)
            return

        # Insert under direct_messages node (like Mastodon's ConversationBuffer)
        chats_position = controller.view.search("direct_messages", account_name)
        if chats_position is None:
            chats_position = controller.view.search(account_name, account_name)

        controller.create_buffer(
            buffer_type="chat_messages",
            session_type="blueski",
            buffer_title=title,
            parent_tab=chats_position,
            kwargs={"session": self.session, "convo_id": convo_id, "name": title},
            start=True
        )

        # Navigate to the newly created buffer and announce it
        new_index = controller.view.search(title, account_name)
        if new_index is not None:
            controller.view.change_buffer(new_index)
            buffer_obj = controller.search_buffer(title, account_name)
            if buffer_obj and hasattr(buffer_obj.buffer, "list"):
                try:
                    count = buffer_obj.buffer.list.get_count()
                    if count > 0:
                        msg = _("{0}, {1} of {2}").format(title, buffer_obj.buffer.list.get_selected()+1, count)
                    else:
                        msg = _("{0}. Empty").format(title)
                except Exception:
                    msg = _("{0}. Empty").format(title)
                output.speak(msg, True)

    def destroy_status(self):
        pass

class ChatBuffer(BaseBuffer):
    """Buffer for displaying messages in a conversation, similar to Mastodon's ConversationBuffer."""

    def __init__(self, *args, **kwargs):
        kwargs["compose_func"] = "compose_chat_message"
        super(ChatBuffer, self).__init__(*args, **kwargs)
        self.type = "chat_messages"
        self.convo_id = kwargs.get("convo_id")
        self.sound = "dm_received.ogg"

    def create_buffer(self, parent, name):
        self.buffer = BlueskiPanels.ChatMessagePanel(parent, name)
        self.buffer.session = self.session

    def start_stream(self, mandatory=False, play_sound=True):
        if not self.convo_id:
            return 0
        count = self.get_max_items()
        try:
            res = self.session.get_convo_messages(self.convo_id, limit=count)
            items = res.get("items", [])
            items = list(reversed(items))
            return self.process_items(items, play_sound)
        except Exception:
            log.exception("Error fetching chat messages")
            return 0

    def get_more_items(self):
        output.speak(_("This action is not supported for this buffer"), True)

    def fav(self):
        pass

    def unfav(self):
        pass

    def can_share(self):
        return False

    def destroy_status(self):
        pass

    def url(self, *args, **kwargs):
        """Enter key opens reply dialog in chat."""
        self.on_reply(None)

    def on_reply(self, evt):
        """Open dialog to send a message in this conversation."""
        if not self.convo_id:
            output.speak(_("Cannot send message: no conversation selected."), True)
            return

        # Get conversation title from buffer name or use generic
        title = _("Send Message")
        if self.name and self.name.startswith(_("Chat: ")):
            title = self.name
        caption = _("Write your message here")

        post = blueski_messages.post(session=self.session, title=title, caption=caption, text="")
        if post.message.ShowModal() == wx.ID_OK:
            text, files, cw_text, langs = post.get_data()
            if text:
                def do_send():
                    try:
                        self.session.send_chat_message(self.convo_id, text)
                        wx.CallAfter(self.session.sound.play, "dm_sent.ogg")
                        wx.CallAfter(output.speak, _("Message sent."))
                        wx.CallAfter(self.start_stream, True, False)
                    except Exception:
                        log.exception("Error sending chat message")
                        wx.CallAfter(output.speak, _("Failed to send message."), True)
                call_threaded(do_send)
        if hasattr(post.message, "Destroy"):
            post.message.Destroy()

    def reply(self, *args, **kwargs):
        """Handle reply action (from menu or keyboard shortcut)."""
        self.on_reply(None)

    def send_message(self, *args, **kwargs):
        """Global shortcut for DM."""
        self.on_reply(None)

    def get_message(self):
        """Return a readable summary for the selected chat message."""
        item = self.get_item()
        if item is None:
            return None
        composed = self.compose_function(
            item, self.session.db, self.session.settings,
            self.session.settings["general"].get("relative_times", False),
            self.session.settings["general"].get("show_screen_names", False),
        )
        return " ".join(composed)

    def get_formatted_message(self):
        """Return the text content of the selected chat message."""
        item = self.get_item()
        if item is None:
            return None
        composed = self.compose_function(
            item, self.session.db, self.session.settings,
            self.session.settings["general"].get("relative_times", False),
            self.session.settings["general"].get("show_screen_names", False),
        )
        return composed[1]

    def view_item(self, item=None):
        """View the selected chat message in a dialog."""
        msg = self.get_formatted_message()
        if not msg:
            output.speak(_("No message selected."), True)
            return
        viewer = blueski_messages.text(title=_("Chat message"), text=msg)
        viewer.message.ShowModal()
        viewer.message.Destroy()

    def remove_buffer(self, force=False):
        """Allow removing this buffer."""
        from wxUI import commonMessageDialogs
        if force == False:
            dlg = commonMessageDialogs.remove_buffer()
        else:
            dlg = widgetUtils.YES
        if dlg == widgetUtils.YES:
            if self.name in self.session.db:
                self.session.db.pop(self.name)
            return True
        elif dlg == widgetUtils.NO:
            return False
