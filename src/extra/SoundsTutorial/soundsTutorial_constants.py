#-*- coding: utf-8 -*-

#-*- coding: utf-8 -*-
from . import reverse_sort
import application
actions = reverse_sort.reverse_sort([  ("audio", _("Audio tweet.")),
  ("create_timeline", _("User timeline buffer created.")),
    ("delete_timeline", _("Buffer destroied.")),
    ("dm_received", _("Direct message received.")),
    ("dm_sent", _("Direct message sent.")),
    ("error", _("Error.")),
  ("favourite", _("Tweet liked.")),
  ("favourites_timeline_updated", _("Likes buffer updated.")),
  ("geo",   _("Geotweet.")),
("image", _("Tweet contains one or more images")),
("limit", _("Boundary reached.")),
    ("list_tweet", _("List updated.")),
    ("max_length", _("Too many characters.")),
    ("mention_received", _("Mention received.")),
  ("new_event", _("New event.")),
  ("ready", _("{0} is ready.").format(application.name,)),
    ("reply_send", _("Mention sent.")),
    ("retweet_send", _("Tweet retweeted.")),
    ("search_updated", _("Search buffer updated.")),
    ("tweet_received", _("Tweet received.")),
    ("tweet_send", _("Tweet sent.")),
    ("trends_updated", _("Trending topics buffer updated.")),
    ("tweet_timeline", _("New tweet in user timeline buffer.")),
    ("update_followers", _("New follower.")),
    ("volume_changed", _("Volume changed."))])
