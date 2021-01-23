TWBlue Changelog

## changes in this version

* Fixed error when displaying an URL at the end of a line, when the tweet or direct message contained multiple lines. Now the URL should be displayed correctly. ([#305,](https://github.com/manuelcortez/TWBlue/issues/305) [#272,](https://github.com/manuelcortez/TWBlue/issues/272))
* TWBlue has been migrated completely to Python 3 (currently, the software builds with Python 3.8).
* TWBlue should be restarted gracefully. Before, the application was alerting users of not being closed properly every time the application restarted by itself.
* If TWBlue attemps to load an account with invalid tokens (this happens when reactivating a previously deactivated account, or when access to the ap is revoqued), TWBlue will inform the user about this error and will skip the account. Before, the app was unable to start due to a critical error. ([#328,](https://github.com/manuelcortez/TWBlue/issues/328))
* When sending a direct message, the title of the window will change appropiately when the recipient is edited. ([#276,](https://github.com/manuelcortez/TWBlue/issues/276))
* URL'S in user profiles are expanded automatically. ([#275,](https://github.com/manuelcortez/TWBlue/issues/275))
* TWBlue now uses [Tweepy,](https://github.com/tweepy/tweepy) to connect with Twitter. We have adopted this change in order to support Twitter'S API V 2 in the very near future. ([#333,](https://github.com/manuelcortez/TWBlue/issues/337) [#347](https://github.com/manuelcortez/TWBlue/pull/347))
* TWBlue can upload images in Tweets and replies again. ([#240,](https://github.com/manuelcortez/TWBlue/issues/240))
* Fixed the way we use to count characters in Twitter. The new methods in TWBlue take into account special characters and URLS as documented in Twitter. ([#199,](https://github.com/manuelcortez/TWBlue/issues/199) [#315](https://github.com/manuelcortez/TWBlue/issues/315))
* Proxy support now works as expected.
* And more. ([#352,](https://github.com/manuelcortez/TWBlue/issues/352))

## Changes in version 0.95

* TWBlue can open a Tweet or user directly in Twitter. There is a new option in the context menu for people and tweet buffers, and also, the shortcut control+win+alt+Enter will open the focused item in Twitter.
* Some keystrokes were remapped in the Windows 10 Keymap:
    * Read location of a tweet: Ctrl+Win+G. ([#177](https://github.com/manuelcortez/TWBlue/pull/177))
    * Open global settings dialogue: Ctrl+Win+Alt+O.
    * Mute/unmute current session: Control + Windows + Alt + M.
* Fixed an error that was preventing TWBlue to load the direct messages buffer if an user who sent a message has been deleted.
* Added support for playing audios posted in [AnyAudio.net](http://anyaudio.net) directly from TWBlue. Thanks to [Sam Tupy](http://www.samtupy.com/)
* Custom buffer ordering will not be reset every time the application restarts after an account setting has been modified.
* When adding or removing an user from a list, it is possible to press enter in the focused list instead of having to search for the "add" or "delete" button.
* Quoted and long tweets are displayed properly in the sent tweets buffer after being send. ([#253](https://github.com/manuelcortez/TWBlue/issues/253))
* Fixed an issue that was making the list manager keystroke unable to be shown in the keystroke editor. Now the keystroke is listed properly. ([#260](https://github.com/manuelcortez/TWBlue/issues/260))
* The volume slider, located in the account settings of TWBlue, now should decrease and increase value properly when up and down arrows are pressed. Before it was doing it in inverted order. ([#261](https://github.com/manuelcortez/TWBlue/issues/261))
* autoreading has been redesigned to work in a similar way for almost all buffers. Needs testing. ([#221](https://github.com/manuelcortez/TWBlue/issues/221))
* When displaying tweets or direct messages, a new field has been added to show the date when the item has been posted to Twitter.
* Added support for deleting direct messages by using the new Twitter API methods.
* When quoting a retweet, the quote will be made to the original tweet instead of the retweet.
* If the sent direct messages buffer is hidden, TWBlue should keep loading everything as expected. ([#246](https://github.com/manuelcortez/TWBlue/issues/246))
* There is a new soundpack, called FreakyBlue (Thanks to [Andre Louis](https://twitter.com/FreakyFwoof)) as a new option in TWBlue. This pack can be the default in the next stable, so users can take a look and share their opinion in snapshot versions. ([#247](https://github.com/manuelcortez/TWBlue/issues/247))
* There is a new option in the help menu that allows you to visit the soundpacks section in the TWBlue website. ([#247](https://github.com/manuelcortez/TWBlue/issues/247))
* When reading location of a geotagged tweet, it will be translated for users of other languages. ([#251](https://github.com/manuelcortez/TWBlue/pull/251))
* When there are no more items to retrieve in direct messages and people buffers, a message will announce it.
* Fixed an issue reported by some users that was making them unable to load more items in their direct messages.
* It is possible to add a tweet to the likes buffer from the menu bar again.
* Tweets, replies and retweets will be added to sent tweets right after being posted in Twitter.
* Extended Tweets should be displayed properly in list buffers.

## Changes in version 0.94

* Added an option in the global settings dialog to disable the Streaming features of TWBlue. TWBlue will remove all Streaming features after August 16, so this option will give people an idea about how it will be. ([#219](https://github.com/manuelcortez/TWBlue/issues/219))
* Due to Twitter API changes, Switched authorisation method to Pin-code based authorisation. When you add new accounts to TWBlue, you will be required to paste a code displayed in the Twitter website in order to grant access to TWBlue. ([#216](https://github.com/manuelcortez/TWBlue/issues/216))
* In order to comply with latest Twitter changes, TWBlue has switched to the new method used to send and receive direct messages, according to issue [#215.](https://github.com/manuelcortez/twblue/issues/215)
    * The new method does not allow direct messages to be processed in real time. Direct messages will be updated periodically.
* After august 16 or when streaming is disabled, the events buffer will no longer be created in TWBlue.
* You can configure frequency for buffer updates in TWBlue. By default, TWBlue will update all buffers every 2 minutes, but you can change this setting in the global settings dialog. ([#223](https://github.com/manuelcortez/TWBlue/issues/223))
* Added a new tab called feedback, in the account settings dialog. This tab allows you to control whether automatic speech or Braille feedbak in certain events (mentions and direct messages received) is enabled. Take into account that this option will take preference over automatic reading of buffers and any kind of automatic output. ([#203](https://github.com/manuelcortez/TWBlue/issues/203))
* The spell checking dialog now has access keys defined for the most important actions. ([#211](https://github.com/manuelcortez/TWBlue/issues/211))
* TWBlue now Uses WXPython 4.0.1. This will allow us to migrate all important components to Python 3 in the future. ([#207](https://github.com/manuelcortez/TWBlue/issues/207))
* When you quote a Tweet, if the original tweet was posted with Twishort, TWBlue should display properly the quoted tweet. Before it was displaying the original tweet only. ([#206](https://github.com/manuelcortez/TWBlue/issues/206))
* It is possible to filter by retweets, quotes and replies when creating a new filter.
* Added support for playing youtube Links directly from the client. ([#94](https://github.com/manuelcortez/TWBlue/issues/94))
* Replaced Bass with libVLC for playing URL streams.
* the checkbox for indicating whether TWBlue will include everyone in a reply or not, will be unchecked by default.
* You can request TWBlue to save the state for two checkboxes: Long tweet and mention all, from the global settings dialogue.
* For windows 10 users, some keystrokes in the invisible user interface have been changed or merged:
    * control+Windows+alt+F will be used for toggling between adding and removing a tweet to user's likes. This function will execute the needed action based in the current status for the focused tweet.
* TWBlue will show an error if something goes wrong in an audio upload.
* And more. ([#171,](https://github.com/manuelcortez/TWBlue/issues/171) 

## Changes in version 0.93

* A new soundpack has been added to TWBlue. Thanks to [@ValeriaK305](https://twitter.com/ValeriaK305)
* In the Windows 10 keymap, we have changed some default keystrokes as windows now uses some previously assigned shortcuts:
    * For liking a tweet, press Control+Windows+alt+f
    * for opening a trends buffer, press control+Windows+T
* TWBlue has received improvements in some functions for handling extended tweets, long tweets and quoted retweets. It should render some tweets in a better way.
* In the spell checker module, there is a new button that will allow you to add your own words to your personal dictionary so the module won't mark them as mispelled the next time you will check spelling.
* Added filtering capabilities to TWBlue. ([#102](https://github.com/manuelcortez/TWBlue/issues/102))
    * You can create a filter for the current buffer from the buffer menu in the menu bar. At this moment, invisible interface does not have any shorcut for this.
    * You can create filters by word or languages.
    * For deleting already created filters, you can go to the filter manager in the buffer menu and delete the filters you won't need.
* Links should be opened properly in quoted tweets ([#167,](https://github.com/manuelcortez/TWBlue/issues/167) [#184](https://github.com/manuelcortez/TWBlue/issues/184))
* Increased display name limit up to 50 characters in update profile dialog.
* When authorising an account, you will see a dialogue with a cancel button, in case you want to abort the process. Also, NVDA will not be blocked when the process starts. ([#101](https://github.com/manuelcortez/TWBlue/issues/101))
* In the translator module, the list of available languages is fetched automatically from the provider. That means all of these languages will work and there will not be inconsistencies. Also we've removed the first combo box, because the language is detected automatically by Yandex'S API. ([#153](https://github.com/manuelcortez/TWBlue/issues/153))
* Trending topics, searches and conversation buffers will use mute settings set for the session in wich  they were opened. ([#157](https://github.com/manuelcortez/TWBlue/issues/157))
* The Tweet limit is now 280 characters lenght instead 140. It means you can tweet longer tweets. ([#172](https://github.com/manuelcortez/TWBlue/issues/172))
* Per popular request, Status for mention to all and long tweet checkboxes will not be saved in settings. ([#170](https://github.com/manuelcortez/TWBlue/issues/170))
* Fixed a problem that was making TWBlue unable to start if it was being ran in Windows with Serbian language. ([#175](https://github.com/manuelcortez/TWBlue/issues/175))
* Added Danish translation.
* And more. ([#156,](https://github.com/manuelcortez/TWBlue/issues/156) [#163,](https://github.com/manuelcortez/TWBlue/issues/163) [#159,](https://github.com/manuelcortez/TWBlue/issues/159) [#173,](https://github.com/manuelcortez/TWBlue/issues/173) [#174,](https://github.com/manuelcortez/TWBlue/issues/174) [#176,](https://github.com/manuelcortez/TWBlue/issues/176))

## changes in version 0.91 and 0.92

* Fixed incorrect unicode handling when copying tweet to clipboard. ([#150](https://github.com/manuelcortez/TWBlue/issues/150))
* TWBlue will show an error when trying to open a timeline for a suspended user. ([#128](https://github.com/manuelcortez/TWBlue/issues/128))
* Removed TwUp as service as it no longer exists. ([#112](https://github.com/manuelcortez/TWBlue/issues/112))
* Release audio files after uploading them. ([#130](https://github.com/manuelcortez/TWBlue/issues/130))
* Now TWBlue will use Yandex's translation services instead microsoft translator. ([#132](https://github.com/manuelcortez/TWBlue/issues/132))
* SndUp users will be able to upload audio in their account by using their API Key again. ([#134](https://github.com/manuelcortez/TWBlue/issues/134))
* old tweets shouldn't be added as new items in buffers. ([#116,](https://github.com/manuelcortez/TWBlue/issues/116)) ([#133](https://github.com/manuelcortez/TWBlue/issues/133))
* All mentionned users should be displayed correctly in Twishort's long tweets. ([#116,](https://github.com/manuelcortez/TWBlue/issues/116)) ([#135](https://github.com/manuelcortez/TWBlue/issues/135))
* It is possible to select a language for OCR service from the extras panel, in the account settings dialogue. You can, however, set this to detect automatically. OCR should work better in languages with special characters or non-english symbols. ([#107](https://github.com/manuelcortez/TWBlue/issues/107))
* Fixed a problem with JAWS for Windows and TWBlue. Now JAWS will work normally in this update. [#100](https://github.com/manuelcortez/twblue/issues/100)
* And more ([#136,](https://github.com/manuelcortez/TWBlue/issues/136))

## Changes in version 0.90

* Fixed a bug in long tweet parsing that was making TWBlue to disconnect the streaming API. ([#103](https://github.com/manuelcortez/TWBlue/issues/103))
* Now OCR will work in images from retweets. It fixes a bug where TWBlue was detecting images but couldn't apply OCR on them. ([#105](https://github.com/manuelcortez/TWBlue/issues/105))
* TWBlue won't try to load tweets already deleted, made with Twishort. Before, if someone posted a long tweet but deleted it in the Twishort's site, TWBlue was trying to load the tweet and it was causing problems in all the client. ([#113](https://github.com/manuelcortez/TWBlue/issues/113))
* TWBlue shows an error message when you try to view the profile of an user that does not exist or has been suspended. ([#114,](https://github.com/manuelcortez/TWBlue/issues/114) [#115](https://github.com/manuelcortez/TWBlue/issues/115))
* The spellchecker module should select the right language when is set to "user default". ([#117](https://github.com/manuelcortez/TWBlue/issues/117))
* Image description will be displayed in retweets too. ([#119](https://github.com/manuelcortez/TWBlue/issues/119))
* When reading a long tweet, you shouldn't read strange entities anymore. ([#118](https://github.com/manuelcortez/twblue/issues/118))
* TWBlue will not try to load timelines if the user is blocking you. ([#125](https://github.com/manuelcortez/twblue/issues/125))

## Changes in version 0.88 and 0.89

* Fixed more issues with streams and reconnections.
* newer updates will indicate the release date in the updater.
* Changes to keystrokes are reflected in keystroke editor automatically.
* In replies with multiple users, if the mention to all checkbox is unchecked, you will see a checkbox per user so you will be able to control who will be mentioned in the reply.
* Fixed a bug that caused duplicated user mentions in replies when the tweet was made with Twishort.
* Retweets should be displayed normally again when the originating tweet is a Twishort's long tweet.
* Changed the way TWBlue saves user timelines in configuration. Now it uses user IDS instead usernames. With user IDS, if an user changes the username, TWBlue still will create his/her timeline. This was not possible by using usernames.
* Added a new setting in the account settings dialogue that makes TWBlue to show twitter usernames instead the full name.
* Added OCR in twitter pictures. There is a new item in the tweet menu that allows you to extract and display text in images. Also the keystroke alt+Win+o has been added for the same purpose from the invisible interface.
* Now TWBlue will play a sound when the focused tweet contains  images.
* Your own quoted tweets will not appear in the mentions buffer anymore.
* The config file is saved in a different way, it should fix the bug where TWBlue needs to be restarted after the config folder is deleted.
* Mentioning people from friends or followers buffers works again.
* Support for proxy servers has been improved. Now TWBlue supports http, https, socks4 and socks5 proxies, with and without autentication.

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
* Redesigned upload image dialog.
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
* Updated russian documentation and main program interface (thanks to Natalia Hedlund (Наталья Хедлунд), [@lifestar_n](https://twitter.com/lifestar_n) in twitter)
* updated translations.

## Changes in Version 0.81

* Updated translations
* The updater module has received some improvements. Now it includes a Mirror URL for checking updates  if the main URL is not available at the moment. If something is wrong and both locations don't work, the program will start anyway.
* some GUI elements now use keyboard shortcuts for common actions.
* fixed a bug in the geolocation dialog.
* the chicken nugget keymap should work properly.
* Added a new soundpack to the default installation of TWBlue, thanks to [@Deng90](https://twitter.com/deng90)
* Now the changelog is  written in an html File.
* Added some missed dictionaries in last version for the spell checking feature.
* Trimmed the beginnings of the sounds in the default soundpack. Thanks to [@masonasons](https://github.com/masonasons)
* Added Opus support for sound playback in TWBlue. Thanks to [@masonasons](https://github.com/masonasons)
* Added a source field in view tweet dialogue. Thanks to [@masonasons](https://github.com/masonasons)
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
Copyright © 2014-2017, Manuel Cortez.