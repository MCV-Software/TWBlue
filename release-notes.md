## Changelog

In this version, we have focused on expanding content management capabilities within Mastodon. It is now possible to edit sent posts and schedule them for future publication. Additionally, support for reading quoted posts has been implemented, and a new buffer for server announcements is available. On the Core side, visual stability has been prioritized to ensure proper window display, along with an expansion of keyboard shortcuts.

* Core:
    * Fixed a critical issue where buffers were not visible on screen in certain configurations. Now the main window maximizes correctly and visual fixes have been applied to ensure content is accessible. ([#886](https://github.com/mcv-software/twblue/issues/886))
    * Keyboard shortcut improvements: Several shortcuts have been added and fixed to improve efficiency and avoid conflicts:
        * New shortcuts for the autocomplete users manager and menu bar items. ([#842](https://github.com/mcv-software/twblue/issues/842))
        * Added a shortcut for the "Restore Template" button in the template editor dialog. ([#841](https://github.com/mcv-software/twblue/issues/841))
        * New shortcuts for user list and poll dialogs.
        * Resolved a conflict with the 's' key shortcut used for seeking media.
        * Updated the shortcut for marking an account as a "Bot" to avoid conflict with the biography field.
* Mastodon:
    * **Post Editing:** It is finally possible to edit Mastodon posts from TWBlue! You can now correct errors in your posts. ([#859](https://github.com/mcv-software/twblue/issues/859))
        * Safety warning: if you edit a post containing a poll, votes will be reset.
        * Polls are now correctly displayed as attachments within the edit dialog.
    * **Scheduled Posts:** It is now possible to schedule your posts to be published at a later time!
        * Added a "Schedule post" checkbox to the post dialog with date and time pickers.
        * Implemented validation to ensure posts are scheduled at least 5 minutes in the future, as required by Mastodon.
        * The default time is automatically set to 6 minutes in the future for convenience.
    * **Quoted Posts:** Significantly improved the reading and display of quoted posts. TWBlue now structures and reads this content more clearly. ([#860](https://github.com/mcv-software/twblue/issues/860))
    * **Content Cleaning:** Implemented a more robust HTML filter to remove junk elements or unnecessary CSS classes from post text, offering a cleaner reading experience.
    * **Mute Conversation:** Enhanced the "Mute Conversation" feature.
        * Posts from muted conversations will now be visually hidden from the Home timeline immediately upon muting, ensuring a cleaner experience.
        * Added a new invisible shortcut to toggle mute on the focused conversation: `Alt+Windows+Shift+Delete` (Default) or `Control+Alt+Windows+Backspace` (Windows 10/11).
        * The action is also available in the context menu of the post.
    * **Announcements:** Added support for viewing server announcements.
        * New dedicated buffer for "Announcements" where you can read instance-wide news.
        * Added ability to dismiss (mark as read) announcements directly from the buffer.