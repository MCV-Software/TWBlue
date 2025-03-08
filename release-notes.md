## Changelog

In this version, we have focused on providing initial support for Mastodon filters and pinned posts. From TWBlue, it is now possible to initially use filters for posts in most buffers, as well as manage them (create, edit, and delete filters, in addition to adding keywords). A new variable has also been added for post templates in the invisible interface that allows displaying whether a post has been pinned by its author.

* Mastodon:
    * Added filters support to TWBlue. Filters are only implemented in posts for the moment. TWBlue will, depending in the selected settings, hide behind a content warning or completely ignore a post based on filters. Also it is possible to add, delete or edit filters from the buffer menu in the menu bar.
    * A language selector has been added for posting in TWBlue. It is now possible to choose the language in which a post will be made, which will be useful for content filtering and other language-dependent features. The default language can be chosen based on your Mastodon account’s language, the language of the post you’re replying to, or, if no automatic selection is possible, TWBlue’s own language will be used by default.
    * TWBlue now supports announcing (via a new template variable for posts) pinned posts. You can edit your posts template and use the $pinned variable. When reading the post, TWBlue will indicate if the post is pinned. Also, when loading an user timeline, pinned posts will be loaded at the top or bottom of the buffer according to local settings.
    * TWBlue should be able to display all posts in the post displayer dialog.
    * reading long posts in the graphical user interface should work better.
