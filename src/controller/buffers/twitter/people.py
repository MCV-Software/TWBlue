# -*- coding: utf-8 -*-
import time
from wxUI import commonMessageDialogs, menus
from controller import user
from controller import messages
import widgetUtils
import webbrowser
import output
import config
import logging
from mysc.thread_utils import call_threaded
from tweepy.errors import TweepyException
from pubsub import pub
from sessions.twitter import compose, templates
from . import base

log = logging.getLogger("controller.buffers.twitter.peopleBuffer")

def _tweets_exist(function):
    """ A decorator to execute a function only if the selected buffer contains at least one item."""
    def function_(self, *args, **kwargs):
        if self.buffer.list.get_count() > 0:
            function(self, *args, **kwargs)
    return function_

class PeopleBuffer(base.BaseBuffer):
    def __init__(self, parent, function, name, sessionObject, account, bufferType=None, *args, **kwargs):
        super(PeopleBuffer, self).__init__(parent, function, name, sessionObject, account, bufferType="peoplePanel", *args, **kwargs)
        log.debug("Initializing buffer %s, account %s" % (name, account,))
        self.compose_function = compose.compose_followers_list
        log.debug("Compose_function: %s" % (self.compose_function,))
        self.get_tweet = self.get_right_tweet
        self.url = self.interact
        if "-followers" in self.name or "-friends" in self.name:
            self.finished_timeline = False
            # Add a compatibility layer for username based timelines from config.
            # ToDo: Remove this in some new versions of the client, when user ID timelines become mandatory.
            try:
                int(self.kwargs["user_id"])
            except ValueError:
                self.is_screen_name = True
                self.kwargs["screen_name"] = self.kwargs["user_id"]
                self.kwargs.pop("user_id")

    def remove_buffer(self, force=True):
        if "-followers" in self.name:
            if force == False:
                dlg = commonMessageDialogs.remove_buffer()
            else:
                dlg = widgetUtils.YES
            if dlg == widgetUtils.YES:
                if self.name[:-10] in self.session.settings["other_buffers"]["followers_timelines"]:
                    self.session.settings["other_buffers"]["followers_timelines"].remove(self.name[:-10])
                    if self.name in self.session.db:
                        self.session.db.pop(self.name)
                    self.session.settings.write()
                    return True
            elif dlg == widgetUtils.NO:
                return False
        elif "-friends" in self.name:
            if force == False:
                dlg = commonMessageDialogs.remove_buffer()
            else:
                dlg = widgetUtils.YES
            if dlg == widgetUtils.YES:
                if self.name[:-8] in self.session.settings["other_buffers"]["friends_timelines"]:
                    self.session.settings["other_buffers"]["friends_timelines"].remove(self.name[:-8])
                    if self.name in self.session.db:
                        self.session.db.pop(self.name)
                    self.session.settings.write()
                    return True
            elif dlg == widgetUtils.NO:
                return False
        else:
            output.speak(_(u"This buffer is not a timeline; it can't be deleted."), True)
            return False

    def onFocus(self, ev):
        pass

    def get_message(self):
        template = self.session.settings["templates"]["person"]
        user = self.get_right_tweet()
        t = templates.render_person(user, template, self.session, relative_times=True, offset_seconds=self.session.db["utc_offset"])
        return t

    def delete_item(self): pass

    @_tweets_exist
    def reply(self, *args, **kwargs):
        tweet = self.get_right_tweet()
        screen_name = tweet.screen_name
        message = messages.tweet(session=self.session, title=_("Mention"), caption=_("Mention to %s") % (screen_name,), text="@%s " % (screen_name,), thread_mode=False)
        if message.message.ShowModal() == widgetUtils.OK:
            tweet_data = message.get_tweet_data()
            call_threaded(self.session.send_tweet, *tweet_data)
        if hasattr(message.message, "destroy"):
            message.message.destroy()

    def start_stream(self, mandatory=False, play_sound=True, avoid_autoreading=False):
        # starts stream every 3 minutes.
        current_time = time.time()
        if self.execution_time == 0 or current_time-self.execution_time >= 180 or mandatory==True:
            self.execution_time = current_time
            log.debug("Starting stream for %s buffer, %s account" % (self.name, self.account,))
            log.debug("args: %s, kwargs: %s" % (self.args, self.kwargs))
            try:
                val = getattr(self.session.twitter, self.function)(return_cursors=True, count=self.session.settings["general"]["max_tweets_per_call"], *self.args, **self.kwargs)
                if type(val) == tuple:
                    val, cursor = val
                    if type(cursor) == tuple:
                        cursor = cursor[1]
                    cursors = self.session.db["cursors"]
                    cursors[self.name] = cursor
                    self.session.db["cursors"] = cursors
                results = [i for i in val]
                val = results
                val.reverse()
                log.debug("Retrieved %d items from cursored search in function %s" % (len(val), self.function))
            except TweepyException as e:
                log.exception("Error %s" % (str(e)))
                return
            number_of_items = self.session.order_people(self.name, val)
            log.debug("Number of items retrieved: %d" % (number_of_items,))
            self.put_items_on_list(number_of_items)
            if hasattr(self, "finished_timeline") and self.finished_timeline == False:
                self.username = self.session.api_call("get_user", **self.kwargs).screen_name
                self.finished_timeline = True
            if number_of_items > 0 and self.sound != None and self.session.settings["sound"]["session_mute"] == False and self.name not in self.session.settings["other_buffers"]["muted_buffers"] and play_sound == True:
                self.session.sound.play(self.sound)
            # Autoread settings
            if avoid_autoreading == False and mandatory == True and number_of_items > 0 and self.name in self.session.settings["other_buffers"]["autoread_buffers"]:
                self.auto_read(number_of_items)
            return number_of_items

    def get_more_items(self):
        try:
            cursor = self.session.db["cursors"].get(self.name)
            items = getattr(self.session.twitter, self.function)(return_cursors=True, users=True, cursor=cursor, count=self.session.settings["general"]["max_tweets_per_call"], *self.args, **self.kwargs)
            if type(items) == tuple:
                items, cursor = items
                if type(cursor) == tuple:
                    cursor = cursor[1]
                cursors = self.session.db["cursors"]
                cursors[self.name] = cursor
                self.session.db["cursors"] = cursors
            results = [i for i in items]
            items = results
            log.debug("Retrieved %d items from cursored search in function %s" % (len(items), self.function))
        except TweepyException as e:
            log.exception("Error %s" % (str(e)))
            return
        if items == None:
            return
        items_db = self.session.db[self.name]
        for i in items:
            if self.session.settings["general"]["reverse_timelines"] == False:
                items_db.insert(0, i)
            else:
                items_db.append(i)
        self.session.db[self.name] = items_db
        selected = self.buffer.list.get_selected()
        if self.session.settings["general"]["reverse_timelines"] == True:
            for i in items:
                tweet = self.compose_function(i, self.session.db, self.session.settings["general"]["relative_times"], self.session)
                self.buffer.list.insert_item(True, *tweet)
            self.buffer.list.select_item(selected)
        else:
            for i in items:
                tweet = self.compose_function(i, self.session.db, self.session.settings["general"]["relative_times"], self.session)
                self.buffer.list.insert_item(True, *tweet)
        output.speak(_(u"%s items retrieved") % (len(items)), True)

    def put_items_on_list(self, number_of_items):
        log.debug("The list contains %d items" % (self.buffer.list.get_count(),))
#  log.debug("Putting %d items on the list..." % (number_of_items,))
        if self.buffer.list.get_count() == 0:
            for i in self.session.db[self.name]:
                tweet = self.compose_function(i, self.session.db, self.session.settings["general"]["relative_times"], self.session)
                self.buffer.list.insert_item(False, *tweet)
            self.buffer.set_position(self.session.settings["general"]["reverse_timelines"])
#   self.buffer.set_list_position()
        elif self.buffer.list.get_count() > 0:
            if self.session.settings["general"]["reverse_timelines"] == False:
                for i in self.session.db[self.name][len(self.session.db[self.name])-number_of_items:]:
                    tweet = self.compose_function(i, self.session.db)
                    self.buffer.list.insert_item(False, *tweet)
            else:
                items = self.session.db[self.name][0:number_of_items]
                items.reverse()
                for i in items:
                    tweet = self.compose_function(i, self.session.db)
                    self.buffer.list.insert_item(True, *tweet)
        log.debug("now the list contains %d items" % (self.buffer.list.get_count(),))

    def get_right_tweet(self):
        tweet = self.session.db[self.name][self.buffer.list.get_selected()]
        return tweet

    def add_new_item(self, item):
        tweet = self.compose_function(item, self.session.db, self.session.settings["general"]["relative_times"], self.session)
        if self.session.settings["general"]["reverse_timelines"] == False:
            self.buffer.list.insert_item(False, *tweet)
        else:
            self.buffer.list.insert_item(True, *tweet)
        if self.name in self.session.settings["other_buffers"]["autoread_buffers"] and self.name not in self.session.settings["other_buffers"]["muted_buffers"] and self.session.settings["sound"]["session_mute"] == False:
            output.speak(" ".join(tweet))

    def clear_list(self):
        dlg = commonMessageDialogs.clear_list()
        if dlg == widgetUtils.YES:
            self.session.db[self.name] = []
            self.session.db["cursors"][self.name] = -1
            self.buffer.list.clear()

    def interact(self):
        user.profileController(self.session, user=self.get_right_tweet().screen_name)

    def show_menu(self, ev, pos=0, *args, **kwargs):
        menu = menus.peoplePanelMenu()
        widgetUtils.connect_event(menu, widgetUtils.MENU, self.send_message, menuitem=menu.reply)
        widgetUtils.connect_event(menu, widgetUtils.MENU, self.user_actions, menuitem=menu.userActions)
        widgetUtils.connect_event(menu, widgetUtils.MENU, self.details, menuitem=menu.details)
#  widgetUtils.connect_event(menu, widgetUtils.MENU, self.lists, menuitem=menu.lists)
        widgetUtils.connect_event(menu, widgetUtils.MENU, self.view, menuitem=menu.view)
        widgetUtils.connect_event(menu, widgetUtils.MENU, self.copy, menuitem=menu.copy)
        if hasattr(menu, "openInBrowser"):
            widgetUtils.connect_event(menu, widgetUtils.MENU, self.open_in_browser, menuitem=menu.openInBrowser)
        if pos != 0:
            self.buffer.PopupMenu(menu, pos)
        else:
            self.buffer.PopupMenu(menu, ev.GetPosition())

    def details(self, *args, **kwargs):
        pub.sendMessage("execute-action", action="user_details")

    def auto_read(self, number_of_items):
        if number_of_items == 1 and self.name in self.session.settings["other_buffers"]["autoread_buffers"] and self.name not in self.session.settings["other_buffers"]["muted_buffers"] and self.session.settings["sound"]["session_mute"] == False:
            if self.session.settings["general"]["reverse_timelines"] == False:
                tweet = self.session.db[self.name][-1]
            else:
                tweet = self.session.db[self.name][0]
            output.speak(" ".join(self.compose_function(tweet, self.session.db, self.session.settings["general"]["relative_times"], self.session.settings["general"]["show_screen_names"], self.session)))
        elif number_of_items > 1 and self.name in self.session.settings["other_buffers"]["autoread_buffers"] and self.name not in self.session.settings["other_buffers"]["muted_buffers"] and self.session.settings["sound"]["session_mute"] == False:
            output.speak(_(u"{0} new followers.").format(number_of_items))

    def get_item_url(self, *args, **kwargs):
        tweet = self.get_tweet()
        url = "https://twitter.com/{screen_name}".format(screen_name=tweet.screen_name)
        return url