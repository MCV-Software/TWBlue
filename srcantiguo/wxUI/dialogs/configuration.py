# -*- coding: utf-8 -*-
import logging as original_logger
import wx
import application
import output
import config
import widgetUtils
from . import baseDialog
from multiplatform_widgets import widgets

class general(wx.Panel, baseDialog.BaseWXDialog):
    def __init__(self, parent, languages,keymaps):
        super(general, self).__init__(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        language = wx.StaticText(self, -1, _(u"&Language"))
        self.language = wx.ListBox(self, -1, choices=languages)
        self.language.SetSize(self.language.GetBestSize())
        langBox = wx.BoxSizer(wx.HORIZONTAL)
        langBox.Add(language, 0, wx.ALL, 5)
        langBox.Add(self.language, 0, wx.ALL, 5)
        sizer.Add(langBox, 0, wx.ALL, 5)
        self.ask_at_exit = wx.CheckBox(self, -1, _(U"&Ask before exiting {0}").format(application.name,))
        sizer.Add(self.ask_at_exit, 0, wx.ALL, 5)
        self.no_streaming = wx.CheckBox(self, -1, _(U"&Disable Streaming functions"))
        sizer.Add(self.no_streaming, 0, wx.ALL, 5)
        updatePeriodBox = wx.BoxSizer(wx.HORIZONTAL)
        updatePeriodBox.Add(wx.StaticText(self, -1, _(u"&Buffer update interval, in minutes")), 0, wx.ALL, 5)
        self.update_period = wx.SpinCtrl(self, wx.ID_ANY)
        self.update_period.SetRange(1, 30)
        self.update_period.SetSize(self.update_period.GetBestSize())
        updatePeriodBox.Add(self.update_period, 0, wx.ALL, 5)
        sizer.Add(updatePeriodBox, 0, wx.ALL, 5)
        self.play_ready_sound = wx.CheckBox(self, -1, _(U"Pla&y a sound when {0} launches").format(application.name,))
        sizer.Add(self.play_ready_sound, 0, wx.ALL, 5)
        self.speak_ready_msg = wx.CheckBox(self, -1, _(U"Sp&eak a message when {0} launches").format(application.name,))
        sizer.Add(self.speak_ready_msg, 0, wx.ALL, 5)
        self.use_invisible_shorcuts = wx.CheckBox(self, -1, _(u"&Use invisible interface's keyboard shortcuts while GUI is visible"))
        sizer.Add(self.use_invisible_shorcuts, 0, wx.ALL, 5)
        self.disable_sapi5 = wx.CheckBox(self, -1, _(u"A&ctivate Sapi5 when any other screen reader is not being run"))
        sizer.Add(self.disable_sapi5, 0, wx.ALL, 5)
        self.hide_gui = wx.CheckBox(self, -1, _(u"&Hide GUI on launch"))
        sizer.Add(self.hide_gui, 0, wx.ALL, 5)
        self.read_long_posts_in_gui = wx.CheckBox(self, wx.ID_ANY, _("&Read long posts in GUI"))
        sizer.Add(self.read_long_posts_in_gui, 0, wx.ALL, 5)
        kmbox =  wx.BoxSizer(wx.VERTICAL)
        km_label = wx.StaticText(self, -1, _(u"&Keymap"))
        self.km = wx.ComboBox(self, -1, choices=keymaps, style=wx.CB_READONLY)
        self.km.SetSize(self.km.GetBestSize())
        kmbox.Add(km_label, 0, wx.ALL, 5)
        kmbox.Add(self.km, 0, wx.ALL, 5)
        self.check_for_updates = wx.CheckBox(self, -1, _(U"Check for u&pdates when {0} launches").format(application.name,))
        sizer.Add(self.check_for_updates, 0, wx.ALL, 5)
        sizer.Add(kmbox, 0, wx.ALL, 5)
        self.SetSizer(sizer)

class proxy(wx.Panel, baseDialog.BaseWXDialog):

    def __init__(self, parent, proxyTypes):
        super(proxy, self).__init__(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        type=wx.StaticText(self, wx.ID_ANY, _(u"Proxy &type: "))
        self.type=wx.ComboBox(self, -1, choices=proxyTypes, style=wx.CB_READONLY)
        self.type.SetSize(self.type.GetBestSize())
        typeBox = wx.BoxSizer(wx.HORIZONTAL)
        typeBox.Add(type, 0, wx.ALL, 5)
        typeBox.Add(self.type, 0, wx.ALL, 5)
        sizer.Add(typeBox, 0, wx.ALL, 5)
        lbl = wx.StaticText(self, wx.ID_ANY, _(u"Proxy s&erver: "))
        self.server = wx.TextCtrl(self, -1)
        serverBox = wx.BoxSizer(wx.HORIZONTAL)
        serverBox.Add(lbl, 0, wx.ALL, 5)
        serverBox.Add(self.server, 0, wx.ALL, 5)
        sizer.Add(serverBox, 0, wx.ALL, 5)
        lbl = wx.StaticText(self, wx.ID_ANY, _(u"&Port: "))
        self.port = wx.SpinCtrl(self, wx.ID_ANY, min=1, max=65535)
        portBox = wx.BoxSizer(wx.HORIZONTAL)
        portBox.Add(lbl, 0, wx.ALL, 5)
        portBox.Add(self.port, 0, wx.ALL, 5)
        sizer.Add(portBox, 0, wx.ALL, 5)
        lbl = wx.StaticText(self, wx.ID_ANY, _(u"&User: "))
        self.user = wx.TextCtrl(self, wx.ID_ANY)
        userBox = wx.BoxSizer(wx.HORIZONTAL)
        userBox.Add(lbl, 0, wx.ALL, 5)
        userBox.Add(self.user, 0, wx.ALL, 5)
        sizer.Add(userBox, 0, wx.ALL, 5)
        lbl = wx.StaticText(self, wx.ID_ANY, _(u"P&assword: "))
        self.password = wx.TextCtrl(self, wx.ID_ANY, style=wx.TE_PASSWORD)
        passwordBox = wx.BoxSizer(wx.HORIZONTAL)
        passwordBox.Add(lbl, 0, wx.ALL, 5)
        passwordBox.Add(self.password, 0, wx.ALL, 5)
        sizer.Add(serverBox, 0, wx.ALL, 5)
        self.SetSizer(sizer)

class reporting(wx.Panel, baseDialog.BaseWXDialog):
    def __init__(self, parent):
        super(reporting, self).__init__(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.speech_reporting = wx.CheckBox(self, wx.ID_ANY, _(U"Enable automatic s&peech feedback"))
        sizer.Add(self.speech_reporting, 0, wx.ALL, 5)
        self.braille_reporting = wx.CheckBox(self, wx.ID_ANY, _(U"Enable automatic &Braille feedback"))
        sizer.Add(self.braille_reporting, 0, wx.ALL, 5)
        self.SetSizer(sizer)

class other_buffers(wx.Panel):
    def __init__(self, parent):
        super(other_buffers, self).__init__(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.buffers = widgets.list(self, _(u"Buffer"), _(u"Name"), _(u"Status"), style=wx.LC_SINGLE_SEL|wx.LC_REPORT)
        sizer.Add(self.buffers.list, 0, wx.ALL, 5)
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.toggle_state = wx.Button(self, -1, _(u"S&how/hide"))
        self.up = wx.Button(self, -1, _(u"Move &up"))
        self.down = wx.Button(self, -1, _(u"Move &down"))
        btnSizer.Add(self.toggle_state, 0, wx.ALL, 5)
        btnSizer.Add(self.up, 0, wx.ALL, 5)
        btnSizer.Add(self.down, 0, wx.ALL, 5)
        sizer.Add(btnSizer, 0, wx.ALL, 5)
        self.SetSizer(sizer)

    def insert_buffers(self, buffers):
        for i in buffers:
            if i[2] == True:
                self.buffers.insert_item(False, *[i[0], i[1], _(u"Show")])
            else:
                self.buffers.insert_item(False, *[i[0], i[1], _(u"Hide")])

    def connect_hook_func(self, func):
        self.buffers.list.Bind(wx.EVT_CHAR_HOOK, func)

    def move_up(self, *args, **kwargs):
        current = self.buffers.get_selected()
        if current == -1:
            output.speak(_(u"Select a buffer first."), True)
            return False
        if self.buffers.get_text_column(current, 2) == _(u"Hide"):
            output.speak(_(u"The buffer is hidden, show it first."), True)
            return False
        if current <= 0:
            output.speak(_(u"The buffer is already at the top of the list."), True)
            return False
        current_text = self.buffers.get_text_column(self.buffers.get_selected(), 0)
        current_name = self.buffers.get_text_column(self.buffers.get_selected(), 1)
        current_text_state = self.buffers.get_text_column(self.buffers.get_selected(), 2)
        text_above = self.buffers.get_text_column(self.buffers.get_selected()-1, 0)
        name_above = self.buffers.get_text_column(self.buffers.get_selected()-1, 1)
        text_above_state = self.buffers.get_text_column(self.buffers.get_selected()-1, 2)
        self.buffers.set_text_column(self.buffers.get_selected()-1, 0, current_text)
        self.buffers.set_text_column(self.buffers.get_selected()-1, 1, current_name)
        self.buffers.set_text_column(self.buffers.get_selected()-1, 2, current_text_state)
        self.buffers.set_text_column(self.buffers.get_selected(), 0, text_above)
        self.buffers.set_text_column(self.buffers.get_selected(), 1, name_above)
        self.buffers.set_text_column(self.buffers.get_selected(), 2, text_above_state)

    def move_down(self, *args, **kwargs):
        current = self.buffers.get_selected()
        if current == -1:
            output.speak(_(u"Select a buffer first."), True)
            return False
        if self.buffers.get_text_column(current, 2) == _(u"Hide"):
            output.speak(_(u"The buffer is hidden, show it first."), True)
            return False
        if current+1 >= self.buffers.get_count():
            output.speak(_(u"The buffer is already at the bottom of the list."), True)
            return False
        current_text = self.buffers.get_text_column(self.buffers.get_selected(), 0)
        current_name = self.buffers.get_text_column(self.buffers.get_selected(), 1)
        current_text_state = self.buffers.get_text_column(self.buffers.get_selected(), 2)
        text_below = self.buffers.get_text_column(self.buffers.get_selected()+1, 0)
        name_below = self.buffers.get_text_column(self.buffers.get_selected()+1, 1)
        text_below_state = self.buffers.get_text_column(self.buffers.get_selected()+1, 2)
        self.buffers.set_text_column(self.buffers.get_selected()+1, 0, current_text)
        self.buffers.set_text_column(self.buffers.get_selected()+1, 1, current_name)
        self.buffers.set_text_column(self.buffers.get_selected()+1, 2, current_text_state)
        self.buffers.set_text_column(self.buffers.get_selected(), 0, text_below)
        self.buffers.set_text_column(self.buffers.get_selected(), 1, name_below)
        self.buffers.set_text_column(self.buffers.get_selected(), 2, text_below_state)

    def get_event(self, ev):
        if ev.GetKeyCode() == wx.WXK_SPACE:
            return True
        else:
            ev.Skip()
            return False

    def change_selected_item(self):
        current = self.buffers.get_selected()
        text = self.buffers.get_text_column(current, 2)
        if text == _(u"Show"):
            self.buffers.set_text_column(current, 2, _(u"Hide"))
        else:
            self.buffers.set_text_column(current, 2, _(u"Show"))
        output.speak(self.buffers.get_text_column(current, 2),True)
    def get_list(self):
        buffers_list = []
        for i in range(0, self.buffers.get_count()):
            if self.buffers.get_text_column(i, 2) == _(u"Show"):
                buffers_list.append(self.buffers.get_text_column(i, 0))
        return buffers_list

class TranslatorPanel(wx.Panel, baseDialog.BaseWXDialog):
    def __init__(self, parent):
        super(TranslatorPanel, self).__init__(parent)

        sizer = wx.BoxSizer(wx.VERTICAL)
        lbl_libre_url = wx.StaticText(self, wx.ID_ANY, _(u"&LibreTranslate API URL: "))
        self.libre_api_url = wx.TextCtrl(self, wx.ID_ANY)
        libreUrlBox = wx.BoxSizer(wx.HORIZONTAL)
        libreUrlBox.Add(lbl_libre_url, 0, wx.ALL, 5)
        libreUrlBox.Add(self.libre_api_url, 1, wx.ALL | wx.EXPAND, 5)
        sizer.Add(libreUrlBox, 0, wx.ALL | wx.EXPAND, 5)
        lbl_libre_api_key = wx.StaticText(self, wx.ID_ANY, _(u"LibreTranslate API &Key (optional): "))
        self.libre_api_key = wx.TextCtrl(self, wx.ID_ANY)
        libreApiKeyBox = wx.BoxSizer(wx.HORIZONTAL)
        libreApiKeyBox.Add(lbl_libre_api_key, 0, wx.ALL, 5)
        libreApiKeyBox.Add(self.libre_api_key, 1, wx.ALL | wx.EXPAND, 5)
        sizer.Add(libreApiKeyBox, 0, wx.ALL | wx.EXPAND, 5)
        lbl_deepL_api_key = wx.StaticText(self, wx.ID_ANY, _(u"&DeepL API Key: "))
        self.deepL_api_key = wx.TextCtrl(self, wx.ID_ANY)
        deepLApiKeyBox = wx.BoxSizer(wx.HORIZONTAL)
        deepLApiKeyBox.Add(lbl_deepL_api_key, 0, wx.ALL, 5)
        deepLApiKeyBox.Add(self.deepL_api_key, 1, wx.ALL | wx.EXPAND, 5)
        sizer.Add(deepLApiKeyBox, 0, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(sizer)
class configurationDialog(baseDialog.BaseWXDialog):
    def set_title(self, title):
        self.SetTitle(title)

    def __init__(self):
        super(configurationDialog, self).__init__(None, -1)
        self.panel = wx.Panel(self)
        self.SetTitle(_(u"{0} preferences").format(application.name,))
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.notebook = wx.Notebook(self.panel)

    def create_general(self, languageList,keymaps):
        self.general = general(self.notebook, languageList,keymaps)
        self.notebook.AddPage(self.general, _(u"General"))
        self.general.SetFocus()

    def create_proxy(self, proxyTypes):
        self.proxy = proxy(self.notebook, proxyTypes)
        self.notebook.AddPage(self.proxy, _(u"Proxy"))

    def create_translator_panel(self):
        self.translator_panel= TranslatorPanel(self.notebook)
        self.notebook.AddPage(self.translator_panel, _("Translation services"))

    def realize(self):
        self.sizer.Add(self.notebook, 0, wx.ALL, 5)
        ok_cancel_box = wx.BoxSizer(wx.HORIZONTAL)
        ok = wx.Button(self.panel, wx.ID_OK, _(u"&Save"))
        ok.SetDefault()
        cancel = wx.Button(self.panel, wx.ID_CANCEL, _(u"&Close"))
        self.SetEscapeId(cancel.GetId())
        ok_cancel_box.Add(ok, 0, wx.ALL, 5)
        ok_cancel_box.Add(cancel, 0, wx.ALL, 5)
        self.sizer.Add(ok_cancel_box, 0, wx.ALL, 5)
        self.panel.SetSizer(self.sizer)
        self.SetClientSize(self.sizer.CalcMin())

    def get_value(self, panel, key):
        p = getattr(self, panel)
        return getattr(p, key).GetValue()

    def set_value(self, panel, key, value):
        p = getattr(self, panel)
        control = getattr(p, key)
        getattr(control, "SetValue")(value)

