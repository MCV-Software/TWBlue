# -*- coding: utf-8 -*-
import datetime
import wx
import widgetUtils
from wxUI import commonMessageDialogs
from wxUI.dialogs.mastodon.filters import manage_filters as dialog
from . import create_filter
from mastodon import MastodonError

class ManageFiltersController(object):
    def __init__(self, session):
        super(ManageFiltersController, self).__init__()
        self.session = session
        self.selected_filter_idx = -1
        self.error_loading = False
        self.dialog = dialog.ManageFiltersDialog(parent=None)
        self.dialog.filter_list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_filter_selected)
        self.dialog.filter_list.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_filter_deselected)
        widgetUtils.connect_event(self.dialog.add_button, wx.EVT_BUTTON, self.on_add_filter)
        widgetUtils.connect_event(self.dialog.edit_button, wx.EVT_BUTTON, self.on_edit_filter)
        widgetUtils.connect_event(self.dialog.remove_button, wx.EVT_BUTTON, self.on_remove_filter)
        self.load_filter_data()

    def on_filter_selected(self, event):
        """Handle filter selection event."""
        self.selected_filter_idx = event.GetIndex()
        self.dialog.edit_button.Enable()
        self.dialog.remove_button.Enable()

    def on_filter_deselected(self, event):
        """Handle filter deselection event."""
        self.selected_filter_idx = -1
        self.dialog.edit_button.Disable()
        self.dialog.remove_button.Disable()

    def get_selected_filter_id(self):
        """Get the ID of the currently selected filter."""
        if self.selected_filter_idx != -1:
            return self.dialog.filter_list.GetItemData(self.selected_filter_idx)
        return None

    def load_filter_data(self):
        try:
            filters = self.session.api.filters_v2()
            self.dialog.filter_list.DeleteAllItems()
            for i, filter_obj in enumerate(filters):
                index = self.dialog.filter_list.InsertItem(i, filter_obj.title)
                keyword_count = len(filter_obj.keywords)
                self.dialog.filter_list.SetItem(index, 1, str(keyword_count))
                contexts = ", ".join(filter_obj.context)
                self.dialog.filter_list.SetItem(index, 2, contexts)
                self.dialog.filter_list.SetItem(index, 3, filter_obj.filter_action)
                if filter_obj.expires_at:
                    expiry_str = filter_obj.expires_at.strftime("%Y-%m-%d %H:%M")
                else:
                    expiry_str = _("Never")
                self.dialog.filter_list.SetItem(index, 4, expiry_str)
                self.dialog.filter_list.SetItemData(index, int(filter_obj.id) if isinstance(filter_obj.id, (int, str)) else 0)
        except MastodonError as e:
            commonMessageDialogs.error_loading_filters()
            self.error_loading = True

    def on_add_filter(self, *args, **kwargs):
        filterController = create_filter.CreateFilterController(self.session)
        try:
            filter = filterController.get_response()
            self.load_filter_data()
        except MastodonError as error:
            commonMessageDialogs.error_adding_filter()
            return self.on_add_filter()

    def on_edit_filter(self, *args, **kwargs):
        filter_id = self.get_selected_filter_id()
        if filter_id == None:
            return
        try:
            filter_data = self.session.api.filter_v2(filter_id)
            filterController = create_filter.CreateFilterController(self.session, filter_data=filter_data)
            filterController.get_response()
            self.load_filter_data()
        except MastodonError as error:
            commonMessageDialogs.error_adding_filter()

    def on_remove_filter(self, *args, **kwargs):
        filter_id = self.get_selected_filter_id()
        if filter_id == None:
            return
        dlg = commonMessageDialogs.remove_filter()
        if dlg == widgetUtils.NO:
            return
        try:
            self.session.api.delete_filter_v2(filter_id)
            self.load_filter_data()
        except  MastodonError as error:
            commonMessageDialogs.error_removing_filter()

    def get_response(self):
        return self.dialog.ShowModal() == wx.ID_OK