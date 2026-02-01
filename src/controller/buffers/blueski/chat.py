# -*- coding: utf-8 -*-
import logging
import wx
import output
from .base import BaseBuffer
from wxUI.buffers.blueski import panels as BlueskiPanels
from sessions.blueski import compose
from mysc.thread_utils import call_threaded

log = logging.getLogger("controller.buffers.blueski.chat")

class ConversationListBuffer(BaseBuffer):
    def __init__(self, *args, **kwargs):
        kwargs["compose_func"] = "compose_convo"
        super(ConversationListBuffer, self).__init__(*args, **kwargs)
        self.type = "chat"
        self.sound = "dm_received.ogg"
        
    def create_buffer(self, parent, name):
        self.buffer = BlueskiPanels.ChatPanel(parent, name)
        self.buffer.session = self.session

    def start_stream(self, mandatory=False, play_sound=True):
        count = self.get_max_items()
        try:
            res = self.session.list_convos(limit=count)
            items = res.get("items", [])
            self.session.db[self.name] = []
            self.buffer.list.clear()
            return self.process_items(items, play_sound)
        except Exception as e:
            log.error("Error fetching conversations: %s", e)
            return 0

    def url(self, *args, **kwargs):
        # In chat list, Enter (URL) should open the chat conversation buffer
        self.view_chat()

    def send_message(self, *args, **kwargs):
        # Global shortcut for DM
        self.view_chat()

    def view_chat(self):
        item = self.get_item()
        if not item: return
        
        convo_id = getattr(item, "id", None) or item.get("id")
        if not convo_id: return
        
        # Determine participants names for title
        members = getattr(item, "members", []) or item.get("members", [])
        others = [m for m in members if (getattr(m, "did", None) or m.get("did")) != self.session.db["user_id"]]
        if not others: others = members
        names = ", ".join([getattr(m, "handle", "unknown") or m.get("handle") for m in others])
        
        title = _("Chat: {0}").format(names)
        
        import application
        application.app.controller.create_buffer(
            buffer_type="chat_messages",
            session_type="blueski",
            buffer_title=title,
            kwargs={"session": self.session, "convo_id": convo_id, "name": title},
            start=True
        )

class ChatBuffer(BaseBuffer):
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
            self.session.db[self.name] = []
            self.buffer.list.clear()
            items = list(reversed(items))
            return self.process_items(items, play_sound)
        except Exception as e:
            log.error("Error fetching chat messages: %s", e)
            return 0

    def on_reply(self, evt):
        # Open a text entry chat box
        dlg = wx.TextEntryDialog(None, _("Message:"), _("Send Message"), style=wx.TE_MULTILINE | wx.OK | wx.CANCEL)
        if dlg.ShowModal() == wx.ID_OK:
            text = dlg.GetValue()
            if text:
                 def do_send():
                      try:
                           self.session.send_chat_message(self.convo_id, text)
                           wx.CallAfter(self.session.sound.play, "dm_sent.ogg")
                           wx.CallAfter(output.speak, _("Message sent."))
                           wx.CallAfter(self.start_stream, True, False)
                      except Exception:
                           wx.CallAfter(output.speak, _("Failed to send message."), True)
                 call_threaded(do_send)
        dlg.Destroy()

    def send_message(self, *args, **kwargs):
         # Global shortcut for DM
         self.on_reply(None)
