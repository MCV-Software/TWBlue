# -*- coding: utf-8 -*-
import wx

class CommunityTimeline(wx.Dialog):
    def __init__(self, *args, **kwargs):
        super(CommunityTimeline, self).__init__(parent=None, *args, **kwargs)
        panel = wx.Panel(self)
        communitySizer = wx.BoxSizer()
        self.SetTitle(_("Create community timeline"))
        communityLabel = wx.StaticText(panel, -1, _("Community URL"))
        self.url = wx.TextCtrl(panel, -1)
        self.url.SetFocus()
        communitySizer.Add(communityLabel, 0, wx.ALL, 5)
        communitySizer.Add(self.url, 0, wx.ALL, 5)
        actionSizer = wx.BoxSizer(wx.VERTICAL)
        label2 = wx.StaticText(panel, -1, _(u"Buffer type"))
        self.local= wx.RadioButton(panel, -1, _("&Local timeline"), style=wx.RB_GROUP)
        self.federated= wx.RadioButton(panel, -1, _("&Federated Timeline"))
        hSizer = wx.BoxSizer(wx.HORIZONTAL)
        hSizer.Add(label2, 0, wx.ALL, 5)
        actionSizer.Add(self.local, 0, wx.ALL, 5)
        actionSizer.Add(self.federated, 0, wx.ALL, 5)
        hSizer.Add(actionSizer, 0, wx.ALL, 5)
        sizer = wx.BoxSizer(wx.VERTICAL)
        ok = wx.Button(panel, wx.ID_OK, _(u"&OK"))
        ok.SetDefault()
        cancel = wx.Button(panel, wx.ID_CANCEL, _(u"&Close"))
        btnsizer = wx.BoxSizer()
        btnsizer.Add(ok)
        btnsizer.Add(cancel)
        sizer.Add(communitySizer)
        sizer.Add(hSizer, 0, wx.ALL, 5)
        sizer.Add(btnsizer)
        panel.SetSizer(sizer)

    def get_action(self):
        if self.local.GetValue() == True: return "local"
        elif self.federated.GetValue() == True: return "federated"
