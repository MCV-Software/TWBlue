TWBlue Changelog

## changes in this version

* In the graphical interface, TWBlue will update menu items, in the menu bar, depending on whether you are focusing a Twitter or Mastodon session. This makes it possible for TWBlue to display the correct terms in each social network. Take into account that there might be unavailable items for the currently active session.
* in the keystroke editor for the invisible interface, TWBlue displays the available shortcuts for the currently active session. Descriptions of those keystrokes are also different for Twitter and mastodon sessions to use correct terms for both networks.
* In the invisible interface, TWBlue will skip sessions that have not been started when using the keyboard shortcut to switch between different accounts.
* Mastodon:
    * Added basic support to notifications buffer. This buffer shows mastodon notifications in real time. Every notification is attached to a kind of object (posts, users, relationships or polls). At the moment, the only supported action for notification is dismissing, which allows you to remove the notification from the buffer (take into account, though, that mention notifications will remove also the mention in its corresponding buffer, due to the way TWBlue reads mentions from mastodon instances).
    * Fixed an issue that was preventing TWBlue to create more than one user timeline during startup.
    * TWBlue will display properly new paragraphs in mastodon posts.

## Changes in version 2022.12.13

* per popular request, We will generate a 32-bit portable version of TWBlue available for Windows 7 operating systems. This version will not be supported in our automatic updater, so in case of using such version, you would need to download it manually every time there is a new update. TWBlue will continue to be available for Windows 7 as long as it is possible to build it using Python 3.7.
* Fixed a couple of bugs that were making TWBlue unable to be opened in some computers, related to our translator module and some COM objects handled incorrectly.
* Fixed an issue that was making TWBlue unable to open in certain computers due to errors related to Win32 API'S.
* Twitter:
    * Fixed a bug that was making sent direct messages to be placed in received direct messages buffer.
    * When quoting a tweet, you can use all 280 characters to send your quoted tweet, as opposed to the 256 characters TWBlue allowed before.
    * Fixed a bug that was making TWBlue unable to reply to direct messages by using the "reply" keystroke.
* Mastodon:
    * Added account settings dialog.
    * Added template editing functionality for mastodon accounts.
    * When a post is edited, TWBlue will update the post object in the buffer to reflect the latest edit.
    * Fixed a small issue that was preventing TWBlue to display some posts in their corresponding dialog.

## Changes in version 2022.12.6

Most of all changes in this release are focused on adding Mastodon support to TWBlue. The features present to handle Twitter should not have been altered in any way. We were not intended to release this version so soon, but unfortunately, Twitter started to present issues in some regions with one particular API endpoint we were using, making impossible for everyone in such regions to use the application. We will release more updates to fix any possible issue regarding Twitter API, but please take into account that this is sometimes an issue happening in Twitter's servers and while we do our best to make TWBlue work despite those problems, you might encounter glitches from time to time.

* TWBlue now builds with Python 3.10.8. ([#493](https://github.com/MCV-Software/TWBlue/issues/493))
    * This change also drops support for Windows 7.
* The TWBlue interface has not been translated yet, as we are releasing this update to fix an important Twitter issue for some regions.
* Twitter sessions should be able to be opened properly again in TWBlue, in regions where it didn't work since last week.
* It is now possible to log in to instances of mastodon, hometown and similar software (Pleroma should work as well, although it has not been tested at this time). From the session manager, clicking on the “new account” button will bring up a menu from which you can select whether you want to log in to Twitter or Mastodon. For instances that have a different character limit than the one set by Mastodon, TWBlue will detect the new limit and adjust the dialogs to allow you to use it correctly.
* Most of the TWBlue GUI has been adapted so that the buffers reflect the change of social network (in mastodon, for example, the buttons to write posts say post instead of tweet). However, the menu bar has not yet been updated. This means that most of the options still refer to Twitter, although they can be used with mastodon accounts. For example, if you select the “tweet” menu in the menu bar, and then select the “Retweet” option, TWBlue will actually do a “boost” if the buffer you are in is a Mastodon account buffer.
* Keystrokes for the invisible interface also refer to terms used in Twitter, but can be applied to Mastodon as well.
* There are some features, within TWBlue, that are not yet compatible with mastodon accounts. These are as follows:
    * User autocompletion.
    * Currently, it is not possible to update account settings for mastodon sessions. However, if you know how to edit configuration files, you can close TWBlue, change your session file with any text editor and restart the application to update what you want.
    * The template editor is not yet available for mastodon accounts.
    * Filters have not yet been implemented in TWBlue mastodon support.
    * User aliases are not implemented yet.
    * It is not possible to view a user’s profile, nor edit your own, for now. However, you can use the keystroke to open the item in the browser when focusing a user to access their profile website. This only works in buffers where users are listed.
    * You cannot manage lists in TWBlue at the moment.
* Most of the buffers planned for mastodon should just work. Among those currently tested are: home (main timeline for the logged-in user), Local (public posts for the instance), federated (public posts for all federating instances), mentions, direct messages, sent posts, favorites, bookmarks, followers, following, blocked users, muted users, user searches and timelines for users.
    *  The difference between favorites and bookmarks is that the author of the post can see who has marked his posts as favorites, but bookmarks are completely private. In any buffer containing mastodon posts, except direct messages, the GUI will display an option to add the post to favorites or bookmarks.
    * Direct messages in mastodon are posts, exactly like normal posts, but with their privacy setting set so that they can only be seen by the accounts that are mentioned. In the direct message buffer, a conversation will appear for each item in the buffer. The conversation represents a thread of messages, but TWBlue can only display the last of the messages sent. This is similar to what happens on platforms like Telegram, where you can only see the list of conversations at the beginning. To see the entire thread of direct messages present in a conversation, you can use the command to open the conversation, or go to the “tweet” menu in the menu bar, and then towards the “view conversation” option. This will create a new conversation buffer that will be located just after the direct messages buffer (for the GUI, the buffer will be located just inside the direct messages buffer in the buffer tree). When a private post appears (whose visibility only allows the mentioned accounts to see it), TWBlue will display that post in the home buffer, in mentions and also will update/create the conversation with that item. This is because Mastodon does not differentiate between a private message and a normal post. You can reply to the post in any buffer to continue the conversation. If you reply to any post, the privacy set in the original post is maintained by default, but can also be changed.
    * The buffer showing the federated timeline has been disabled from settings. This is because on servers that federate with many instances it can load many posts in a very short time. To enable this buffer, for now, edit the TWBlue configuration while the application is closed, and add the “federated” buffer in the option called “buffer_order”. As soon as buffers can be shown or hidden, this process can be done through the GUI.
    * There is a Streaming API that allows the elements for the start buffers, mentions, direct messages, sent posts and followers to appear in real time. This feature is implemented by default and should also just work.
    * Timelines for users only allow to get all posts from users who are in the same instance. For users belonging to other instances, you can get the posts that have been downloaded to your instance since your instance “knows” the remote user.
    * Timelines for followers and following can be fully retrieved only for users belonging to the same instance. Remote users may yield unclear results.
    * You can search by users (by opening a search and selecting the “users” radio button). The search can be done by local users, such as twblue, or by remote users, such as @twblue@maaw.social.
* In all buffers, a maximum of 40 items are retrieved per load, but more can be retrieved by using the option to load more items in the buffer.
* In post buffers, you can do most of the actions already supported in TWBlue (boost, add/remove from favorites or bookmarks, reply, send message to user, open post URL, play audio or video, open post on web, view conversation, open action dialog for user).
* In user buffers, you can send private message to the user, and open user actions dialog, which in turn allows you to follow/unfollow, block/unblock and mute/unmute.
* When writing posts, it is possible to attach up to 4 images, 4 givs, or even a video, poll, or audio. It is also possible to add the “sensitive content” tag to posts, change privacy and write a content warning text. It is possible to create threads using the “add post” button.
* When replying to a post, TWBlue will place the username of all participants in the item you reply to. The privacy options will default to those of the original post.

## Changes in version 2022.8.28

* the user autocompletion feature has been completely rewritten to be easier to use, particularly for people with many followers/following users:
    * In the account settings dialog, there's a button that opens up a new dialog that allows you to "scan" your account in order to add all users from your followers/following list. This process will read your data directly from Twitter and depending in the amount of people you have in your account it might take too many API calls. Please use it with caution. You can, for example, do the process separately for your followers/following people so it will be easier to handle, in case you have a massive amount of people. If TWBlue is unable to complete the scan, you will see an error and will be prompted to try again in 15 minutes, once your API calls have refreshed.
    * It is possible to use the user autocompletion functionality in dialogs where you can select an user, for example when adding or removing someone from a list, or displaying lists for someone.
* Implemented a new setting, available in the account settings dialog, that allows to hide emojis in twitter usernames.
* TWBlue should be able to sort conversations in a more logical way. This should make it easier to follow a long thread in Twitter.
* When opening a thread, TWBlue should be able to load the right conversation if the original tweet from where the thread was loaded was a retweet.
* TWBlue will restart the Streaming subsystem every time there are changes to followed, muted or blocked users within the application.
* Fixed error when attempting to mention an user by using the "mention" button in any people buffer. Now tweets should be posted normally.
* Fixed error when loading other user lists. ([#465](https://github.com/MCV-Software/TWBlue/issues/465))
* Fixed an issue that was making TWBlue to display incorrectly some retweets of quoted tweets.
* If TWBlue is unable to open a timeline for someone who has blocked you, this will be reported in a dialog. ([#485,](https://github.com/mcv-software/twblue/issues/485))
* Added "find a string in the currently focused buffer" action into Windows 10 and windows 11 keymap. ([#476](https://github.com/MCV-Software/TWBlue/pull/476))

## changes in version 22.2.23

* We have added Experimental support for templates in the invisible interface. The GUI will remain unchanged for now:
    * Each object (tweet, received direct message, sent direct message and people) has its own template in the settings. You can edit those templates from the account settings dialog, in the new "templates" tab.
    * Every template is composed of the group of variables you want to display for each object. Each variable will start with a dollar sign ($) and cannot contain spaces or special characters. Templates can include arbitrary text that will not be processed. When editing the example templates, you can get an idea of the variables that are available for each object by using the template editing dialog. When you press enter on a variable from the list of available variables, it will be added to the template automatically. When you try to save a template, TWBlue will warn you if the template is incorrectly formatted or if it includes variables that do not exist in the information provided by objects. It is also possible to return to default values from the same dialog when editing a template.
    * TWBlue can display image descriptions within Tweet templates. For that, you can use the $image_description variable in your template.
* We have restored conversation and threads support powered by Twitter API V2 thanks to a set of improvements we have done in the application, as well as more generous limits to Tweet monthly cap by Twitter.
* In the Windows 11 Keymap, the default shortcut to open the keystrokes editor is now CTRL+Alt+Windows+K to avoid conflicts with the new global mute microphone shortcut.
* TWBlue show display properly HTML entities in tweet's text.
* TWBlue should no longer load old tweets in buffers.
* Fixed issue when uploading attachments (images, videos or gif files) while sending tweets or replies.
* Fixed an error that was making TWBlue to ask for a restart after saving account settings, even if such restart was not required. ([#413,](https://github.com/manuelcortez/TWBlue/issues/413))

## Changes in version 2021.11.12

* Now it is possible to create a tweet from a trending topics buffer again.
* TWBlue now includes a completely new set of dialogs to handle tweeting, replying and sending direct messages that takes advantage of more Twitter features.
    * It is possible to add videos in tweets and direct messages by using the new "add" button, located in every dialog where  media can be added. Twitter suggests to add videos from 5 seconds up to 2 minutes lenght, in mp4 format (video Codec H.264 and audio codec AAC). Currently, TWBlue does not check if the uploaded video complies with Twitter media requirements. You can add only a video in a tweet or direct message. No other kind of media can be added after a video is in a tweet. If the video was unable to be uploaded successfully, the tweet or direct message won't be created.
    * Now you can add a poll to tweets. Polls can have up to 4 different options and allow voting up to 7 days after being created. Take into account, though, that currently TWBlue does not support reading polls in tweets.
    * TWBlue now support threads while creating a new tweet. There is a new button, called add tweet which will add the current tweet to the thread and will allow you to write another tweet in the thread. Every tweet might include media (up to 4 photos, or one GIF image or a video) or up to one poll.
    * Some functionality was removed from tweet dialogs within TWBlue. Particularly, URL shorteners and long tweets via Twishort. You still can read long tweets posted via Twishort, though.

## Changes in version 2021.11.07

* TWBlue should retrieve tweets from threads and conversations in a more reliable way. Tweets in the same thread (made by the same author) will be sorted correctly, although replies to the thread (made by different people) may not be ordered in the same way they are displayed in Twitter apps. ([#417](https://github.com/manuelcortez/TWBlue/issues/417))
* When creating a filter, TWBlue will show an error if user has not provided a name for the filter. Before, unnamed filters were a cause of config breaks in the application.
* It is again possible to read the changelog for TWBlue from the help menu in the menu bar.
* fixed a bug when clearing the direct messages buffer. ([#418](https://github.com/manuelcortez/TWBlue/issues/418))
* fixed an issue that was making TWBlue to show incorrectly titles for trending topic buffers upon startup. ([#421](https://github.com/manuelcortez/TWBlue/issues/421))
* fixed an issue that was making users of the graphical user interface to delete a buffer if a trends buffer was opened in the same session.
* Updated Spanish, Japanese and french translations.

## Changes in Version 2021.10.30

* Fixed many errors in the way we compile TWBlue, so users of 64 bits systems and particularly windows 7 users would be able to install TWBlue again. In case of issues with versions prior to 2021.10.30, please remove everything related to TWBlue (except configs) and reinstall the version 2021.10.30 to fix any possible error. This step won't be needed again in 23 months. ([#416,](https://github.com/manuelcortez/TWBlue/issues/416), [#415,](https://github.com/manuelcortez/TWBlue/issues/415))
* fixed an issue that was making impossible to manually add an user to the autocomplete users database.
* Started to improve support to conversations by searching for conversation_id.

## changes in version 2021.10.27

* Added an user alias manager, located in the application menu in the menu bar. From this dialog, it is possible to review, add, edit or remove user aliases for the current account. ([#401](https://github.com/manuelcortez/TWBlue/issues/401))
* TWBlue now closes the VLC player window automatically when a video reaches its end. ([#399](https://github.com/manuelcortez/TWBlue/issues/399))
* After a lot of time, TWBlue now uses a new default Soundpack, called FreakyBlue. This soundpack will be set by default in all new sessions created in the application. Thanks to [Andre Louis](https://twitter.com/FreakyFwoof) for the pack. ([#247](https://github.com/manuelcortez/TWBlue/issues/247))
* When reading a tweet, if the tweet contains more than 2 consecutive mentions, TWBlue will announce how many more users the tweet includes, as opposed to read every user in the conversation. You still can display the tweet to read all users.
* In the tweet displayer, It is possible to copy a link to the current tweet or person by pressing a button called "copy link to clipboard".
* Added a keymap capable to work under Windows 11. ([#391](https://github.com/manuelcortez/TWBlue/pull/391))
* Added user aliases to TWBlue. This feature allows you to rename user's display names on Twitter, so the next time you'll read an user it will be announced as you configured. For adding an alias to an user, select the "add alias" option in the user menu, located in the menu bar. This feature works only if you have set display screen names unchecked. Users are displayed with their display name in people buffers only. This action is supported in all keymaps, although it is undefined by default. ([#389](https://github.com/manuelcortez/TWBlue/pull/389))
* There are some changes to the autocomplete users feature:
    * Now users can search for twitter screen names or display names in the database.
* It is possible to undefine keystrokes in the current keymap in TWBlue. This allows you, for example, to redefine keystrokes completely.
* We have changed our Geocoding service to the Nominatim API from OpenStreetMap. Addresses present in tweets are going to be determined by this service, as the Google Maps API now requires an API key. ([#390](https://github.com/manuelcortez/TWBlue/issues/390))
* Added a limited version of the Twitter's Streaming API: The Streaming API will work only for tweets, and will receive tweets only by people you follow. Protected users are not possible to be streamed. It is possible that during high tweet traffic, the Stream might get disconnected at times, but TWBlue should be capable of detecting this problem and reconnecting the stream again. ([#385](https://github.com/manuelcortez/TWBlue/pull/385))
* Fixed an issue that made TWBlue to not show a dialog when attempting to show a profile for a suspended user. ([#387](https://github.com/manuelcortez/TWBlue/issues/387))
* Added support for Twitter audio and videos: Tweets which contains audio or videos will be detected as audio items, and you can playback those with the regular command to play audios. ([#384,](https://github.com/manuelcortez/TWBlue/pull/384))
* We just implemented some changes in the way TWBlue handles tweets in order to reduce its RAM memory usage [#380](https://github.com/manuelcortez/TWBlue/pull/380):
    * We reduced the tweets size by storing only the tweet fields we currently use. This should reduce tweet's size in memory for every object up to 75%.
    * When using the cache database to store your tweets, there is a new setting present in the account settings dialog, in the general tab. This setting allows you to control whether TWBlue will load the whole database into memory (which is the current behaviour) or not.
        * Loading the whole database into memory has the advantage of being extremely fast to access any element (for example when moving through tweets in a buffer), but it requires more memory as the tweet buffers grow up. This should, however, use less memory than before thanks to the optimizations performed in tweet objects. If you have a machine with enough memory, this should be a good option for your case.
        * If you uncheck this setting, TWBlue will read the whole database from disk. This is significantly slower, but the advantage of this setting is that it will consume almost no extra memory, no matter how big is the tweets dataset. Be ware, though, that TWBlue might start to feel slower when accessing elements (for example when reading tweets) as the buffers grow up. This setting is suggested for computers with low memory or for those people not wanting to keep a really big amount of tweets stored.
* Changed the label in the direct message's text control so it will indicate that the user needs to write the text there, without referring to any username in particular. ([#366,](https://github.com/manuelcortez/TWBlue/issues/366))
* TWBlue will take Shift+F10 again as the contextual menu key in the list of items in a buffer. This stopped working after we have migrated to WX 4.1. ([#353,](https://github.com/manuelcortez/TWBlue/issues/353))
* TWBlue should render correctly retweets of quoted tweets. ([#365,](https://github.com/manuelcortez/TWBlue/issues/365))
* Fixed an error that was causing TWBlue to be unable to output to screen readers at times. ([#369,](https://github.com/manuelcortez/TWBlue/issues/369))
* Fixed autocomplete users feature. ([#367,](https://github.com/manuelcortez/TWBlue/issues/367))
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
* Changed translation service from yandex.translate to Google Translator. ([#355,](https://github.com/manuelcortez/TWBlue/issues/355))
* Improved method to load direct messages in the buffers. Now it should be faster due to less calls to Twitter API performed from the client.
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
Copyright © 2014-2021, Manuel Cortez.