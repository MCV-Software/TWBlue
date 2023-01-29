# -*- coding: utf-8 -*-
import re
import arrow
import languageHandler
from string import Template
from . import utils, compose

# Define variables that would be available for all template objects.
# This will be used for the edit template dialog.
# Available variables for post objects.
# safe_text will be the content warning in case a post contains one, text will always be the full text, no matter if has a content warning or not.
post_variables = ["date", "display_name", "screen_name", "source", "lang", "safe_text", "text", "image_descriptions", "visibility"]
person_variables = ["display_name", "screen_name", "description", "followers", "following", "favorites", "posts", "created_at"]
conversation_variables = ["users", "last_post"]
notification_variables = ["display_name", "screen_name", "text", "date"]

# Default, translatable templates.
post_default_template = _("$display_name, $text $image_descriptions $date. $source")
dm_sent_default_template = _("Dm to $recipient_display_name, $text $date")
person_default_template = _("$display_name (@$screen_name). $followers followers, $following following, $posts posts. Joined $created_at.")
notification_default_template = _("$display_name $text, $date")

def process_date(field, relative_times=True, offset_hours=0):
    original_date = arrow.get(field)
    if relative_times == True:
        ts = original_date.humanize(locale=languageHandler.curLang[:2])
    else:
        ts = original_date.shift(hours=offset_hours).format(_("dddd, MMMM D, YYYY H:m:s"), locale=languageHandler.curLang[:2])
    return ts

def process_text(post, safe=True):
#    text = utils.clean_mentions(utils.StripChars(text))
    if safe == True and post.sensitive == True and post.spoiler_text != "":
        return _("Content warning: {}").format(post.spoiler_text)
    return utils.html_filter(post.content)

def process_image_descriptions(media_attachments):
    """ Attempt to extract information for image descriptions. """
    image_descriptions = []
    for media in media_attachments:
        if media.get("description") != None and media.get("description") != "":
            image_descriptions.append(media.get("description"))
    idescriptions = ""
    for image in image_descriptions:
        idescriptions = idescriptions + _("Image description: {}").format(image) + "\n"
    return idescriptions

def remove_unneeded_variables(template, variables):
    for variable in variables:
        template = re.sub("\$"+variable, "", template)
    return template

def render_post(post, template, relative_times=False, offset_hours=0):
    """ Renders any given post according to the passed template.
    Available data for posts will be stored in the following variables:
    $date: Creation date.
    $display_name: User profile name.
    $screen_name: User screen name, this is the same name used to reference the user in Twitter.
    $ source: Source client from where the current tweet was sent.
    $lang: Two letter code for the automatically detected language for the tweet. This detection is performed by Twitter.
    $safe_text: Safe text to display. If a content warning is applied in posts, display those instead of the whole post.
    $text: Toot text. This always displays the full text, even if there is a content warning present.
    $image_descriptions: Information regarding image descriptions added by twitter users.
    $visibility: post's visibility: public, not listed, followers only or direct.
    """
    global post_variables
    available_data = dict()
    created_at = process_date(post.created_at, relative_times, offset_hours)
    available_data.update(date=created_at)
    # user.
    display_name = post.account.display_name
    if display_name == "":
        display_name = post.account.username
    available_data.update(display_name=display_name, screen_name=post.account.acct)
    # Source client from where tweet was originated.
    source = ""
    if hasattr(post, "application") and post.application != None:
        available_data.update(source=post.application.get("name"))
    if post.reblog != None:
        text = _("Boosted from @{}: {}").format(post.reblog.account.acct, process_text(post.reblog, safe=False), )
        safe_text = _("Boosted from @{}: {}").format(post.reblog.account.acct, process_text(post.reblog), )
    else:
        text = process_text(post, safe=False)
        safe_text = process_text(post)
    visibility_settings = dict(public=_("Public"), unlisted=_("Not listed"), private=_("Followers only"), direct=_("Direct"))
    visibility = visibility_settings.get(post.visibility)
    available_data.update(lang=post.language, text=text, safe_text=safe_text, visibility=visibility)
    # process image descriptions
    image_descriptions = ""
    if post.reblog != None:
        image_descriptions = process_image_descriptions(post.reblog.media_attachments)
    else:
        image_descriptions = process_image_descriptions(post.media_attachments)
    if image_descriptions != "":
        available_data.update(image_descriptions=image_descriptions)
    result = Template(_(template)).safe_substitute(**available_data)
    result = remove_unneeded_variables(result, post_variables)
    return result

def render_user(user, template, relative_times=True, offset_hours=0):
    """ Renders persons by using the provided template.
    Available data will be stored in the following variables:
    $display_name: The name of the user, as they’ve defined it. Not necessarily a person’s name. Typically capped at 50 characters, but subject to change.
    $screen_name: The screen name, handle, or alias that this user identifies themselves with.
    $description: The user-defined UTF-8 string describing their account.
    $followers: The number of followers this account currently has. This value might be inaccurate.
    $following: The number of users this account is following (AKA their “followings”). This value might be inaccurate.
    $posts: The number of Tweets (including retweets) issued by the user. This value might be inaccurate.
    $created_at: The date and time that the user account was created on Twitter.
    """
    global person_variables
    display_name = user.display_name
    if display_name == "":
        display_name = user.username
    available_data = dict(display_name=display_name, screen_name=user.acct, followers=user.followers_count, following=user.following_count, posts=user.statuses_count)
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

def render_conversation(conversation, template, post_template, relative_times=False, offset_hours=0):
    users = []
    for account in conversation.accounts:
        if account.display_name != "":
            users.append(account.display_name)
        else:
            users.append(account.username)
    users = ", ".join(users)
    last_post = render_post(conversation.last_status, post_template, relative_times=relative_times, offset_hours=offset_hours)
    available_data = dict(users=users, last_post=last_post)
    result = Template(_(template)).safe_substitute(**available_data)
    result = remove_unneeded_variables(result, conversation_variables)
    return result

def render_notification(notification, template, post_template, relative_times=False, offset_hours=0):
    """ Renders any given notification according to the passed template.
    Available data for notifications will be stored in the following variables:
    $date: Creation date.
    $display_name: User profile name.
    $screen_name: User screen name, this is the same name used to reference the user in Twitter.
    $text: Notification text, describing the action.
    """
    global notification_variables
    available_data = dict()
    created_at = process_date(notification.created_at, relative_times, offset_hours)
    available_data.update(date=created_at)
    # user.
    display_name = notification.account.display_name
    if display_name == "":
        display_name = notification.account.username
    available_data.update(display_name=display_name, screen_name=notification.account.acct)
    text = "Unknown: %r" % (notification)
    # Remove date from status, so it won't be rendered twice.
    post_template = post_template.replace("$date", "")
    if notification.type == "status":
        text = _("has posted: {status}").format(status=render_post(notification.status, post_template, relative_times, offset_hours))
    elif notification.type == "mention":
        text = _("has mentionned you: {status}").format(status=render_post(notification.status, post_template, relative_times, offset_hours))
    elif notification.type == "reblog":
        text = _("has boosted: {status}").format(status=render_post(notification.status, post_template, relative_times, offset_hours))
    elif notification.type == "favourite":
        text = _("has added to favorites: {status}").format(status=render_post(notification.status, post_template, relative_times, offset_hours))
    elif notification.type == "update":
        text = _("has updated a status: {status}").format(status=render_post(notification.status, post_template, relative_times, offset_hours))
    elif notification.type == "follow":
        text = _("has followed you.")
    elif notification.type == "poll":
        text = _("A poll in which you have voted has expired: {status}").format(status=render_post(notification.status, post_template, relative_times, offset_hours))
    elif notification.type == "follow_request":
        text = _("wants to follow you.")
    available_data.update(text=text)
    result = Template(_(template)).safe_substitute(**available_data)
    result = remove_unneeded_variables(result, post_variables)
    result = result.replace(" . ", "")
    return result
