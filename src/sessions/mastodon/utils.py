import re
import demoji
from html.parser import HTMLParser
from datetime import datetime, timezone

url_re = re.compile(r'<a\s*href=[\'|"](.*?)[\'"].*?>')

class HTMLFilter(HTMLParser):
    # Classes to ignore when parsing HTML
    IGNORED_CLASSES = ["quote-inline"]

    text = ""
    first_paragraph = True
    skip_depth = 0  # Track nesting depth of ignored elements

    def handle_data(self, data):
        # Only add data if we're not inside an ignored element
        if self.skip_depth == 0:
            self.text += data

    def handle_starttag(self, tag, attrs):
        # Check if this tag has a class that should be ignored
        attrs_dict = dict(attrs)
        tag_class = attrs_dict.get("class", "")

        # Check if any ignored class is present in this tag
        should_skip = any(ignored_class in tag_class for ignored_class in self.IGNORED_CLASSES)

        if should_skip:
            self.skip_depth += 1
        elif self.skip_depth == 0:  # Only process tags if we're not skipping
            if tag == "br":
                self.text = self.text+"\n"
            elif tag == "p":
                if self.first_paragraph:
                    self.first_paragraph = False
                else:
                    self.text = self.text+"\n\n"
        else:
            # We're inside a skipped element, increment depth for nested tags
            self.skip_depth += 1

    def handle_endtag(self, tag):
        # Decrement skip depth when closing any tag while skipping
        if self.skip_depth > 0:
            self.skip_depth -= 1

def html_filter(data):
    f = HTMLFilter()
    f.feed(data)
    return f.text

def find_item(item, listItems):
    for i in range(0, len(listItems)):
        if listItems[i].id == item.id:
            return i
        if hasattr(item, "reblog") and item.reblog != None and item.reblog.id == listItems[i].id:
            return i
    return None

def is_audio_or_video(post):
    if post.reblog != None:
        return is_audio_or_video(post.reblog)
    # Checks firstly for Mastodon native videos and audios.
    for media in post.media_attachments:
        if media["type"] == "video" or media["type"] == "audio":
            return True

def is_image(post):
    if post.reblog != None:
        return is_image(post.reblog)
    # Checks firstly for Mastodon native videos and audios.
    for media in post.media_attachments:
        if media["type"] == "gifv" or media["type"] == "image":
            return True

def get_media_urls(post):
    if hasattr(post, "reblog") and post.reblog != None:
            return get_media_urls(post.reblog)
    urls = []
    for media in post.media_attachments:
        if media.get("type") == "audio" or media.get("type") == "video":
            url_keys = ["remote_url", "url"]
            for url_key in url_keys:
                if media.get(url_key) != None:
                    urls.append(media.get(url_key))
                    break
    return urls

def find_urls(post, include_tags=False):
    urls = url_re.findall(post.content)
    if include_tags == False:
        for tag in post.tags:
            for url in urls[::]:
                if url.lower().endswith("/tags/"+tag["name"]):
                    urls.remove(url)
    return urls

def get_user_alias(user, settings):
    if user.display_name == None or user.display_name == "":
        display_name = user.username
    else:
        display_name = user.display_name
    aliases = settings.get("user-aliases")
    if aliases == None:
        return demoji_user(display_name, settings)
    user_alias = aliases.get(str(user.id))
    if user_alias != None:
        return user_alias
    return demoji_user(display_name, settings)

def demoji_user(name, settings):
    if settings["general"]["hide_emojis"] == True:
        user = demoji.replace(name, "")
        # Take care of Mastodon instance emojis.
        user = re.sub(r":(.*?):", "", user)
        return user
    return name

def get_current_context(buffer: str) -> str:
    """ Gets the name of a buffer and returns the context it belongs to. useful for filtering. """
    if buffer == "home_timeline":
        return "home"
    elif buffer == "mentions" or buffer == "notifications":
        return "notifications"

def evaluate_filters(post: dict, current_context: str) -> str | None:
    """
    Evaluates the 'filtered' attribute of a Mastodon post to determine its visibility,
    considering the current context, expiration, and matches (keywords or status).

    Parameters:
      post (dict): A dictionary representing a Mastodon post.
      current_context (str): The context in which the post is displayed 
                             (e.g., "home", "notifications", "public", "thread", or "profile").

    Returns:
      - "hide" if any applicable filter indicates the post should be hidden.
      - A string with the filter's title if an applicable "warn" filter is present.
      - None if no applicable filters are found, meaning the post should be shown normally.
    """
    filters = post.get("filtered", None)

    # Automatically hide muted conversations from home timeline.
    if current_context == "home" and post.get("muted") == True:
        return "hide"

    if filters == None:
        return
    warn_filter_title = None
    now = datetime.now(timezone.utc)
    for result in filters:
        filter_data = result.get("filter", {})
        # Check if the filter applies to the current context.
        filter_contexts = filter_data.get("context", [])
        if current_context not in filter_contexts:
            continue  # Skip filters not applicable in this context
        # Check if the filter has expired.
        expires_at = filter_data.get("expires_at")
        if expires_at is not None:
            # If expires_at is a string, attempt to parse it.
            if isinstance(expires_at, str):
                try:
                    expiration_dt = datetime.fromisoformat(expires_at)
                except ValueError:
                    continue  # Skip if the date format is invalid
            else:
                expiration_dt = expires_at
            if expiration_dt < now:
                continue  # Skip expired filters
        action = filter_data.get("filter_action", "")
        if action == "hide":
            return "hide"
        elif action == "warn":
            title = filter_data.get("title", "")
            warn_filter_title = title if title else "warn"
    if warn_filter_title:
        return warn_filter_title
    return None