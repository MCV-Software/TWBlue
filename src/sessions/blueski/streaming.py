# -*- coding: utf-8 -*-
"""
Bluesky polling-based update system for TWBlue.

Since Bluesky's Firehose requires complex CAR/CBOR decoding and filtering
of millions of events, we use a polling approach instead of true streaming.
This matches the existing start_stream() pattern used by buffers.

Events are published via pub/sub to maintain consistency with Mastodon's
streaming implementation.
"""

import logging
import threading
import time
from pubsub import pub

log = logging.getLogger("sessions.blueski.streaming")


class BlueskyPoller:
    """
    Polling-based update system for Bluesky.

    Periodically checks for new notifications and publishes them via pub/sub.
    This provides a similar interface to Mastodon's StreamListener but uses
    polling instead of WebSocket streaming.
    """

    def __init__(self, session, session_name, poll_interval=60):
        """
        Initialize the poller.

        Args:
            session: The Bluesky session instance
            session_name: Unique identifier for this session (for pub/sub routing)
            poll_interval: Seconds between API polls (default 60, min 30)
        """
        self.session = session
        self.session_name = session_name
        self.poll_interval = max(30, poll_interval)  # Minimum 30 seconds to respect rate limits

        self._stop_event = threading.Event()
        self._thread = None
        self._last_notification_cursor = None
        self._last_seen_notification_uri = None

    def start(self):
        """Start the polling thread."""
        if self._thread is not None and self._thread.is_alive():
            log.warning(f"Bluesky poller for {self.session_name} is already running.")
            return

        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._poll_loop,
            name=f"BlueskyPoller-{self.session_name}",
            daemon=True
        )
        self._thread.start()
        log.info(f"Bluesky poller started for {self.session_name} (interval: {self.poll_interval}s)")

    def stop(self):
        """Stop the polling thread."""
        if self._thread is None:
            return

        self._stop_event.set()
        self._thread.join(timeout=5)
        self._thread = None
        log.info(f"Bluesky poller stopped for {self.session_name}")

    def is_alive(self):
        """Check if the polling thread is running."""
        return self._thread is not None and self._thread.is_alive()

    def _poll_loop(self):
        """Main polling loop running in background thread."""
        log.debug(f"Polling loop started for {self.session_name}")

        # Initial delay to let the app fully initialize
        time.sleep(5)

        while not self._stop_event.is_set():
            try:
                self._check_notifications()
            except Exception as e:
                log.exception(f"Error in Bluesky polling loop for {self.session_name}: {e}")

            # Wait for next poll interval, checking stop event periodically
            for _ in range(self.poll_interval):
                if self._stop_event.is_set():
                    break
                time.sleep(1)

        log.debug(f"Polling loop ended for {self.session_name}")

    def _check_notifications(self):
        """Check for new notifications and publish events."""
        if not self.session.logged:
            return

        try:
            api = self.session._ensure_client()
            if not api:
                return

            # Fetch recent notifications
            res = api.app.bsky.notification.list_notifications({"limit": 20})
            notifications = getattr(res, "notifications", [])

            if not notifications:
                return

            # Track which notifications are new
            new_notifications = []
            newest_uri = None

            for notif in notifications:
                uri = getattr(notif, "uri", None)
                if not uri:
                    continue

                # First time running - just record the newest and don't flood
                if self._last_seen_notification_uri is None:
                    newest_uri = uri
                    break

                # Check if we've seen this notification before
                if uri == self._last_seen_notification_uri:
                    break

                new_notifications.append(notif)
                if newest_uri is None:
                    newest_uri = uri

            # Update last seen
            if newest_uri:
                self._last_seen_notification_uri = newest_uri

            # Publish new notifications (in reverse order so oldest first)
            for notif in reversed(new_notifications):
                self._publish_notification(notif)

        except Exception as e:
            log.debug(f"Error checking notifications for {self.session_name}: {e}")

    def _publish_notification(self, notification):
        """Publish a notification event via pub/sub."""
        try:
            reason = getattr(notification, "reason", "unknown")
            log.debug(f"Publishing Bluesky notification: {reason} for {self.session_name}")

            pub.sendMessage(
                "blueski.notification_received",
                notification=notification,
                session_name=self.session_name
            )

            # Also publish specific events for certain notification types
            if reason == "mention":
                pub.sendMessage(
                    "blueski.mention_received",
                    notification=notification,
                    session_name=self.session_name
                )
            elif reason == "reply":
                pub.sendMessage(
                    "blueski.reply_received",
                    notification=notification,
                    session_name=self.session_name
                )
            elif reason == "follow":
                pub.sendMessage(
                    "blueski.follow_received",
                    notification=notification,
                    session_name=self.session_name
                )

        except Exception as e:
            log.exception(f"Error publishing notification event: {e}")


def create_poller(session, session_name, poll_interval=60):
    """
    Factory function to create a BlueskyPoller instance.

    Args:
        session: The Bluesky session instance
        session_name: Unique identifier for this session
        poll_interval: Seconds between polls (default 60)

    Returns:
        BlueskyPoller instance
    """
    return BlueskyPoller(session, session_name, poll_interval)
