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
import widgetUtils
import application
class reportBugDialog(widgetUtils.BaseDialog):
 def __init__(self, categories, reproducibilities, severities):
  super(reportBugDialog, self).__init__(parent=None, id=wx.NewId())
  self.SetTitle(_("Report an error"))
  panel = wx.Panel(self)
  sizer = wx.BoxSizer(wx.VERTICAL)
  categoryLabel = wx.StaticText(panel, -1, _("Select a category"), size=wx.DefaultSize)
  self.category = wx.ComboBox(panel, -1, choices=categories, style=wx.CB_READONLY)
  self.category.SetSelection(0)
  categoryB = wx.BoxSizer(wx.HORIZONTAL)
  categoryB.Add(categoryLabel, 0, wx.ALL, 5)
  categoryB.Add(self.category, 0, wx.ALL, 5)
  self.category.SetFocus()
  sizer.Add(categoryB, 0, wx.ALL, 5)
  summaryLabel = wx.StaticText(panel, -1, _("Briefly describe what happened. You will be able to thoroughly explain it later"), size=wx.DefaultSize)
  self.summary = wx.TextCtrl(panel, -1)
  dc = wx.WindowDC(self.summary)
  dc.SetFont(self.summary.GetFont())
  self.summary.SetSize(dc.GetTextExtent("a"*80))
  summaryB = wx.BoxSizer(wx.HORIZONTAL)
  summaryB.Add(summaryLabel, 0, wx.ALL, 5)
  summaryB.Add(self.summary, 0, wx.ALL, 5)
  sizer.Add(summaryB, 0, wx.ALL, 5)
  descriptionLabel = wx.StaticText(panel, -1, _("Here, you can describe the bug in detail"), size=wx.DefaultSize)
  self.description = wx.TextCtrl(panel, -1, style=wx.TE_MULTILINE)
  dc = wx.WindowDC(self.description)
  dc.SetFont(self.description.GetFont())
  (x, y, z) = dc.GetMultiLineTextExtent("0"*2000)
  self.description.SetSize((x, y))
  descBox = wx.BoxSizer(wx.HORIZONTAL)
  descBox.Add(descriptionLabel, 0, wx.ALL, 5)
  descBox.Add(self.description, 0, wx.ALL, 5)
  sizer.Add(descBox, 0, wx.ALL, 5)
  reproducibilityLabel = wx.StaticText(panel, -1, _("how often does this bug happen?"), size=wx.DefaultSize)
  self.reproducibility = wx.ComboBox(panel, -1, choices=reproducibilities, style=wx.CB_READONLY)
  self.reproducibility.SetSelection(3)
  reprB = wx.BoxSizer(wx.HORIZONTAL)
  reprB.Add(reproducibilityLabel, 0, wx.ALL, 5)
  reprB.Add(self.reproducibility, 0, wx.ALL, 5)
  sizer.Add(reprB, 0, wx.ALL, 5)
  severityLabel = wx.StaticText(panel, -1, _("Select the importance that you think this bug has"))
  self.severity = wx.ComboBox(panel, -1, choices=severities, style=wx.CB_READONLY)
  self.severity.SetSelection(3)
  severityB = wx.BoxSizer(wx.HORIZONTAL)
  severityB.Add(severityLabel, 0, wx.ALL, 5)
  severityB.Add(self.severity, 0, wx.ALL, 5)
  sizer.Add(severityB, 0, wx.ALL, 5)
  self.agree = wx.CheckBox(panel, -1, _("I know that the {0} bug system will get my Twitter username to contact me and fix the bug quickly").format(application.name,))
  self.agree.SetValue(False)
  sizer.Add(self.agree, 0, wx.ALL, 5)
  self.ok = wx.Button(panel, wx.ID_OK, _("Send report"))
  self.ok.SetDefault()
  cancel = wx.Button(panel, wx.ID_CANCEL, _("Cancel"))
  btnBox = wx.BoxSizer(wx.HORIZONTAL)
  btnBox.Add(self.ok, 0, wx.ALL, 5)
  btnBox.Add(cancel, 0, wx.ALL, 5)
  sizer.Add(btnBox, 0, wx.ALL, 5)
  panel.SetSizer(sizer)
  self.SetClientSize(sizer.CalcMin())

 def no_filled(self):
  wx.MessageDialog(self, _("You must fill out both fields"), _("Error"), wx.OK|wx.ICON_ERROR).ShowModal()

 def no_checkbox(self):
  wx.MessageDialog(self, _("You need to mark the checkbox to provide us your twitter username to contact you if it is necessary."), _("Error"), wx.ICON_ERROR).ShowModal()

 def success(self, id):
  wx.MessageDialog(self, _("Thanks for reporting this bug! In future versions, you may be able to find it in the changes list. You've reported the bug number %i") % (id), _("reported"), wx.OK).ShowModal()
  self.EndModal(wx.ID_OK)

 def error(self):
  wx.MessageDialog(self, _("Something unexpected occurred while trying to report the bug. Please, try again later"), _("Error while reporting"), wx.ICON_ERROR|wx.OK).ShowModal()
  self.EndModal(wx.ID_CANCEL)