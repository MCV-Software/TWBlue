# -*- coding: utf-8 -*-
import wx
import widgetUtils
import application

def returnTrue():
    return True

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
    def __init__(self, followers_count=0, following_count=0, *args, **kwargs):
        super(autocompletionScanProgressDialog, self).__init__(parent=None, id=wx.ID_ANY, title=_("Updating autocompletion database"), *args, **kwargs)
        self.cancelled = False
        self.followers_count = followers_count
        self.following_count = following_count
        self.total_users = followers_count + following_count
        panel = wx.Panel(self, style=wx.TAB_TRAVERSAL)
        sizer = wx.BoxSizer(wx.VERTICAL)
        # Account information label and field
        info_label_text = wx.StaticText(panel, label=_("Account information:"))
        sizer.Add(info_label_text, 0, wx.LEFT | wx.TOP, 5)
        info_text = _("Followers: {followers} | Following: {following} | Total: {total}").format(
            followers=followers_count,
            following=following_count,
            total=self.total_users
        )
        self.info_field = wx.TextCtrl(panel, value=info_text, style=wx.TE_READONLY | wx.TE_PROCESS_TAB)
        self.info_field.AcceptsFocusFromKeyboard = returnTrue
        sizer.Add(self.info_field, 0, wx.ALL | wx.EXPAND, 5)
        # Current status label and field
        status_label_text = wx.StaticText(panel, label=_("Current status:"))
        sizer.Add(status_label_text, 0, wx.LEFT | wx.TOP, 5)
        self.status_field = wx.TextCtrl(panel, value=_("Preparing..."), style=wx.TE_READONLY | wx.TE_PROCESS_TAB)
        self.status_field.AcceptsFocusFromKeyboard = returnTrue
        sizer.Add(self.status_field, 0, wx.ALL | wx.EXPAND, 5)
        # Progress label and field
        progress_label_text = wx.StaticText(panel, label=_("Progress:"))
        sizer.Add(progress_label_text, 0, wx.LEFT | wx.TOP, 5)
        self.progress_field = wx.TextCtrl(panel, value="", style=wx.TE_READONLY | wx.TE_PROCESS_TAB)
        self.progress_field.AcceptsFocusFromKeyboard = returnTrue
        sizer.Add(self.progress_field, 0, wx.ALL | wx.EXPAND, 5)
        # Progress bar
        self.progress_bar = wx.Gauge(parent=panel, range=self.total_users if self.total_users > 0 else 100)
        sizer.Add(self.progress_bar, 0, wx.ALL | wx.EXPAND, 5)
        # Cancel button
        self.cancel_button = wx.Button(panel, wx.ID_CANCEL, _("&Cancel"))
        self.cancel_button.Bind(wx.EVT_BUTTON, self.on_cancel)
        sizer.Add(self.cancel_button, 0, wx.ALL | wx.ALIGN_CENTER, 10)
        panel.SetSizer(sizer)
        self.SetClientSize(sizer.CalcMin())
        self.SetSize(400, -1)
        # Handle window close - same as cancel, don't close immediately
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def on_close(self, event):
        """Handle window close event (X button). Same as cancel, but prevent immediate close."""
        if not self.cancelled:
            self.on_cancel()
        # Don't call event.Skip() - this prevents the window from closing
        # The window will be destroyed by done() after the scan thread finishes

    def on_cancel(self, event=None):
        self.cancelled = True
        self._update_field_preserving_cursor(self.status_field, _("Cancelling... Please wait."))
        self.cancel_button.Disable()

    def _update_field_preserving_cursor(self, field, new_value):
        """Update a text field while preserving cursor position."""
        cursor_pos = field.GetInsertionPoint()
        field.SetValue(new_value)
        # Restore cursor, but don't go beyond the new text length
        new_length = len(new_value)
        field.SetInsertionPoint(min(cursor_pos, new_length))

    def update_progress(self, current_users, current_page, scanning_type):
        """Update the progress dialog with current scan status.
        
        :param current_users: Number of users scanned so far
        :param current_page: Current page being processed
        :param scanning_type: 'following' or 'followers'
        """
        if scanning_type == "following":
            status = _("Scanning following users...")
        else:
            status = _("Scanning followers...")
        self._update_field_preserving_cursor(self.status_field, status)
        progress_text = _("Page {page} | Users processed: {current} / {total}").format(
            page=current_page,
            current=current_users,
            total=self.total_users
        )
        self._update_field_preserving_cursor(self.progress_field, progress_text)
        # Update progress bar
        if self.total_users > 0:
            self.progress_bar.SetValue(min(current_users, self.total_users))

    def set_saving_status(self):
        """Update status to show we're saving to database."""
        self._update_field_preserving_cursor(self.status_field, _("Saving users to database..."))
        self._update_field_preserving_cursor(self.progress_field, "")
        self.progress_bar.SetValue(self.total_users)

def confirm():
    with wx.MessageDialog(None, _("This process will retrieve the users you selected from your Mastodon account, and add them to the user autocomplete database. Please note that if there are many users or you have tried to perform this action less than 15 minutes ago, TWBlue may reach a limit in API calls when trying to load the users into the database. If this happens, we will show you an error, in which case you will have to try this process again in a few minutes. If this process ends with no error, you will be redirected back to the account settings dialog. Do you want to continue?"), _("Attention"), style=wx.ICON_QUESTION|wx.YES_NO) as result:
        if result.ShowModal() == wx.ID_YES:
            return True
        return False

def show_success(total_users, new_users):
    already_existed = total_users - new_users
    message = _("Scan completed. {new} new users imported, {existing} already in database.").format(
        new=new_users,
        existing=already_existed
    )
    with wx.MessageDialog(None, message, _("Done")) as dlg:
        dlg.ShowModal()

def show_cancelled(total_users, new_users):
    already_existed = total_users - new_users
    message = _("Operation cancelled. {new} new users imported, {existing} already in database.").format(
        new=new_users,
        existing=already_existed
    )
    with wx.MessageDialog(None, message, _("Cancelled"), style=wx.ICON_INFORMATION) as dlg:
        dlg.ShowModal()

def show_error():
    with wx.MessageDialog(None, _("Error adding users from Mastodon. Please try again in about 15 minutes."), _("Error"), style=wx.ICON_ERROR) as dlg:
        dlg.ShowModal()