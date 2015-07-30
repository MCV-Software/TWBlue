# -*- coding: utf-8 -*-
import wx
import application
def retweet_as_link(parent):
 return wx.MessageDialog(parent, _(u"This retweet is over 140 characters. Would you like to post it as a mention to the poster with your comments and a link to the original tweet?"), application.name, wx.YES_NO|wx.ICON_QUESTION).ShowModal()

def retweet_question(parent):
 return wx.MessageDialog(parent, _(u"Would you like to add a comment to this tweet?"), _("Retweet"), wx.YES_NO|wx.CANCEL|wx.ICON_QUESTION).ShowModal()

def delete_tweet_dialog(parent):
 return wx.MessageDialog(parent, _(u"Do you really want to delete this tweet? It will be deleted from Twitter as well."), _(u"Delete"), wx.ICON_QUESTION|wx.YES_NO).ShowModal()

def exit_dialog(parent):
 dlg = wx.MessageDialog(parent, _(u"Do you really want to close {0}?").format(application.name,), _(u"Exit"), wx.YES_NO|wx.ICON_QUESTION)
 return dlg.ShowModal()

def needs_restart():
 wx.MessageDialog(None, _(u" {0} must be restarted for these changes to take effect.").format(application.name,), _("Restart {0} ").format(application.name,), wx.OK).ShowModal()

def delete_user_from_db():
 return wx.MessageDialog(None, _(u"Are you sure you want to delete this user from the database? This user will not appear in autocomplete results anymore."), _(u"Confirm"), wx.YES_NO|wx.ICON_QUESTION).ShowModal()

def get_ignored_client():
 entry = wx.TextEntryDialog(None, _(u"Enter the name of the client : "), _(u"Add client"))
 if entry.ShowModal() == wx.ID_OK:
  return entry.GetValue()
 return None

def clear_list():
 dlg = wx.MessageDialog(None, _(u"Do you really want to empty this buffer? It's  items will be removed from the list but not from Twitter"), _(u"Empty buffer"), wx.ICON_QUESTION|wx.YES_NO)
 return dlg.ShowModal()

def remove_buffer():
 return wx.MessageDialog(None, _(u"Do you really want to destroy this buffer?"), _(u"Attention"), style=wx.ICON_QUESTION|wx.YES_NO).ShowModal()

def user_not_exist():
 return wx.MessageDialog(None, _(u"That user does not exist"), _(u"Error"), wx.ICON_ERROR).ShowModal()

def timeline_exist():
 return wx.MessageDialog(None, _(u"A timeline for this user already exists. You can't open another"), _(u"Existing timeline"), wx.ICON_ERROR).ShowModal()

def no_tweets():
 return wx.MessageDialog(None, _(u"This user has no tweets, so you can't open a timeline for them."), _(u"Error!"), wx.ICON_ERROR).ShowModal()

def protected_user():
 return wx.MessageDialog(None, _(u"This is a protected Twitter user, which means you can't open a timeline using the Streaming API. The user's tweets will not update due to a twitter policy. Do you want to continue?"), _(u"Warning"), wx.ICON_WARNING|wx.YES_NO).ShowModal()

def no_following():
 return wx.MessageDialog(None, _(u"This is a protected user account, you need to follow this user to view their tweets or favorites."), _(u"Error"), wx.ICON_ERROR).ShowModal()

def donation():
 dlg = wx.MessageDialog(None, _(u"If you like " + application.name + ", we need your help to keep it going. Help us by donating to the project. This will help us pay for the server, the domain and some other things to ensure that " + application.name + " will be actively maintained. Your donation will give us the means to continue the development of " + application.name + ", and to keep " + application.name + " free. Would you like to donate now?"), _(u"We need your help"), wx.ICON_QUESTION|wx.YES_NO)
 return dlg.ShowModal()
