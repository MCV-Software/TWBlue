# -*- coding: utf-8 -*-
""" Strips unneeded tweet information in order to store tweet objects by using less memory. This is especially useful when buffers start to contain more than a certain amount of items. """
from tweepy.models import Status

def reduce_tweet(tweet):
    """ generates a new Tweet model with the fields we currently need, excluding everything else  including null values and empty collections. """
    allowed_values = ["created_at", "id", "full_text", "text", "message", "in_reply_to_status_id", "in_reply_to_user_id", "is_quote_status", "lang", "source", "coordinates", "quoted_status_id", "extended_entities"]
    allowed_entities = ["hashtags", "media", "urls", "user_mentions", "polls"]
    status_dict = {}
    for key in allowed_values:
        if tweet._json.get(key):
            status_dict[key] = tweet._json[key]
    entities = dict()
    for key in allowed_entities:
        if tweet._json["entities"].get(key) and tweet._json["entities"].get(key) != None:
            entities[key] = tweet._json["entities"][key]
    status_dict["entities"] = entities
    # If tweet comes from the cached database, it does not include an API,  so we can pass None here as we do not use that reference to tweepy's API.
    if hasattr(tweet, "_api"):
        api = tweet._api
    else:
        api = None
    status = Status().parse(api=api, json=status_dict)
    # Quotes and retweets are different objects. So we parse a new tweet when we have a quoted or retweeted status here.
    if tweet._json.get("quoted_status"):
        quoted_tweet = reduce_tweet(tweet.quoted_status)
        status.quoted_status = quoted_tweet
    if tweet._json.get("retweeted_status"):
        retweeted_tweet = reduce_tweet(tweet.retweeted_status)
        status.retweeted_status = retweeted_tweet
    # Adds user ID to here so we can reference it later.
    # Sometimes, the conversations buffer would send an already reduced tweet here so we will need to return it as is.
    if isinstance(tweet.user, str) == False:
        status.user = tweet.user.id_str
    else:
        return tweet
    return status