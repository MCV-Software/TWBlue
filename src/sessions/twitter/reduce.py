# -*- coding: utf-8 -*-
""" Strips unneeded tweet information in order to store tweet objects by using less memory. """
from tweepy.models import Status

def reduce_tweet(tweet):
    allowed_values = ["created_at", "id", "full_text", "text", "message", "in_reply_to_status_id", "in_reply_to_user_id", "is_quote_status", "lang", "source", "coordinates", "quoted_status_id", ]
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
    # Quotes and retweets are different objects.
    status = Status().parse(api=tweet._api, json=status_dict)
    if tweet._json.get("quoted_status"):
        quoted_tweet = reduce_tweet(tweet.quoted_status)
#        print(quoted_tweet)
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