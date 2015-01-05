# -*- coding: utf-8 -*-
import wx

def retweet_question(parent):
 return wx.MessageDialog(parent, _(u"Would you like to add a comment to this tweet?"), _("Retweet"), wx.YES_NO|wx.CANCEL|wx.ICON_QUESTION).ShowModal()

def delete_tweet_dialog(parent):
 return wx.MessageDialog(parent, _(u"Do you really want to delete this message? It will be eliminated from Twitter as well."), _(u"Delete"), wx.ICON_QUESTION|wx.YES_NO).ShowModal()
