# -*- coding: utf-8 -*-
import arrow
from .  import utils, templates

def compose_toot(toot, db, relative_times, show_screen_names):
    if show_screen_names == False:
        user = toot.account.get("display_name")
        if user == "":
            user = toot.account.get("username")
    else:
        user = toot.account.get("acct")
    original_date = arrow.get(toot.created_at)
    if relative_times:
        ts = original_date.humanize(locale="es")
    else:
        ts = original_date.shift(hours=db["utc_offset"]).format(_("dddd, MMMM D, YYYY H:m:s"), locale="es")
    if toot.reblog != None:
        text = _("Boosted from @{}: {}").format(toot.reblog.account.acct, templates.process_text(toot.reblog))
    else:
        text = templates.process_text(toot)
    source = toot.get("application", "")
    # "" means remote user, None for legacy apps so we should cover both sides.
    if source != None and source != "":
        source = source.get("name", "")
    else:
        source = ""
    return [user+", ", text, ts+", ", source]

def compose_user(user, db, relative_times=True):
    original_date = arrow.get(user.created_at)
    if relative_times:
        ts = original_date.humanize(locale="es")
    else:
        ts = original_date.shift(hours=db["utc_offset"]).format(_("dddd, MMMM D, YYYY H:m:s"), locale="es")
    name = user.display_name
    if name == "":
        name = user.get("username")
    return [_("%s (@%s). %s followers, %s following, %s toots. Joined %s") % (name, user.acct, user.followers_count, user.following_count,  user.statuses_count, ts)]
