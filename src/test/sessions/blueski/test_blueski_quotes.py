# -*- coding: utf-8 -*-
import builtins
import unittest

from sessions.blueski import compose, templates, utils


class TestBlueskyQuotedPosts(unittest.TestCase):

    def setUp(self):
        if not hasattr(builtins, "_"):
            builtins._ = lambda s: s

    def _build_quoted_post(self):
        return {
            "post": {
                "author": {"handle": "alice.bsky.social", "displayName": "Alice"},
                "record": {"text": "Main post text"},
                "embed": {
                    "$type": "app.bsky.embed.recordWithMedia#view",
                    "record": {
                        "$type": "app.bsky.embed.record#view",
                        "record": {
                            "$type": "app.bsky.embed.record#viewRecord",
                            "author": {"handle": "bob.bsky.social"},
                            "value": {"text": "Quoted post text"},
                        },
                    },
                    "media": {
                        "$type": "app.bsky.embed.images#view",
                        "images": [],
                    },
                },
                "indexedAt": "2026-02-15T10:00:00Z",
            }
        }

    def _with_reply_context(self, item, reply_to_handle="carol.bsky.social"):
        if isinstance(item, dict):
            item["reply"] = {
                "parent": {
                    "author": {
                        "handle": reply_to_handle,
                    }
                }
            }
        return item

    def test_extract_quoted_post_info_with_text(self):
        item = self._build_quoted_post()
        info = utils.extract_quoted_post_info(item)
        self.assertIsNotNone(info)
        self.assertEqual(info["kind"], "post")
        self.assertEqual(info["handle"], "bob.bsky.social")
        self.assertEqual(info["text"], "Quoted post text")

    def test_compose_post_includes_quoted_text(self):
        item = self._build_quoted_post()
        result = compose.compose_post(
            item,
            db={},
            settings={"general": {}},
            relative_times=True,
            show_screen_names=False,
            safe=True,
        )
        self.assertIn("Quoting @bob.bsky.social: Quoted post text", result[1])

    def test_template_render_post_includes_quoted_text(self):
        item = self._build_quoted_post()
        rendered = templates.render_post(
            item,
            template="$display_name, $safe_text $date.",
            settings={"general": {}},
            relative_times=True,
            offset_hours=0,
        )
        self.assertIn("Quoting @bob.bsky.social: Quoted post text", rendered)

    def test_extract_quoted_post_info_includes_urls(self):
        item = self._build_quoted_post()
        quoted = item["post"]["embed"]["record"]["record"]
        quoted["value"]["facets"] = [
            {
                "features": [
                    {
                        "$type": "app.bsky.richtext.facet#link",
                        "uri": "https://example.com/full-link",
                    }
                ]
            }
        ]

        info = utils.extract_quoted_post_info(item)
        self.assertIn("https://example.com/full-link", info["urls"])

    def test_find_urls_includes_quoted_urls(self):
        item = self._build_quoted_post()
        quoted = item["post"]["embed"]["record"]["record"]
        quoted["value"]["facets"] = [
            {
                "features": [
                    {
                        "$type": "app.bsky.richtext.facet#link",
                        "uri": "https://example.com/quoted-only",
                    }
                ]
            }
        ]

        urls = utils.find_urls(item)
        self.assertIn("https://example.com/quoted-only", urls)

    def test_compose_post_appends_full_quoted_url(self):
        item = self._build_quoted_post()
        quoted = item["post"]["embed"]["record"]["record"]
        quoted["value"]["text"] = "Mira example.com/..."
        quoted["value"]["facets"] = [
            {
                "features": [
                    {
                        "$type": "app.bsky.richtext.facet#link",
                        "uri": "https://example.com/full-target",
                    }
                ]
            }
        ]

        result = compose.compose_post(
            item,
            db={},
            settings={"general": {}},
            relative_times=True,
            show_screen_names=False,
            safe=True,
        )
        self.assertIn("[https://example.com/full-target]", result[1])

    def test_extract_reply_to_handle_from_record_parent_author(self):
        item = {
            "post": {
                "record": {
                    "text": "Reply text",
                    "reply": {
                        "parent": {
                            "uri": "at://did:plc:parent/app.bsky.feed.post/abc",
                            "author": {"handle": "parent.user"},
                        }
                    },
                }
            }
        }
        handle = utils.extract_reply_to_handle(item)
        self.assertEqual(handle, "parent.user")

    def test_template_render_post_reply_fallback_without_reply_to_variable(self):
        item = {
            "post": {
                "author": {"handle": "alice.bsky.social", "displayName": "Alice"},
                "record": {
                    "text": "Reply body",
                    "reply": {
                        "parent": {
                            "uri": "at://did:plc:parent/app.bsky.feed.post/abc",
                            "author": {"handle": "parent.user"},
                        }
                    },
                },
                "indexedAt": "2026-02-15T10:00:00Z",
            }
        }

        rendered = templates.render_post(
            item,
            template="$display_name, $safe_text $date.",
            settings={"general": {}},
            relative_times=True,
            offset_hours=0,
        )
        self.assertIn("Replying to @parent.user.", rendered)

    def test_extract_reply_to_handle(self):
        item = self._with_reply_context(self._build_quoted_post())
        handle = utils.extract_reply_to_handle(item)
        self.assertEqual(handle, "carol.bsky.social")

    def test_compose_post_includes_reply_context(self):
        item = self._with_reply_context(self._build_quoted_post())
        result = compose.compose_post(
            item,
            db={},
            settings={"general": {}},
            relative_times=True,
            show_screen_names=False,
            safe=True,
        )
        self.assertIn("Replying to @carol.bsky.social:", result[1])

    def test_template_render_post_exposes_reply_to_variable(self):
        item = self._with_reply_context(self._build_quoted_post())
        rendered = templates.render_post(
            item,
            template="$reply_to$text",
            settings={"general": {}},
            relative_times=True,
            offset_hours=0,
        )
        self.assertIn("Replying to @carol.bsky.social.", rendered)


if __name__ == "__main__":
    unittest.main()
