# -*- coding: utf-8 -*-
import arrow
from .  import utils

def compose_toot(toot, db, relative_times, show_screen_names):
    if show_screen_names == False:
        user = toot.account.get("display_name")
    else:
        user = toot.account.get("acct")
    original_date = arrow.get(toot.created_at)
    if relative_times:
        ts = original_date.humanize(locale="es")
    else:
        ts = original_date.shift(hours=db["utc_offset"]).format(_("dddd, MMMM D, YYYY H:m:s"), locale="es")
    if toot.reblog != None:
        text = _("Boosted from @{}: {}").format(toot.reblog.account.acct, utils.html_filter(toot.reblog.content))
    else:
        text = utils.html_filter(toot.content)
    source = toot.get("application", "")
    # "" means remote user, None for legacy apps so we should cover both sides.
    if source != None and source != "":
        source = source.get("name", "")
    else:
        source = ""
    return [user+", ", text, ts+", ", source]
