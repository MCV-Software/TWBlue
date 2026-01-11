# -*- coding: utf-8 -*-
import wx
import widgetUtils
import application

class autocompletionScanDialog(widgetUtils.BaseDialog):
    def __init__(self):
        super(autocompletionScanDialog, self).__init__(parent=None, id=-1, title=_(u"Autocomplete users' settings"))
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.followers = wx.CheckBox(panel, -1, _("Add &followers to database"))
        self.friends = wx.CheckBox(panel, -1, _("Add  f&ollowing to database"))
        sizer.Add(self.followers, 0, wx.ALL, 5)
        sizer.Add(self.friends, 0, wx.ALL, 5)
        ok = wx.Button(panel, wx.ID_OK)
        cancel = wx.Button(panel, wx.ID_CANCEL)
        sizerBtn = wx.BoxSizer(wx.HORIZONTAL)
        sizerBtn.Add(ok, 0, wx.ALL, 5)
        sizer.Add(cancel, 0, wx.ALL, 5)
        sizer.Add(sizerBtn, 0, wx.ALL, 5)
        panel.SetSizer(sizer)
        self.SetClientSize(sizer.CalcMin())

class autocompletionScanProgressDialog(widgetUtils.BaseDialog):
    def __init__(self, *args, **kwargs):
        super(autocompletionScanProgressDialog, self).__init__(parent=None, id=wx.ID_ANY, title=_("Updating autocompletion database"), *args, **kwargs)
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.progress_bar = wx.Gauge(parent=panel)
        sizer.Add(self.progress_bar)
        panel.SetSizerAndFit(sizer)

def confirm():
    with wx.MessageDialog(None, _("This process will retrieve the users you selected from your Mastodon account, and add them to the user autocomplete database. Please note that if there are many users or you have tried to perform this action less than 15 minutes ago, TWBlue may reach a limit in API calls when trying to load the users into the database. If this happens, we will show you an error, in which case you will have to try this process again in a few minutes. If this process ends with no error, you will be redirected back to the account settings dialog. Do you want to continue?"), _("Attention"), style=wx.ICON_QUESTION|wx.YES_NO) as result:
        if result.ShowModal() == wx.ID_YES:
            return True
        return False

def show_success(users):
    with wx.MessageDialog(None, _("TWBlue has imported {} users successfully.").format(users), _("Done")) as dlg:
        dlg.ShowModal()

def show_error():
    with wx.MessageDialog(None, _("Error adding users from Mastodon. Please try again in about 15 minutes."), _("Error"), style=wx.ICON_ERROR) as dlg:
        dlg.ShowModal()