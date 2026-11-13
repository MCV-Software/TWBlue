## Changelog

This release adds Bluesky support and improves profile dialogs, keyboard navigation, and the reliability of Mastodon sessions.

* Core:
    * Added more actions to the keystroke editor, including account management, filters, aliases, community timelines, favorites timelines, post pinning, and media seeking. These actions can be assigned custom shortcuts.
    * Added runtime diagnostics when running TWBlue from source, showing memory, CPU, thread, session, and buffer counts.
    * Changed profile dialogs to announce successful actions without an additional modal confirmation dialog. Blocking and unfollowing ask for confirmation before the action is performed.
    * Changed profile updates after user actions to preserve the current window and focus. When an action button is replaced, focus moves to its inverse action.
    * Changed profile queries, image downloads, and user actions to run in the background. Responses arriving after a profile dialog is closed are ignored.
    * Fixed post-action refresh failures clearing the visible profile or losing focus. TWBlue now reports that the action completed but the profile could not be refreshed, without repeating the action.
    * Fixed list insertion and selection problems that could make the displayed order differ from the post read or acted on in the invisible interface, or announce an invalid position such as "0 of 1". ([#1038](https://github.com/MCV-Software/TWBlue/pull/1038), [#1002](https://github.com/MCV-Software/TWBlue/pull/1002))
    * Fixed overlapping manual buffer updates and unnecessary duplicate initialization of buffers.
    * Fixed focus and keyboard navigation problems in post, poll, template, alias, user-list, and configuration dialogs, as well as missing options in the poll voting dialog. ([#1037](https://github.com/MCV-Software/TWBlue/pull/1037))
    * Fixed an "Unknown image format" error when viewing or updating profiles whose images use formats such as WebP. ([#977](https://github.com/MCV-Software/TWBlue/issues/977), [#978](https://github.com/MCV-Software/TWBlue/pull/978))
    * Changed the internal organization of profile views, controllers, and session operations, with automated tests for profile actions, account settings, persistence, and focus handling.
* Mastodon:
    * Added the ability to send quoted posts from the post context menu or the Boost dialog. ([#858](https://github.com/MCV-Software/TWBlue/issues/858))
    * Added pinning and unpinning of your own posts from the context menu or a custom keyboard shortcut.
    * Changed the profile dialog to offer an experience consistent with Bluesky, while retaining account fields, registration date, and private-account, bot, and discoverability information. These profile improvements also apply to GoToSocial accounts.
    * Added direct follow, mute, and block controls and their inverse actions to the profile dialog, according to the account relationship, including an option to cancel a pending follow request.
    * Changed handling of sign-in failures: TWBlue reports the problem and lets you choose whether to keep the account configuration.
    * Fixed ordering and pagination around pinned posts, which could cause old content to be fetched again or appear in the wrong position.
    * Fixed character counting when composing posts, using Mastodon's counting rules.
    * Fixed HTML entity decoding when editing posts. ([#893](https://github.com/mcv-software/twblue/issues/893))
    * Fixed duplicated recipient mentions in direct messages. ([#1024](https://github.com/MCV-Software/TWBlue/pull/1024))
    * Fixed duplicate streaming connections and improved their cleanup when reconnecting or closing a session.
* Bluesky:
    * Added support for adding and managing Bluesky accounts using a handle and an App Password, alongside existing Mastodon and GoToSocial accounts. ([#912](https://github.com/MCV-Software/TWBlue/pull/912))
    * Added Home (accounts you follow), Discover, Mentions, Notifications, Sent, Likes, Followers, Following, and Blocked Users buffers, as well as user timelines and searches.
    * Added posting, replies, quotes, reposts, likes, and deletion of your own posts. Posts can include images with alternative text and a selected language.
    * Added conversation views and chats, including sending and reading messages through the invisible interface. Open chats are grouped under the Chats buffer.
    * Added profile viewing and user actions: follow, unfollow, mute, unmute, block, and unblock.
    * Changed the reading of replies, quoted posts, quoted links, and image descriptions to include their context more clearly. Default post templates now include image descriptions while preserving custom templates. ([#912](https://github.com/MCV-Software/TWBlue/pull/912), [#959](https://github.com/MCV-Software/TWBlue/pull/959))
    * Changed replies and direct messages to no longer start with an unnecessary prefilled @handle. Replies retain their parent and conversation context without requiring a textual mention. ([#1024](https://github.com/MCV-Software/TWBlue/pull/1024))
    * Fixed duplicated conversation buffers when opening an existing chat or thread. ([#1002](https://github.com/MCV-Software/TWBlue/pull/1002))
    * Fixed duplicated posts in conversation views, repeated refreshes, and incorrect selection announcements in chats. Conversations opened from different posts now retain their own content. ([#1002](https://github.com/MCV-Software/TWBlue/pull/1002))
    * Fixed sender names that appeared as unknown in chats and reduced false new-message notifications.
    * Fixed problems with opening URLs and searching from shortcuts.
    * Fixed the Home buffer remaining empty when posts contain image galleries. ([#959](https://github.com/MCV-Software/TWBlue/pull/959))
    * Fixed account credentials being saved before sign-in was verified. Credentials are now saved only after a successful sign-in.
    * Fixed conversion of older account settings not being retried after a saving failure.
