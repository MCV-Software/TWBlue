# -*- coding: utf-8 -*-
""" Attach dialog. Taken from socializer: https://github.com/manuelcortez/socializer"""
import wx
import widgetUtils
from multiplatform_widgets  import widgets 

class attachDialog(widgetUtils.BaseDialog):
	def __init__(self):
		super(attachDialog, self).__init__(None,  title=_("Add an attachment"))
		panel = wx.Panel(self)
		sizer = wx.BoxSizer(wx.VERTICAL)
		lbl1 = wx.StaticText(panel, wx.NewId(), _("Attachments"))
		self.attachments = widgets.list(panel, _("Type"), _("Title"), style=wx.LC_REPORT)
		box = wx.BoxSizer(wx.HORIZONTAL)
		box.Add(lbl1, 0, wx.ALL, 5)
		box.Add(self.attachments.list, 0, wx.ALL, 5)
		sizer.Add(box, 0, wx.ALL, 5)
		static = wx.StaticBox(panel, label=_("Add attachments"))
		self.photo = wx.Button(panel, wx.NewId(), _("&Photo"))
		self.remove = wx.Button(panel, wx.NewId(), _("Remove attachment"))
		self.remove.Enable(False)
		btnsizer = wx.StaticBoxSizer(static, wx.HORIZONTAL)
		btnsizer.Add(self.photo, 0, wx.ALL, 5)
		sizer.Add(btnsizer, 0, wx.ALL, 5)
		ok = wx.Button(panel, wx.ID_OK)
		ok.SetDefault()
		cancelBtn = wx.Button(panel, wx.ID_CANCEL)
		btnSizer = wx.BoxSizer()
		btnSizer.Add(ok, 0, wx.ALL, 5)
		btnSizer.Add(cancelBtn, 0, wx.ALL, 5)
		sizer.Add(btnSizer, 0, wx.ALL, 5)
		panel.SetSizer(sizer)
		self.SetClientSize(sizer.CalcMin())

	def get_image(self):
		openFileDialog = wx.FileDialog(self, _("Select the picture to be uploaded"), "", "", _("Image files (*.png, *.jpg, *.gif)|*.png; *.jpg; *.gif"), wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
		if openFileDialog.ShowModal() == wx.ID_CANCEL:
			return (None, None)
		dsc = self.ask_description()
		return (openFileDialog.GetPath(), dsc)

	def ask_description(self):
		dlg = wx.TextEntryDialog(self, _("please provide a description"), _("Description"), defaultValue="")
		dlg.ShowModal()
		result = dlg.GetValue()
		dlg.Destroy()
		return result
