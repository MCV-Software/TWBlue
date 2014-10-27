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
import platform
import output
import config
import gui
from multiplatform_widgets import widgets
from twython import TwythonError
from twitter import compose, utils

class listViewer(wx.Dialog):

 def __init__(self, parent):
  self.twitter = parent.twitter
  self.db = parent.db
  self.nb = parent.nb
  self.parent = parent
  wx.Dialog.__init__(self, None)
  self.SetTitle(_(u"Lists manager"))
  panel = wx.Panel(self)
  label = wx.StaticText(panel, -1, _(u"Lists"))
  self.lista = widgets.list(panel, _(u"List"), _(u"Description"), _(u"Owner"), _(u"Members"), _(u"mode"), size=(800, 800), style=wx.LC_REPORT|wx.LC_SINGLE_SEL)
  self.lista.list.SetFocus()
  sizer = wx.BoxSizer(wx.VERTICAL)
  sizer.Add(label)
  sizer.Add(self.lista.list)
  self.createBtn = wx.Button(panel, wx.NewId(), _(u"Create a new list"))
  self.createBtn.Bind(wx.EVT_BUTTON, self.onGo)
  self.editBtn = wx.Button(panel, -1, _(u"Edit"))
  self.Bind(wx.EVT_BUTTON, self.onEdit, self.editBtn)
  self.deleteBtn = wx.Button(panel, -1, _(u"Remove"))
  self.Bind(wx.EVT_BUTTON, self.onDelete, self.deleteBtn)
  self.view = wx.Button(panel, -1, _(u"Open in buffer"))
  self.Bind(wx.EVT_BUTTON, self.onView, self.view)
#  self.members = wx.Button(panel, -1, _(u"View members"))
#  self.members.Disable()
#  self.subscriptors = wx.Button(panel, -1, _(u"View subscribers"))
#  self.subscriptors.Disable()
#  self.get_linkBtn = wx.Button(panel, -1, _(u"Get link for the list"))
#  self.get_linkBtn.Bind(wx.EVT_BUTTON, self.onGetLink)
  self.cancelBtn = wx.Button(panel, wx.ID_CANCEL)
  btnSizer = wx.BoxSizer()
  btnSizer.Add(self.createBtn)
  btnSizer.Add(self.editBtn)
  btnSizer.Add(self.cancelBtn)
  panel.SetSizer(sizer)
  self.populate_list()
  self.lista.select_item(0)

 def onGo(self, ev):
  ev.Skip()
  dlg = createListDialog()
  if dlg.ShowModal() == wx.ID_OK:
   name = dlg.name.GetValue()
   description = dlg.description.GetValue()
   if dlg.public.GetValue() == True: mode = "public"
   else: mode = "private"
   try:
    new_list = self.twitter.twitter.create_list(name=name, description=description, mode=mode)
    self.db.settings["lists"].append(new_list)
    self.lista.insert_item(False, *compose.compose_list(new_list))
   except TwythonError as e:
    output.speak("error %s: %s" % (e.status_code, e.msg))
  else:
   return
  dlg.Destroy()

 def onEdit(self, ev):
  ev.Skip()
  if self.lista.get_count() == 0: return
  list = self.db.settings["lists"][self.lista.get_selected()]
  dlg = editListDialog(list)
  if dlg.ShowModal() == wx.ID_OK:
   name = dlg.name.GetValue()
   description = dlg.description.GetValue()
   if dlg.public.GetValue() == True: mode = "public"
   else: mode = "private"
   try:
    self.twitter.twitter.update_list(list_id=self.lists[self.get_selected()]["id"], name=name, description=description, mode=mode)
   except TwythonError as e:
    output.speak("error %s: %s" % (e.error_code, e.msg))
  else:
   return
  dlg.Destroy()

 def onDelete(self, ev):
  ev.Skip()
  if self.lista.get_count() == 0: return
  list = self.db.settings["lists"][self.lista.get_selected()]["id"]
  dlg = wx.MessageDialog(self, _("Do you really want to delete this list?"), _("Delete"), wx.YES_NO)
  if dlg.ShowModal() == wx.ID_YES:
   try:
    self.twitter.twitter.delete_list(list_id=list)
    self.db.settings["lists"].pop(self.lista.get_selected())
    self.remove_item(self.lista.get_selected())
   except TwythonError as e:
    output.speak("error %s: %s" % (e.error_code, e.msg))
  dlg.Destroy()

 def onView(self, ev):
  ev.Skip()
  if self.lista.get_count() == 0: return
  list_id = self.db.settings["lists"][self.lista.get_selected()]["id"]
  list_updated = self.twitter.twitter.get_specific_list(list_id=list_id)
  self.db.settings["lists"][self.lista.get_selected()] = list_updated
  if list_updated["slug"] not in config.main["other_buffers"]["lists"]:
   config.main["other_buffers"]["lists"].append(list_updated["slug"])
   output.speak(_(u"List opened"))
  else:
   output.speak(_(u"This list is arready opened."))
   return
  listUI = gui.buffers.lists.listPanel(self.nb, self.parent, list_updated["slug"]+"-list", argumento=utils.find_list(list_updated["slug"], self.db.settings["lists"]))
  self.nb.AddPage(listUI, _(u"List for %s") % (list_updated["slug"],))
  self.db.settings["buffers"].append(list_updated["slug"]+"-list")
  num = listUI.start_streams()
  listUI.put_items(num)
  listUI.sound = "tweet_timeline.wav"
  self.parent.stream2.disconnect()
  del self.parent.stream2
  self.parent.get_tls()

 def populate_list(self):
  for i in self.db.settings["lists"]:
   item = compose.compose_list(i)
   self.lista.insert_item(False, *item)

class userListViewer(listViewer):
 def __init__(self, parent, username):
  self.username = username
  super(userListViewer, self).__init__(parent)
  self.SetTitle(_(u"Viewing lists for %s") % (self.username))
  self.createBtn.SetLabel(_(u"Subscribe"))
  self.deleteBtn.SetLabel(_(u"Unsubscribe"))
  self.editBtn.Disable()
  self.view.Disable()

 def populate_list(self):
  self.lists =   self.twitter.twitter.show_owned_lists(screen_name=self.username, count=200)["lists"]
  for i in self.lists:
   item = compose.compose_list(i)
   self.lista.insert_item(False, *item)

 def onGo(self, ev):
  list_id = self.lists[self.lista.get_selected()]["id"]
  try:
   list = self.twitter.twitter.subscribe_to_list(list_id=list_id)
   item = utils.find_item(list["id"], self.db.settings["lists"])
   self.db.settings["lists"].append(list)
  except TwythonError as e:
   output.speak("error %s: %s" % (e.status_code, e.msg))

class createListDialog(wx.Dialog):

 def __init__(self):
  wx.Dialog.__init__(self, None, size=(450, 400))
  self.SetTitle(_(u"Create a new list"))
  panel = wx.Panel(self)
  sizer = wx.BoxSizer(wx.VERTICAL)
  name = wx.StaticText(panel, -1, _(u"Name (20 characters maximun)"))
  self.name = wx.TextCtrl(panel, -1)
  nameSizer = wx.BoxSizer(wx.HORIZONTAL)
  nameSizer.Add(name)
  nameSizer.Add(self.name)
  description = wx.StaticText(panel, -1, _(u"Description"))
  self.description = wx.TextCtrl(panel, -1)
  descriptionSizer = wx.BoxSizer(wx.HORIZONTAL)
  descriptionSizer.Add(description)
  descriptionSizer.Add(self.description)
  mode = wx.StaticText(panel, -1, _(u"Mode"))
  self.public = wx.RadioButton(panel, -1, _(u"Public"), style=wx.RB_GROUP)
  self.private = wx.RadioButton(panel, -1, _(u"Private"))
  modeBox = wx.BoxSizer(wx.HORIZONTAL)
  modeBox.Add(mode)
  modeBox.Add(self.public)
  modeBox.Add(self.private)
  ok = wx.Button(panel, wx.ID_OK)
  ok.SetDefault()
  cancel = wx.Button(panel, wx.ID_CANCEL)
  btnBox = wx.BoxSizer(wx.HORIZONTAL)
  btnBox.Add(ok)
  btnBox.Add(cancel)
  sizer.Add(nameSizer)
  sizer.Add(descriptionSizer)
  sizer.Add(modeBox)
  sizer.Add(btnBox)

class editListDialog(createListDialog):

 def __init__(self, list):
  createListDialog.__init__(self)
  self.SetTitle(_(u"Editing the list %s") % (list["name"]))
  self.name.ChangeValue(list["name"])
  self.description.ChangeValue(list["description"])
  if list["mode"] == "public":
   self.public.SetValue(True)
  else:
   self.private.SetValue(True)

class addUserListDialog(listViewer):
 def __init__(self, parent):
  listViewer.__init__(self, parent)
  self.SetTitle(_(u"Select a list to add the user"))
  self.createBtn.SetLabel(_(u"Add"))
  self.createBtn.SetDefault()
  self.editBtn.Disable()
  self.view.Disable()
#  self.subscriptors.Disable()
#  self.members.Disable()
  self.deleteBtn.Disable()

 def onGo(self, ev):
  self.EndModal(wx.ID_OK)

class removeUserListDialog(listViewer):
 def __init__(self, parent):
  listViewer.__init__(self, parent)
  self.SetTitle(_(u"Select a list to remove the user"))
  self.createBtn.SetLabel(_(u"Remove"))
  self.createBtn.SetDefault()
  self.editBtn.Disable()
  self.view.Disable()
#  self.subscriptors.Disable()
#  self.members.Disable()
  self.deleteBtn.Disable()

 def onGo(self, ev):
  self.EndModal(wx.ID_OK)