# -*- coding: utf-8 -*-
import wx

def retweet_question(parent):
 return wx.MessageDialog(parent, _(u"Would you like to add a comment to this tweet?"), _("Retweet"), wx.YES_NO|wx.CANCEL|wx.ICON_QUESTION).ShowModal()