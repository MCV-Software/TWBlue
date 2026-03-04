# -*- coding: utf-8 -*-
"""Context menus for Bluesky buffers."""

import wx


class baseMenu(wx.Menu):
    """Base context menu for Bluesky posts."""

    def __init__(self):
        super(baseMenu, self).__init__()
        self.repost = wx.MenuItem(self, wx.ID_ANY, _("&Repost"))
        self.Append(self.repost)
        self.quote = wx.MenuItem(self, wx.ID_ANY, _("&Quote"))
        self.Append(self.quote)
        self.reply = wx.MenuItem(self, wx.ID_ANY, _("Re&ply"))
        self.Append(self.reply)
        self.like = wx.MenuItem(self, wx.ID_ANY, _("&Like"))
        self.Append(self.like)
        self.unlike = wx.MenuItem(self, wx.ID_ANY, _("&Unlike"))
        self.Append(self.unlike)
        self.openUrl = wx.MenuItem(self, wx.ID_ANY, _("&Open URL"))
        self.Append(self.openUrl)
        self.openInBrowser = wx.MenuItem(self, wx.ID_ANY, _("Open in &browser"))
        self.Append(self.openInBrowser)
        self.view = wx.MenuItem(self, wx.ID_ANY, _("&Show post"))
        self.Append(self.view)
        self.copy = wx.MenuItem(self, wx.ID_ANY, _("&Copy to clipboard"))
        self.Append(self.copy)
        self.remove = wx.MenuItem(self, wx.ID_ANY, _("&Delete"))
        self.Append(self.remove)
        self.userActions = wx.MenuItem(self, wx.ID_ANY, _("&User actions..."))
        self.Append(self.userActions)


class notificationMenu(wx.Menu):
    """Context menu for Bluesky notifications."""

    def __init__(self, notification_type="like"):
        super(notificationMenu, self).__init__()
        # Notification types that have associated posts
        post_types = ["like", "repost", "mention", "reply", "quote"]

        if notification_type in post_types:
            self.repost = wx.MenuItem(self, wx.ID_ANY, _("&Repost"))
            self.Append(self.repost)
            self.reply = wx.MenuItem(self, wx.ID_ANY, _("Re&ply"))
            self.Append(self.reply)
            self.like = wx.MenuItem(self, wx.ID_ANY, _("&Like"))
            self.Append(self.like)
            self.openUrl = wx.MenuItem(self, wx.ID_ANY, _("&Open URL"))
            self.Append(self.openUrl)

        self.openInBrowser = wx.MenuItem(self, wx.ID_ANY, _("Open in &browser"))
        self.Append(self.openInBrowser)
        self.view = wx.MenuItem(self, wx.ID_ANY, _("&Show post"))
        self.Append(self.view)
        self.copy = wx.MenuItem(self, wx.ID_ANY, _("&Copy to clipboard"))
        self.Append(self.copy)
        self.userActions = wx.MenuItem(self, wx.ID_ANY, _("&User actions..."))
        self.Append(self.userActions)


class userMenu(wx.Menu):
    """Context menu for Bluesky user lists."""

    def __init__(self):
        super(userMenu, self).__init__()
        self.timeline = wx.MenuItem(self, wx.ID_ANY, _("View &timeline"))
        self.Append(self.timeline)
        self.followers = wx.MenuItem(self, wx.ID_ANY, _("View f&ollowers"))
        self.Append(self.followers)
        self.following = wx.MenuItem(self, wx.ID_ANY, _("View &following"))
        self.Append(self.following)
        self.dm = wx.MenuItem(self, wx.ID_ANY, _("Send &message"))
        self.Append(self.dm)
        self.view = wx.MenuItem(self, wx.ID_ANY, _("View &profile"))
        self.Append(self.view)
        self.copy = wx.MenuItem(self, wx.ID_ANY, _("&Copy to clipboard"))
        self.Append(self.copy)
        self.userActions = wx.MenuItem(self, wx.ID_ANY, _("&User actions..."))
        self.Append(self.userActions)


class chatMenu(wx.Menu):
    """Context menu for Bluesky chat messages."""

    def __init__(self):
        super(chatMenu, self).__init__()
        self.reply = wx.MenuItem(self, wx.ID_ANY, _("&Reply"))
        self.Append(self.reply)
        self.copy = wx.MenuItem(self, wx.ID_ANY, _("&Copy to clipboard"))
        self.Append(self.copy)
        self.view = wx.MenuItem(self, wx.ID_ANY, _("&Show message"))
        self.Append(self.view)
        self.userActions = wx.MenuItem(self, wx.ID_ANY, _("&User actions..."))
        self.Append(self.userActions)
