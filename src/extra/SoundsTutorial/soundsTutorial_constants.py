#-*- coding: utf-8 -*-
from __future__ import absolute_import
#-*- coding: utf-8 -*-
from . import reverse_sort
import application
actions = reverse_sort.reverse_sort([  ("audio", _(u"Audio tweet.")),
  ("create_timeline", _(u"User timeline buffer created.")),
    ("delete_timeline", _(u"Buffer destroied.")),
    ("dm_received", _(u"Direct message received.")),
    ("dm_sent", _(u"Direct message sent.")),
    ("error", _(u"Error.")),
  ("favourite", _(u"Tweet liked.")),
  ("favourites_timeline_updated", _(u"Likes buffer updated.")),
  ("geo",   _(u"Geotweet.")),
("image", _("Tweet contains one or more images")),
("limit", _(u"Boundary reached.")),
    ("list_tweet", _(u"List updated.")),
    ("max_length", _(u"Too many characters.")),
    ("mention_received", _(u"Mention received.")),
  ("new_event", _(u"New event.")),
  ("ready", _(u"{0} is ready.").format(application.name,)),
    ("reply_send", _(u"Mention sent.")),
    ("retweet_send", _(u"Tweet retweeted.")),
    ("search_updated", _(u"Search buffer updated.")),
    ("tweet_received", _(u"Tweet received.")),
    ("tweet_send", _(u"Tweet sent.")),
    ("trends_updated", _(u"Trending topics buffer updated.")),
    ("tweet_timeline", _(u"New tweet in user timeline buffer.")),
    ("update_followers", _(u"New follower.")),
    ("volume_changed", _(u"Volume changed."))])
