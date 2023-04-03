# -*- coding: utf-8 -*-
import wx
import wx.adv
import application

class mainFrame(wx.Frame):
    """ Main class of the Frame. This is the Main Window."""

    ### MENU
    def makeMenus(self):
        """ Creates, bind and returns the menu bar for the application. Also in this function, the accel table is created."""
        self.menubar = wx.MenuBar()

        # Application menu
        self.menubar_application = wx.Menu()
        self.manage_accounts = self.menubar_application.Append(wx.ID_ANY, _(u"&Manage accounts"))
        self.updateProfile = self.menubar_application.Append(wx.ID_ANY, _("&Update profile"))
        self.updateProfile.Enable(False)
        self.show_hide = self.menubar_application.Append(wx.ID_ANY, _(u"&Hide window"))
        self.menuitem_search = self.menubar_application.Append(wx.ID_ANY, _(u"&Search"))
        self.lists = self.menubar_application.Append(wx.ID_ANY, _(u"&Lists manager"))
        self.lists.Enable(False)
        self.manageAliases = self.menubar_application.Append(wx.ID_ANY, _("Manage user aliases"))
        self.manageAliases.Enable(False)
        self.keystroke_editor = self.menubar_application.Append(wx.ID_ANY, _(u"&Edit keystrokes"))
        self.account_settings = self.menubar_application.Append(wx.ID_ANY, _(u"Account se&ttings"))
        self.prefs = self.menubar_application.Append(wx.ID_PREFERENCES, _(u"&Global settings"))
        self.close = self.menubar_application.Append(wx.ID_EXIT, _(u"E&xit"))

        # Compose menu
        self.menubar_item = wx.Menu()
        self.compose = self.menubar_item.Append(wx.ID_ANY, _(u"&Post"))
        self.reply = self.menubar_item.Append(wx.ID_ANY, _(u"Re&ply"))
        self.share = self.menubar_item.Append(wx.ID_ANY, _(u"&Boost"))
        self.fav = self.menubar_item.Append(wx.ID_ANY, _(u"&Add to favorites"))
        self.unfav = self.menubar_item.Append(wx.ID_ANY, _(u"&Remove from favorites"))
        self.view = self.menubar_item.Append(wx.ID_ANY, _(u"&Show post"))
        self.view_conversation = self.menubar_item.Append(wx.ID_ANY, _(u"View conversa&tion"))
        self.ocr = self.menubar_item.Append(wx.ID_ANY, _(u"Read text in picture"))
        self.ocr.Enable(False)
        self.delete = self.menubar_item.Append(wx.ID_ANY, _(u"&Delete"))

        # User menu
        self.menubar_user = wx.Menu()
        self.follow = self.menubar_user.Append(wx.ID_ANY, _(u"&Actions..."))
        self.timeline = self.menubar_user.Append(wx.ID_ANY, _(u"&View timeline..."))
        self.dm = self.menubar_user.Append(wx.ID_ANY, _(u"Direct me&ssage"))
        self.addAlias = self.menubar_user.Append(wx.ID_ANY, _("Add a&lias"))
        self.addAlias.Enable(False)
        self.addToList = self.menubar_user.Append(wx.ID_ANY, _(u"&Add to list"))
        self.removeFromList = self.menubar_user.Append(wx.ID_ANY, _(u"R&emove from list"))
        self.details = self.menubar_user.Append(wx.ID_ANY, _(u"Show user &profile"))
        self.favs = self.menubar_user.Append(wx.ID_ANY, _(u"V&iew likes"))

        # buffer menu
        self.menubar_buffer = wx.Menu()
        self.update_buffer = self.menubar_buffer.Append(wx.ID_ANY, _(u"&Update buffer"))
        self.trends = self.menubar_buffer.Append(wx.ID_ANY, _(u"New &trending topics buffer..."))
        self.filter = self.menubar_buffer.Append(wx.ID_ANY, _(u"Create a &filter"))
        self.manage_filters = self.menubar_buffer.Append(wx.ID_ANY, _(u"&Manage filters"))
        self.find = self.menubar_buffer.Append(wx.ID_ANY, _(u"Find a string in the currently focused buffer..."))
        self.load_previous_items = self.menubar_buffer.Append(wx.ID_ANY, _(u"&Load previous items"))
        self.menubar_buffer.AppendSeparator()
        self.mute_buffer = self.menubar_buffer.AppendCheckItem(wx.ID_ANY, _(u"&Mute"))
        self.autoread = self.menubar_buffer.AppendCheckItem(wx.ID_ANY, _(u"&Autoread"))
        self.clear = self.menubar_buffer.Append(wx.ID_ANY, _(u"&Clear buffer"))
        self.deleteTl = self.menubar_buffer.Append(wx.ID_ANY, _(u"&Destroy"))

        # audio menu
        self.menubar_audio = wx.Menu()
        self.seekLeft = self.menubar_audio.Append(wx.ID_ANY, _(u"&Seek back 5 seconds"))
        self.seekRight = self.menubar_audio.Append(wx.ID_ANY, _(u"&Seek forward 5 seconds"))

    # Help Menu
        self.menubar_help = wx.Menu()
        self.doc = self.menubar_help.Append(-1, _(u"&Documentation"))
        self.sounds_tutorial = self.menubar_help.Append(wx.ID_ANY, _(u"Sounds &tutorial"))
        self.changelog = self.menubar_help.Append(wx.ID_ANY, _(u"&What's new in this version?"))
        self.check_for_updates = self.menubar_help.Append(wx.ID_ANY, _(u"&Check for updates"))
        self.reportError = self.menubar_help.Append(wx.ID_ANY, _(u"&Report an error"))
        self.visit_website = self.menubar_help.Append(-1, _(u"{0}'s &website").format(application.name,))
        self.get_soundpacks = self.menubar_help.Append(-1, _(u"Get soundpacks for TWBlue"))
        self.about = self.menubar_help.Append(-1, _(u"About &{0}").format(application.name,))

        # Add all to the menu Bar
        self.menubar.Append(self.menubar_application, _(u"&Application"))
        self.menubar.Append(self.menubar_item, _("&Tweet"))
        self.menubar.Append(self.menubar_user, _(u"&User"))
        self.menubar.Append(self.menubar_buffer, _(u"&Buffer"))
        self.menubar.Append(self.menubar_audio, _(u"&Audio"))
        self.menubar.Append(self.menubar_help, _(u"&Help"))

        self.accel_tbl = wx.AcceleratorTable([
            (wx.ACCEL_CTRL, ord('N'), self.compose.GetId()),
            (wx.ACCEL_CTRL, ord('R'), self.reply.GetId()),
            (wx.ACCEL_CTRL|wx.ACCEL_SHIFT, ord('R'), self.share.GetId()),
            (wx.ACCEL_CTRL, ord('F'), self.fav.GetId()),
            (wx.ACCEL_CTRL|wx.ACCEL_SHIFT, ord('F'), self.unfav.GetId()),
            (wx.ACCEL_CTRL|wx.ACCEL_SHIFT, ord('V'), self.view.GetId()),
            (wx.ACCEL_CTRL, ord('D'), self.dm.GetId()),

            (wx.ACCEL_CTRL, ord('Q'), self.close.GetId()),
            (wx.ACCEL_CTRL, ord('S'), self.follow.GetId()),
            (wx.ACCEL_CTRL, ord('I'), self.timeline.GetId()),
            (wx.ACCEL_CTRL|wx.ACCEL_SHIFT, ord('I'), self.deleteTl.GetId()),
            (wx.ACCEL_CTRL, ord('M'), self.show_hide.GetId()),
            (wx.ACCEL_CTRL, wx.WXK_LEFT, self.seekLeft.GetId()),
            (wx.ACCEL_CTRL, ord('P'), self.updateProfile.GetId()),
            (wx.ACCEL_CTRL, wx.WXK_RIGHT, self.seekRight.GetId()),
            (wx.ACCEL_CTRL, ord(' '), self.seekLeft.GetId()),
        ])

        self.SetAcceleratorTable(self.accel_tbl)

    ### MAIN
    def __init__(self):
        """ Main function of this class."""
        super(mainFrame, self).__init__(None, -1, application.name, size=(1600, 1600))
        self.panel = wx.Panel(self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetTitle(application.name)
        self.makeMenus()
        self.SetMenuBar(self.menubar)
        self.nb = wx.Treebook(self.panel, wx.ID_ANY)
        self.buffers = {}

    def get_buffer_count(self):
        return self.nb.GetPageCount()

    def add_buffer(self, buffer, name):
        self.nb.AddPage(buffer, name)
        self.buffers[name] = buffer.GetId()

    def insert_buffer(self, buffer, name, pos):
        self.nb.InsertSubPage(pos, buffer, name)
        self.buffers[name] = buffer.GetId()

    def prepare(self):
        self.sizer.Add(self.nb, 0, wx.ALL, 5)
        self.panel.SetSizer(self.sizer)
#  self.Maximize()
        self.sizer.Layout()
        self.SetClientSize(self.sizer.CalcMin())
#  print self.GetSize()

    def get_buffers(self):
        return [self.nb.GetPage(i) for i in range(0, self.nb.GetPageCount())]

    def search(self, name_, account):
        for i in range(0, self.nb.GetPageCount()):
            if self.nb.GetPage(i).name == name_ and self.nb.GetPage(i).account == account: return i

    def get_current_buffer(self):
        return self.nb.GetCurrentPage()

    def get_current_buffer_pos(self):
        return self.nb.GetSelection()

    def get_buffer(self, pos):
        return self.GetPage(pos)

    def change_buffer(self, position):
        self.nb.ChangeSelection(position)

    def get_buffer_text(self):
        return self.nb.GetPageText(self.nb.GetSelection())

    def get_buffer_by_id(self, id):
        return self.nb.FindWindowById(id)
    def advance_selection(self, forward):
        self.nb.AdvanceSelection(forward)

    def show(self):
        self.Show()

    def show_address(self, address):
        wx.MessageDialog(self, address, _(u"Address"), wx.OK).ShowModal()

    def delete_buffer(self, pos):
        self.nb.DeletePage(pos)

    def about_dialog(self):
        info = wx.adv.AboutDialogInfo()
        info.SetName(application.name)
        info.SetVersion(application.version)
        info.SetDescription(application.description)
        info.SetCopyright(application.copyright)
        info.SetTranslators(application.translators)
#  info.SetLicence(application.licence)
        for i in application.authors:
            info.AddDeveloper(i)
        wx.adv.AboutBox(info)

    def set_focus(self):
        self.SetFocus()

    def check_menuitem(self, menuitem, check=True):
        if hasattr(self, menuitem):
            getattr(self, menuitem).Check(check)

    def set_page_title(self, page, title):
        return self.nb.SetPageText(page, title)

    def get_page_title(self, page):
        return self.nb.GetPageText(page)

def no_update_available():
    wx.MessageDialog(None, _(u"Your {0} version is up to date").format(application.name,), _(u"Update"), style=wx.OK).ShowModal()
