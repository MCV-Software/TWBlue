# -*- coding: utf-8 -*-
import time
import wx
import widgetUtils
import arrow
import webbrowser
import output
import config
import sound
import languageHandler
import logging
from audio_services import youtube_utils
from controller.buffers.base import base
from sessions.mastodon import compose, utils, templates
from mysc.thread_utils import call_threaded
from pubsub import pub
from extra import ocr
from wxUI import buffers, dialogs, commonMessageDialogs, menus

log = logging.getLogger("controller.buffers.mastodon.base")

class BaseBuffer(base.Buffer):
    def __init__(self, parent, function, name, sessionObject, account, sound=None, compose_func="compose_toot", *args, **kwargs):
        super(BaseBuffer, self).__init__(parent, function, *args, **kwargs)
        log.debug("Initializing buffer %s, account %s" % (name, account,))
        self.buffer = buffers.mastodon.basePanel(parent, name)
        self.invisible = True
        self.name = name
        self.type = self.buffer.type
        self.session = sessionObject
        self.compose_function = getattr(compose, compose_func)
        log.debug("Compose_function: %s" % (self.compose_function,))
        self.account = account
        self.buffer.account = account
        self.bind_events()
        self.sound = sound

    def get_buffer_name(self):
        """ Get buffer name from a set of different techniques."""
        # firstly let's take the easier buffers.
        basic_buffers = dict(home_timeline=_("Home"), local_timeline=_("Local"), federated_timeline=_("Federated"), mentions=_(u"Mentions"), direct_messages=_(u"Direct messages"), sent_direct_messages=_(u"Sent direct messages"), sent_tweets=_(u"Sent tweets"), favourites=_(u"Likes"), followers=_(u"Followers"), friends=_(u"Friends"), blocked=_(u"Blocked users"), muted=_(u"Muted users"))
        if self.name in list(basic_buffers.keys()):
            return basic_buffers[self.name]
        # Check user timelines
        elif hasattr(self, "username"):
            if "-timeline" in self.name:
                return _(u"{username}'s timeline").format(username=self.username,)
            elif "-favorite" in self.name:
                return _(u"{username}'s likes").format(username=self.username,)
            elif "-followers" in self.name:
                return _(u"{username}'s followers").format(username=self.username,)
            elif "-friends" in self.name:
                return _(u"{username}'s friends").format(username=self.username,)
        log.error("Error getting name for buffer %s" % (self.name,))
        return _(u"Unknown buffer")

    def post_status(self, *args, **kwargs):
        title = _("Toot")
        caption = _("Write your message here")
        pass

    def get_formatted_message(self):
        return self.compose_function(self.get_item(), self.session.db, self.session.settings["general"]["relative_times"], self.session.settings["general"]["show_screen_names"])[1]

    def get_message(self):
        template = self.session.settings["templates"]["toot"]
        toot = self.get_item()
        t = templates.render_toot(toot, template, relative_times=self.session.settings["general"]["relative_times"], offset_hours=self.session.db["utc_offset"])
        return t

    def start_stream(self, mandatory=False, play_sound=True, avoid_autoreading=False):
        current_time = time.time()
        if self.execution_time == 0 or current_time-self.execution_time >= 180 or mandatory==True:
            self.execution_time = current_time
            log.debug("Starting stream for buffer %s, account %s and type %s" % (self.name, self.account, self.type))
            log.debug("args: %s, kwargs: %s" % (self.args, self.kwargs))
            count = self.session.settings["general"]["max_toots_per_call"]
            min_id = None
            if self.name in self.session.db and len(self.session.db[self.name]) > 0:
                min_id = self.session.db[self.name][0].id
            try:
                results = getattr(self.session.api, self.function)(min_id=min_id, limit=count, *self.args, **self.kwargs)
                results.reverse()
            except Exception as e:
                log.exception("Error %s" % (str(e)))
                return
            number_of_items = self.session.order_buffer(self.name, results)
            log.debug("Number of items retrieved: %d" % (number_of_items,))
            self.put_items_on_list(number_of_items)
            if number_of_items > 0 and  self.name != "sent_toots" and self.name != "sent_direct_messages" and self.sound != None and self.session.settings["sound"]["session_mute"] == False and self.name not in self.session.settings["other_buffers"]["muted_buffers"] and play_sound == True:
                self.session.sound.play(self.sound)
            # Autoread settings
            if avoid_autoreading == False and mandatory == True and number_of_items > 0 and self.name in self.session.settings["other_buffers"]["autoread_buffers"]:
                self.auto_read(number_of_items)
            return number_of_items

    def auto_read(self, number_of_items):
        if number_of_items == 1 and self.name in self.session.settings["other_buffers"]["autoread_buffers"] and self.name not in self.session.settings["other_buffers"]["muted_buffers"] and self.session.settings["sound"]["session_mute"] == False:
            if self.session.settings["general"]["reverse_timelines"] == False:
                toot = self.session.db[self.name][-1]
            else:
                toot = self.session.db[self.name][0]
            output.speak(_("New toot in {0}").format(self.get_buffer_name()))
            output.speak(" ".join(self.compose_function(toot, self.session.db, self.session.settings["general"]["relative_times"], self.session.settings["general"]["show_screen_names"])))
        elif number_of_items > 1 and self.name in self.session.settings["other_buffers"]["autoread_buffers"] and self.name not in self.session.settings["other_buffers"]["muted_buffers"] and self.session.settings["sound"]["session_mute"] == False:
            output.speak(_("{0} new toots in {1}.").format(number_of_items, self.get_buffer_name()))

    def get_more_items(self):
        elements = []
        if self.session.settings["general"]["reverse_timelines"] == False:
            max_id = self.session.db[self.name][0].id
        else:
            max_id = self.session.db[self.name][-1].id
        try:
            items = getattr(self.session.api, self.function)(max_id=max_id, limit=self.session.settings["general"]["max_tweets_per_call"], *self.args, **self.kwargs)
        except Exception as e:
            log.exception("Error %s" % (str(e)))
            return
        items_db = self.session.db[self.name]
        for i in items:
            if utils.find_item(i, self.session.db[self.name]) == None:
                elements.append(i)
                if self.session.settings["general"]["reverse_timelines"] == False:
                    items_db.insert(0, i)
                else:
                    items_db.append(i)
        self.session.db[self.name] = items_db
        selection = self.buffer.list.get_selected()
        log.debug("Retrieved %d items from cursored search in function %s." % (len(elements), self.function))
        if self.session.settings["general"]["reverse_timelines"] == False:
            for i in elements:
                toot = self.compose_function(i, self.session.db, self.session.settings["general"]["relative_times"], self.session.settings["general"]["show_screen_names"])
                self.buffer.list.insert_item(True, *toot)
        else:
            for i in items:
                toot = self.compose_function(i, self.session.db, self.session.settings["general"]["relative_times"], self.session.settings["general"]["show_screen_names"])
                self.buffer.list.insert_item(False, *toot)
            self.buffer.list.select_item(selection)
        output.speak(_(u"%s items retrieved") % (str(len(elements))), True)

    def remove_buffer(self, force=False):
        if "-timeline" in self.name:
            if force == False:
                dlg = commonMessageDialogs.remove_buffer()
            else:
                dlg = widgetUtils.YES
            if dlg == widgetUtils.YES:
                if self.name[:-9] in self.session.settings["other_buffers"]["timelines"]:
                    self.session.settings["other_buffers"]["timelines"].remove(self.name[:-9])
                    self.session.settings.write()
                    if self.name in self.session.db:
                        self.session.db.pop(self.name)
                    return True
            elif dlg == widgetUtils.NO:
                return False
        elif "favorite" in self.name:
            if force == False:
                dlg = commonMessageDialogs.remove_buffer()
            else:
                dlg = widgetUtils.YES
            if dlg == widgetUtils.YES:
                if self.name[:-9] in self.session.settings["other_buffers"]["favourites_timelines"]:
                    self.session.settings["other_buffers"]["favourites_timelines"].remove(self.name[:-9])
                    if self.name in self.session.db:
                        self.session.db.pop(self.name)
                    self.session.settings.write()
                    return True
            elif dlg == widgetUtils.NO:
                return False
        else:
            output.speak(_(u"This buffer is not a timeline; it can't be deleted."), True)
            return False

    def put_items_on_list(self, number_of_items):
        list_to_use = self.session.db[self.name]
        if number_of_items == 0 and self.session.settings["general"]["persist_size"] == 0: return
        log.debug("The list contains %d items " % (self.buffer.list.get_count(),))
        log.debug("Putting %d items on the list" % (number_of_items,))
        if self.buffer.list.get_count() == 0:
            for i in list_to_use:
                toot = self.compose_function(i, self.session.db, self.session.settings["general"]["relative_times"], self.session.settings["general"]["show_screen_names"])
                self.buffer.list.insert_item(False, *toot)
            self.buffer.set_position(self.session.settings["general"]["reverse_timelines"])
        elif self.buffer.list.get_count() > 0 and number_of_items > 0:
            if self.session.settings["general"]["reverse_timelines"] == False:
                items = list_to_use[len(list_to_use)-number_of_items:]
                for i in items:
                    toot = self.compose_function(i, self.session.db, self.session.settings["general"]["relative_times"], self.session.settings["general"]["show_screen_names"])
                    self.buffer.list.insert_item(False, *toot)
            else:
                items = list_to_use[0:number_of_items]
                items.reverse()
                for i in items:
                    toot = self.compose_function(i, self.session.db, self.session.settings["general"]["relative_times"], self.session.settings["general"]["show_screen_names"])
                    self.buffer.list.insert_item(True, *toot)
        log.debug("Now the list contains %d items " % (self.buffer.list.get_count(),))

    def add_new_item(self, item):
        toot = self.compose_function(item, self.session.db, self.session.settings["general"]["relative_times"], self.session.settings["general"]["show_screen_names"])
        if self.session.settings["general"]["reverse_timelines"] == False:
            self.buffer.list.insert_item(False, *toot)
        else:
            self.buffer.list.insert_item(True, *toot)
        if self.name in self.session.settings["other_buffers"]["autoread_buffers"] and self.name not in self.session.settings["other_buffers"]["muted_buffers"] and self.session.settings["sound"]["session_mute"] == False:
            output.speak(" ".join(toot[:2]), speech=self.session.settings["reporting"]["speech_reporting"], braille=self.session.settings["reporting"]["braille_reporting"])

    def bind_events(self):
        log.debug("Binding events...")
        self.buffer.set_focus_function(self.onFocus)
        widgetUtils.connect_event(self.buffer.list.list, widgetUtils.KEYPRESS, self.get_event)
#        widgetUtils.connect_event(self.buffer, widgetUtils.BUTTON_PRESSED, self.post_status, self.buffer.tweet)
#        widgetUtils.connect_event(self.buffer, widgetUtils.BUTTON_PRESSED, self.share_item, self.buffer.retweet)
#        widgetUtils.connect_event(self.buffer, widgetUtils.BUTTON_PRESSED, self.send_message, self.buffer.dm)
#        widgetUtils.connect_event(self.buffer, widgetUtils.BUTTON_PRESSED, self.reply, self.buffer.reply)
#        widgetUtils.connect_event(self.buffer.list.list, wx.EVT_LIST_ITEM_RIGHT_CLICK, self.show_menu)
#        widgetUtils.connect_event(self.buffer.list.list, wx.EVT_LIST_KEY_DOWN, self.show_menu_by_key)

    def show_menu(self, ev, pos=0, *args, **kwargs):
        pass

    def view(self, *args, **kwargs):
        pub.sendMessage("execute-action", action="view_item")

    def copy(self, *args, **kwargs):
        pub.sendMessage("execute-action", action="copy_to_clipboard")

    def user_actions(self, *args, **kwargs):
        pub.sendMessage("execute-action", action="follow")

    def fav(self, *args, **kwargs):
        pub.sendMessage("execute-action", action="add_to_favourites")

    def unfav(self, *args, **kwargs):
        pub.sendMessage("execute-action", action="remove_from_favourites")

    def delete_item_(self, *args, **kwargs):
        pub.sendMessage("execute-action", action="delete_item")

    def url_(self, *args, **kwargs):
        self.url()

    def show_menu_by_key(self, ev):
        if self.buffer.list.get_count() == 0:
            return
        if ev.GetKeyCode() == wx.WXK_WINDOWS_MENU:
            self.show_menu(widgetUtils.MENU, pos=self.buffer.list.list.GetPosition())

    def get_item(self):
        index = self.buffer.list.get_selected()
        if index > -1 and self.session.db.get(self.name) != None:
            return self.session.db[self.name][index]

    def can_share(self):
        return True

    def reply(self, *args, **kwargs):
        toot = self.get_item()
        pass

    def send_message(self, *args, **kwargs):
        toot = self.get_item()
        pass

    def share_item(self, *args, **kwargs):
        if self.can_share() == False:
            return output.speak(_("This action is not supported on protected accounts."))
        toot = self.get_right_tweet()
        id = toot.id
        pass

    def _direct_retweet(self, id):
        item = self.session.api_call(call_name="retweet", _sound="retweet_send.ogg", id=id)
        pass

    def onFocus(self, *args, **kwargs):
        toot = self.get_item()
        if self.session.settings["general"]["relative_times"] == True:
            original_date = arrow.get(self.session.db[self.name][self.buffer.list.get_selected()].created_at)
            ts = original_date.humanize(locale=languageHandler.getLanguage())
            self.buffer.list.list.SetItem(self.buffer.list.get_selected(), 2, ts)
#        if self.session.settings['sound']['indicate_audio'] and utils.is_audio(toot):
#            self.session.sound.play("audio.ogg")
#        if self.session.settings['sound']['indicate_img'] and utils.is_media(toot):
#            self.session.sound.play("image.ogg")
#        can_share = self.can_share()
#        pub.sendMessage("toggleShare", shareable=can_share)
#        self.buffer.retweet.Enable(can_share)

    def audio(self, url='', *args, **kwargs):
        if sound.URLPlayer.player.is_playing():
            return sound.URLPlayer.stop_audio()
        toot = self.get_item()
        if toot == None:
            return
        pass

    def url(self, url='', announce=True, *args, **kwargs):
        if url == '':
            toot = self.get_item()
            pass

    def clear_list(self):
        dlg = commonMessageDialogs.clear_list()
        if dlg == widgetUtils.YES:
            self.session.db[self.name] = []
            self.buffer.list.clear()

    def destroy_status(self, *args, **kwargs):
        index = self.buffer.list.get_selected()
        pass

    def user_details(self):
        item = self.get_item()
        pass

    def get_item_url(self):
        toot = self.get_item()
        return toot.url

    def open_in_browser(self, *args, **kwargs):
        url = self.get_item_url()
        output.speak(_(u"Opening item in web browser..."))
        webbrowser.open(url)

    def add_to_favorites(self):
        id = self.get_item().id
        pass

    def remove_from_favorites(self):
        id = self.get_item().id
        pass

    def toggle_favorite(self):
        id = self.get_toot().id
        pass

    def view_item(self):
        toot = self.get_item()
        pass

    def ocr_image(self):
        toot = self.get_item()
        media_list = []
        pass