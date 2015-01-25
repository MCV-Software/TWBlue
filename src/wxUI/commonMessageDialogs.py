# -*- coding: utf-8 -*-
import wx

def retweet_question(parent):
 return wx.MessageDialog(parent, _(u"Would you like to add a comment to this tweet?"), _("Retweet"), wx.YES_NO|wx.CANCEL|wx.ICON_QUESTION).ShowModal()

def delete_tweet_dialog(parent):
 return wx.MessageDialog(parent, _(u"Do you really want to delete this message? It will be eliminated from Twitter as well."), _(u"Delete"), wx.ICON_QUESTION|wx.YES_NO).ShowModal()

def exit_dialog():
 dlg = wx.MessageDialog(None, _(u"Do you really want to close TW Blue?"), _(u"Exit"), wx.YES_NO|wx.ICON_QUESTION)
 return dlg.ShowModal()

def needs_restart():
 wx.MessageDialog(None, _(u"The application requires to be restarted to save these changes. Press OK to do it now."), _("Restart TW Blue"), wx.OK).ShowModal()