# -*- coding: utf-8 -*-
import wx
import languageHandler
from multiplatform_widgets import widgets

class HomePanel(wx.Panel):
    def __init__(self, parent, name, account="Unknown"):
        super().__init__(parent, name=name)
        self.name = name
        self.account = account
        self.type = "home_timeline"
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        # List
        self.list = widgets.list(self, _("Author"), _("Post"), _("Date"), style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_VRULES)
        self.list.set_windows_size(0, 120)
        self.list.set_windows_size(1, 400)
        self.list.set_windows_size(2, 120)
        self.list.set_size()

        # Buttons
        self.post = wx.Button(self, -1, _("Post"))
        self.repost = wx.Button(self, -1, _("Repost"))
        self.reply = wx.Button(self, -1, _("Reply"))
        self.like = wx.Button(self, wx.ID_ANY, _("Like"))
        # self.bookmark = wx.Button(self, wx.ID_ANY, _("Bookmark")) # Not yet common in Bsky API usage here
        self.dm = wx.Button(self, -1, _("Chat"))
        
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSizer.Add(self.post, 0, wx.ALL, 5)
        btnSizer.Add(self.repost, 0, wx.ALL, 5)
        btnSizer.Add(self.reply, 0, wx.ALL, 5)
        btnSizer.Add(self.like, 0, wx.ALL, 5)
        # btnSizer.Add(self.bookmark, 0, wx.ALL, 5)
        btnSizer.Add(self.dm, 0, wx.ALL, 5)
        
        self.sizer.Add(btnSizer, 0, wx.ALL, 5)
        
        self.sizer.Add(self.list.list, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(self.sizer)

    # Some helper methods expected by controller might be needed?
    # Controller accesses self.buffer.list directly.
    # Some older code expected .set_position, .post, .message, .actions attributes or buttons on the panel?
    # Mastodon panels usually have bottom buttons (Post, Reply, etc).
    # I should add them if I want to "reuse Mastodon".
    
    # But for now, simple list is what the previous code had.
    
    def set_focus_function(self, func):
        self.list.list.Bind(wx.EVT_SET_FOCUS, func)
        
    def set_position(self, reverse):
        if reverse:
            self.list.select_item(0)
        else:
            self.list.select_item(self.list.get_count() - 1)

    def set_focus_in_list(self):
        self.list.list.SetFocus()

class NotificationPanel(HomePanel):
    pass

class UserPanel(wx.Panel):
    def __init__(self, parent, name, account="Unknown"):
        super().__init__(parent, name=name)
        self.name = name
        self.account = account
        self.type = "user"
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        
        # List: User
        self.list = widgets.list(self, _("User"), style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_VRULES)
        self.list.set_windows_size(0, 600)
        self.list.set_size()

        # Buttons
        self.post = wx.Button(self, -1, _("Post"))
        self.actions = wx.Button(self, -1, _("Actions"))
        self.message = wx.Button(self, -1, _("Message"))
        
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSizer.Add(self.post, 0, wx.ALL, 5)
        btnSizer.Add(self.actions, 0, wx.ALL, 5)
        btnSizer.Add(self.message, 0, wx.ALL, 5)
        
        self.sizer.Add(btnSizer, 0, wx.ALL, 5)
        
        self.sizer.Add(self.list.list, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(self.sizer)

    def set_focus_function(self, func):
        self.list.list.Bind(wx.EVT_SET_FOCUS, func)
        
    def set_position(self, reverse):
        if reverse:
            self.list.select_item(0)
        else:
            self.list.select_item(self.list.get_count() - 1)

    def set_focus_in_list(self):
        self.list.list.SetFocus()

class ChatPanel(wx.Panel):
    def __init__(self, parent, name, account="Unknown"):
        super().__init__(parent, name=name)
        self.name = name
        self.account = account
        self.type = "chat"
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        # List: Participants, Last Message, Date
        self.list = widgets.list(self, _("Participants"), _("Last Message"), _("Date"), style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_VRULES)
        self.list.set_windows_size(0, 200)
        self.list.set_windows_size(1, 600)
        self.list.set_windows_size(2, 200)
        self.list.set_size()
        
        self.sizer.Add(self.list.list, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(self.sizer)

    def set_focus_function(self, func):
        self.list.list.Bind(wx.EVT_SET_FOCUS, func)

    def set_focus_in_list(self):
        self.list.list.SetFocus()

class ChatMessagePanel(HomePanel):
    def __init__(self, parent, name, account="Unknown"):
        super().__init__(parent, name, account)
        self.type = "chat_messages"
        # Adjust buttons for chat
        self.repost.Hide()
        self.like.Hide()
        self.reply.SetLabel(_("Send Message"))
        
        # Refresh columns
        self.list.list.ClearAll()
        self.list.list.InsertColumn(0, _("Sender"))
        self.list.list.InsertColumn(1, _("Message"))
        self.list.list.InsertColumn(2, _("Date"))
        self.list.set_windows_size(0, 100)
        self.list.set_windows_size(1, 400)
        self.list.set_windows_size(2, 100)
        self.list.set_size()
