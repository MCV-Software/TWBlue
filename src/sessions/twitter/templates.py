# -*- coding: utf-8 -*-
import re
import arrow
import languageHandler
from string import Template
from . import utils

def process_date(field, relative_times=True, offset_seconds=0):
    original_date = arrow.get(field, locale="en")
    if relative_times == True:
        ts = original_date.humanize(locale=languageHandler.curLang[:2])
    else:
        ts = original_date.shift(seconds=offset_seconds).format(_("dddd, MMMM D, YYYY H:m:s"), locale=languageHandler.curLang[:2])
    return ts

def process_text(tweet):
    if hasattr(tweet, "full_text"):
        text = tweet.full_text
    elif hasattr(tweet, "text"):
        text = tweet.text
    # Cleanup mentions, so we'll remove more than 2 mentions to make the tweet easier to read.
    text = utils.clean_mentions(text)
    # Replace URLS for extended version of those.
    if hasattr(tweet, "entities"):
        text = utils.expand_urls(text, tweet.entities)
    text = re.sub(r"https://twitter.com/\w+/status/\d+", "", text)
    return text

def process_image_descriptions(entities):
    """ Attempt to extract information for image descriptions. """
    image_descriptions = []
    for media in entities["media"]:
        if media.get("ext_alt_text") != None:
            image_descriptions.append(media.get("ext_alt_text"))
    idescriptions = ""
    for image in image_descriptions:
        idescriptions += "Image description: {}.".format(image)
    return idescriptions

def render_tweet(tweet, template, session, relative_times=False, offset_seconds=0):
    """ Renders any given Tweet according to the passed template.
    Available data for tweets will be stored in the following variables:
    $date: Creation date.
    $display_name: User profile name.
    $screen_name: User screen name, this is the same name used to reference the user in Twitter.
    $ source: Source client from where the current tweet was sent.
    $lang: Two letter code for the automatically detected language for the tweet. This detection is performed by Twitter.
    $text: Tweet text.
    $image_descriptions: Information regarding image descriptions added by twitter users.
    """
    available_data = dict()
    created_at = process_date(tweet.created_at, relative_times, offset_seconds)
    available_data.update(date=created_at)
    # user.
    available_data.update(display_name=session.get_user(tweet.user).name, screen_name=session.get_user(tweet.user).screen_name)
    # Source client from where tweet was originated.
    available_data.update(source=tweet.source)
    if hasattr(tweet, "retweeted_status"):
        if hasattr(tweet.retweeted_status, "quoted_status"):
            text = "RT @{}: {} Quote from @{}: {}".format(session.get_user(tweet.retweeted_status.user).screen_name, process_text(tweet.retweeted_status), session.get_user(tweet.retweeted_status.quoted_status.user).screen_name, process_text(tweet.retweeted_status.quoted_status))
        else:
            text = "RT @{}: {}".format(session.get_user(tweet.retweeted_status.user).screen_name, process_text(tweet.retweeted_status))
    elif hasattr(tweet, "quoted_status"):
        text = "{} Quote from @{}: {}".format(process_text(tweet), session.get_user(tweet.quoted_status.user).screen_name, process_text(tweet.quoted_status))
    else:
        text = process_text(tweet)
    available_data.update(lang=tweet.lang, text=text)
    # process image descriptions
    image_descriptions = ""
    if hasattr(tweet, "quoted_status") and hasattr(tweet.quoted_status, "extended_entities"):
        image_descriptions = process_image_descriptions(tweet.quoted_status.extended_entities)
    elif hasattr(tweet, "retweeted_status") and hasattr(tweet.retweeted_status, "quoted_status") and hasattr(tweet.retweeted_status.quoted_status, "extended_entities"):
        image_descriptions = process_image_descriptions(tweet.retweeted_status.quoted_status.extended_entities)
    elif hasattr(tweet, "extended_entities"):
        image_descriptions = process_image_descriptions(tweet.extended_entities)
    if image_descriptions != "":
        available_data.update(image_descriptions=image_descriptions)
    result = Template(template).safe_substitute(**available_data)
    result = re.sub(r"\$\w+", "", result)
    return result

def render_dm(dm, template, session, relative_times=False, offset_seconds=0):
    """ Renders direct messages by using the provided template.
    Available data will be stored in the following variables:
    $date: Creation date.
    $sender_display_name: User profile name for user who sent the dm.
    $sender_screen_name: User screen name for user sending the dm, this is the same name used to reference the user in Twitter.
    $recipient_display_name: User profile name for user who received the dm.
    $recipient_screen_name: User screen name for user receiving the dm, this is the same name used to reference the user in Twitter.
    $text: Text of the direct message.
    """
    available_data = dict()
    available_data.update(text=utils.expand_urls(dm.message_create["message_data"]["text"], dm.message_create["message_data"]["entities"]))
    # Let's remove the last 3 digits in the timestamp string.
    # Twitter sends their "epoch" timestamp with 3 digits for milliseconds and arrow doesn't like it.
    original_date = arrow.get(int(dm.created_timestamp))
    if relative_times == True:
        ts = original_date.humanize(locale=languageHandler.curLang[:2])
    else:
        ts = original_date.shift(seconds=offset_seconds)
    available_data.update(date=ts)
    sender = session.get_user(dm.message_create["sender_id"])
    recipient = session.get_user(dm.message_create["target"]["recipient_id"])
    available_data.update(sender_display_name=sender.name, sender_screen_name=sender.screen_name, recipient_display_name=recipient.name, recipient_screen_name=recipient.screen_name)
    result = Template(template).safe_substitute(**available_data)
    result = re.sub(r"\$\w+", "", result)
    return result