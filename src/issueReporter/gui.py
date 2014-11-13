# -*- coding: utf-8 -*-
############################################################
#    Copyright (c) 2013, 2014 Manuel Eduardo Cortéz Vallejo <manuel@manuelcortez.net>
#       
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
############################################################
import wx
import application
from suds.client import Client
import constants

class reportBug(wx.Dialog):
 def __init__(self, user_name):
  self.user = "informador"
  self.user_name = user_name
  self.password = "contrasena"
  self.url = application.report_bugs_url
  self.categories = [_(u"General")]
  self.reproducibilities = [_(u"always"), _(u"sometimes"), _(u"random"), _(u"have not tried"), _(u"unable to duplicate")]
  self.severities = [_(u"block"), _(u"crash"), _(u"major"), _(u"minor"), _(u"tweak"), _(u"text"), _(u"trivial"), _(u"feature")]
  wx.Dialog.__init__(self, None, -1)
  self.SetTitle(_(u"Report an error"))
  panel = wx.Panel(self)
  sizer = wx.BoxSizer(wx.VERTICAL)
  categoryLabel = wx.StaticText(panel, -1, _(u"Select a category"), size=wx.DefaultSize)
  self.category = wx.ComboBox(panel, -1, choices=self.categories, style=wx.CB_READONLY)
  self.category.SetSize(self.category.GetBestSize())
  self.category.SetSelection(0)
  categoryB = wx.BoxSizer(wx.HORIZONTAL)
  categoryB.Add(categoryLabel, 0, wx.ALL, 5)
  categoryB.Add(self.category, 0, wx.ALL, 5)
  self.category.SetFocus()
  sizer.Add(categoryB, 0, wx.ALL, 5)
  summaryLabel = wx.StaticText(panel, -1, _(u"Briefly describe what happened. You will be able to thoroughly explain it later"), size=wx.DefaultSize)
  self.summary = wx.TextCtrl(panel, -1)
  dc = wx.WindowDC(self.summary)
  dc.SetFont(self.summary.GetFont())
  self.summary.SetSize(dc.GetTextExtent("a"*80))
#  self.summary.SetFocus()
  summaryB = wx.BoxSizer(wx.HORIZONTAL)
  summaryB.Add(summaryLabel, 0, wx.ALL, 5)
  summaryB.Add(self.summary, 0, wx.ALL, 5)
  sizer.Add(summaryB, 0, wx.ALL, 5)
  descriptionLabel = wx.StaticText(panel, -1, _(u"Here, you can describe the bug in detail"), size=wx.DefaultSize)
  self.description = wx.TextCtrl(panel, -1, style=wx.TE_MULTILINE)
  dc = wx.WindowDC(self.description)
  dc.SetFont(self.description.GetFont())
  (x, y, z) = dc.GetMultiLineTextExtent("0"*2000)
  self.description.SetSize((x, y))
  descBox = wx.BoxSizer(wx.HORIZONTAL)
  descBox.Add(descriptionLabel, 0, wx.ALL, 5)
  descBox.Add(self.description, 0, wx.ALL, 5)
  sizer.Add(descBox, 0, wx.ALL, 5)
  reproducibilityLabel = wx.StaticText(panel, -1, _(u"how often does this bug happen?"), size=wx.DefaultSize)
  self.reproducibility = wx.ComboBox(panel, -1, choices=self.reproducibilities, style=wx.CB_READONLY)
  self.reproducibility.SetSelection(3)
  self.reproducibility.SetSize(self.reproducibility.GetBestSize())
  reprB = wx.BoxSizer(wx.HORIZONTAL)
  reprB.Add(reproducibilityLabel, 0, wx.ALL, 5)
  reprB.Add(self.reproducibility, 0, wx.ALL, 5)
  sizer.Add(reprB, 0, wx.ALL, 5)
  severityLabel = wx.StaticText(panel, -1, _(u"Select the importance that you think this bug has"))
  self.severity = wx.ComboBox(panel, -1, choices=self.severities, style=wx.CB_READONLY)
  self.severity.SetSize(self.severity.GetBestSize())
  self.severity.SetSelection(3)
  severityB = wx.BoxSizer(wx.HORIZONTAL)
  severityB.Add(severityLabel, 0, wx.ALL, 5)
  severityB.Add(self.severity, 0, wx.ALL, 5)
  sizer.Add(severityB, 0, wx.ALL, 5)
  self.agree = wx.CheckBox(panel, -1, _(u"I know that the TW Blue bug system will get my Twitter username to contact me and fix the bug quickly"))
  self.agree.SetValue(False)
  sizer.Add(self.agree, 0, wx.ALL, 5)
  ok = wx.Button(panel, wx.ID_OK, _(u"Send report"))
  ok.Bind(wx.EVT_BUTTON, self.onSend)
  ok.SetDefault()
  cancel = wx.Button(panel, wx.ID_CANCEL, _(u"Cancel"))
  btnBox = wx.BoxSizer(wx.HORIZONTAL)
  btnBox.Add(ok, 0, wx.ALL, 5)
  btnBox.Add(cancel, 0, wx.ALL, 5)
  sizer.Add(btnBox, 0, wx.ALL, 5)
  panel.SetSizer(sizer)
  self.SetClientSize(sizer.CalcMin())
  
 def onSend(self, ev):
  if self.summary.GetValue() == "" or self.description.GetValue() == "":
   wx.MessageDialog(self, _(u"You must fill out both fields"), _(u"Error"), wx.OK|wx.ICON_ERROR).ShowModal()
   return
  if self.agree.GetValue() == False:
   wx.MessageDialog(self, _(u"You need to mark the checkbox to provide us your twitter username to contact to you if is necessary."), _(u"Error"), wx.ICON_ERROR).ShowModal()
   return
  try:
   client = Client(self.url)
   issue = client.factory.create('IssueData')
   issue.project.name = "TW Blue"
   issue.project.id = 0
   issue.summary = self.summary.GetValue(),
   issue.description = "Reported by @%s\n\n" % (self.user_name) + self.description.GetValue()
   issue.category = constants.categories[self.category.GetSelection()]
   issue.reproducibility.name = constants.reproducibilities[self.reproducibility.GetSelection()]
   issue.severity.name = constants.severities[self.severity.GetSelection()]
   issue.priority.name = "normal"
   issue.view_state.name = "public"
   issue.resolution.name = "open"
   issue.projection.name = "none"
   issue.eta.name = "eta"
   issue.status.name = "new"
   id = client.service.mc_issue_add(self.user, self.password, issue)
   wx.MessageDialog(self, _(u"Thanks for reporting this bug! In future versions, you may be able to find it in the changes list. You've reported the bug number %i") % (id), _(u"reported"), wx.OK).ShowModal()
   self.EndModal(wx.ID_OK)
  except:
   wx.MessageDialog(self, _(u"Something unexpected occurred while trying to report the bug. Please, try again later"), _(u"Error while reporting"), wx.ICON_ERROR|wx.OK).ShowModal()
   self.EndModal(wx.ID_CANCEL)