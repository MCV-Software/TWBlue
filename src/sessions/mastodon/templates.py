# -*- coding: utf-8 -*-
import re
import arrow
import languageHandler
from string import Template
from . import utils

# Define variables that would be available for all template objects.
# This will be used for the edit template dialog.
# Available variables for toot objects.
toot_variables = ["date", "display_name", "screen_name", "source", "lang", "text", "image_descriptions"]
person_variables = ["display_name", "screen_name", "description", "followers", "following", "favorites", "toots", "created_at"]

# Default, translatable templates.
toot_default_template = _("$display_name, $text $image_descriptions $date. $source")
dm_sent_default_template = _("Dm to $recipient_display_name, $text $date")
person_default_template = _("$display_name (@$screen_name). $followers followers, $following following, $toots toots. Joined $created_at.")

def process_date(field, relative_times=True, offset_hours=0):
    original_date = arrow.get(field)
    if relative_times == True:
        ts = original_date.humanize(locale=languageHandler.curLang[:2])
    else:
        ts = original_date.shift(hours=offset_hours).format(_("dddd, MMMM D, YYYY H:m:s"), locale=languageHandler.curLang[:2])
    return ts

def process_text(toot):
#    text = utils.clean_mentions(utils.StripChars(text))
        return utils.html_filter(toot.content)

def process_image_descriptions(media_attachments):
    """ Attempt to extract information for image descriptions. """
    image_descriptions = []
    for media in media_attachments:
        if media.get("description") != None:
            image_descriptions.append(media.get("description"))
    idescriptions = ""
    for image in image_descriptions:
        idescriptions += _("Image description: {}").format(image)
    return idescriptions

def remove_unneeded_variables(template, variables):
    for variable in variables:
        template = re.sub("\$"+variable, "", template)
    return template

def render_toot(toot, template, relative_times=False, offset_hours=0):
    """ Renders any given toot according to the passed template.
    Available data for toots will be stored in the following variables:
    $date: Creation date.
    $display_name: User profile name.
    $screen_name: User screen name, this is the same name used to reference the user in Twitter.
    $ source: Source client from where the current tweet was sent.
    $lang: Two letter code for the automatically detected language for the tweet. This detection is performed by Twitter.
    $text: Tweet text.
    $image_descriptions: Information regarding image descriptions added by twitter users.
    """
    global toot_variables
    available_data = dict()
    created_at = process_date(toot.created_at, relative_times, offset_hours)
    available_data.update(date=created_at)
    # user.
    display_name = toot.account.display_name
    if display_name == "":
        display_name = toot.account.username
    available_data.update(display_name=display_name, screen_name=toot.account.acct)
    # Source client from where tweet was originated.
    source = ""
    if hasattr(toot, "application") and toot.application != None:
        available_data.update(source=toot.application.get("name"))
    if toot.reblog != None:
        text = _("Boosted from @{}: {}").format(toot.reblog.account.acct, process_text(toot.reblog), )
    else:
        text = process_text(toot)
    available_data.update(lang=toot.language, text=text)
    # process image descriptions
    image_descriptions = ""
    if toot.reblog != None:
        image_descriptions = process_image_descriptions(toot.reblog.media_attachments)
    else:
        image_descriptions = process_image_descriptions(toot.media_attachments)
    if image_descriptions != "":
        available_data.update(image_descriptions=image_descriptions)
    result = Template(_(template)).safe_substitute(**available_data)
    result = remove_unneeded_variables(result, toot_variables)
    return result

def render_person(user, template, relative_times=True, offset_hours=0):
    """ Renders persons by using the provided template.
    Available data will be stored in the following variables:
    $display_name: The name of the user, as they’ve defined it. Not necessarily a person’s name. Typically capped at 50 characters, but subject to change.
    $screen_name: The screen name, handle, or alias that this user identifies themselves with.
    $location: The user-defined location for this account’s profile. Not necessarily a location, nor machine-parseable.
    $description: The user-defined UTF-8 string describing their account.
    $followers: The number of followers this account currently has. This value might be inaccurate.
    $following: The number of users this account is following (AKA their “followings”). This value might be inaccurate.
    $favorites: The number of Tweets this user has liked in the account’s lifetime. This value might be inaccurate.
    $tweets: The number of Tweets (including retweets) issued by the user. This value might be inaccurate.
    $created_at: The date and time that the user account was created on Twitter.
    """
    global person_variables
    display_name = user.display_name
    if display_name == "":
        display_name = user.username
    available_data = dict(display_name=display_name, screen_name=user.acct, followers=user.followers_count, following=user.following_count, favorites=user.favourites_count, toots=user.statuses_count)
    # Nullable values.
    nullables = ["description"]
    for nullable in nullables:
        if hasattr(user, nullable) and getattr(user, nullable) != None:
            available_data[nullable] = getattr(user, nullable)
    created_at = process_date(user.created_at, relative_times=relative_times, offset_hours=offset_hours)
    available_data.update(created_at=created_at)
    result = Template(_(template)).safe_substitute(**available_data)
    result = remove_unneeded_variables(result, person_variables)
    return result