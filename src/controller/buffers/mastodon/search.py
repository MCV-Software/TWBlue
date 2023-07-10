# -*- coding: utf-8 -*-
"""
Implements searching functionality for mastodon
Used for searching for statuses (posts) or possibly hashtags
"""

import logging
import time
from pubsub import pub

from .base import BaseBuffer
import widgetUtils
from wxUI import commonMessageDialogs


log = logging.getLogger("controller.buffers.mastodon.search")


class SearchBuffer(BaseBuffer):
    """Search buffer
    There are some methods of the Base Buffer that can't be used here
    """

    def start_stream(self, mandatory: bool=False, play_sound: bool=True, avoid_autoreading: bool=False) -> None:
        """Start streaming
        Parameters:
        - mandatory [bool]: Force start stream if True
        - play_sound [bool]: Specifies whether to play sound after receiving posts
        avoid_autoreading [bool]: Reads the posts if set to True
        returns [None | int]: Number of posts received
        """
        log.debug(f"Starting streamd for buffer {self.name} account {self.account} and type {self.type}")
        log.debug(f"Args: {self.args}, Kwargs: {self.kwargs}")

        current_time = time.time()
        if self.execution_time == 0 or current_time-self.execution_time >= 180 or mandatory==True:
            self.execution_time = current_time

        min_id = None
        if self.name in self.session.db and len(self.session.db[self.name]) > 0:
            if self.session.settings["general"]["reverse_timelines"]:
                min_id = self.session.db[self.name][0].id
            else:
                min_id = self.session.db[self.name][-1].id
        try:
            results = getattr(self.session.api, self.function)(min_id=min_id, **self.kwargs)
        except Exception as mess:
            log.exception(f"Error while receiving search posts {mess}")
            return

        # Results is either in results.statuses or results.hashtags.
        results = results.statuses if results.statuses else results.hashtags
        results.reverse()
        num_of_items = self.session.order_buffer(self.name, results)
        log.debug(f"Number of items retrieved: {num_of_items}")
        self.put_items_on_list(num_of_items)

        if hasattr(self, "finished_timeline") and self.finished_timeline == False:
            pub.sendMessage("core.change_buffer_title", name=self.session.get_name(), buffer=self.name, title=_("{}-searchterm").format(self.kwargs['q']))
            self.finished_timeline = True

            # playsound and autoread
            if num_of_items > 0:
                if self.sound != None and self.session.settings["sound"]["session_mute"] == False and self.name not in self.session.settings["other_buffers"]["muted_buffers"] and play_sound == True:
                    self.session.sound.play(self.sound)
            if avoid_autoreading == False and mandatory == True and self.name in self.session.settings["other_buffers"]["autoread_buffers"]:
                self.auto_read(num_of_items)

        return num_of_items

    def remove_buffer(self, force: bool=False) -> bool:
        """Performs clean-up tasks before removing buffer
        Parameters:
        - force [bool]: Force removes buffer if true
        Returns [bool]: True proceed with removing buffer or False abort
        removing buffer
        """
        # Ask user
        if not force:
            response = commonMessageDialogs.remove_buffer()
        else:
            response = widgetUtils.YES

        if response == widgetUtils.NO:
            return False

        # remove references of this buffer in db and settings
        if self.name in self.session.db:
            self.session.db.pop(self.name)
        if self.kwargs.get('q') in self.session.settings['other_buffers']['post_searches']:
            self.session.settings['other_buffers']['post_searches'].remove(self.kwargs['q'])

        return True
