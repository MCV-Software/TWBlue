# -*- coding: utf-8 -*-
import wx

class UserTimeline(wx.Dialog):
    def __init__(self, users=[], default="posts", *args, **kwargs):
        super(UserTimeline, self).__init__(parent=None, *args, **kwargs)
        panel = wx.Panel(self)
        userSizer = wx.BoxSizer()
        self.SetTitle(_("Timeline for %s") % (users[0]))
        userLabel = wx.StaticText(panel, -1, _(u"User"))
        self.cb = wx.ComboBox(panel, -1, choices=users, value=users[0])
        self.cb.SetFocus()
        self.autocompletion = wx.Button(panel, -1, _(u"&Autocomplete users"))
        userSizer.Add(userLabel, 0, wx.ALL, 5)
        userSizer.Add(self.cb, 0, wx.ALL, 5)
        userSizer.Add(self.autocompletion, 0, wx.ALL, 5)
        actionSizer = wx.BoxSizer(wx.VERTICAL)
        label2 = wx.StaticText(panel, -1, _(u"Buffer type"))
        self.posts = wx.RadioButton(panel, -1, _(u"&Posts"), style=wx.RB_GROUP)
        self.followers = wx.RadioButton(panel, -1, _(u"&Followers"))
        self.following = wx.RadioButton(panel, -1, _(u"F&ollowing"))
        self.setup_default(default)
        hSizer = wx.BoxSizer(wx.HORIZONTAL)
        hSizer.Add(label2, 0, wx.ALL, 5)
        actionSizer.Add(self.posts, 0, wx.ALL, 5)
        actionSizer.Add(self.followers, 0, wx.ALL, 5)
        actionSizer.Add(self.following, 0, wx.ALL, 5)
        hSizer.Add(actionSizer, 0, wx.ALL, 5)
        sizer = wx.BoxSizer(wx.VERTICAL)
        ok = wx.Button(panel, wx.ID_OK, _(u"&OK"))
        ok.SetDefault()
        cancel = wx.Button(panel, wx.ID_CANCEL, _(u"&Close"))
        btnsizer = wx.BoxSizer()
        btnsizer.Add(ok)
        btnsizer.Add(cancel)
        sizer.Add(userSizer)
        sizer.Add(hSizer, 0, wx.ALL, 5)
        sizer.Add(btnsizer)
        panel.SetSizer(sizer)

    def get_action(self):
        if self.posts.GetValue() == True: return "posts"
        elif self.followers.GetValue() == True: return "followers"
        elif self.following.GetValue() == True: return "following"

    def setup_default(self, default):
        if default == "posts":
            self.posts.SetValue(True)

    def get_user(self):
        return self.cb.GetValue()

    def get_position(self):
        return self.cb.GetPosition()

    def popup_menu(self, menu):
        self.PopupMenu(menu, self.cb.GetPosition())
