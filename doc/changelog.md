TWBlue Changelog

## changes in this version

* Fixed more issues with streams and reconnections.
* newer updates will indicate the release date in the updater.
* Changes to keystrokes are reflected in keystroke editor automatically.
* In replies with multiple users, if the mention to all checkbox is unchecked, you will see a checkbox per user so you will be able to control who will be mentioned in the reply.
* Fixed a bug that caused duplicated user mentions in replies when the tweet was made with Twishort.
* Retweets should be displayed normally again when the originating tweet is a Twishort's long tweet.
* Changed the way TWBlue saves user timelines in configuration. Now it uses user IDS instead usernames. With user IDS, if an user changes the username, TWBlue still will create his/her timeline. This was not possible by using usernames.

## Changes in version 0.87

* Fixed stream connection errors.
* Now TWBlue can handle properly a reply to the sender without including all other mentioned users.
* Updated translations.
* The status of the mention to all checkbox will be remembered the next time you  reply to multiple users.

## Changes in version 0.86

* Fixed a very important security issue. Now TWBlue will send tweets to twishort without using any other server.
* When you add a comment to a tweet, it will be sent as a quoted tweet, even if your reply plus the original tweet is not exceeding 140 characters.
* Updated windows 10 keymap for reflecting changes made in the last windows 10 build.
* Added last changes in the twitter API.
* When replying, it will not show the twitter username in the text box. When you send the tweet, the username will be added automatically.
* When replying to multiple users, you'll have a checkbox instead a button for mentioning all people. If this is checked, twitter usernames will be added automatically when you send your reply.

## Changes in version 0.85

* Long and quoted tweets should be displayed properly In lists.
* The connection should be more stable.
* Added an autostart option in the global settings dialogue.
* Updated translation.
* Updated russian documentation.
* Tweets in cached database should be loaded properly.
* Added some missed dictionaries for spelling correction.
* Timelines, lists and other buffer should be created in the right order at startup.

## Changes in version 0.84 

* More improvements in quoted and long tweets.
* Updated translations: Russian, Italian, French, Romanian, Galician and Finnish.
* Improvements in the audio uploader module: Now it can handle audio with non-english characters.
* the title of the window should be updated properly when spellcheck, translate or shorten/unshorten URL buttons are pressed.
* the bug that changes the selected tweet in the home timeline shouldn't be happening so often.

## Changes in version 0.82 and 0.83

* If the tweet source (client) is an application with unicode characters (example: российская газета) it will not break the tweet displayer.
* Added a new field for image description in tweet displayer. When available, it will show description for images posted in tweets.
* users can add image descriptions to their photos. When uploading an image, a dialog will show for asking a description.
* Redessigned upload image dialog.
* Fixed photo uploads when posting tweets.
* When getting tweets for a conversation, ignores deleted tweets or some errors, now TWBlue will try to get as much tweets as possible, even if some of these are no longer available.
* Added audio playback from soundcloud.
* Now the session mute option don't makes the screen reader speaks.
* Fixed the direct message dialog. Now it should be displayed properly.
* when a tweet is deleted in twitter, TWBlue should reflect this change and delete that tweet in every buffer it is displayed.
* If your session is broken, TWBlue will be able to remove it automatically instead just crashing.
* audio uploader should display the current progress.
* users can disable the check for updates feature at startup from the general tab, in the global settings dialogue.
* The invisible interface and the window should be synchronized when the client reconnects.
* The documentation option in the systray icon should be enabled.
* In trending buffers, you can press enter for posting a tweet about  the focused trend.
* Updated russian documentation and main program interface (thanks to Natalia Hedlund (Наталья Хедлунд), [\@lifestar](https://twitter.com/lifestar) in twitter)
* updated translations.

## Changes in Version 0.81

* Updated translations
* The updater module has receibed some improvements. Now it includes a Mirror URL for checking updates  if the main URL is not available at the moment. If something is wrong and both locations don't work, the program will start anyway.
* some GUI elements now use keyboard shorcuts for common actions.
* fixed a bug in the geolocation dialog.
* the chicken nugget keymap should work properly.
* Added a new soundpack to the default installation of TWBlue, thanks to [\@Deng90](https://twitter.com/deng90)
* Now the changelog is  written in an html File.
* Added some missed dictionaries in last version for the spell checking feature.
* Trimmed the beginnings of the sounds in the default soundpack. Thanks to [\@masonasons](https://github.com/masonasons)
* Added Opus support for sound playback in TWBlue. Thanks to [\@masonasons](https://github.com/masonasons)
* Added a source field in view tweet dialogue. Thanks to [\@masonasons](https://github.com/masonasons)
* You can load previous items in followers and friend buffers for others.
* The Spell Checker dialogue should not display an error message when you have set "default language" in the global settings dialogue if your language is supported [#168](http://twblue.es/bugs/view.php?id=168)
* Updated romanian translation.
* Some code cleanups.
* The bug reports feature is fully operational again.
* TWBlue should work again for users that contains special characters in windows usernames.
* Added more options for the tweet searches.
* Added play_audio to the keymap editor.
* Windows key is no longer required in the keymap editor
* Switched to the Microsoft translator.
* You can update the current buffer by pressing ctrl+win+shift+u in the default keymap or in the buffer menu.
* Changed some keystrokes in the windows 10 default keymap
* New followers and friends buffer for user timelines.

---
Copyright © 2014-2016, Manuel Cortez.