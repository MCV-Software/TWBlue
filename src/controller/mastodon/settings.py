# -*- coding: utf-8 -*-
import os
import threading
import logging
import sound_lib
import paths
import widgetUtils
import output
from collections import OrderedDict
from wxUI import commonMessageDialogs
from wxUI.dialogs.mastodon import configuration
from extra.autocompletionUsers import manage
from extra.autocompletionUsers.mastodon import scan
from extra.ocr import OCRSpace
from controller.settings import globalSettingsController
from . templateEditor import EditTemplate

log = logging.getLogger("Settings")

class accountSettingsController(globalSettingsController):
    def __init__(self, buffer, window):
        self.user = buffer.session.db["user_name"]
        self.buffer = buffer
        self.window = window
        self.config = buffer.session.settings
        self.dialog = configuration.configurationDialog()
        self.create_config()
        self.needs_restart = False
        self.is_started = True

    def create_config(self):
        self.dialog.create_general_account()
        widgetUtils.connect_event(self.dialog.general.userAutocompletionScan, widgetUtils.BUTTON_PRESSED, self.on_autocompletion_scan)
        widgetUtils.connect_event(self.dialog.general.userAutocompletionManage, widgetUtils.BUTTON_PRESSED, self.on_autocompletion_manage)
        self.dialog.set_value("general", "disable_streaming", self.config["general"]["disable_streaming"])
        self.dialog.set_value("general", "relative_time", self.config["general"]["relative_times"])
        self.dialog.set_value("general", "read_preferences_from_instance", self.config["general"]["read_preferences_from_instance"])
        self.dialog.set_value("general", "show_screen_names", self.config["general"]["show_screen_names"])
        self.dialog.set_value("general", "hide_emojis", self.config["general"]["hide_emojis"])
        self.dialog.set_value("general", "itemsPerApiCall", self.config["general"]["max_posts_per_call"])
        self.dialog.set_value("general", "reverse_timelines", self.config["general"]["reverse_timelines"])
        boost_mode = self.config["general"]["boost_mode"]
        if boost_mode == "ask":
            self.dialog.set_value("general", "ask_before_boost", True)
        else:
            self.dialog.set_value("general", "ask_before_boost", False)
        self.dialog.set_value("general", "persist_size", str(self.config["general"]["persist_size"]))
        self.dialog.set_value("general", "load_cache_in_memory", self.config["general"]["load_cache_in_memory"])
        self.dialog.create_reporting()
        self.dialog.set_value("reporting", "speech_reporting", self.config["reporting"]["speech_reporting"])
        self.dialog.set_value("reporting", "braille_reporting", self.config["reporting"]["braille_reporting"])
        post_template = self.config["templates"]["post"]
        conversation_template = self.config["templates"]["conversation"]
        person_template = self.config["templates"]["person"]
        self.dialog.create_templates(post_template=post_template, conversation_template=conversation_template, person_template=person_template)
        widgetUtils.connect_event(self.dialog.templates.post, widgetUtils.BUTTON_PRESSED, self.edit_post_template)
        widgetUtils.connect_event(self.dialog.templates.conversation, widgetUtils.BUTTON_PRESSED, self.edit_conversation_template)
        widgetUtils.connect_event(self.dialog.templates.person, widgetUtils.BUTTON_PRESSED, self.edit_person_template)
        self.dialog.create_other_buffers()
        buffer_values = self.get_buffers_list()
        self.dialog.buffers.insert_buffers(buffer_values)
        self.dialog.buffers.connect_hook_func(self.toggle_buffer_active)
        widgetUtils.connect_event(self.dialog.buffers.toggle_state, widgetUtils.BUTTON_PRESSED, self.toggle_state)
        widgetUtils.connect_event(self.dialog.buffers.up, widgetUtils.BUTTON_PRESSED, self.dialog.buffers.move_up)
        widgetUtils.connect_event(self.dialog.buffers.down, widgetUtils.BUTTON_PRESSED, self.dialog.buffers.move_down)
        self.input_devices = sound_lib.input.Input.get_device_names()
        self.output_devices = sound_lib.output.Output.get_device_names()
        self.soundpacks = []
        [self.soundpacks.append(i) for i in os.listdir(paths.sound_path()) if os.path.isdir(os.path.join(paths.sound_path(), i)) == True ]
        self.dialog.create_sound(self.input_devices, self.output_devices, self.soundpacks)
        self.dialog.set_value("sound", "volumeCtrl", int(self.config["sound"]["volume"]*100))
        self.dialog.set_value("sound", "input", self.config["sound"]["input_device"])
        self.dialog.set_value("sound", "output", self.config["sound"]["output_device"])
        self.dialog.set_value("sound", "session_mute", self.config["sound"]["session_mute"])
        self.dialog.set_value("sound", "soundpack", self.config["sound"]["current_soundpack"])
        self.dialog.set_value("sound", "indicate_audio", self.config["sound"]["indicate_audio"])
        self.dialog.set_value("sound", "indicate_img", self.config["sound"]["indicate_img"])
        self.dialog.create_extras(OCRSpace.translatable_langs)
        language_index = OCRSpace.OcrLangs.index(self.config["mysc"]["ocr_language"])
        self.dialog.extras.ocr_lang.SetSelection(language_index)
        self.dialog.realize()
        self.dialog.set_title(_("Account settings for %s") % (self.user,))
        self.response = self.dialog.get_response()

    def edit_post_template(self, *args, **kwargs):
        template = self.config["templates"]["post"]
        control = EditTemplate(template=template, type="post")
        result = control.run_dialog()
        if result != "": # Template has been saved.
            self.config["templates"]["post"] = result
            self.config.write()
            self.dialog.templates.post.SetLabel(_("Edit template for posts. Current template: {}").format(result))

    def edit_conversation_template(self, *args, **kwargs):
        template = self.config["templates"]["conversation"]
        control = EditTemplate(template=template, type="conversation")
        result = control.run_dialog()
        if result != "": # Template has been saved.
            self.config["templates"]["conversation"] = result
            self.config.write()
            self.dialog.templates.conversation.SetLabel(_("Edit template for conversations. Current template: {}").format(result))

    def edit_person_template(self, *args, **kwargs):
        template = self.config["templates"]["person"]
        control = EditTemplate(template=template, type="person")
        result = control.run_dialog()
        if result != "": # Template has been saved.
            self.config["templates"]["person"] = result
            self.config.write()
            self.dialog.templates.person.SetLabel(_("Edit template for persons. Current template: {}").format(result))

    def save_configuration(self):
        if self.config["general"]["relative_times"] != self.dialog.get_value("general", "relative_time"):
            self.needs_restart = True
            log.debug("Triggered app restart due to change in relative times.")
            self.config["general"]["relative_times"] = self.dialog.get_value("general", "relative_time")
        if self.config["general"]["disable_streaming"] != self.dialog.get_value("general", "disable_streaming"):
            self.needs_restart = True
            log.debug("Triggered app restart due to change in streaming settings.")
            self.config["general"]["disable_streaming"] = self.dialog.get_value("general", "disable_streaming")
        self.config["general"]["read_preferences_from_instance"] = self.dialog.get_value("general", "read_preferences_from_instance")
        self.config["general"]["show_screen_names"] = self.dialog.get_value("general", "show_screen_names")
        self.config["general"]["hide_emojis"] = self.dialog.get_value("general", "hide_emojis")
        self.config["general"]["max_posts_per_call"] = self.dialog.get_value("general", "itemsPerApiCall")
        if self.config["general"]["load_cache_in_memory"] != self.dialog.get_value("general", "load_cache_in_memory"):
            self.config["general"]["load_cache_in_memory"] = self.dialog.get_value("general", "load_cache_in_memory")
            self.needs_restart = True
            log.debug("Triggered app restart due to change in database strategy management.")
        if self.config["general"]["persist_size"] != self.dialog.get_value("general", "persist_size"):
            if self.dialog.get_value("general", "persist_size") == '':
                self.config["general"]["persist_size"] =-1
            else:
                try:
                    self.config["general"]["persist_size"] = int(self.dialog.get_value("general", "persist_size"))
                except ValueError:
                    output.speak("Invalid cache size, setting to default.",True)
                    self.config["general"]["persist_size"] =1764

        if self.config["general"]["reverse_timelines"] != self.dialog.get_value("general", "reverse_timelines"):
            self.needs_restart = True
            log.debug("Triggered app restart due to change in timeline order.")
            self.config["general"]["reverse_timelines"] = self.dialog.get_value("general", "reverse_timelines")
        ask_before_boost = self.dialog.get_value("general", "ask_before_boost")
        if ask_before_boost == True:
            self.config["general"]["boost_mode"] = "ask"
        else:
            self.config["general"]["boost_mode"] = "direct"
        buffers_list = self.dialog.buffers.get_list()
        if buffers_list != self.config["general"]["buffer_order"]:
            self.needs_restart = True
            log.debug("Triggered app restart due to change in buffer ordering.")
            self.config["general"]["buffer_order"] = buffers_list
        self.config["reporting"]["speech_reporting"] = self.dialog.get_value("reporting", "speech_reporting")
        self.config["reporting"]["braille_reporting"] = self.dialog.get_value("reporting", "braille_reporting")
        self.config["mysc"]["ocr_language"] = OCRSpace.OcrLangs[self.dialog.extras.ocr_lang.GetSelection()]
        if self.config["sound"]["input_device"] != self.dialog.sound.get("input"):
            self.config["sound"]["input_device"] = self.dialog.sound.get("input")
            try:
                self.buffer.session.sound.input.set_device(self.buffer.session.sound.input.find_device_by_name(self.config["sound"]["input_device"]))
            except:
                self.config["sound"]["input_device"] = "default"
        if self.config["sound"]["output_device"] != self.dialog.sound.get("output"):
            self.config["sound"]["output_device"] = self.dialog.sound.get("output")
            try:
                self.buffer.session.sound.output.set_device(self.buffer.session.sound.output.find_device_by_name(self.config["sound"]["output_device"]))
            except:
                self.config["sound"]["output_device"] = "default"
        self.config["sound"]["volume"] = self.dialog.get_value("sound", "volumeCtrl")/100.0
        self.config["sound"]["session_mute"] = self.dialog.get_value("sound", "session_mute")
        self.config["sound"]["current_soundpack"] = self.dialog.sound.get("soundpack")
        self.config["sound"]["indicate_audio"] = self.dialog.get_value("sound", "indicate_audio")
        self.config["sound"]["indicate_img"] = self.dialog.get_value("sound", "indicate_img")
        self.buffer.session.sound.config = self.config["sound"]
        self.buffer.session.sound.check_soundpack()
        self.config.write()

    def toggle_state(self,*args,**kwargs):
        return self.dialog.buffers.change_selected_item()

    def on_autocompletion_scan(self, *args, **kwargs):
        configuration = scan.autocompletionScan(self.buffer.session.settings, self.buffer, self.window)
        to_scan = configuration.show_dialog()
        if to_scan == True:
            configuration.prepare_progress_dialog()
            t = threading.Thread(target=configuration.scan)
            t.start()

    def on_autocompletion_manage(self, *args, **kwargs):
        configuration = manage.autocompletionManage(self.buffer.session)
        configuration.show_settings()

    def get_buffers_list(self):
        all_buffers=OrderedDict()
        all_buffers['home']=_("Home")
        all_buffers['local'] = _("Local")
        all_buffers['federated'] = _("Federated")
        all_buffers['mentions']=_("Mentions")
        all_buffers['direct_messages']=_("Direct Messages")
        all_buffers['sent']=_("Sent")
        all_buffers['favorites']=_("Favorites")
        all_buffers['bookmarks']=_("Bookmarks")
        all_buffers['followers']=_("Followers")
        all_buffers['following']=_("Following")
        all_buffers['blocked']=_("Blocked users")
        all_buffers['muted']=_("Muted users")
        all_buffers['notifications']=_("Notifications")
        list_buffers = []
        hidden_buffers=[]
        all_buffers_keys = list(all_buffers.keys())
        # Check buffers shown first.
        for i in self.config["general"]["buffer_order"]:
            if i in all_buffers_keys:
                list_buffers.append((i, all_buffers[i], True))
            # This second pass will retrieve all hidden buffers.
        for i in all_buffers_keys:
            if i not in self.config["general"]["buffer_order"]:
                hidden_buffers.append((i, all_buffers[i], False))
        list_buffers.extend(hidden_buffers)
        return list_buffers

    def toggle_buffer_active(self, ev):
        change = self.dialog.buffers.get_event(ev)
        if change == True:
            self.dialog.buffers.change_selected_item()
