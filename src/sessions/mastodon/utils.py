import re
from html.parser import HTMLParser

url_re = re.compile('<a\s*href=[\'|"](.*?)[\'"].*?>')

class HTMLFilter(HTMLParser):
    text = ""
    first_paragraph = True

    def handle_data(self, data):
        self.text += data

    def handle_starttag(self, tag, attrs):
        if tag == "br":
            self.text = self.text+"\n"
        elif tag == "p":
            if self.first_paragraph:
                self.first_paragraph = False
            else:
                self.text = self.text+"\n\n"

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