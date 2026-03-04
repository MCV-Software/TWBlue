# -*- coding: utf-8 -*-
import wx
import languageHandler


class AccountSettingsDialog(wx.Dialog):
    def __init__(self, parent=None, ask_before_boost=True):
        super(AccountSettingsDialog, self).__init__(parent, title=_("Bluesky Account Settings"))
        panel = wx.Panel(self)

        sizer = wx.BoxSizer(wx.VERTICAL)

        # Ask before boost/share
        self.ask_before_boost = wx.CheckBox(panel, wx.ID_ANY, _("Ask confirmation before sharing a post"))
        self.ask_before_boost.SetValue(bool(ask_before_boost))
        sizer.Add(self.ask_before_boost, 0, wx.ALL, 8)

        templates_box = wx.StaticBoxSizer(wx.StaticBox(panel, wx.ID_ANY, _("Templates")), wx.VERTICAL)
        self.template_post = wx.Button(panel, wx.ID_ANY, _("Edit template for posts"))
        self.template_person = wx.Button(panel, wx.ID_ANY, _("Edit template for persons"))
        self.template_notification = wx.Button(panel, wx.ID_ANY, _("Edit template for notifications"))
        templates_box.Add(self.template_post, 0, wx.ALL, 4)
        templates_box.Add(self.template_person, 0, wx.ALL, 4)
        templates_box.Add(self.template_notification, 0, wx.ALL, 4)
        sizer.Add(templates_box, 0, wx.EXPAND | wx.ALL, 8)

        # Buttons
        btn_sizer = self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL)

        panel.SetSizer(sizer)

        main = wx.BoxSizer(wx.VERTICAL)
        main.Add(panel, 1, wx.EXPAND | wx.ALL, 10)
        if btn_sizer:
            main.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 10)
        self.SetSizerAndFit(main)

    def get_values(self):
        return {
            "ask_before_boost": self.ask_before_boost.GetValue(),
        }

    def set_template_labels(self, post_template, person_template, notification_template):
        self.template_post.SetLabel(_("Edit template for posts. Current template: {}").format(post_template))
        self.template_person.SetLabel(_("Edit template for persons. Current template: {}").format(person_template))
        self.template_notification.SetLabel(_("Edit template for notifications. Current template: {}").format(notification_template))

