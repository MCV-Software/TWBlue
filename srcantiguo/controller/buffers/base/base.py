# -*- coding: utf-8 -*-
""" Common logic to all buffers in TWBlue."""
import logging
import wx
import output
import sound
import widgetUtils

log = logging.getLogger("controller.buffers.base.base")

class Buffer(object):
    """ A basic buffer object. This should be the base class for all other derived buffers."""

    def __init__(self, parent=None, function=None, session=None, *args, **kwargs):
        """Inits the main controller for this buffer:
          @ parent wx.Treebook object: Container where we will put this buffer.
          @ function str or None: function to be called periodically and update items on this buffer.
          @ session sessionmanager.session object or None: Session handler for settings, database and data access.
        """
        super(Buffer, self).__init__()
        self.function = function
        # Compose_function will be used to render an object on this buffer. Normally, signature is as follows:
        # compose_function(item, db, relative_times, show_screen_names=False, session=None)
        # Read more about compose functions in sessions/twitter/compose.py.
        self.compose_function = None
        self.args = args
        self.kwargs = kwargs
        # This will be used as a reference to the wx.Panel object wich stores the buffer GUI.
        self.buffer = None
        # This should countains the account associated to this buffer.
        self.account = ""
        # This controls whether the start_stream function should be called when starting the program.
        self.needs_init = True
        # if this is set to False, the buffer will be ignored on the invisible interface.
        self.invisible = False
        # Control variable, used to track time of execution for calls to start_stream.
        self.execution_time = 0

    def clear_list(self):
        pass

    def get_event(self, ev):
        """ Catch key presses in the WX interface and generate the corresponding event names."""
        if ev.GetKeyCode() == wx.WXK_RETURN and ev.ControlDown(): event = "audio"
        elif ev.GetKeyCode() == wx.WXK_RETURN: event = "url"
        elif ev.GetKeyCode() == wx.WXK_F5: event = "volume_down"
        elif ev.GetKeyCode() == wx.WXK_F6: event = "volume_up"
        elif ev.GetKeyCode() == wx.WXK_DELETE and ev.ShiftDown(): event = "clear_list"
        elif ev.GetKeyCode() == wx.WXK_DELETE: event = "destroy_status"
        # Raise a Special event when pressed Shift+F10 because Wx==4.1.x does not seems to trigger this by itself.
        # See https://github.com/manuelcortez/TWBlue/issues/353
        elif ev.GetKeyCode() == wx.WXK_F10 and ev.ShiftDown(): event = "show_menu"
        else:
            event = None
            ev.Skip()
        if event != None:
            try:
                ### ToDo: Remove after WX fixes issue #353 in the widgets.
                if event == "show_menu":
                    return self.show_menu(widgetUtils.MENU, pos=self.buffer.list.list.GetPosition())
                getattr(self, event)()
            except AttributeError:
                pass

    def volume_down(self):
        """ Decreases volume by 5%"""
        if self.session.settings["sound"]["volume"] > 0.0:
            if self.session.settings["sound"]["volume"] <= 0.05:
                self.session.settings["sound"]["volume"] = 0.0
            else:
                self.session.settings["sound"]["volume"] -=0.05
        sound.URLPlayer.player.audio_set_volume(int(self.session.settings["sound"]["volume"]*100.0))
        self.session.sound.play("volume_changed.ogg")
        self.session.settings.write()

    def volume_up(self):
        """ Increases volume by 5%."""
        if self.session.settings["sound"]["volume"] < 1.0:
            if self.session.settings["sound"]["volume"] >= 0.95:
                self.session.settings["sound"]["volume"] = 1.0
            else:
                self.session.settings["sound"]["volume"] +=0.05
        sound.URLPlayer.player.audio_set_volume(int(self.session.settings["sound"]["volume"]*100))
        self.session.sound.play("volume_changed.ogg")
        self.session.settings.write()

    def start_stream(self, mandatory=False, play_sound=True):
        pass

    def get_more_items(self):
        output.speak(_(u"This action is not supported for this buffer"), True)

    def put_items_on_list(self, items):
        pass

    def remove_buffer(self):
        return False

    def remove_item(self, item):
        f = self.buffer.list.get_selected()
        self.buffer.list.remove_item(item)
        self.buffer.list.select_item(f)

    def bind_events(self):
        pass

    def get_object(self):
        return self.buffer

    def get_message(self):
        pass

    def set_list_position(self, reversed=False):
        if reversed == False:
            self.buffer.list.select_item(-1)
        else:
            self.buffer.list.select_item(0)

    def reply(self):
        pass

    def send_message(self):
        pass

    def share_item(self):
        pass

    def can_share(self):
        pass

    def destroy_status(self):
        pass

    def post_status(self, *args, **kwargs):
        pass

    def save_positions(self):
        try:
            self.session.db[self.name+"_pos"]=self.buffer.list.get_selected()
        except AttributeError:
            pass

    def view_item(self):
        pass