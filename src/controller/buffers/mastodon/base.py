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
from mastodon import MastodonNotFoundError
from audio_services import youtube_utils
from controller.buffers.base import base
from controller.mastodon import messages
from sessions.mastodon import compose, utils, templates
from mysc.thread_utils import call_threaded
from pubsub import pub
from extra import ocr
from wxUI import buffers, commonMessageDialogs
from wxUI.dialogs.mastodon import menus
from wxUI.dialogs.mastodon import dialogs as mastodon_dialogs
from wxUI.dialogs.mastodon.postDialogs import attachedPoll
from wxUI.dialogs import urlList

log = logging.getLogger("controller.buffers.mastodon.base")

class BaseBuffer(base.Buffer):
    def __init__(self, parent, function, name, sessionObject, account, sound=None, compose_func="compose_post", *args, **kwargs):
        super(BaseBuffer, self).__init__(parent, function, *args, **kwargs)
        log.debug("Initializing buffer %s, account %s" % (name, account,))
        self.create_buffer(parent, name)
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
        if "-timeline" in self.name or "-followers" in self.name or "-following" in self.name or "searchterm" in self.name:
            self.finished_timeline = False

    def create_buffer(self, parent, name):
        self.buffer = buffers.mastodon.basePanel(parent, name)

    def get_buffer_name(self):
        """ Get buffer name from a set of different techniques."""
        # firstly let's take the easier buffers.
        basic_buffers = dict(home_timeline=_("Home"), local_timeline=_("Local"), federated_timeline=_("Federated"), mentions=_("Mentions"), bookmarks=_("Bookmarks"), direct_messages=_("Direct messages"),  sent=_("Sent"), favorites=_("Favorites"), followers=_("Followers"), following=_("Following"), blocked=_("Blocked users"), muted=_("Muted users"), notifications=_("Notifications"))
        if self.name in list(basic_buffers.keys()):
            return basic_buffers[self.name]
        # Check user timelines
        elif hasattr(self, "username"):
            if "-timeline" in self.name:
                return _(u"{username}'s timeline").format(username=self.username,)
            elif "-followers" in self.name:
                return _(u"{username}'s followers").format(username=self.username,)
            elif "-following" in self.name:
                return _(u"{username}'s following").format(username=self.username,)
        log.error("Error getting name for buffer %s" % (self.name,))
        return _(u"Unknown buffer")

    def post_status(self, *args, **kwargs):
        title = _("Post")
        caption = _("Write your post here")
        post = messages.post(session=self.session, title=title, caption=caption)
        response = post.message.ShowModal()
        if response == wx.ID_OK:
            post_data = post.get_data()
            call_threaded(self.session.send_post, posts=post_data, visibility=post.get_visibility(), **kwargs)
        if hasattr(post.message, "destroy"):
            post.message.destroy()

    def get_formatted_message(self):
        safe = True
        if self.session.settings["general"]["read_preferences_from_instance"]:
            safe = self.session.expand_spoilers == False
        return self.compose_function(self.get_item(), self.session.db, self.session.settings, self.session.settings["general"]["relative_times"], self.session.settings["general"]["show_screen_names"], safe=safe)[1]

    def get_message(self):
        post = self.get_item()
        if post == None:
            return
        template = self.session.settings["templates"]["post"]
        # If template is set to hide sensitive media by default, let's change it according to user preferences.
        if self.session.settings["general"]["read_preferences_from_instance"] == True:
            if self.session.expand_spoilers == True and "$safe_text" in template:
                template = template.replace("$safe_text", "$text")
            elif self.session.expand_spoilers == False and "$text" in template:
                template = template.replace("$text", "$safe_text")
        t = templates.render_post(post, template, self.session.settings, relative_times=self.session.settings["general"]["relative_times"], offset_hours=self.session.db["utc_offset"])
        return t

    def start_stream(self, mandatory=False, play_sound=True, avoid_autoreading=False):
        current_time = time.time()
        if self.execution_time == 0 or current_time-self.execution_time >= 180 or mandatory==True:
            self.execution_time = current_time
            log.debug("Starting stream for buffer %s, account %s and type %s" % (self.name, self.account, self.type))
            log.debug("args: %s, kwargs: %s" % (self.args, self.kwargs))
            count = self.session.settings["general"]["max_posts_per_call"]
            min_id = None
            # toDo: Implement reverse timelines properly here.
            if (self.name != "favorites" and self.name != "bookmarks") and self.name in self.session.db and len(self.session.db[self.name]) > 0:
                if self.session.settings["general"]["reverse_timelines"]:
                    min_id = self.session.db[self.name][0].id
                else:
                    min_id = self.session.db[self.name][-1].id
            try:
                results = getattr(self.session.api, self.function)(min_id=min_id, limit=count, *self.args, **self.kwargs)
                results.reverse()
            except Exception as e:
                log.exception("Error %s" % (str(e)))
                return
            number_of_items = self.session.order_buffer(self.name, results)
            log.debug("Number of items retrieved: %d" % (number_of_items,))
            if hasattr(self, "finished_timeline") and self.finished_timeline == False:
                if "-timeline" in self.name:
                    self.username = self.session.db[self.name][0]["account"].username
                    pub.sendMessage("core.change_buffer_title", name=self.session.get_name(), buffer=self.name, title=_("Timeline for {}").format(self.username))
                self.finished_timeline = True
            self.put_items_on_list(number_of_items)
            if number_of_items > 0 and  self.name != "sent_posts" and self.name != "sent_direct_messages" and self.sound != None and self.session.settings["sound"]["session_mute"] == False and self.name not in self.session.settings["other_buffers"]["muted_buffers"] and play_sound == True:
                self.session.sound.play(self.sound)
            # Autoread settings
            if avoid_autoreading == False and mandatory == True and number_of_items > 0 and self.name in self.session.settings["other_buffers"]["autoread_buffers"]:
                self.auto_read(number_of_items)
            return number_of_items

    def auto_read(self, number_of_items):
        if number_of_items == 1 and self.name in self.session.settings["other_buffers"]["autoread_buffers"] and self.name not in self.session.settings["other_buffers"]["muted_buffers"] and self.session.settings["sound"]["session_mute"] == False:
            if self.session.settings["general"]["reverse_timelines"] == False:
                post = self.session.db[self.name][-1]
            else:
                post = self.session.db[self.name][0]
            output.speak(_("New post in {0}").format(self.get_buffer_name()))
            safe = True
            if self.session.settings["general"]["read_preferences_from_instance"]:
                safe = self.session.expand_spoilers == False
            output.speak(" ".join(self.compose_function(post, self.session.db, self.session.settings, self.session.settings["general"]["relative_times"], self.session.settings["general"]["show_screen_names"], safe=safe)))
        elif number_of_items > 1 and self.name in self.session.settings["other_buffers"]["autoread_buffers"] and self.name not in self.session.settings["other_buffers"]["muted_buffers"] and self.session.settings["sound"]["session_mute"] == False:
            output.speak(_("{0} new posts in {1}.").format(number_of_items, self.get_buffer_name()))

    def get_more_items(self):
        elements = []
        if self.session.settings["general"]["reverse_timelines"] == False:
            max_id = self.session.db[self.name][0].id
        else:
            max_id = self.session.db[self.name][-1].id
        try:
            items = getattr(self.session.api, self.function)(max_id=max_id, limit=self.session.settings["general"]["max_posts_per_call"], *self.args, **self.kwargs)
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
        safe = True
        if self.session.settings["general"]["read_preferences_from_instance"]:
            safe = self.session.expand_spoilers == False
        if self.session.settings["general"]["reverse_timelines"] == False:
            for i in elements:
                post = self.compose_function(i, self.session.db, self.session.settings, self.session.settings["general"]["relative_times"], self.session.settings["general"]["show_screen_names"], safe=safe)
                self.buffer.list.insert_item(True, *post)
        else:
            for i in elements:
                post = self.compose_function(i, self.session.db, self.session.settings, self.session.settings["general"]["relative_times"], self.session.settings["general"]["show_screen_names"], safe=safe)
                self.buffer.list.insert_item(False, *post)
            self.buffer.list.select_item(selection)
        output.speak(_(u"%s items retrieved") % (str(len(elements))), True)

    def remove_buffer(self, force=False):
        if "-timeline" in self.name:
            if force == False:
                dlg = commonMessageDialogs.remove_buffer()
            else:
                dlg = widgetUtils.YES
            if dlg == widgetUtils.YES:
                if self.kwargs.get("id") in self.session.settings["other_buffers"]["timelines"]:
                    self.session.settings["other_buffers"]["timelines"].remove(self.kwargs.get("id"))
                    self.session.settings.write()
                if self.name in self.session.db:
                    self.session.db.pop(self.name)
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
        safe = True
        if self.session.settings["general"]["read_preferences_from_instance"]:
            safe = self.session.expand_spoilers == False
        if self.buffer.list.get_count() == 0:
            for i in list_to_use:
                post = self.compose_function(i, self.session.db, self.session.settings, self.session.settings["general"]["relative_times"], self.session.settings["general"]["show_screen_names"], safe=safe)
                self.buffer.list.insert_item(False, *post)
            self.buffer.set_position(self.session.settings["general"]["reverse_timelines"])
        elif self.buffer.list.get_count() > 0 and number_of_items > 0:
            if self.session.settings["general"]["reverse_timelines"] == False:
                items = list_to_use[len(list_to_use)-number_of_items:]
                for i in items:
                    post = self.compose_function(i, self.session.db, self.session.settings, self.session.settings["general"]["relative_times"], self.session.settings["general"]["show_screen_names"], safe=safe)
                    self.buffer.list.insert_item(False, *post)
            else:
                items = list_to_use[0:number_of_items]
                items.reverse()
                for i in items:
                    post = self.compose_function(i, self.session.db, self.session.settings, self.session.settings["general"]["relative_times"], self.session.settings["general"]["show_screen_names"], safe=safe)
                    self.buffer.list.insert_item(True, *post)
        log.debug("Now the list contains %d items " % (self.buffer.list.get_count(),))

    def add_new_item(self, item):
        safe = True
        if self.session.settings["general"]["read_preferences_from_instance"]:
            safe = self.session.expand_spoilers == False
        post = self.compose_function(item, self.session.db, self.session.settings, self.session.settings["general"]["relative_times"], self.session.settings["general"]["show_screen_names"], safe=safe)
        if self.session.settings["general"]["reverse_timelines"] == False:
            self.buffer.list.insert_item(False, *post)
        else:
            self.buffer.list.insert_item(True, *post)
        if self.name in self.session.settings["other_buffers"]["autoread_buffers"] and self.name not in self.session.settings["other_buffers"]["muted_buffers"] and self.session.settings["sound"]["session_mute"] == False:
            output.speak(" ".join(post[:2]), speech=self.session.settings["reporting"]["speech_reporting"], braille=self.session.settings["reporting"]["braille_reporting"])

    def update_item(self, item, position):
        safe = True
        if self.session.settings["general"]["read_preferences_from_instance"]:
            safe = self.session.expand_spoilers == False
        post = self.compose_function(item, self.session.db, self.session.settings, self.session.settings["general"]["relative_times"], self.session.settings["general"]["show_screen_names"], safe=safe)
        self.buffer.list.list.SetItem(position, 1, post[1])

    def bind_events(self):
        log.debug("Binding events...")
        self.buffer.set_focus_function(self.onFocus)
        widgetUtils.connect_event(self.buffer.list.list, widgetUtils.KEYPRESS, self.get_event)
        widgetUtils.connect_event(self.buffer, widgetUtils.BUTTON_PRESSED, self.post_status, self.buffer.post)
        widgetUtils.connect_event(self.buffer, widgetUtils.BUTTON_PRESSED, self.share_item, self.buffer.boost)
        widgetUtils.connect_event(self.buffer, widgetUtils.BUTTON_PRESSED, self.send_message, self.buffer.dm)
        widgetUtils.connect_event(self.buffer, widgetUtils.BUTTON_PRESSED, self.reply, self.buffer.reply)
        widgetUtils.connect_event(self.buffer, widgetUtils.BUTTON_PRESSED, self.toggle_favorite, self.buffer.fav)
        widgetUtils.connect_event(self.buffer, widgetUtils.BUTTON_PRESSED, self.toggle_bookmark, self.buffer.bookmark)
        widgetUtils.connect_event(self.buffer.list.list, wx.EVT_LIST_ITEM_RIGHT_CLICK, self.show_menu)
        widgetUtils.connect_event(self.buffer.list.list, wx.EVT_LIST_KEY_DOWN, self.show_menu_by_key)

    def show_menu(self, ev, pos=0, *args, **kwargs):
        if self.buffer.list.get_count() == 0:
            return
        menu = menus.base()
        widgetUtils.connect_event(menu, widgetUtils.MENU, self.reply, menuitem=menu.reply)
        widgetUtils.connect_event(menu, widgetUtils.MENU, self.user_actions, menuitem=menu.userActions)
        if self.can_share() == True:
            widgetUtils.connect_event(menu, widgetUtils.MENU, self.share_item, menuitem=menu.boost)
        else:
            menu.boost.Enable(False)
        widgetUtils.connect_event(menu, widgetUtils.MENU, self.fav, menuitem=menu.fav)
        widgetUtils.connect_event(menu, widgetUtils.MENU, self.unfav, menuitem=menu.unfav)
        widgetUtils.connect_event(menu, widgetUtils.MENU, self.url_, menuitem=menu.openUrl)
        widgetUtils.connect_event(menu, widgetUtils.MENU, self.audio, menuitem=menu.play)
        widgetUtils.connect_event(menu, widgetUtils.MENU, self.view, menuitem=menu.view)
        widgetUtils.connect_event(menu, widgetUtils.MENU, self.copy, menuitem=menu.copy)
        widgetUtils.connect_event(menu, widgetUtils.MENU, self.destroy_status, menuitem=menu.remove)
        if hasattr(menu, "openInBrowser"):
            widgetUtils.connect_event(menu, widgetUtils.MENU, self.open_in_browser, menuitem=menu.openInBrowser)
        if pos != 0:
            self.buffer.PopupMenu(menu, pos)
        else:
            self.buffer.PopupMenu(menu, self.buffer.list.list.GetPosition())

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

    def can_share(self, item=None):
        if item == None:
            item = self.get_item()
        if item.visibility == "direct":
            return False
        return True

    def reply(self, event=None, item=None, *args, **kwargs):
        if item == None:
            item = self.get_item()
        visibility = item.visibility
        if visibility == "direct":
            title = _("Conversation with {}").format(item.account.username)
            caption = _("Write your message here")
        else:
            title = _("Reply to {}").format(item.account.username)
            caption = _("Write your reply here")
            # Set unlisted by default, so we will not clutter other user's buffers with replies.
            # see https://github.com/MCV-Software/TWBlue/issues/504
            visibility = "unlisted"
        if item.reblog != None:
            users = ["@{} ".format(user.acct) for user in item.reblog.mentions if user.id != self.session.db["user_id"]]
            if item.reblog.account.acct != item.account.acct and "@{} ".format(item.reblog.account.acct) not in users:
                users.append("@{} ".format(item.reblog.account.acct))
        else:
            users = ["@{} ".format(user.acct) for user in item.mentions if user.id != self.session.db["user_id"]]
        if "@{} ".format(item.account.acct) not in users and item.account.id != self.session.db["user_id"]:
            users.insert(0, "@{} ".format(item.account.acct))
        users_str = "".join(users)
        post = messages.post(session=self.session, title=title, caption=caption, text=users_str)
        visibility_settings = dict(public=0, unlisted=1, private=2, direct=3)
        post.message.visibility.SetSelection(visibility_settings.get(visibility))
        # Respect content warning settings.
        if item.sensitive:
            post.message.sensitive.SetValue(item.sensitive)
            post.message.spoiler.ChangeValue(item.spoiler_text)
            post.message.on_sensitivity_changed()
        response = post.message.ShowModal()
        if response == wx.ID_OK:
            post_data = post.get_data()
            call_threaded(self.session.send_post, reply_to=item.id, posts=post_data, visibility=post.get_visibility())
        if hasattr(post.message, "destroy"):
            post.message.destroy()

    def send_message(self, event=None, item=None, *args, **kwargs):
        if item == None:
            item = self.get_item()
        title = _("Conversation with {}").format(item.account.username)
        caption = _("Write your message here")
        if item.reblog != None:
            users = ["@{} ".format(user.acct) for user in item.reblog.mentions if user.id != self.session.db["user_id"]]
            if item.reblog.account.acct != item.account.acct and "@{} ".format(item.reblog.account.acct) not in users:
                users.append("@{} ".format(item.reblog.account.acct))
        else:
            users = ["@{} ".format(user.acct) for user in item.mentions if user.id != self.session.db["user_id"]]
        if item.account.acct not in users and item.account.id != self.session.db["user_id"]:
            users.insert(0, "@{} ".format(item.account.acct))
        users_str = "".join(users)
        post = messages.post(session=self.session, title=title, caption=caption, text=users_str)
        post.message.visibility.SetSelection(3)
        if item.sensitive:
            post.message.sensitive.SetValue(item.sensitive)
            post.message.spoiler.ChangeValue(item.spoiler_text)
            post.message.on_sensitivity_changed()
        response = post.message.ShowModal()
        if response == wx.ID_OK:
            post_data = post.get_data()
            call_threaded(self.session.send_post, posts=post_data, visibility="direct", reply_to=item.id)
        if hasattr(post.message, "destroy"):
            post.message.destroy()

    def share_item(self, event=None, item=None, *args, **kwargs):
        if item == None:
            item = self.get_item()
        if self.can_share(item=item) == False:
            return output.speak(_("This action is not supported on conversations."))
        id = item.id
        if self.session.settings["general"]["boost_mode"] == "ask":
            answer = mastodon_dialogs.boost_question()
            if answer == True:
                self._direct_boost(id)
        else:
            self._direct_boost(id)

    def _direct_boost(self, id):
        item = self.session.api_call(call_name="status_reblog", _sound="retweet_send.ogg", id=id)

    def onFocus(self, *args, **kwargs):
        post = self.get_item()
        if self.session.settings["general"]["relative_times"] == True:
            original_date = arrow.get(self.session.db[self.name][self.buffer.list.get_selected()].created_at)
            ts = original_date.humanize(locale=languageHandler.getLanguage())
            self.buffer.list.list.SetItem(self.buffer.list.get_selected(), 2, ts)
        if self.session.settings['sound']['indicate_audio'] and utils.is_audio_or_video(post):
            self.session.sound.play("audio.ogg")
        if self.session.settings['sound']['indicate_img'] and utils.is_image(post):
            self.session.sound.play("image.ogg")
        can_share = self.can_share()
        pub.sendMessage("toggleShare", shareable=can_share)
        self.buffer.boost.Enable(can_share)

    def audio(self, event=None, item=None, *args, **kwargs):
        if sound.URLPlayer.player.is_playing():
            return sound.URLPlayer.stop_audio()
        if item == None:
            item = self.get_item()
        urls = utils.get_media_urls(item)
        if len(urls) == 1:
            url=urls[0]
        elif len(urls) > 1:
            urls_list = urlList.urlList()
            urls_list.populate_list(urls)
            if urls_list.get_response() == widgetUtils.OK:
                url=urls_list.get_string()
            if hasattr(urls_list, "destroy"): urls_list.destroy()
        if url != '':
            #   try:
            sound.URLPlayer.play(url, self.session.settings["sound"]["volume"])
#   except:
#    log.error("Exception while executing audio method.")

    def url(self, announce=True, item=None, *args, **kwargs):
        if item == None:
            item = self.get_item()
        if item.reblog != None:
            urls = utils.find_urls(item.reblog)
        else:
            urls = utils.find_urls(item)
        if len(urls) == 1:
            url=urls[0]
        elif len(urls) > 1:
            urls_list = urlList.urlList()
            urls_list.populate_list(urls)
            if urls_list.get_response() == widgetUtils.OK:
                url=urls_list.get_string()
            if hasattr(urls_list, "destroy"): urls_list.destroy()
        if url != '':
            if announce:
                output.speak(_(u"Opening URL..."), True)
            webbrowser.open_new_tab(url)

    def clear_list(self):
        dlg = commonMessageDialogs.clear_list()
        if dlg == widgetUtils.YES:
            self.session.db[self.name] = []
            self.buffer.list.clear()

    def destroy_status(self, *args, **kwargs):
        index = self.buffer.list.get_selected()
        item = self.session.db[self.name][index]
        if item.account.id != self.session.db["user_id"] or item.reblog != None:
            output.speak(_("You can delete only your own posts."))
            return
        answer = mastodon_dialogs.delete_post_dialog()
        if answer == True:
            items = self.session.db[self.name]
            try:
                self.session.api.status_delete(id=item.id)
                items.pop(index)
                self.buffer.list.remove_item(index)
            except Exception as e:
                self.session.sound.play("error.ogg")
                log.exception("")
            self.session.db[self.name] = items

    def user_details(self):
        item = self.get_item()
        pass

    def get_item_url(self, item=None):
        if item == None:
            item = self.get_item()
        if item.reblog != None:
            return item.reblog.url
        return item.url

    def open_in_browser(self, event=None, item=None, *args, **kwargs):
        if item == None:
            item = self.get_item()
        url = self.get_item_url(item=item)
        output.speak(_("Opening item in web browser..."))
        webbrowser.open(url)

    def add_to_favorites(self, item=None):
        if item == None:
            item = self.get_item()
        if item.reblog != None:
            item = item.reblog
        call_threaded(self.session.api_call, call_name="status_favourite", preexec_message=_("Adding to favorites..."), _sound="favourite.ogg", id=item.id)

    def remove_from_favorites(self, item=None):
        if item == None:
            item = self.get_item()
        if item.reblog != None:
            item = item.reblog
        call_threaded(self.session.api_call, call_name="status_unfavourite", preexec_message=_("Removing from favorites..."), _sound="favourite.ogg", id=item.id)

    def toggle_favorite(self, event=None, item=None, *args, **kwargs):
        if item == None:
            item = self.get_item()
        if item.reblog != None:
            item = item.reblog
        try:
            item = self.session.api.status(item.id)
        except MastodonNotFoundError:
            output.speak(_("No status found with that ID"))
            return
        if item.favourited == False:
            call_threaded(self.session.api_call, call_name="status_favourite", preexec_message=_("Adding to favorites..."), _sound="favourite.ogg", id=item.id)
        else:
            call_threaded(self.session.api_call, call_name="status_unfavourite", preexec_message=_("Removing from favorites..."), _sound="favourite.ogg", id=item.id)

    def toggle_bookmark(self, event=None, item=None, *args, **kwargs):
        if item == None:
            item = self.get_item()
        if item.reblog != None:
            item = item.reblog
        try:
            item = self.session.api.status(item.id)
        except MastodonNotFoundError:
            output.speak(_("No status found with that ID"))
            return
        if item.bookmarked == False:
            call_threaded(self.session.api_call, call_name="status_bookmark", preexec_message=_("Adding to bookmarks..."), _sound="favourite.ogg", id=item.id)
        else:
            call_threaded(self.session.api_call, call_name="status_unbookmark", preexec_message=_("Removing from bookmarks..."), _sound="favourite.ogg", id=item.id)

    def view_item(self, item=None):
        if item == None:
            item = self.get_item()
        # Update object so we can retrieve newer stats
        try:
            item = self.session.api.status(id=item.id)
        except MastodonNotFoundError:
            output.speak(_("No status found with that ID"))
            return
#        print(post)
        msg = messages.viewPost(item, offset_hours=self.session.db["utc_offset"], item_url=self.get_item_url(item=item))

    def ocr_image(self):
        post = self.get_item()
        media_list = []
        if post.reblog != None:
            post = post.reblog
        for media in post.get("media_attachments"):
            if media.get("type", "") == "image":
                media_list.append(media)
        if len(media_list) > 1:
            image_list = [_(u"Picture {0}").format(i+1,) for i in range(0, len(media_list))]
            dialog = urlList.urlList(title=_(u"Select the picture"))
            dialog.populate_list(image_list)
            if dialog.get_response() == widgetUtils.OK:
                img = media_list[dialog.get_item()]
            else:
                return
        elif len(media_list) == 1:
            img = media_list[0]
        else:
            return
        if self.session.settings["mysc"]["ocr_language"] != "":
            ocr_lang = self.session.settings["mysc"]["ocr_language"]
        else:
            ocr_lang = ocr.OCRSpace.short_langs.index(post.language)
            ocr_lang = ocr.OCRSpace.OcrLangs[ocr_lang]
        if img["remote_url"] != None:
            url = img["remote_url"]
        else:
            url = img["url"]
        api = ocr.OCRSpace.OCRSpaceAPI()
        try:
            text = api.OCR_URL(url)
        except ocr.OCRSpace.APIError as er:
            output.speak(_(u"Unable to extract text"))
            return
        viewer = messages.text(title=_("OCR Result"), text=text["ParsedText"])
        response = viewer.message.ShowModal()
        viewer.message.Destroy()

    def vote(self):
        post = self.get_item()
        if not hasattr(post, "poll") or post.poll == None:
            return
        poll = post.poll
        try:
            poll = self.session.api.poll(id=poll.id)
        except MastodonNotFoundError:
            output.speak(_("this poll no longer exists."))
            return
        if poll.expired:
            output.speak(_("This poll has already expired."))
            return
        if poll.voted:
            output.speak(_("You have already voted on this poll."))
            return
        options = poll.options
        dlg = attachedPoll(poll_options=[option.title for option in options], multiple=poll.multiple)
        answer = dlg.ShowModal()
        options = dlg.get_selected()
        dlg.Destroy()
        if answer != wx.ID_OK:
            return
        poll = self.session.api_call(call_name="poll_vote", id=poll.id, choices=options, preexec_message=_("Sending vote..."))

    def post_from_error(self, visibility, reply_to, data):
        title = _("Post")
        caption = _("Write your post here")
        post = messages.post(session=self.session, title=title, caption=caption)
        post.set_post_data(visibility=visibility, data=data)
        response = post.message.ShowModal()
        if response == wx.ID_OK:
            post_data = post.get_data()
            call_threaded(self.session.send_post, posts=post_data, reply_to=reply_to, visibility=post.get_visibility())
        if hasattr(post.message, "destroy"):
            post.message.destroy()
