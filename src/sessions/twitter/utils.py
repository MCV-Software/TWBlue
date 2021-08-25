# -*- coding: utf-8 -*-
import url_shortener, re
import output
import config
import logging
import requests
import time
import sound
from tweepy.error import TweepError
log = logging.getLogger("twitter.utils")
""" Some utilities for the twitter interface."""

__version__ = 0.1
__doc__ = "Find urls in tweets and #audio hashtag."

url_re = re.compile(r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))")

url_re2 = re.compile("(?:\w+://|www\.)[^ ,.?!#%=+][^ \\n\\t]*")
bad_chars = '\'\\\n.,[](){}:;"'

def find_urls_in_text(text):
    return  url_re2.findall(text)

def find_urls (tweet, twitter_media=False):
    urls = []
    if twitter_media and hasattr(tweet, "extended_entities"):
        for mediaItem in tweet.extended_entities["media"]:
            if mediaItem["type"] == "video":
                for variant in mediaItem["video_info"]["variants"]:
                    if variant["content_type"] == "video/mp4":
                        urls.append(variant["url"])
                        break
    # Let's add URLS from tweet entities.
    if hasattr(tweet, "message_create"):
        entities = tweet.message_create["message_data"]["entities"]
    else:
        if hasattr(tweet, "entities") == True:
            entities = tweet.entities
    if entities.get("urls") != None:
        for i in entities["urls"]:
            if i["expanded_url"] not in urls:
                urls.append(i["expanded_url"])
    if hasattr(tweet, "quoted_status"):
        urls.extend(find_urls(tweet.quoted_status, twitter_media))
    if hasattr(tweet, "retweeted_status"):
        urls.extend(find_urls(tweet.retweeted_status, twitter_media))
    if hasattr(tweet, "message"):
        i = "message"
    elif hasattr(tweet, "full_text"):
        i = "full_text"
    else:
        i = "text"
    if hasattr(tweet, "message_create"):
        extracted_urls = find_urls_in_text(tweet.message_create["message_data"]["text"])
    else:
        extracted_urls = find_urls_in_text(getattr(tweet, i))
    # Don't include t.co links (mostly they are photos or shortened versions of already added URLS).
    for i in extracted_urls:
        if i not in urls and "https://t.co" not in i:
            urls.append(i)
    return urls

def find_item(item, listItems):
    for i in range(0, len(listItems)):
        if listItems[i].id == item.id:
            return i
        # Check also retweets.
        if hasattr(item, "retweeted_status") and item.retweeted_status.id == listItems[i].id:
            return i
    return None

def find_list(name, lists):
    for i in range(0, len(lists)):
        if lists[i].name == name:  return lists[i].id

def is_audio(tweet):
    if hasattr(tweet, "quoted_status") and hasattr(tweet.quoted_status, "extended_entities"):
        result = is_audio(tweet.quoted_status)
        if result != None:
            return result
    if hasattr(tweet, "retweeted_status") and hasattr(tweet.retweeted_status, "extended_entities"):
        result = is_audio(tweet.retweeted_status)
        if result == True:
            return result
    # Checks firstly for Twitter videos and audios.
    if hasattr(tweet, "extended_entities"):
        for mediaItem in tweet.extended_entities["media"]:
            if mediaItem["type"] == "video":
                return True
    try:
        if len(find_urls(tweet)) < 1:
            return False
        if hasattr(tweet, "message_create"):
            entities = tweet.message_create["message_data"]["entities"]
        else:
            if hasattr(tweet, "entities") == False or tweet.entities.get("hashtags") == None:
                return False
            entities = tweet.entities
        if len(entities["hashtags"]) > 0:
            for i in entities["hashtags"]:
                if i["text"] == "audio":
                    return True
    except IndexError:
        log.exception("Exception while executing is_audio hashtag algorithm")

def is_geocoded(tweet):
    if hasattr(tweet, "coordinates") and tweet.coordinates != None:
        return True

def is_media(tweet):
    if hasattr(tweet, "message_create"):
        entities = tweet.message_create["message_data"]["entities"]
    else:
        if hasattr(tweet, "entities") == False or tweet.entities.get("hashtags") == None:
            return False
        entities = tweet.entities
    if entities.get("media") == None:
        return False
    for i in entities["media"]:
        if i.get("type") != None and i.get("type") == "photo":
            return True
    return False

def get_all_mentioned(tweet, conf, field="screen_name"):
    """ Gets all users that have been mentioned."""
    results = []
    if hasattr(tweet, "retweeted_status"):
        results.extend(get_all_mentioned(tweet.retweeted_status, conf, field))
    if hasattr(tweet, "quoted_status"):
        results.extend(get_all_mentioned(tweet.quoted_status, conf, field))
    if hasattr(tweet, "entities") and tweet.entities.get("user_mentions"):
        for i in tweet.entities["user_mentions"]:
            if i["screen_name"] != conf["user_name"] and i["id_str"] != tweet.user:
                if i.get(field) not in results:
                    results.append(i.get(field))
    return results

def get_all_users(tweet, session):
    string = []
    user = session.get_user(tweet.user)
    if user.screen_name != session.db["user_name"]:
        string.append(user.screen_name)
    if hasattr(tweet, "retweeted_status"):
        string.extend(get_all_users(tweet.retweeted_status, session))
    if hasattr(tweet, "quoted_status"):
        string.extend(get_all_users(tweet.quoted_status, session))
    if hasattr(tweet, "entities") and tweet.entities.get("user_mentions"):
        for i in tweet.entities["user_mentions"]:
            if i["screen_name"] != session.db["user_name"] and i["screen_name"] != user.screen_name:
                if i["screen_name"] not in string:
                    string.append(i["screen_name"])
    # Attempt to remove duplicates, tipically caused by nested tweets.
    string = list(dict.fromkeys(string))
    if len(string) == 0:
        string.append(user.screen_name)
    return string

def if_user_exists(twitter, user):
    try:
        data = twitter.get_user(screen_name=user)
        return data
    except TweepError as err:
        if err.api_code == 50:
            return None
        else:
            return user

def is_allowed(tweet, settings, buffer_name):
    clients = settings["twitter"]["ignored_clients"]
    if hasattr(tweet, "sender"): return True
    allowed = True
    tweet_data = {}
    if hasattr(tweet, "retweeted_status"):
        tweet_data["retweet"] = True
    if hasattr(tweet, "in_reply_to_status_id"):
        tweet_data["reply"] = True
    if hasattr(tweet, "quoted_status"):
        tweet_data["quote"] = True
    if hasattr(tweet, "retweeted_status"):
        tweet = tweet.retweeted_status
    source = tweet.source
    for i in clients:
        if i.lower() == source.lower():
            return False
    return filter_tweet(tweet, tweet_data, settings, buffer_name)

def filter_tweet(tweet, tweet_data, settings, buffer_name):
    if hasattr(tweet, "full_text"):
        value = "full_text"
    else:
        value = "text"
    for i in settings["filters"]:
        if settings["filters"][i]["in_buffer"] == buffer_name:
            regexp = settings["filters"][i]["regexp"]
            word = settings["filters"][i]["word"]
            # Added if/else for compatibility reasons.
            if "allow_rts" in settings["filters"][i]:
                allow_rts = settings["filters"][i]["allow_rts"]
            else:
                allow_rts = "True"
            if "allow_quotes" in settings["filters"][i]:
                allow_quotes = settings["filters"][i]["allow_quotes"]
            else:
                allow_quotes = "True"
            if "allow_replies" in settings["filters"][i]:
                allow_replies = settings["filters"][i]["allow_replies"]
            else:
                allow_replies = "True"
            if allow_rts == "False" and "retweet" in tweet_data:
                return False
            if allow_quotes == "False" and "quote" in tweet_data:
                return False
            if allow_replies == "False" and "reply" in tweet_data:
                return False
            if word != "" and settings["filters"][i]["if_word_exists"]:
                if word in getattr(tweet, value):
                    return False
            elif word != "" and settings["filters"][i]["if_word_exists"] == False:
                if word not in getattr(tweet, value):
                    return False
            if settings["filters"][i]["in_lang"] == "True":
                if getattr(tweet, lang) not in settings["filters"][i]["languages"]:
                    return False
            elif settings["filters"][i]["in_lang"] == "False":
                if tweet.lang in settings["filters"][i]["languages"]:
                    return False
    return True

def twitter_error(error):
    if error.api_code == 179:
        msg = _(u"Sorry, you are not authorised to see this status.")
    elif error.api_code == 144:
        msg = _(u"No status found with that ID")
    else:
        msg = _(u"Error code {0}").format(error.api_code,)
    output.speak(msg)

def expand_urls(text, entities):
    """ Expand all URLS present in text with information found in entities"""
    if entities.get("urls") == None:
        return text
    urls = find_urls_in_text(text)
    for url in entities["urls"]:
        if url["url"] in text:
            text = text.replace(url["url"], url["expanded_url"])
    return text

def clean_mentions(text):
    new_text = text
    mentionned_people = [u for u in re.finditer("(?<=^|(?<=[^a-zA-Z0-9-\.]))@([A-Za-z0-9_]+)", text)]
    if len(mentionned_people) <= 2:
        return text
    end = -2
    total_users = 0
    for user in mentionned_people:
        if abs(user.start()-end) < 3:
            new_text = new_text.replace(user.group(0), "")
            total_users = total_users+1
            end = user.end()
    if total_users < 1:
        return text
    new_text = _("{user_1}, {user_2} and {all_users} more: {text}").format(user_1=mentionned_people[0].group(0), user_2=mentionned_people[1].group(0), all_users=total_users-2, text=new_text)
    return new_text