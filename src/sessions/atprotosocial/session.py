from __future__ import annotations

import logging
from typing import Any

import wx

from sessions import base
from sessions import session_exceptions as Exceptions
import output
import application

log = logging.getLogger("sessions.atprotosocialSession")

# Optional import of atproto. Code handles absence gracefully.
try:
    from atproto import Client as AtpClient  # type: ignore
except Exception:  # ImportError or missing deps
    AtpClient = None  # type: ignore


class Session(base.baseSession):
    """Minimal Bluesky (atproto) session for TWBlue.

    Provides basic authorisation, login, and posting support to unblock
    the integration while keeping compatibility with TWBlue's session API.
    """

    name = "Bluesky"
    KIND = "atprotosocial"

    def __init__(self, *args, **kwargs):
        super(Session, self).__init__(*args, **kwargs)
        self.config_spec = "atprotosocial.defaults"
        self.type = "atprotosocial"
        self.char_limit = 300
        self.api = None

    def get_name(self):
        """Return a human-friendly, stable account name for UI.

        Prefer the user's handle if available so accounts are uniquely
        identifiable, falling back to a generic network name otherwise.
        """
        try:
            # Prefer runtime DB, then persisted settings, then SDK client
            handle = (
                self.db.get("user_name")
                or (self.settings and self.settings.get("atprotosocial", {}).get("handle"))
                or (getattr(getattr(self, "api", None), "me", None) and self.api.me.handle)
            )
            if handle:
                return handle
        except Exception:
            pass
        return self.name

    def _ensure_client(self):
        if AtpClient is None:
            raise RuntimeError(
                "The 'atproto' package is not installed. Install it to use Bluesky."
            )
        if self.api is None:
            self.api = AtpClient()
        return self.api

    def login(self, verify_credentials=True):
        if self.settings.get("atprotosocial") is None:
            raise Exceptions.RequireCredentialsSessionError
        handle = self.settings["atprotosocial"].get("handle")
        app_password = self.settings["atprotosocial"].get("app_password")
        session_string = self.settings["atprotosocial"].get("session_string")
        if not handle or (not app_password and not session_string):
            self.logged = False
            raise Exceptions.RequireCredentialsSessionError
        try:
            # Ensure db exists (can be set to None on logout paths)
            if not isinstance(self.db, dict):
                self.db = {}
            # Ensure general settings have a default for boost confirmations like Mastodon
            try:
                if "general" in self.settings and self.settings["general"].get("boost_mode") is None:
                    self.settings["general"]["boost_mode"] = "ask"
            except Exception:
                pass
            api = self._ensure_client()
            # Prefer resuming session if we have one
            if session_string:
                try:
                    api.import_session_string(session_string)
                except Exception:
                    # Fall back to login below
                    pass
            if not getattr(api, "me", None):
                # Fresh login
                api.login(handle, app_password)
            # Cache basics
            if getattr(api, "me", None) is None:
                raise RuntimeError("Bluesky SDK client has no 'me' after login")
            self.db["user_name"] = api.me.handle
            self.db["user_id"] = api.me.did
            # Persist DID in settings for session manager display
            self.settings["atprotosocial"]["did"] = api.me.did
            # Export session for future reuse
            try:
                self.settings["atprotosocial"]["session_string"] = api.export_session_string()
            except Exception:
                pass
            self.settings.write()
            self.logged = True
            log.debug("Logged in to Bluesky as %s", api.me.handle)
        except Exception:
            log.exception("Bluesky login failed")
            self.logged = False

    def authorise(self):
        if self.logged:
            raise Exceptions.AlreadyAuthorisedError("Already authorised.")
        # Ask for handle
        dlg = wx.TextEntryDialog(
            None,
            _("Enter your Bluesky handle (e.g., username.bsky.social)"),
            _("Bluesky Login"),
        )
        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return
        handle = dlg.GetValue().strip()
        dlg.Destroy()
        # Ask for app password
        pwd = wx.PasswordEntryDialog(
            None,
            _("Enter your Bluesky App Password (from Settings > App passwords)"),
            _("Bluesky Login"),
        )
        if pwd.ShowModal() != wx.ID_OK:
            pwd.Destroy()
            return
        app_password = pwd.GetValue().strip()
        pwd.Destroy()
        # Create session folder and config, then attempt login
        self.create_session_folder()
        self.get_configuration()
        self.settings["atprotosocial"]["handle"] = handle
        self.settings["atprotosocial"]["app_password"] = app_password
        self.settings.write()
        try:
            self.login()
        except Exceptions.RequireCredentialsSessionError:
            return
        except Exception:
            log.exception("Authorisation failed")
            wx.MessageBox(
                _("We could not log in to Bluesky. Please verify your handle and app password."),
                _("Login error"), wx.ICON_ERROR
            )
            return
        return True

    def get_message_url(self, message_id, context=None):
        # message_id may be full at:// URI or rkey
        handle = self.db.get("user_name") or self.settings["atprotosocial"].get("handle", "")
        rkey = message_id
        if isinstance(message_id, str) and message_id.startswith("at://"):
            parts = message_id.split("/")
            rkey = parts[-1]
        return f"https://bsky.app/profile/{handle}/post/{rkey}"

    def send_message(self, message, files=None, reply_to=None, cw_text=None, is_sensitive=False, **kwargs):
        if not self.logged:
            raise Exceptions.NotLoggedSessionError("You are not logged in yet.")
        try:
            api = self._ensure_client()
            # Basic text-only post for now. Attachments and CW can be extended later.
            # Prefer convenience if available
            uri = None
            text = message or ""
            # Naive CW handling: prepend CW label to text if provided
            if cw_text:
                text = f"CW: {cw_text}\n\n{text}" if text else f"CW: {cw_text}"

            # Build base record
            record: dict[str, Any] = {
                "$type": "app.bsky.feed.post",
                "text": text,
            }
            # createdAt
            try:
                record["createdAt"] = api.get_current_time_iso()
            except Exception:
                pass
            # languages
            langs = kwargs.get("langs") or kwargs.get("languages")
            if isinstance(langs, (list, tuple)) and langs:
                record["langs"] = list(langs)

            # Helper to build a StrongRef (uri+cid) for a given post URI
            def _get_strong_ref(uri: str):
                try:
                    # Try typed models first
                    posts_res = api.app.bsky.feed.get_posts({"uris": [uri]})
                    posts = getattr(posts_res, "posts", None) or []
                except Exception:
                    try:
                        posts_res = api.app.bsky.feed.get_posts(uris=[uri])
                        posts = getattr(posts_res, "posts", None) or []
                    except Exception:
                        posts = []
                if posts:
                    post0 = posts[0]
                    post_uri = getattr(post0, "uri", uri)
                    post_cid = getattr(post0, "cid", None) or (post0.get("cid") if isinstance(post0, dict) else None)
                    if post_cid:
                        return {"uri": post_uri, "cid": post_cid}
                return None

            # Upload images if provided
            embed_images = []
            if files:
                for f in files:
                    path = f
                    alt = ""
                    if isinstance(f, dict):
                        path = f.get("path") or f.get("file")
                        alt = f.get("alt") or f.get("alt_text") or ""
                    if not path:
                        continue
                    try:
                        with open(path, "rb") as fp:
                            data = fp.read()
                        # Try typed upload
                        try:
                            up = api.com.atproto.repo.upload_blob(data)
                            blob_ref = getattr(up, "blob", None) or getattr(up, "data", None) or up
                        except Exception:
                            # Some SDK variants expose upload via api.upload_blob
                            up = api.upload_blob(data)
                            blob_ref = getattr(up, "blob", None) or getattr(up, "data", None) or up
                        if blob_ref:
                            embed_images.append({
                                "image": blob_ref,
                                "alt": alt or "",
                            })
                    except Exception:
                        log.exception("Error uploading media for Bluesky post")
                        continue

            # Quote post (takes precedence over images)
            quote_uri = kwargs.get("quote_uri") or kwargs.get("quote")
            if quote_uri:
                strong = _get_strong_ref(quote_uri)
                if strong:
                    record["embed"] = {
                        "$type": "app.bsky.embed.record",
                        "record": strong,
                    }
                    embed_images = []  # Ignore images when quoting

            if embed_images and not record.get("embed"):
                record["embed"] = {
                    "$type": "app.bsky.embed.images",
                    "images": embed_images,
                }

            # Helper: normalize various incoming identifiers to an at:// URI
            def _normalize_to_uri(identifier: str) -> str | None:
                try:
                    if not isinstance(identifier, str):
                        return None
                    if identifier.startswith("at://"):
                        return identifier
                    if "bsky.app/profile/" in identifier and "/post/" in identifier:
                        # Accept full web URL and try to resolve via get_post_thread below
                        return identifier
                    # Accept bare rkey case by constructing a guess using own handle
                    handle = self.db.get("user_name") or self.settings["atprotosocial"].get("handle")
                    did = self.db.get("user_id") or self.settings["atprotosocial"].get("did")
                    if handle and did and len(identifier) in (13, 14, 15):
                        # rkey length is typically ~13 chars base32
                        return f"at://{did}/app.bsky.feed.post/{identifier}"
                except Exception:
                    pass
                return None

            # Reply-to handling (sets correct root/parent strong refs)
            if reply_to:
                # Resolve to proper at:// uri when possible
                reply_uri = _normalize_to_uri(reply_to) or reply_to
                parent_ref = _get_strong_ref(reply_uri)
                root_ref = parent_ref
                # Try to fetch thread to find actual root for deep replies
                try:
                    # atproto SDK usually exposes get_post_thread
                    thread_res = None
                    try:
                        thread_res = api.app.bsky.feed.get_post_thread({"uri": reply_uri})
                    except Exception:
                        # Try typed model call variant if available
                        from atproto import models as at_models  # type: ignore
                        params = at_models.AppBskyFeedGetPostThread.Params(uri=reply_uri)
                        thread_res = api.app.bsky.feed.get_post_thread(params)
                    thread = getattr(thread_res, "thread", None)
                    # Walk to the root if present
                    node = thread
                    while node and getattr(node, "parent", None):
                        node = getattr(node, "parent")
                    root_uri = getattr(node, "post", None)
                    if root_uri:
                        root_uri = getattr(root_uri, "uri", None)
                    if root_uri and isinstance(root_uri, str):
                        maybe_root = _get_strong_ref(root_uri)
                        if maybe_root:
                            root_ref = maybe_root
                except Exception:
                    # If anything fails, keep parent as root for a simple two-level reply
                    pass
                if parent_ref:
                    record["reply"] = {
                        "root": root_ref or parent_ref,
                        "parent": parent_ref,
                    }

            # Fallback to convenience if available
            try:
                if hasattr(api, "send_post") and not embed_images and not langs and not cw_text:
                    res = api.send_post(text)
                    uri = getattr(res, "uri", None) or getattr(res, "cid", None)
                else:
                    out = api.com.atproto.repo.create_record({
                        "repo": api.me.did,
                        "collection": "app.bsky.feed.post",
                        "record": record,
                    })
                    uri = getattr(out, "uri", None)
            except Exception:
                log.exception("Error creating Bluesky post record")
                uri = None
            if not uri:
                raise RuntimeError("Post did not return a URI")
            # Store last post id if useful
            self.db.setdefault("sent", [])
            self.db["sent"].append(dict(id=uri, text=message))
            self.save_persistent_data()
            return uri
        except Exception:
            log.exception("Error sending Bluesky post")
            output.speak(_("An error occurred while posting to Bluesky."), True)
            return None

    def repost(self, post_uri: str, post_cid: str | None = None) -> str | None:
        """Create a simple repost of a given post. Returns URI of the repost record or None."""
        if not self.logged:
            raise Exceptions.NotLoggedSessionError("You are not logged in yet.")
        try:
            api = self._ensure_client()

            def _get_strong_ref(uri: str):
                try:
                    posts_res = api.app.bsky.feed.get_posts({"uris": [uri]})
                    posts = getattr(posts_res, "posts", None) or []
                except Exception:
                    try:
                        posts_res = api.app.bsky.feed.get_posts(uris=[uri])
                        posts = getattr(posts_res, "posts", None) or []
                    except Exception:
                        posts = []
                if posts:
                    post0 = posts[0]
                    s_uri = getattr(post0, "uri", uri)
                    s_cid = getattr(post0, "cid", None) or (post0.get("cid") if isinstance(post0, dict) else None)
                    if s_cid:
                        return {"uri": s_uri, "cid": s_cid}
                return None

            if not post_cid:
                strong = _get_strong_ref(post_uri)
                if not strong:
                    return None
                post_uri = strong["uri"]
                post_cid = strong["cid"]

            out = api.com.atproto.repo.create_record({
                "repo": api.me.did,
                "collection": "app.bsky.feed.repost",
                "record": {
                    "$type": "app.bsky.feed.repost",
                    "subject": {"uri": post_uri, "cid": post_cid},
                    "createdAt": getattr(api, "get_current_time_iso", lambda: None)() or None,
                },
            })
            return getattr(out, "uri", None)
        except Exception:
            log.exception("Error creating Bluesky repost record")
            return None
