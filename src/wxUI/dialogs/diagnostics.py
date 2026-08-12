# -*- coding: utf-8 -*-
"""Source-only runtime diagnostics dialog."""

import wx


class DiagnosticsDialog(wx.Dialog):
    """Display a periodically refreshed snapshot of application resources."""

    def __init__(self, parent, snapshot_provider, on_close):
        super(DiagnosticsDialog, self).__init__(parent, title=_("Runtime diagnostics"))
        self.snapshot_provider = snapshot_provider
        self.on_close_callback = on_close
        self.timer = wx.Timer(self)
        self.values = {}

        panel = wx.Panel(self)
        self.panel = panel
        sizer = wx.BoxSizer(wx.VERTICAL)
        grid = wx.FlexGridSizer(cols=2, hgap=12, vgap=8)
        grid.AddGrowableCol(1, 1)
        self._add_row(grid, "rss", _("Resident memory (RSS)"))
        self._add_row(grid, "private", _("Private memory"))
        self._add_row(grid, "vms", _("Virtual memory (VMS)"))
        self._add_row(grid, "cpu", _("Process CPU usage"))
        self._add_row(grid, "threads", _("Process threads"))
        self._add_row(grid, "sessions", _("Loaded sessions"))
        self._add_row(grid, "buffers", _("Application buffers"))
        sizer.Add(grid, 0, wx.ALL | wx.EXPAND, 12)

        close_button = wx.Button(panel, wx.ID_CLOSE, _("&Close"))
        close_button.SetDefault()
        sizer.Add(close_button, 0, wx.ALL | wx.ALIGN_RIGHT, 8)
        panel.SetSizer(sizer)
        self.SetClientSize(sizer.CalcMin())
        self.CentreOnParent()

        self.Bind(wx.EVT_TIMER, self.refresh, self.timer)
        self.Bind(wx.EVT_BUTTON, self.on_close, close_button)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.refresh()
        self.timer.Start(1000)

    def _add_row(self, sizer, key, label):
        sizer.Add(wx.StaticText(self.panel, wx.ID_ANY, label), 0, wx.ALIGN_CENTER_VERTICAL)
        value = wx.StaticText(self.panel, wx.ID_ANY, "-")
        sizer.Add(value, 0, wx.ALIGN_CENTER_VERTICAL)
        self.values[key] = value

    def refresh(self, event=None):
        """Refresh values without creating a background monitoring task."""
        try:
            snapshot = self.snapshot_provider()
        except Exception:
            return

        self.values["rss"].SetLabel(self._format_mib(snapshot["rss"]))
        self.values["private"].SetLabel(self._format_mib(snapshot["private"]))
        self.values["vms"].SetLabel(self._format_mib(snapshot["vms"]))
        self.values["cpu"].SetLabel("{:.1f}%".format(snapshot["cpu_percent"]))
        self.values["threads"].SetLabel(str(snapshot["threads"]))
        self.values["sessions"].SetLabel(str(snapshot["sessions"]))
        self.values["buffers"].SetLabel(str(snapshot["buffers"]))

    @staticmethod
    def _format_mib(value):
        if value is None:
            return _("Not available")
        return "{:.2f} MiB".format(value / 1024**2)

    def on_close(self, event):
        if self.timer.IsRunning():
            self.timer.Stop()
        self.on_close_callback()
        self.Destroy()
