## Changelog

* Core:
    * The TWBlue website will no longer be available on the twblue.es domain. Beginning in January 2024, TWBlue will live at https://twblue.mcvsoftware.com. Also, we will start releasing versions on [gitHub releases](https://github.com/mcv-software/twblue/releases) so it will be easier to track specific versions.
    * As of the first release of TWBlue in 2024, we will officially stop generating 32-bit (X86) compatible binaries due to the increasing difficulty of generating versions compatible with this architecture in modern Python.
    * TWBlue should be more reliable when checking for updates.
    * If running from source, automatic updates will not be checked as this works only for distribution. ([#540](https://github.com/MCV-Software/TWBlue/pull/540))
    * Fixed the 'report an error' item in the help menu. Now this item redirects to our gitHub issue tracker. ([#524](https://github.com/MCV-Software/TWBlue/pull/524))
* Mastodon:
    * Implemented actions for the notifications buffer on a mastodon instance. Actions can be performed from the contextual menu on every notification, or by using invisible keystrokes. ([#517](https://github.com/mcv-software/twblue/issues/517))
    * Implemented update profile dialog. ([#547](https://github.com/MCV-Software/TWBlue/pull/547))
    * It is possible to display an user profile from the user menu within the menu bar, or by using the invisible keystroke for user details. ([#555](https://github.com/MCV-Software/TWBlue/pull/555))
    * Added possibility to vote in polls. This is mapped to Alt+Win+Shift+V in the invisible keymaps for windows 10/11.
    * Added posts search. Take into account that Mastodon instances should be configured with full text search enabled. Search for posts only include posts the logged-in user has interacted with. ([#541](https://github.com/MCV-Software/TWBlue/pull/541))
    * Added user autocompletion settings in account settings dialog, so it is possible to ask TWBlue to scan mastodon accounts and add people from followers and following buffers. For now, user autocompletion can be used only when composing new posts or replies.
    * TWBlue should be able to ignore deleted direct messages or messages from deleted accounts. Previously, a direct message that no longer existed in the instance caused errors when loading the direct messages buffer and could potentially affect notifications as well.
    * TWBlue should be able to ignore notifications from deleted accounts or posts.
