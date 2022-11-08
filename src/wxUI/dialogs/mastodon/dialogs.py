# -*- coding: utf-8 -*-
import wx
import application

def boost_question():
    result = False
    dlg = wx.MessageDialog(None, _("Would you like to share this toot?"), _("Boost"), wx.YES_NO|wx.ICON_QUESTION)
    if dlg.ShowModal() == wx.ID_YES:
        result = True
    dlg.Destroy()
    return result

def delete_toot_dialog():
    result = False
    dlg = wx.MessageDialog(None, _("Do you really want to delete this toot? It will be deleted from the instance as well."), _("Delete"), wx.ICON_QUESTION|wx.YES_NO)
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

def no_toots():
    dlg = wx.MessageDialog(None, _("This user has no toots. {0} can't create a timeline.").format(application.name), _(u"Error"), wx.ICON_ERROR)
    dlg.ShowModal()
    dlg.Destroy()

def no_favs():
    dlg = wx.MessageDialog(None, _(u"This user has no favorited toots. {0} can't create a timeline.").format(application.name), _(u"Error"), wx.ICON_ERROR)
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