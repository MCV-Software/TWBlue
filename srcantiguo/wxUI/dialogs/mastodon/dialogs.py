# -*- coding: utf-8 -*-
import wx
import application

class BoostDialog(wx.Dialog):
    def __init__(self):
        super(BoostDialog, self).__init__(None, title=_("Boost"))
        p = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        lbl = wx.StaticText(p, wx.ID_ANY, _("What would you like to do with this post?"))
        sizer.Add(lbl, 0, wx.ALL, 10)
        
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_boost = wx.Button(p, wx.ID_ANY, _("Boost"))
        self.btn_quote = wx.Button(p, wx.ID_ANY, _("Quote"))
        self.btn_cancel = wx.Button(p, wx.ID_CANCEL, _("Cancel"))
        
        btn_sizer.Add(self.btn_boost, 0, wx.ALL, 5)
        btn_sizer.Add(self.btn_quote, 0, wx.ALL, 5)
        btn_sizer.Add(self.btn_cancel, 0, wx.ALL, 5)
        
        sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER)
        p.SetSizer(sizer)
        sizer.Fit(self)
        
        self.btn_boost.Bind(wx.EVT_BUTTON, self.on_boost)
        self.btn_quote.Bind(wx.EVT_BUTTON, self.on_quote)
        self.result = 0

    def on_boost(self, event):
        self.result = 1
        self.EndModal(wx.ID_OK)

    def on_quote(self, event):
        self.result = 2
        self.EndModal(wx.ID_OK)

def boost_question():
    dlg = BoostDialog()
    dlg.ShowModal()
    result = dlg.result
    dlg.Destroy()
    return result

def delete_post_dialog():
    result = False
    dlg = wx.MessageDialog(None, _("Do you really want to delete this post? It will be deleted from the instance as well."), _("Delete"), wx.ICON_QUESTION|wx.YES_NO)
    if dlg.ShowModal() == wx.ID_YES:
        result = True
    dlg.Destroy()
    return result

def delete_notification_dialog():
    result = False
    dlg = wx.MessageDialog(None, _("Are you sure you want to dismiss this notification? If you dismiss a mention notification, it also disappears from your mentions buffer. The post is not going to be deleted from the instance, though."), _("Dismiss"), wx.ICON_QUESTION|wx.YES_NO)
    if dlg.ShowModal() == wx.ID_YES:
        result = True
    dlg.Destroy()
    return result

def clear_list():
    result = False
    dlg = wx.MessageDialog(None, _("Do you really want to empty this buffer? It's  items will be removed from the list but not from the instance"), _(u"Empty buffer"), wx.ICON_QUESTION|wx.YES_NO)
    if dlg.ShowModal() == wx.ID_YES:
        result = True
    dlg.Destroy()
    return result

def no_posts():
    dlg = wx.MessageDialog(None, _("This user has no posts. {0} can't create a timeline.").format(application.name), _(u"Error"), wx.ICON_ERROR)
    dlg.ShowModal()
    dlg.Destroy()

def no_favs():
    dlg = wx.MessageDialog(None, _(u"This user has no favorited posts. {0} can't create a timeline.").format(application.name), _(u"Error"), wx.ICON_ERROR)
    dlg.ShowModal()
    dlg.Destroy()

def no_followers():
    dlg = wx.MessageDialog(None, _(u"This user has no followers yet. {0} can't create a timeline.").format(application.name), _(u"Error"), wx.ICON_ERROR)
    dlg.ShowModal()
    dlg.Destroy()

def no_following():
    dlg = wx.MessageDialog(None, _("This user is not following anyone. {0} can't create a timeline.").format(application.name), _(u"Error"), wx.ICON_ERROR)
    dlg.ShowModal()
    dlg.Destroy()

    dlg.Destroy()

def no_user():
    dlg = wx.MessageDialog(None, _("The focused item has no user in it. {} ca't open a user profile").format(application.name), _(u"Error"), wx.ICON_ERROR)
    dlg.ShowModal()
    dlg.Destroy()
