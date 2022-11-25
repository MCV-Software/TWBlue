# -*- coding: utf-8 -*-
import widgetUtils
from pubsub import pub
from wxUI.dialogs import userAliasDialogs

class userAliasController(object):
    def __init__(self, settings):
        super(userAliasController, self).__init__()
        self.settings = settings
        self.dialog = userAliasDialogs.userAliasEditorDialog()
        self.update_aliases_manager()
        widgetUtils.connect_event(self.dialog.add, widgetUtils.BUTTON_PRESSED, self.on_add)
        widgetUtils.connect_event(self.dialog.edit, widgetUtils.BUTTON_PRESSED, self.on_edit)
        widgetUtils.connect_event(self.dialog.remove, widgetUtils.BUTTON_PRESSED, self.on_remove)
        pub.subscribe(self.update_aliases_manager, "alias-added")
        self.dialog.ShowModal()

    def update_aliases_manager(self):
        self.dialog.users.Clear()
        aliases = [self.settings["user-aliases"].get(k) for k in self.settings["user-aliases"].keys()]
        if len(aliases) > 0:
            self.dialog.users.InsertItems(aliases, 0)
        self.dialog.on_selection_changes()

    def on_add(self, *args, **kwargs):
        pub.sendMessage("execute-action", action="add_alias")

    def on_edit(self, *args, **kwargs):
        selection = self.dialog.get_selected_user()
        if selection != "":
            edited = self.dialog.edit_alias_dialog(_("Edit alias for {}").format(selection))
            if edited == None or edited == "":
                return
            for user_key in self.settings["user-aliases"].keys():
                if self.settings["user-aliases"][user_key] == selection:
                    self.settings["user-aliases"][user_key] = edited
                    self.settings.write()
                    self.update_aliases_manager()
                    break

    def on_remove(self, *args, **kwargs):
        selection = self.dialog.get_selected_user()
        if selection == None or selection == "":
            return
        should_remove = self.dialog.remove_alias_dialog()
        if should_remove:
            for user_key in self.settings["user-aliases"].keys():
                if self.settings["user-aliases"][user_key] == selection:
                    self.settings["user-aliases"].pop(user_key)
                    self.settings.write()
                    self.update_aliases_manager()
                    break
