# -*- coding: utf-8 -*-
import wx
import logging
from pubsub import pub
from multiplatform_widgets import widgets # Assuming this provides generic widgets
from approve.translation import translate as _ # For Approve's _ shortcut
from approve.notifications import NotificationError

logger = logging.getLogger(__name__)

# Supported languages for posts (ISO 639-1 codes) - can be expanded
# This might ideally come from the session or a global config
SUPPORTED_LANG_CHOICES = {
    _("English"): "en",
    _("Spanish"): "es",
    _("French"): "fr",
    _("German"): "de",
    _("Japanese"): "ja",
    _("Portuguese"): "pt",
    _("Russian"): "ru",
    _("Chinese"): "zh",
    # Add more as needed
}

class ComposeDialog(wx.Dialog):
    def __init__(self, parent, session, reply_to_uri: str | None = None, quote_uri: str | None = None, initial_text: str = ""):
        super(ComposeDialog, self).__init__(parent, title=_("Compose Post"), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        self.session = session
        self.panel_config = self.session.compose_panel.get_panel_configuration()
        self.reply_to_uri = reply_to_uri
        self.initial_quote_uri = quote_uri # Store initial quote URI
        self.current_quote_uri = quote_uri # Mutable quote URI
        self.attached_files_info = [] # List of dicts: {"path": str, "alt_text": str}

        self._init_ui(initial_text)
        self.SetMinSize((550, 450)) # Increased min size
        self.CentreOnParent()

    def _init_ui(self, initial_text: str):
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Reply Info (if applicable)
        if self.reply_to_uri:
            # In a real app, fetch & show post snippet or author
            reply_info_label = wx.StaticText(panel, label=_("Replying to: {uri_placeholder}").format(uri_placeholder=self.reply_to_uri[-10:]))
            reply_info_label.SetToolTip(self.reply_to_uri)
            main_sizer.Add(reply_info_label, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 5)

        # Text Area
        self.text_ctrl = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_RICH2 | wx.HSCROLL)
        self.text_ctrl.SetValue(initial_text)
        self.text_ctrl.Bind(wx.EVT_TEXT, self.on_text_changed)
        main_sizer.Add(self.text_ctrl, 1, wx.EXPAND | wx.ALL, 5)

        # Character Counter
        self.max_chars = self.panel_config.get("max_chars", 0)
        self.char_count_label = wx.StaticText(panel, label=f"0 / {self.max_chars if self.max_chars > 0 else 'N/A'}")
        main_sizer.Add(self.char_count_label, 0, wx.ALIGN_RIGHT | wx.RIGHT | wx.BOTTOM, 5)
        self.on_text_changed(None)

        # Attachments Area
        self.max_media_attachments = self.panel_config.get("max_media_attachments", 0)
        if self.max_media_attachments > 0:
            attachment_sizer = wx.StaticBoxSizer(wx.VERTICAL, panel, _("Media Attachments") + f" (Max: {self.max_media_attachments})")
            self.attachment_list = wx.ListBox(attachment_sizer.GetStaticBox(), style=wx.LB_SINGLE, size=(-1, 60)) # Fixed height for listbox
            attachment_sizer.Add(self.attachment_list, 1, wx.EXPAND | wx.ALL, 5)

            attach_btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
            self.add_attachment_btn = wx.Button(attachment_sizer.GetStaticBox(), label=_("Add Media..."))
            self.add_attachment_btn.Bind(wx.EVT_BUTTON, self.on_add_attachment)
            attach_btn_sizer.Add(self.add_attachment_btn, 0, wx.ALL, 2)

            self.remove_attachment_btn = wx.Button(attachment_sizer.GetStaticBox(), label=_("Remove Selected"))
            self.remove_attachment_btn.Bind(wx.EVT_BUTTON, self.on_remove_attachment)
            self.remove_attachment_btn.Enable(False)
            self.attachment_list.Bind(wx.EVT_LISTBOX, lambda evt: self.remove_attachment_btn.Enable(self.attachment_list.GetSelection() != wx.NOT_FOUND))
            attach_btn_sizer.Add(self.remove_attachment_btn, 0, wx.ALL, 2)
            attachment_sizer.Add(attach_btn_sizer, 0, wx.ALIGN_LEFT)
            main_sizer.Add(attachment_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # Quoting Area
        if self.panel_config.get("supports_quoting", False):
            quote_box_sizer = wx.StaticBoxSizer(wx.VERTICAL, panel, _("Quoting Post"))
            quote_display_sizer = wx.BoxSizer(wx.HORIZONTAL)
            self.quote_uri_text_display = wx.TextCtrl(quote_box_sizer.GetStaticBox(), value=self.current_quote_uri or _("None"), style=wx.TE_READONLY | wx.BORDER_NONE)
            self.quote_uri_text_display.SetBackgroundColour(panel.GetBackgroundColour())
            quote_display_sizer.Add(wx.StaticText(quote_box_sizer.GetStaticBox(), label=_("Quoting URI: ")), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 2)
            quote_display_sizer.Add(self.quote_uri_text_display, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 2)
            quote_box_sizer.Add(quote_display_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 2)

            quote_btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
            self.add_quote_btn = wx.Button(quote_box_sizer.GetStaticBox(), label=_("Set/Change Quote..."))
            self.add_quote_btn.Bind(wx.EVT_BUTTON, self.on_add_quote)
            quote_btn_sizer.Add(self.add_quote_btn, 0, wx.ALL, 2)

            self.remove_quote_btn = wx.Button(quote_box_sizer.GetStaticBox(), label=_("Remove Quote"))
            self.remove_quote_btn.Bind(wx.EVT_BUTTON, self.on_remove_quote)
            self.remove_quote_btn.Enable(bool(self.current_quote_uri))
            quote_btn_sizer.Add(self.remove_quote_btn, 0, wx.ALL, 2)
            quote_box_sizer.Add(quote_btn_sizer, 0, wx.ALIGN_LEFT)
            main_sizer.Add(quote_box_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # Options (Content Warning, Language)
        options_box = wx.StaticBoxSizer(wx.VERTICAL, panel, _("Options"))
        options_grid_sizer = wx.FlexGridSizer(cols=2, vgap=5, hgap=5)
        options_grid_sizer.AddGrowableCol(1, 1)

        if self.panel_config.get("supports_content_warning", False):
            self.sensitive_checkbox = wx.CheckBox(options_box.GetStaticBox(), label=_("Sensitive content (CW)"))
            self.sensitive_checkbox.Bind(wx.EVT_CHECKBOX, self.on_sensitive_changed)
            options_grid_sizer.Add(self.sensitive_checkbox, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 2)

            self.spoiler_text_ctrl = wx.TextCtrl(options_box.GetStaticBox())
            self.spoiler_text_ctrl.SetHint(_("Content warning text (optional)"))
            self.spoiler_text_ctrl.Enable(False)
            options_grid_sizer.Add(self.spoiler_text_ctrl, 1, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 2)

        if self.panel_config.get("supports_language_selection", False):
            lang_label = wx.StaticText(options_box.GetStaticBox(), label=_("Languages:"))
            options_grid_sizer.Add(lang_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 2)

            self.max_langs = self.panel_config.get("max_languages", 1)
            self.lang_choices_map = SUPPORTED_LANG_CHOICES # Using global for now
            lang_display_names = list(self.lang_choices_map.keys())

            if self.max_langs == 1: # Single choice
                choices = [_("Automatic")] + lang_display_names
                self.lang_choice_ctrl = wx.Choice(options_box.GetStaticBox(), choices=choices)
                self.lang_choice_ctrl.SetSelection(0) # Default to Automatic/None
            else: # Multiple choices
                self.lang_choice_ctrl = wx.CheckListBox(options_box.GetStaticBox(), choices=lang_display_names, size=(-1, 70))
                self.lang_choice_ctrl.Bind(wx.EVT_CHECKLISTBOX, self.on_lang_checklist_changed)
            options_grid_sizer.Add(self.lang_choice_ctrl, 1, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 2)

        if options_grid_sizer.GetChildren():
            options_box.Add(options_grid_sizer, 1, wx.EXPAND | wx.ALL, 0) # No border for grid sizer itself
            main_sizer.Add(options_box, 0, wx.EXPAND | wx.ALL, 5)

        # Buttons (Send, Cancel)
        btn_sizer = wx.StdDialogButtonSizer()
        self.send_btn = wx.Button(panel, wx.ID_OK, _("Send"))
        self.send_btn.SetDefault()
        self.send_btn.Bind(wx.EVT_BUTTON, self.on_send)
        btn_sizer.AddButton(self.send_btn)

        cancel_btn = wx.Button(panel, wx.ID_CANCEL, _("Cancel"))
        btn_sizer.AddButton(cancel_btn)
        btn_sizer.Realize()
        main_sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        panel.SetSizer(main_sizer)
        self.Fit()


    def on_text_changed(self, event):
        text_length = len(self.text_ctrl.GetValue())
        self.char_count_label.SetLabel(f"{text_length} / {self.max_chars}")
        if self.max_chars > 0 and text_length > self.max_chars:
            self.char_count_label.SetForegroundColour(wx.RED)
        else:
            self.char_count_label.SetForegroundColour(wx.BLACK) # System default

    def on_add_attachment(self, event):
        max_attachments = self.panel_config.get("max_media_attachments", 0)
        if len(self.attached_files_info) >= self.max_media_attachments:
            wx.MessageBox(_("Maximum number of attachments ({max}) reached.").format(max=self.max_media_attachments), _("Attachment Limit"), wx.OK | wx.ICON_INFORMATION)
            return

        supported_mimes = self.panel_config.get("supported_media_types", [])
        wildcard_parts = []
        if not supported_mimes: # Default if none specified by session
            wildcard_parts.append("All files (*.*)|*.*")
        else:
            for mime_type in supported_mimes:
                # Example: "image/jpeg" -> "JPEG files (*.jpg;*.jpeg)|*.jpg;*.jpeg"
                name = mime_type.split('/')[0].capitalize() + " " + mime_type.split('/')[1].upper()
                if mime_type == "image/jpeg": exts = "*.jpg;*.jpeg"
                elif mime_type == "image/png": exts = "*.png"
                elif mime_type == "image/gif": exts = "*.gif" # If supported
                else: exts = "*." + mime_type.split('/')[-1]
                wildcard_parts.append(f"{name} ({exts})|{exts}")

        wildcard = "|".join(wildcard_parts) if wildcard_parts else wx.FileSelectorDefaultWildcardStr

        dialog = wx.FileDialog(self, _("Select Media File"), wildcard=wildcard, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dialog.ShowModal() == wx.ID_OK:
            path = dialog.GetPath()
            alt_text = ""
            if self.panel_config.get("supports_alternative_text", False) and \
               any(pt in path.lower() for pt in ['.jpg', '.jpeg', '.png']): # crude check for image
                alt_text_dialog = wx.TextEntryDialog(self, _("Enter accessibility description (alt text) for the image:"), _("Image Description"))
                if alt_text_dialog.ShowModal() == wx.ID_OK:
                    alt_text = alt_text_dialog.GetValue()
                alt_text_dialog.Destroy()

            self.attached_files_info.append({"path": path, "alt_text": alt_text})
            self.attachment_list.Append(os.path.basename(path) + (f" ({_('Alt:')} {alt_text})" if alt_text else ""))
        dialog.Destroy()

    def on_remove_attachment(self, event):
        selected_index = self.attachment_list.GetSelection()
        if selected_index != wx.NOT_FOUND:
            self.attachment_list.Delete(selected_index)
            del self.attached_files_info[selected_index]

    def on_add_quote(self, event):
        dialog = wx.TextEntryDialog(self, _("Enter the AT-URI of the Bluesky post to quote:"), _("Quote Post"), self.current_quote_uri or "")
        if dialog.ShowModal() == wx.ID_OK:
            self.current_quote_uri = dialog.GetValue().strip()
            self.quote_uri_text_display.SetValue(self.current_quote_uri or _("None"))
            self.remove_quote_btn.Enable(bool(self.current_quote_uri))
        dialog.Destroy()

    def on_remove_quote(self, event):
        self.current_quote_uri = None
        self.quote_uri_text_display.SetValue(_("None"))
        self.remove_quote_btn.Enable(False)


    def on_sensitive_changed(self, event):
        if hasattr(self, 'spoiler_text_ctrl'):
            self.spoiler_text_ctrl.Enable(event.IsChecked())
            if event.IsChecked():
                self.spoiler_text_ctrl.SetFocus()

    def on_lang_checklist_changed(self, event):
        """Ensure no more than max_languages are selected for CheckListBox."""
        if isinstance(self.lang_choice_ctrl, wx.CheckListBox):
            checked_indices = self.lang_choice_ctrl.GetCheckedItems()
            if len(checked_indices) > self.max_langs:
                # Find the item that was just checked to cause the overflow
                # This is a bit tricky as EVT_CHECKLISTBOX triggers after the change.
                # A simpler approach is to inform the user and let them uncheck.
                wx.MessageBox(
                    _("You can select a maximum of {num} languages.").format(num=self.max_langs),
                    _("Language Selection Limit"), wx.OK | wx.ICON_EXCLAMATION
                )
                # Optionally, uncheck the last checked item if possible to determine
                # For now, just warn. User has to manually correct.


    def on_send(self, event): # Renamed from async on_send
        text_content = self.text_ctrl.GetValue()
        if not text_content.strip() and not self.attached_files_info and not self.current_quote_uri:
            wx.MessageBox(_("Cannot send an empty post."), _("Error"), wx.OK | wx.ICON_ERROR)
            return

        # Language processing
        langs = []
        if hasattr(self, 'lang_choice_ctrl'):
            if isinstance(self.lang_choice_ctrl, wx.Choice):
                sel_idx = self.lang_choice_ctrl.GetSelection()
                if sel_idx > 0: # Index 0 is empty/no selection
                    lang_display_name = self.lang_choice_ctrl.GetString(sel_idx)
                    langs.append(self.lang_choices_map[lang_display_name])
            elif isinstance(self.lang_choice_ctrl, wx.CheckListBox):
                checked_indices = self.lang_choice_ctrl.GetCheckedItems()
                if len(checked_indices) > self.max_langs:
                     wx.MessageBox(_("Please select no more than {num} languages.").format(num=self.max_langs), _("Language Error"), wx.OK | wx.ICON_ERROR)
                     return
                for idx in checked_indices:
                    lang_display_name = self.lang_choice_ctrl.GetString(idx)
                    langs.append(self.lang_choices_map[lang_display_name])

        # Files and Alt Texts
        files_to_send = [f_info["path"] for f_info in self.attached_files_info]
        alt_texts_to_send = [f_info["alt_text"] for f_info in self.attached_files_info]

        # Content Warning
        cw_text = None
        is_sensitive_flag = False
        if hasattr(self, 'sensitive_checkbox') and self.sensitive_checkbox.IsChecked():
            is_sensitive_flag = True
            if hasattr(self, 'spoiler_text_ctrl'):
                cw_text = self.spoiler_text_ctrl.GetValue().strip() or None # Use None if empty for Bluesky

        kwargs_for_send = {
            "quote_uri": self.current_quote_uri,
            "langs": langs if langs else None,
            "media_alt_texts": alt_texts_to_send if alt_texts_to_send else None,
            # "tags" could be extracted from text server-side or client-side (not implemented here)
        }

        # Filter out None values from kwargs to avoid sending them if not set
        kwargs_for_send = {k: v for k, v in kwargs_for_send.items() if v is not None}

        try:
            self.send_btn.Disable()
            # This is an async call, so it should be handled appropriately in wxPython
            # For simplicity in this step, assuming it's handled by the caller or a wrapper
            # In a real wxPython app, this would involve asyncio.create_task and wx.CallAfter
            # or running the send in a separate thread and using wx.CallAfter for UI updates.
            # For now, we'll make this method async and let the caller handle it.

            # wx.BeginBusyCursor() # Indicate work
            # Using pubsub to decouple UI from direct async call to session
            pub.sendMessage(
                "compose_dialog.send_post",
                session=self.session,
                text=text_content,
                files=files_to_send if files_to_send else None,
                reply_to=self.reply_to_uri,
                cw_text=cw_text,
                is_sensitive=is_sensitive_flag,
                kwargs=kwargs_for_send
            )
            # Success will be signaled by another pubsub message if needed, or just close.
            # self.EndModal(wx.ID_OK) # Moved to controller after successful send via pubsub

        except NotificationError as e:
            wx.MessageBox(str(e), _("Post Error"), wx.OK | wx.ICON_ERROR)
        except Exception as e:
            logger.error("Error sending post from compose dialog: %s", e, exc_info=True)
            wx.MessageBox(_("An unexpected error occurred: {error}").format(error=str(e)), _("Error"), wx.OK | wx.ICON_ERROR)
        finally:
            # wx.EndBusyCursor()
            if not self.IsBeingDeleted(): # Ensure dialog still exists
                 self.send_btn.Enable()
                 # Do not automatically close here; let the controller do it on success signal.
                 # self.EndModal(wx.ID_OK) # if successful and no further UI feedback needed in dialog

    def get_data(self):
        """Helper to get all data, though on_send handles it directly."""
        # This method isn't strictly necessary if on_send does all the work,
        # but can be useful for other patterns.
        pass

if __name__ == '__main__':
    # Example usage (requires a mock session and panel_config)
    app = wx.App(False)

    class MockComposePanel:
        def get_panel_configuration(self):
            return {
                "max_chars": 300,
                "max_media_attachments": 4,
                "supported_media_types": ["image/jpeg", "image/png"],
                "supports_alternative_text": True,
                "supports_content_warning": True,
                "supports_language_selection": True,
                "max_languages": 3,
                "supports_quoting": True,
            }

    class MockSession:
        def __init__(self):
            self.compose_panel = MockComposePanel()
            self.uid = "mock_user" # Needed by some base methods if called

        async def send_message(self, message, files=None, reply_to=None, cw_text=None, is_sensitive=False, **kwargs):
            print("MockSession.send_message called:")
            print(f"  Text: {message}")
            print(f"  Files: {files}")
            print(f"  Reply To: {reply_to}")
            print(f"  CW: {cw_text}, Sensitive: {is_sensitive}")
            print(f"  kwargs: {kwargs}")
            # Simulate success or failure
            # raise NotificationError("This is a mock send error!")
            return "at://did:plc:mockposturi/app.bsky.feed.post/mockrkey"

    # Pubsub listener for the send_post event (simulates what mainController would do)
    def on_actual_send(session, text, files, reply_to, cw_text, is_sensitive, kwargs):
        print("Pubsub: compose_dialog.send_post received. Calling session.send_message...")
        async def do_send():
            try:
                uri = await session.send_message(
                    message=text,
                    files=files,
                    reply_to=reply_to,
                    cw_text=cw_text,
                    is_sensitive=is_sensitive,
                    **kwargs
                )
                print(f"Pubsub: Send successful, URI: {uri}")
                # In real app, would call dialog.EndModal(wx.ID_OK) via wx.CallAfter
                wx.CallAfter(dialog.EndModal, wx.ID_OK)
            except Exception as e:
                print(f"Pubsub: Send failed: {e}")
                # In real app, show error and re-enable send button in dialog via wx.CallAfter
                wx.CallAfter(wx.MessageBox, str(e), "Error", wx.OK | wx.ICON_ERROR, dialog)
                wx.CallAfter(dialog.send_btn.Enable, True)

        asyncio.create_task(do_send())

    pub.subscribe(on_actual_send, "compose_dialog.send_post")

    session = MockSession()
    # Example: dialog = ComposeDialog(None, session, reply_to_uri="at://reply_uri", quote_uri="at://quote_uri", initial_text="Hello")
    dialog = ComposeDialog(None, session, initial_text="Hello Bluesky!")
    dialog.ShowModal()
    dialog.Destroy()
    app.MainLoop()
