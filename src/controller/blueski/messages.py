from __future__ import annotations

import logging
from typing import Any

import arrow
import languageHandler
import output
import widgetUtils
from controller import messages as base_messages
from wxUI.dialogs.blueski import postDialogs
from extra.autocompletionUsers import completion

# Translation function is provided globally by TWBlue's language handler (_)

logger = logging.getLogger(__name__)

# This file would typically contain functions to generate complex message bodies or
# interactive components for Blueski, similar to how it might be done for Mastodon.
# Since Blueski's interactive features (beyond basic posts) are still evolving
# or client-dependent (like polls), this might be less complex initially.

# Example: If Blueski develops a standard for "cards" or interactive messages,
# functions to create those would go here. For now, we can imagine placeholders.

def format_welcome_message(session: Any) -> dict[str, Any]:
    """
    Generates a welcome message for a new Blueski session.
    This is just a placeholder and example.
    """
    # user_profile = session.util.get_own_profile_info() # Assuming this method exists and is async or cached
    # handle = user_profile.get("handle", _("your Blueski account")) if user_profile else _("your Blueski account")
    # Expect session to expose username via db/settings
    handle = (getattr(session, "db", {}).get("user_name")
              or getattr(getattr(session, "settings", {}), "get", lambda *_: {})("blueski").get("handle")
              or _("your Bluesky account"))


    return {
        "text": _("Welcome to Approve for Blueski! Your account {handle} is connected.").format(handle=handle),
        # "blocks": [ # If Blueski supports a block kit like Slack or Discord
        #     {
        #         "type": "section",
        #         "text": {
        #             "type": "mrkdwn", # Or Blueski's equivalent
        #             "text": _("Welcome to Approve for Blueski! Your account *{handle}* is connected.").format(handle=handle)
        #         }
        #     },
        #     {
        #         "type": "actions",
        #         "elements": [
        #             {
        #                 "type": "button",
        #                 "text": {"type": "plain_text", "text": _("Post your first Skeet")},
        #                 "action_id": "blueski_compose_new_post" # Example action ID
        #             }
        #         ]
        #     }
        # ]
    }

def format_error_message(error_description: str, details: str | None = None) -> dict[str, Any]:
    """
    Generates a standardized error message.
    """
    message = {"text": f":warning: Error: {error_description}"} # Basic text message
    # if details:
    #     message["blocks"] = [
    #         {
    #             "type": "section",
    #             "text": {"type": "mrkdwn", "text": f":warning: *Error:* {error_description}\n{details}"}
    #         }
    #     ]
    return message

# More functions could be added here as Blueski's capabilities become clearer
# or as specific formatting needs for Approve arise. For example:
# - Formatting a post for display with all its embeds and cards.
# - Generating help messages specific to Blueski features.
# - Creating interactive messages for polls (if supported via some convention).

# Example of adapting a function that might exist in mastodon_messages:
# def build_post_summary_message(session: BlueskiSession, post_uri: str, post_content: dict) -> dict[str, Any]:
#     """
#     Builds a summary message for an Blueski post.
#     """
#     author_handle = post_content.get("author", {}).get("handle", "Unknown user")
#     text_preview = post_content.get("text", "")[:100] # First 100 chars of text
#     # url = session.get_message_url(post_uri) # Assuming this method exists
#     url = f"https://bsky.app/profile/{author_handle}/post/{post_uri.split('/')[-1]}" # Construct a URL

#     return {
#         "text": _("Post by {author_handle}: {text_preview}... ({url})").format(
#             author_handle=author_handle, text_preview=text_preview, url=url
#         ),
#         # Potentially with "blocks" for richer formatting if the platform supports it
#     }

logger.info("Blueski messages module loaded (placeholders).")


class post(base_messages.basicMessage):
    # Bluesky character limit
    MAX_CHARS = 300

    def __init__(self, session: Any, title: str, caption: str, text: str = "", *args, **kwargs):
        self.session = session
        self.title = title
        langs = session.supported_languages
        display_langs = [l.name for l in langs]
        self.message = postDialogs.Post(caption=caption, text=text, languages=display_langs, *args, **kwargs)
        try:
            self.message.SetTitle(title)
            self.message.text.SetInsertionPoint(len(self.message.text.GetValue()))
        except Exception:
            pass
        # Set default language
        self.set_language(session.default_language)
        # Connect events for text processing and buttons
        widgetUtils.connect_event(self.message.text, widgetUtils.ENTERED_TEXT, self.text_processor)
        widgetUtils.connect_event(self.message.spoiler, widgetUtils.ENTERED_TEXT, self.text_processor)
        widgetUtils.connect_event(self.message.spellcheck, widgetUtils.BUTTON_PRESSED, self.spellcheck)
        widgetUtils.connect_event(self.message.translate, widgetUtils.BUTTON_PRESSED, self.translate)
        widgetUtils.connect_event(self.message.autocomplete_users, widgetUtils.BUTTON_PRESSED, self.autocomplete_users)
        # Initial text processing to show character count
        self.text_processor()

    def set_language(self, language_code=None):
        """Set the language selection based on language code."""
        if language_code is None:
            language_code = languageHandler.curLang[:2]
        for idx, lang in enumerate(self.session.supported_languages):
            if lang.code == language_code:
                self.message.language.SetSelection(idx)
                return
        # If not found, select first item (Not set)
        self.message.language.SetSelection(0)

    def get_language(self):
        """Get the selected language code."""
        langs = self.session.supported_languages
        idx = self.message.language.GetSelection()
        if idx >= 0 and idx < len(langs):
            return langs[idx].code
        return None

    def get_data(self):
        text, files, cw_text, lang_index = self.message.get_payload()
        langs = self.session.supported_languages
        lang_code = None
        if lang_index >= 0 and lang_index < len(langs):
            lang_code = langs[lang_index].code
        return text, files, cw_text, ([lang_code] if lang_code else [])

    def text_processor(self, *args, **kwargs):
        text = self.message.text.GetValue()
        cw = self.message.spoiler.GetValue() if self.message.spoiler.IsEnabled() else ""
        char_count = len(text) + len(cw)
        self.message.SetTitle(_("%s - %s of %d characters") % (self.title, char_count, self.MAX_CHARS))
        if char_count > self.MAX_CHARS:
            self.session.sound.play("max_length.ogg")

    def autocomplete_users(self, *args, **kwargs):
        c = completion.autocompletionUsers(self.message, self.session.session_id)
        c.show_menu()


def _g(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def has_post_data(item: Any) -> bool:
    post = _g(item, "post")
    record = _g(post, "record") if post is not None else None
    if record is None:
        record = _g(item, "record")
    return record is not None or post is not None


def _extract_labels(obj: Any) -> list[dict[str, Any]]:
    labels = _g(obj, "labels", None)
    if labels is None:
        return []
    if isinstance(labels, dict):
        labels = labels.get("values", [])
    if isinstance(labels, list):
        return labels
    return []


def _extract_cw_text(post: Any, record: Any) -> str:
    labels = _extract_labels(post) + _extract_labels(record)
    for label in labels:
        val = _g(label, "val", "")
        if val == "warn":
            return _("Sensitive Content")
        if isinstance(val, str) and val.startswith("warn:"):
            return val.split("warn:", 1)[-1].strip()
    return ""


def _extract_image_descriptions(post: Any, record: Any) -> str:
    def _collect_images(embed: Any) -> list[Any]:
        if not embed:
            return []
        etype = _g(embed, "$type") or _g(embed, "py_type") or ""
        if "recordWithMedia" in etype:
            media = _g(embed, "media")
            mtype = _g(media, "$type") or _g(media, "py_type") or ""
            if "images" in mtype:
                return list(_g(media, "images", []) or [])
            return []
        if "images" in etype:
            return list(_g(embed, "images", []) or [])
        return []

    images = []
    images.extend(_collect_images(_g(post, "embed")))
    if not images:
        images.extend(_collect_images(_g(record, "embed")))

    descriptions = []
    for idx, img in enumerate(images, start=1):
        alt = _g(img, "alt", "") or ""
        if alt:
            descriptions.append(_("Image {index}: {alt}").format(index=idx, alt=alt))
    return "\n".join(descriptions)


def _format_date(raw_date: str | None, offset_hours: int = 0) -> str:
    if not raw_date:
        return ""
    try:
        ts = arrow.get(raw_date)
        if offset_hours:
            ts = ts.shift(hours=offset_hours)
        return ts.format(_("dddd, MMMM D, YYYY H:m"), locale=languageHandler.curLang[:2])
    except Exception:
        return str(raw_date)[:16].replace("T", " ")


def _extract_post_view_data(session: Any, item: Any) -> dict[str, Any] | None:
    post = _g(item, "post", item)
    record = _g(post, "record") or _g(item, "record")
    if record is None:
        return None

    author = _g(post, "author") or _g(item, "author") or {}
    handle = _g(author, "handle", "")
    display_name = _g(author, "displayName") or _g(author, "display_name") or handle or _("Unknown")
    if handle and display_name != handle:
        author_label = f"{display_name} (@{handle})"
    elif handle:
        author_label = f"@{handle}"
    else:
        author_label = display_name

    text = _g(record, "text", "") or ""
    cw_text = _extract_cw_text(post, record)
    if cw_text:
        text = f"CW: {cw_text}\n\n{text}" if text else f"CW: {cw_text}"

    created_at = _g(record, "createdAt") or _g(record, "created_at")
    indexed_at = _g(post, "indexedAt") or _g(post, "indexed_at")
    date = _format_date(created_at or indexed_at, offset_hours=_g(session.db, "utc_offset", 0))

    reply_count = _g(post, "replyCount", 0) or 0
    repost_count = _g(post, "repostCount", 0) or 0
    like_count = _g(post, "likeCount", 0) or 0

    uri = _g(post, "uri") or _g(item, "uri")
    item_url = ""
    if uri and handle:
        rkey = uri.split("/")[-1]
        item_url = f"https://bsky.app/profile/{handle}/post/{rkey}"

    image_description = _extract_image_descriptions(post, record)

    return {
        "author": author_label,
        "text": text,
        "date": date,
        "replies": reply_count,
        "reposts": repost_count,
        "likes": like_count,
        "source": _("Bluesky"),
        "privacy": _("Public"),
        "image_description": image_description,
        "item_url": item_url,
    }


class viewPost(base_messages.basicMessage):
    def __init__(self, session: Any, item: Any):
        self.session = session
        data = _extract_post_view_data(session, item)
        if not data:
            output.speak(_("No post available to view."), True)
            return
        self.post_uri = _g(_g(item, "post", item), "uri") or _g(item, "uri")
        title = _("Post from {}").format(data["author"])
        self.message = postDialogs.viewPost(
            text=data["text"],
            reposts_count=data["reposts"],
            likes_count=data["likes"],
            source=data["source"],
            date=data["date"],
            privacy=data["privacy"],
        )
        self.message.SetTitle(title)
        if data["image_description"]:
            self.message.image_description.Enable(True)
            self.message.image_description.ChangeValue(data["image_description"])
        widgetUtils.connect_event(self.message.spellcheck, widgetUtils.BUTTON_PRESSED, self.spellcheck)
        widgetUtils.connect_event(self.message.translateButton, widgetUtils.BUTTON_PRESSED, self.translate)
        if data["item_url"]:
            self.message.enable_button("share")
            self.item_url = data["item_url"]
            widgetUtils.connect_event(self.message.share, widgetUtils.BUTTON_PRESSED, self.share)
        if self.post_uri:
            try:
                self.message.reposts_button.Enable(True)
                self.message.likes_button.Enable(True)
                widgetUtils.connect_event(self.message.reposts_button, widgetUtils.BUTTON_PRESSED, self.on_reposts)
                widgetUtils.connect_event(self.message.likes_button, widgetUtils.BUTTON_PRESSED, self.on_likes)
            except Exception:
                pass
        self.message.ShowModal()

    def text_processor(self):
        pass

    def share(self, *args, **kwargs):
        if hasattr(self, "item_url"):
            output.copy(self.item_url)
            output.speak(_("Link copied to clipboard."))

    def on_reposts(self, *args, **kwargs):
        if not self.post_uri:
            return
        try:
            import application
            controller = application.app.controller
            account_name = self.session.get_name()
            list_name = f"{self.post_uri}-reposts"
            existing = controller.search_buffer(list_name, account_name)
            if existing:
                index = controller.view.search(list_name, account_name)
                if index is not None:
                    controller.view.change_buffer(index)
                return
            title = _("people who reposted this post")
            from pubsub import pub
            pub.sendMessage(
                "createBuffer",
                buffer_type="PostUserListBuffer",
                session_type="blueski",
                buffer_title=title,
                parent_tab=controller.view.search("timelines", account_name),
                start=True,
                kwargs=dict(parent=controller.view.nb, name=list_name, session=self.session,
                            post_uri=self.post_uri, api_method="get_post_reposts")
            )
        except Exception:
            pass

    def on_likes(self, *args, **kwargs):
        if not self.post_uri:
            return
        try:
            import application
            controller = application.app.controller
            account_name = self.session.get_name()
            list_name = f"{self.post_uri}-likes"
            existing = controller.search_buffer(list_name, account_name)
            if existing:
                index = controller.view.search(list_name, account_name)
                if index is not None:
                    controller.view.change_buffer(index)
                return
            title = _("people who liked this post")
            from pubsub import pub
            pub.sendMessage(
                "createBuffer",
                buffer_type="PostUserListBuffer",
                session_type="blueski",
                buffer_title=title,
                parent_tab=controller.view.search("timelines", account_name),
                start=True,
                kwargs=dict(parent=controller.view.nb, name=list_name, session=self.session,
                            post_uri=self.post_uri, api_method="get_post_likes")
            )
        except Exception:
            pass


class text(base_messages.basicMessage):
    """Simple text viewer dialog for OCR results and similar."""

    def __init__(self, title, text="", *args, **kwargs):
        self.title = title
        self.message = postDialogs.viewText(title=title, text=text, *args, **kwargs)
        self.message.text.SetInsertionPoint(len(self.message.text.GetValue()))
        widgetUtils.connect_event(self.message.spellcheck, widgetUtils.BUTTON_PRESSED, self.spellcheck)
        widgetUtils.connect_event(self.message.translateButton, widgetUtils.BUTTON_PRESSED, self.translate)

    def text_processor(self):
        pass
