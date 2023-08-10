# -*- coding: utf-8 -*-
import wx
import application

def boost_question():
    result = False
    dlg = wx.MessageDialog(None, _("Would you like to share this post?"), _("Boost"), wx.YES_NO|wx.ICON_QUESTION)
    if dlg.ShowModal() == wx.ID_YES:
        result = True
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
