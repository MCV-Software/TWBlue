from html.parser import HTMLParser

class HTMLFilter(HTMLParser):
    text = ""
    def handle_data(self, data):
        self.text += data

def html_filter(data):
    f = HTMLFilter()
    f.feed(data)
    return f.text

def find_item(item, listItems):
    for i in range(0, len(listItems)):
        if listItems[i].id == item.id:
            return i
        # Check also retweets.
        if item.reblog != None and item.reblog.id == listItems[i].id:
            return i
    return None

def is_audio_or_video(toot):
    if toot.reblog != None:
        return is_audio_or_video(toot.reblog)
    # Checks firstly for Mastodon native videos and audios.
    for media in toot.media_attachments:
        if media["type"] == "video" or media["type"] == "audio":
            return True

def is_image(toot):
    if toot.reblog != None:
        return is_audio_or_video(toot.reblog)
    # Checks firstly for Mastodon native videos and audios.
    for media in toot.media_attachments:
        if media["type"] == "gifv" or media["type"] == "image":
            return True