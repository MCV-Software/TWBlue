# -*- coding: utf-8 -*-
import wx
import widgetUtils
from wxUI.dialogs import baseDialog
# As some panels are the same than those used in Twitter sessions, let's import them directly.
from wxUI.dialogs.configuration import reporting, other_buffers
from multiplatform_widgets import widgets

class generalAccount(wx.Panel, baseDialog.BaseWXDialog):

    def __init__(self, parent):
        super(generalAccount, self).__init__(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        userAutocompletionBox = wx.StaticBox(self, label=_("User autocompletion settings"))
        self.userAutocompletionScan = wx.Button(self, wx.ID_ANY, _("Scan acc&ount and add followers and following users to the user autocompletion database"))
        self.userAutocompletionManage = wx.Button(self, wx.ID_ANY, _("&Manage autocompletion database"))
        autocompletionSizer = wx.StaticBoxSizer(userAutocompletionBox, wx.HORIZONTAL)
        autocompletionSizer.Add(self.userAutocompletionScan, 0, wx.ALL, 5)
        autocompletionSizer.Add(self.userAutocompletionManage, 0, wx.ALL, 5)
        sizer.Add(autocompletionSizer, 0, wx.ALL, 5)
        self.disable_streaming = wx.CheckBox(self, wx.ID_ANY, _("&Disable Streaming API endpoints"))
        sizer.Add(self.disable_streaming, 0, wx.ALL, 5)
        self.relative_time = wx.CheckBox(self, wx.ID_ANY, _("&Relative timestamps"))
        sizer.Add(self.relative_time, 0, wx.ALL, 5)
        self.read_preferences_from_instance = wx.CheckBox(self, wx.ID_ANY, _("R&ead preferences from instance (default visibility when publishing and displaying sensitive content)"))
        sizer.Add(self.read_preferences_from_instance, 0, wx.ALL, 5)
        itemsPerCallBox = wx.BoxSizer(wx.HORIZONTAL)
        itemsPerCallBox.Add(wx.StaticText(self, -1, _("&Items on each API call")), 0, wx.ALL, 5)
        self.itemsPerApiCall = wx.SpinCtrl(self, wx.ID_ANY)
        self.itemsPerApiCall.SetRange(0, 40)
        self.itemsPerApiCall.SetSize(self.itemsPerApiCall.GetBestSize())
        itemsPerCallBox.Add(self.itemsPerApiCall, 0, wx.ALL, 5)
        sizer.Add(itemsPerCallBox, 0, wx.ALL, 5)
        self.reverse_timelines = wx.CheckBox(self, wx.ID_ANY, _("I&nverted buffers: The newest items will be shown at the beginning while the oldest at the end"))
        sizer.Add(self.reverse_timelines, 0, wx.ALL, 5)
        self.ask_before_boost = wx.CheckBox(self, wx.ID_ANY, _("&Ask confirmation before boosting a post"))
        sizer.Add(self.ask_before_boost, 0, wx.ALL, 5)
        self.show_screen_names = wx.CheckBox(self, wx.ID_ANY, _("S&how screen names instead of full names"))
        sizer.Add(self.show_screen_names, 0, wx.ALL, 5)
        self.hide_emojis = wx.CheckBox(self, wx.ID_ANY, _("Hide e&mojis in usernames"))
        sizer.Add(self.hide_emojis, 0, wx.ALL, 5)
        PersistSizeLabel = wx.StaticText(self, -1, _("&Number of items per buffer to cache in database (0 to disable caching, blank for unlimited)"))
        self.persist_size = wx.TextCtrl(self, -1)
        sizer.Add(PersistSizeLabel, 0, wx.ALL, 5)
        sizer.Add(self.persist_size, 0, wx.ALL, 5)
        self.load_cache_in_memory = wx.CheckBox(self, wx.NewId(), _("&Load cache for items in memory (much faster in big datasets but requires more RAM)"))
        self.SetSizer(sizer)

class templates(wx.Panel, baseDialog.BaseWXDialog):
    def __init__(self, parent, post_template, conversation_template, person_template):
        super(templates, self).__init__(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.post = wx.Button(self, wx.ID_ANY, _("Edit template for &posts. Current template: {}").format(post_template))
        sizer.Add(self.post, 0, wx.ALL, 5)
        self.conversation = wx.Button(self, wx.ID_ANY, _("Edit template for c&onversations. Current template: {}").format(conversation_template))
        sizer.Add(self.conversation, 0, wx.ALL, 5)
        self.person = wx.Button(self, wx.ID_ANY, _("Edit template for p&ersons. Current template: {}").format(person_template))
        sizer.Add(self.person, 0, wx.ALL, 5)
        self.SetSizer(sizer)

class sound(wx.Panel):
    def __init__(self, parent, input_devices, output_devices, soundpacks):
        wx.Panel.__init__(self, parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        volume = wx.StaticText(self, -1, _(u"&Volume"))
        self.volumeCtrl = wx.Slider(self)
        # Connect a key handler here to handle volume slider being inverted when moving with up and down arrows.
        # see https://github.com/manuelcortez/TWBlue/issues/261
        widgetUtils.connect_event(self.volumeCtrl, widgetUtils.KEYPRESS, self.on_keypress)
        self.volumeCtrl.SetRange(0, 100)
        self.volumeCtrl.SetSize(self.volumeCtrl.GetBestSize())
        volumeBox = wx.BoxSizer(wx.HORIZONTAL)
        volumeBox.Add(volume, 0, wx.ALL, 5)
        volumeBox.Add(self.volumeCtrl, 0, wx.ALL, 5)
        sizer.Add(volumeBox, 0, wx.ALL, 5)
        self.session_mute = wx.CheckBox(self, -1, _(u"S&ession mute"))
        sizer.Add(self.session_mute, 0, wx.ALL, 5)
        output_label = wx.StaticText(self, -1, _(u"&Output device"))
        self.output = wx.ComboBox(self, -1, choices=output_devices, style=wx.CB_READONLY)
        self.output.SetSize(self.output.GetBestSize())
        outputBox = wx.BoxSizer(wx.HORIZONTAL)
        outputBox.Add(output_label, 0, wx.ALL, 5)
        outputBox.Add(self.output, 0, wx.ALL, 5)
        sizer.Add(outputBox, 0, wx.ALL, 5)
        input_label = wx.StaticText(self, -1, _(u"&Input device"))
        self.input = wx.ComboBox(self, -1, choices=input_devices, style=wx.CB_READONLY)
        self.input.SetSize(self.input.GetBestSize())
        inputBox = wx.BoxSizer(wx.HORIZONTAL)
        inputBox.Add(input_label, 0, wx.ALL, 5)
        inputBox.Add(self.input, 0, wx.ALL, 5)
        sizer.Add(inputBox, 0, wx.ALL, 5)
        soundBox =  wx.BoxSizer(wx.VERTICAL)
        soundpack_label = wx.StaticText(self, -1, _(u"Sound &pack"))
        self.soundpack = wx.ComboBox(self, -1, choices=soundpacks, style=wx.CB_READONLY)
        self.soundpack.SetSize(self.soundpack.GetBestSize())
        soundBox.Add(soundpack_label, 0, wx.ALL, 5)
        soundBox.Add(self.soundpack, 0, wx.ALL, 5)
        sizer.Add(soundBox, 0, wx.ALL, 5)
        self.indicate_audio = wx.CheckBox(self, -1, _("Indicate &audio or video in posts with sound"))
        sizer.Add(self.indicate_audio, 0, wx.ALL, 5)
        self.indicate_img = wx.CheckBox(self, -1, _("Indicate posts containing i&mages with sound"))
        sizer.Add(self.indicate_img, 0, wx.ALL, 5)
        self.SetSizer(sizer)

    def on_keypress(self, event, *args, **kwargs):
        """ Invert movement of up and down arrow keys when dealing with a wX Slider.
        See https://github.com/manuelcortez/TWBlue/issues/261
        and http://trac.wxwidgets.org/ticket/2068
        """
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_UP:
            return self.volumeCtrl.SetValue(self.volumeCtrl.GetValue()+1)
        elif keycode == wx.WXK_DOWN:
            return self.volumeCtrl.SetValue(self.volumeCtrl.GetValue()-1)
        event.Skip()

    def get(self, control):
        return getattr(self, control).GetStringSelection()

class extrasPanel(wx.Panel):
    def __init__(self, parent, ocr_languages=[], translation_languages=[]):
        super(extrasPanel, self).__init__(parent)
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        OCRBox = wx.StaticBox(self, label=_(u"&Language for OCR"))
        self.ocr_lang = wx.ListBox(self, -1, choices=ocr_languages)
        self.ocr_lang.SetSize(self.ocr_lang.GetBestSize())
        ocrLanguageSizer = wx.StaticBoxSizer(OCRBox, wx.HORIZONTAL)
        ocrLanguageSizer.Add(self.ocr_lang, 0, wx.ALL, 5)
        mainSizer.Add(ocrLanguageSizer, 0, wx.ALL, 5)
        self.SetSizer(mainSizer)

class configurationDialog(baseDialog.BaseWXDialog):
    def set_title(self, title):
        self.SetTitle(title)

    def __init__(self):
        super(configurationDialog, self).__init__(None, -1)
        self.panel = wx.Panel(self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.notebook = wx.Notebook(self.panel)

    def create_general_account(self):
        self.general = generalAccount(self.notebook)
        self.notebook.AddPage(self.general, _(u"General"))
        self.general.SetFocus()

    def create_reporting(self):
        self.reporting = reporting(self.notebook)
        self.notebook.AddPage(self.reporting, _(u"Feedback"))

    def create_other_buffers(self):
        self.buffers = other_buffers(self.notebook)
        self.notebook.AddPage(self.buffers, _(u"Buffers"))

    def create_templates(self, post_template, conversation_template, person_template):
        self.templates = templates(self.notebook, post_template=post_template, conversation_template=conversation_template, person_template=person_template)
        self.notebook.AddPage(self.templates, _("Templates"))

    def create_sound(self, output_devices, input_devices, soundpacks):
        self.sound = sound(self.notebook, output_devices, input_devices, soundpacks)
        self.notebook.AddPage(self.sound, _(u"Sound"))

    def create_extras(self, ocr_languages=[], translator_languages=[]):
        self.extras = extrasPanel(self.notebook, ocr_languages, translator_languages)
        self.notebook.AddPage(self.extras, _(u"Extras"))

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

