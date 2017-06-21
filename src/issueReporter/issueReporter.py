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

from builtins import object
import keys
import wx
from . import wx_ui
import widgetUtils
import application
from suds.client import Client
from . import constants

class reportBug(object):
 def __init__(self, user_name):
  self.user_name = user_name
  self.categories = [_("General")]
  self.reproducibilities = [_("always"), _("sometimes"), _("random"), _("have not tried"), _("unable to duplicate")]
  self.severities = [_("block"), _("crash"), _("major"), _("minor"), _("tweak"), _("text"), _("trivial"), _("feature")]
  self.dialog = wx_ui.reportBugDialog(self.categories, self.reproducibilities, self.severities)
  widgetUtils.connect_event(self.dialog.ok, widgetUtils.BUTTON_PRESSED, self.send)
  self.dialog.get_response()

 def send(self, *args, **kwargs):
  if self.dialog.get("summary") == "" or self.dialog.get("description") == "":
   self.dialog.no_filled()
   return
  if self.dialog.get("agree") == False:
   self.dialog.no_checkbox()
   return
  try:
   client = Client(application.report_bugs_url)
   issue = client.factory.create('IssueData')
   issue.project.name = application.name
   issue.project.id = 0
   issue.summary = self.dialog.get("summary"),
   issue.description = "Reported by @%s on version %s (snapshot = %s)\n\n" % (self.user_name, application.version, application.snapshot) + self.dialog.get("description")
   # to do: Create getters for category, severity and reproducibility in wx_UI.
   issue.category = constants.categories[self.dialog.category.GetSelection()]
   issue.reproducibility.name = constants.reproducibilities[self.dialog.reproducibility.GetSelection()]
   issue.severity.name = constants.severities[self.dialog.severity.GetSelection()]
   issue.priority.name = "normal"
   issue.view_state.name = "public"
   issue.resolution.name = "open"
   issue.projection.name = "none"
   issue.eta.name = "eta"
   issue.status.name = "new"
   id = client.service.mc_issue_add(keys.keyring.get("bts_user"), keys.keyring.get("bts_password"), issue)
   self.dialog.success(id)
  except:
   self.dialog.error()
