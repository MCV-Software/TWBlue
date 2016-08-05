Documentation for TWBlue - 0.84

## Table of contents

[TOC]

## Warning!

You are reading documentation produced for a program still in development. The object of this manual is to explain some details of the operation of the program. Bear in mind that as the software is in the process of active development, parts of this user guide may change in the near future, so it is advisable to keep checking from time to time to avoid missing important information.

If you want to see what has changed from the previous version, [read the list of updates here.](changes.html)

## Introduction

TWBlue is an application to make Twitter simple and fast, while using as few resources as possible. With TWBlue, you can do things like the following:

* Tweet, reply to, retweet and delete tweets,
* Mark and unmark a tweet as favourite,
* Send and delete direct messages,
* See your friends and followers,
* Follow, unfollow, report and block a user,
* Open a user's timeline to see their tweets separately,
* Open URLs from a tweet or direct message,
* Play several types of audio files from addresses,
* And more.

## Usage

Twitter is a social networking or micro-blogging tool which allows you to compose short status updates of your activities in 140 characters or less. Twitter is a way for friends, family and co-workers to communicate and stay connected through the exchange of quick, frequent messages. You can restrict delivery of updates to those in your circle of friends or, by default, allow anyone to access them.

You can monitor the status of updates from your friends, family or co-workers (known as following), and they in turn can read any updates you create, (known as followers). The updates are referred to as Tweets. The Tweets are posted to your Twitter profile or Blog and are searchable using Twitter Search.

In order to use TWBlue, you must first have created an account on the Twitter website. The process for signing up for a Twitter account is very accessible. During the account registration, you will need to choose a Twitter username. This serves two purposes. This is the method through which people will comunicate with you, but most importantly, your username and password will be required to connect TWBlue to your Twitter account. We suggest you choose a username which is memorable both to you and the people you hope will follow you.

We'll start from the premise that you have a Twitter account with its corresponding username and password.

### Authorising the application

First of all, it's necessary to authorise the program so it can access your Twitter account and act on your behalf. The authorisation process is quite simple, and the program never retains data such as your password. In order to authorise the application, you just need to run the main executable file, called TWBlue.exe (on some computers it may appear simply as TWBlue if Windows Explorer is not set to display file extensions). We suggest you may like to place a Windows shortcut on your Desktop pointing to this executable file for quick and easy location.

You can log into several Twitter accounts simultaneously. The program refers to each Twitter account you have configured as a "Session". If this is the first time you have launched TWBlue, and if no Twitter session exists, you will see the Session Manager. This dialogue box allows you to authorise as many accounts as you wish. If you press the Tab key to reach the "new account" button and activate it by pressing the Space Bar, a dialogue box will advise you that your default internet browser will be opened in order to authorise the application and you will be asked if you would like to continue. Activate the "yes" Button by pressing the letter "Y" so the process may start.

Your default browser will open on the Twitter page to request authorisation. Enter your username and password into the appropriate edit fields if you're not already logged in, select the authorise button, and press it.

Once you've authorised your twitter account, the website will redirect you to a page which will notify you that TWBlue has been authorised successfully. Now you are able to close the page by pressing ALT+F4 which will return you to the Session Manager. On the session list, you will see a new item temporarily called "Authorised account x" -where x is a number. The session name will change once you open that session.

To start running TWBlue, press the Ok button in the Session Manager dialogue. By default, the program starts all the configured sessions automatically, however, you can change this behavior.

If all went well, the application will start playing sounds, indicating your data is being updated.

When the process is finished, by default the program will play another sound, and the screen reader will say "ready" (this behaviour can be configured).

## General concepts

Before starting to describe TWBlue's usage, we'll explain some concepts that will be used extensively throughout this manual.

### Buffer

A buffer is a list of items to manage the data which arrives from Twitter, after being processed by the application. When you configure a new session on TWBlue and start it, many buffers are created. Each of them may contain some of the items which this program works with: Tweets, direct messages, users, trends or events. According to the buffer you are focusing, you will be able to do different actions with these items.

The following is a description for every one of TWBlue's buffers and the kind of items they work with.

* Home: this shows all the tweets on the main timeline. These are the tweets by users you follow.
* Mentions: if a user, whether you follow them or not, mentions you on Twitter, you will find it in this list.
* Direct messages: here you will find the private direct messages you exchange with users who follow you , or with any user, if you allow direct messages from everyone (this setting is configurable from Twitter). This list only shows received messages.
* Sent direct messages: this buffer shows all the direct messages sent from your account.
* Sent tweets: this shows all the tweets sent from your account.
* Favourites: here you will see all the tweets you have favourited.
* Followers: when users follow you, you'll be able to see them on this buffer, with some of their account details.
* Friends: the same as the previous buffer, but these are the users you follow.
* User timelines: these are buffers you may create. They contain only the tweets by a specific user. They're used so you can see the tweets by a single person and you don't want to look all over your timeline. You may create as many as you like.
* Events: An event is anything that happens on Twitter, such as when someone follows you, when someone adds or removes one of your tweets from their favourites list, or when you subscribe to a list. There are many more, but the program shows the most common ones in the events buffer so that you can easily keep track of what is happening on your account.
* Lists: A list is similar to a user timeline, except that you can configure it to contain tweets from multiple users.
* Search: A search buffer contains the results of a search operation.
* User favourites: You can have the program create a buffer containing tweets favourited by a particular user.
* Trending Topics: a trend buffer shows the top ten most used terms in a geographical region. This region may be a country or a city. Trends are updated every five minutes.

If a tweet contains a URL, you can press enter in the GUI or Control + Windows + Enter in the invisible interface to open it. If it contains audio, you can press Control + Enter or Control + Windows + Alt + Enter to play it, respectively. TWBlue will play a sound if the tweet contains the \#audio hashtag, but there may be tweets which contain audio without this. Finally, if a tweet contains geographical information, you can press Control + Windows + G in the invisible interface to retrieve it.

### Username fields

These fields accept a Twitter username (without the at sign) as the input. They are present in the send direct message and the user actions dialogue boxes. Those dialogues will be discussed later. The initial value of these fields depends on where they were opened from. They are prepopulated with the username of the sender of the focused tweet (if they were opened from the home and sent timelines, from users' timelines or from lists), the sender of the focused direct message (if from the received or sent direct message buffers) or in the focused user (if from the followers' or friends' buffer). If one of those dialogue boxes is opened from a tweet, and if there are more users mentioned in it, you can use the arrow keys to switch between them. Alternatively, you can also type a username.

## The program's interfaces

### The graphical user interface (GUI)

The graphical user interface of TWBlue consists of a window containing:

* a menu bar accomodating five menus (application, tweet, user, buffer and help);
* One tree view,
* One list of items
* Four buttons in most dialogs: Tweet, retweet , reply and direct message.

The actions that are available for every item will be described later.

In summary, the GUI contains two core components. These are the controls you will find while pressing the Tab key within the program's interface, and the different elements present on the menu bar.

#### Buttons in the application

* Tweet: this button opens up a dialogue box to write your tweet. The message must not exceed 140 characters. If you write past this limit, a sound will play to warn you. Note that the character count is displayed in the title bar. You may use the shorten and expand URL buttons to comply with the character limit. You can upload a picture, check spelling, attach audio or translate your message by selecting one of the available buttons in the dialogue box. In addition, you can autocomplete the entering of users by pressing Alt + A or the button for that purpose if you have the database of users configured. Press enter to send the tweet. If all goes well, you'll hear a sound confirming it. Otherwise, the screen reader will speak an error message in English describing the problem.
* Retweet: this button retweets the message you're reading. After you press it, if you haven't configured the application not to do so, you'll be asked if you want to add a comment or simply send it as written. If you choose to add a comment, and if the original tweet plus the comment exceeds 140 characters, you will be asked if you want to post it as a comment with a mention to the original user and a link to the originating tweet.
* Reply: when you're viewing a tweet, you can reply to the user who sent it by pressing this button. A dialogue will open up similar to the one for tweeting, but with the name of the user already filled in (for example @user) so you only need to write your message. If there are more users referred to in the tweet, you can press shift-tab and activate the mention all users button. When you're on the friends or followers lists, the button will be called mention instead.
* Direct message: exactly like sending a tweet, but it's a private message which can only be read by the user you send it to. Press shift-tab to see the recipient. If there were other users mentioned in the tweet you were reading, you can arrow up or down to choose which one to send it to, or write the username yourself without the at sign.

Bear in mind that buttons will appear according to which actions are possible on the list you are browsing. For example, on the home timeline, mentions, sent, favourites and user timelines you will see the four buttons, while on the direct messages list you'll only get the direct message and tweet buttons, and on friends and followers lists the direct message, tweet, and mention buttons will be available.

#### Menus

Visually, Towards the top of the main application window, can be found a menu bar which contains many of the same functions as listed in the previous section, together with some additional items. To access the menu bar, press the alt key. You will find five menus listed: application, tweet, user, buffer and help. This section describes the items on each one of them.

##### Application menu

* Manage accounts: Opens a window with all the sessions configured in TWBlue, where you can add new sessions or delete the ones you've already created.
* Update profile: opens a dialogue where you can update your information on Twitter: name, location, website and bio. If you have already set this up the fields will be prefilled with the existing information. Also, you can upload a photo to your profile.
* Hide window: turns off the Graphical User Interface. Read the section on the invisible interface for further details.
* Search: shows a dialogue box where you can search for tweets or users on Twitter.
* Lists Manager: This dialogue box allows you to manage your Twitter lists. In order to use them, you must first create them. Here, you can view, edit, create, delete or, optionally, open them in buffers similar to user timelines.
* Edit keystrokes: this opens a dialogue where you can see and edit the shortcuts used in the invisible interface.
* Account settings: Opens a dialogue box which lets you customize settings for the current account.
* Global settings: Opens a dialogue which lets you configure settings for the entire application.
* Exit: asks whether you want to exit the program. If the answer is yes, it closes the application. If you do not want to be asked for confirmation before exiting, uncheck the checkbox from the global settings dialogue box.

##### Tweet menu

* You will first find the items to tweet, reply and retweet, which are equivalent to the buttons with the same name.
* Add to favourites: marks the tweet you're viewing as a favourite.
* Remove from favourites: removes the tweet from your favourites, but not from Twitter.
* Show tweet: opens up a dialogue box where you can read the tweet, direct message, friend or follower which has focus. You can read the text with the arrow keys. It's a similar dialog box as used for composing tweets, without the ability to send the tweet, file attachment and autocompleting capabilities. It does however include a retweets and favourites count. If you are in the followers or the friends list, it will only contain a read-only edit box with the information in the focused item and a close button.
* View address: If the selected tweet has geographical information, TWBlue may display a dialogue box where you can read the tweet address. This address is retrieved by sending the geographical coordinates of the tweet to Google maps.
* View conversation: If you are focusing a tweet with a mention, it opens a buffer where you can view the whole conversation.
* Delete: permanently removes the tweet or direct message which has focus from Twitter and from your lists. Bear in mind that Twitter only allows you to delete tweets you have posted yourself.

##### User menu

* Actions: Opens a dialogue where you can interact with a user. This dialogue box will be populated with the user who sent the tweet or direct message in focus or the selected user in the friends or followers buffer. You can edit it or leave it as is and choose one of the following actions:
 * Follow: Follows a user. This means you'll see his/her tweets on your home timeline, and if he/she also follows you, you'll be able to exchange direct messages. You may also send / receive direct messages from each other if you have configured the option to allow direct messages from anyone.
 * Unfollow: Stops following a user, which causes you not being able to see his/her tweets on your main timeline neither exchanging direct messages, unless they have enabled receiving direct messages from anyone.
 * Mute: While muting someone, TWBlue won't show you nor his/her tweets on your main timeline; neither will you see that person's mentions. But you both will be able to exchange direct messages. The muted user is not informed of this action.
 * Unmute: this option allows TWBlue to display the user's tweets and mentions again.
 * Block: Blocks a user. This forces the user to unfollow you .
 * Unblock: Stops blocking a user.
 * Report as spam: this option sends a message to Twitter suggesting the user is performing prohibited practices on the social network.
 * Ignore tweets from this client: Adds the client from which the focused tweet was sent to the ignored clients list.
* View timeline: Lets you open a user's timeline by choosing the user in a dialog box. It is created when you press enter. If you invoke this option relative to a user that has no tweets, the operation will fail. If you try creating an existing timeline the program will warn you and will not create it again.
* Direct message: same action as the button.
* Add to List: In order to see someone's tweets in one or more of your lists, you must add them first. In the dialogue box that opens after selecting the user, you will be asked to select the list you wish to add the user to. Thereafter, the list will contain a new member and their tweets will be displayed there.
* Remove from list: lets you remove a user from a list.
* View lists: Shows the lists created by a specified user.
* Show user profile: opens a dialogue with the profile of the specified user.
* View favourites: Opens a buffer where you can see the tweets which have been favourited by a particular user.

##### Buffer menu

* New trending topics buffer: This opens a buffer to get the worlwide trending topics or those of a country or a city. You'll be able to select from a dialogue box if you wish to retrieve countries' trends, cities' trends or worldwide trends (this option is in the cities' list) and choose one from the selected list. The trending topics buffer will be created once the "OK" button has been activated within the dialogue box. Remember this kind of buffer will be updated every five minutes.
* Load previous items: This allows more items to be loaded for the specified buffer.
* Mute: Mutes notifications of a particular buffer so you will not hear when new tweets arrive.
* autoread: When enabled, the screen reader or SAPI 5 Text to Speech voice (if enabled) will read the text of incoming tweets. Please note that this could get rather chatty if there are a lot of incoming tweets.
* Clear buffer: Deletes all items from the buffer.
* Destroy: dismisses the list you're on.

##### Help menu

* Documentation: opens up this file, where you can read some useful program concepts.
* Sounds tutorial: Opens a dialog box where you can familiarize yourself with the different sounds of the program.
* What's new in this version?: opens up a document with the list of changes from the current version to the earliest.
* Check for updates: every time you open the program it automatically checks for new versions. If an update is available, it will ask you if you want to download the update. If you accept, the updating process will commence. When complete, TWBlue will be restarted. This item checks for new updates without having to restart the application.
* Report an error: opens up a dialogue box to report a bug by completing a small number of fields. Pressing enter will send the report. If the operation doesn't succeed the program will display a warning.
* TWBlue's website: visit our [home page](http://twblue.es) where you can find all relevant information and downloads for TWBlue and become a part of the community.
* About TWBlue: shows the credits of the program.

### The invisible user interface

The invisible interface, as its name suggests, has no graphical window and works directly with screen readers such as JAWS for Windows, NVDA and System Access. This interface is disabled by default, but you can enable it by pressing Control + M. It works similarly to TheQube and Chicken Nugget. Its shortcuts are similar to those found in these two clients. In addition, the program has builtin support for the keymaps for these applications, configurable through the global settings dialogue. By default, you cannot use this interface's shortcuts in the GUI, but you can configure this in the global settings dialogue.

The next section contains a list of keyboard shortcuts for both interfaces. Bear in mind that we will only describe the default keymap.

## Keyboard shortcuts

### Shortcuts of the graphical user interface (GUI)

* Enter: Open URL.
* Control + Enter: Play audio.
* Control + M: Hide the GUI.
* Control + N: Compose a new tweet.
* Control + R: Reply / mention.
* Control + Shift + R: Retweet.
* Control + D: Send a direct message.
* control + F: Add tweet to favourites.
* Control + Shift + F: Remove a tweet from favourites.
* Control + S: Open the user actions dialogue.
* Control + Shift + V: Show tweet.
* Control + Q: Quit this program.
* Control + I: Open user timeline.
* Control + Shift + i: Destroy buffer.
* F5: Increase volume by 5%.
* F6: Decrease volume by 5%.
* Control + P: Edit your profile.
* Control + Delete: Delete a tweet or direct message.
* Control + Shift + Delete: Empty the current buffer.

### Shortcuts of the invisible interface (default keymap)

* Control + Windows + Up Arrow: moves to the previous item in the buffer.
* Control + Windows + Down Arrow: moves to the next item in the buffer.
* Control + Windows + Left Arrow: Move to the previous buffer.
* Control + Windows + Right Arrow: Move to the next buffer.
* Control + Windows + Shift + Left: Focus the previous session.
* Control + Windows + Shift + Right: Focus the next session.
* Control + Windows + C: View conversation.
* Control + Windows + Enter: Open URL.
* Control + Windows + ALT + Enter: Play audio.
* Control + Windows + M: Show or hide the GUI.
* Control + Windows + N: New tweet.
* Control + Windows + R: Reply / Mention.
* Control + Windows + Shift + R: Retweet.
* Control + Windows + D: Send direct message.
* Windows+ Alt + F: Like a tweet.
* Alt + Windows + Shift + F: Remove from likes.
* Control + Windows + S: Open the user actions dialogue.
* Control + Windows + Alt + N: See user details.
* Control + Windows + V: Show tweet.
* Control + Windows + F4: Quit TWBlue.
* Control + Windows + I: Open user timeline.
* Control + Windows + Shift + I: Destroy buffer.
* Control + Windows + Alt + Up: Increase volume by 5%.
* Control + Windows + Alt + Down: Decrease volume by 5%.
* Control + Windows + Home: Jump to the first element of the current buffer.
* Control + Windows + End: Jump to the last element of the current buffer.
* Control + Windows + PageUp: Jump 20 elements up in the current buffer.
* Control + Windows + PageDown: Jump 20 elements down in the current buffer.
* Windows + Alt + P: Edit profile.
* Control + Windows + Delete: Delete a tweet or direct message.
* Control + Windows + Shift + Delete: Empty the current buffer.
* Control + Windows + Space: Repeat last item.
* Control + Windows + Shift + C: Copy to clipboard.
* Control + Windows+ A: Add user to list.
* Control + Windows + Shift + A: Remove user from list.
* Control + Windows + Shift + M: Mute / unmute the current buffer.
* Windows + Alt + M: Mute / unmute the current session.
* Control + Windows + E: Toggle the automatic reading of incoming tweets in the current buffer.
* Control + Windows + -: Search on Twitter.
* Control + Windows + K: Show the keystroke editor.
* Control + Windows + L: Show lists for a specified user.
* Windows + Alt + PageUp: Load previous items for the current buffer.
* Control + Windows + G: Get geolocation.
* Control + Windows + Shift + G: Display the tweet's geolocation in a dialogue.
* Control + Windows + T: Create a trending topics' buffer.
* Control + Windows + {: Find a string in the current buffer.

## Configuration

As described above, this application has two configuration dialogues, the global settings dialogue and the account settings dialogue.

### The account settings dialogue

#### General tab

* Autocompletion settings: Allows you to configure the autocompletion database. You can add users manually or let TWBlue add your followers, friends or both.
* Relative timestamps: Allows you to configure whether the application will calculate the time the tweet or direct message was sent or received based on the current time, or simply say the time it was received or sent.
* API calls: Allows you to adjust the number of API calls to be made to Twitter by this program.
* Items on each API call: Allows you to specify how many items should be retrieved from Twitter for each API call (default and maximum is 200).
* Inverted buffers: Allows you to specify whether the buffers should be inverted, which means that the oldest items will show at the end of them and the newest at the beginning.
* Retweet mode: Allows you to specify the behaviour when posting a retweet: you can choose between retweeting with a comment, retweeting without comment or being asked.
* Number of items per buffer to cache in database: This allows you to specify how many items TWBlue should cache in a database. You can type any number, 0 to cache all items, or leave blank to disable caching entirely.

#### buffers tab

This tab displays a list for each buffer you have available in TWBlue, except for searches, timelines, favourites' timelines and lists. You can show, hide and move them.

#### The ignored clients tab

In this tab, you can add and remove clients to be ignored by the program.

#### Sound tab

In this tab, you can adjust the sound volume, select the input and output device and set the soundpack used by the program.

#### Audio service tab

In this tab, you can enter your SndUp API key (if you have one) to upload audio to SndUp with your account. Note that if account credentials are not specified you will upload anonimously.

### Global settings

This dialogue allows you to configure some settings which will affect the entire application.

#### General tab {#general-tab_1}

* Language: This allows you to change the language of this program. Currently supported languages are arabic, Catalan, German, English, Spanish, Basque, Finnish, French, Galician, Croatian, Hungarian, Italian, Polish, Portuguese, Russian and Turkish.
* Ask before exiting TWBlue: This checkbox allows you to control whetherthe program will ask for confirmation before exiting.
* Play a sound when TWBlue launches: This checkbox allows you to configure whether the application will play a sound when it has finished loading the buffers.
* Speak a message when TWBlue launches: This is the same as the previous option, but this checkbox configures whether the screen reader will say "ready".
* Use the invisible interface's shortcuts in the GUI: As the invisible interface and the Graphical User Interface have their own shortcuts, you may want to use the invisible interface's keystrokes all the time. If this option is checked, the invisible interface's shortcuts will be usable in the GUI.
* Activate SAPI5 when any other screen reader is not being run: This checkbox allows to activate SAPI 5 TTS when no other screen reader is being run.
* Hide GUI on launch: This allows you to configure whether TWBlue will start with the GUI or the invisible interface.
* Keymap: This option allows you to change the keymap used by the program in the invisible interface. The shipped keymaps are Default, Qwitter, Windows 10 and Chicken Nugget. The keymaps are in the "keymaps" folder, and you can create new ones. Just create a new ".keymap" file and change the keystrokes associated with the actions, as it is done in the shipped keymaps.

#### Proxi tab

In this tab you can configure TWBlue to use a Proxy server by completing the fields displayed (server, port, user and password).

## License, source code and donations

Tw Blue is free software, licensed under the GNU GPL license, either version 2 or, at your option, any later version. You can view the license in the file named license.txt, or online at <http://www.gnu.org/licenses/old-licenses/gpl-2.0.html>.

The source code of the program is available on GitHub at <https://www.github.com/manuelcortez/twblue>.

If you want to donate to the project, you can do so at <http://twblue.es/?q=node/3&language=en>. Thank you for your support!

## Contact

If you still have questions after reading this document, if you wish to collaborate to the project in some other way, or if you simply want to get in touch with the application developer, follow the Twitter account [@tw\_blue2](https://twitter.com/tw_blue2) or [@manuelcortez00.](https://twitter.com/manuelcortez00) You can also visit [our website](http://twblue.es)

## Credits

TWBlue is developed and mantained by [Manuel Cortéz](https://twitter.com/manuelcortez00) and [José Manuel Delicado](https://twitter.com/jmdaweb). It's supported and sponsored by [Technow S. L.](https://twitter.com/technow)

We would also like to thank the translators of TWBlue, who have allowed the spreading of the application.

* English: [Manuel Cortéz](https://twitter.com/manuelcortez00).
* Arabic: [Mohammed Al Shara](https://twitter.com/mohammed0204).
* Catalan: [Francisco Torres](https://twitter.com/ftgalleg)
* Spanish: [Manuel Cortéz](https://twitter.com/manuelcortez00).
* Basque: [Sukil Etxenike](https://twitter.com/sukil2011).
* Finnish: [Jani Kinnunen](https://twitter.com/jani_kinnunen).
* French: [Rémi Ruiz](https://twitter.com/blindhelp38).
* Galician: [Juan Buño](https://twitter.com/Quetzatl_).
* German: [Steffen Schultz](https://twitter.com/schulle4u).
* Croatian: [Zvonimir Stanečić](https://twitter.com/zvonimirek222).
* Hungarian: Robert Osztolykan.
* Italian: [Christian Leo Mameli](https://twitter.com/llajta2012).
* Japanese: [Riku](https://twitter.com/riku_sub001)
* Polish: [Pawel Masarczyk.](https://twitter.com/Piciok)
* Portuguese: Odenilton Júnior Santos.
* Romanian: [Florian Ionașcu](https://twitter.com/7ro) and [Răzvan Ciule](https://twitter.com/pilgrim89)
* Russian: [Наталья Хедлунд](https://twitter.com/Lifestar_n).
* Serbian: [Aleksandar Đurić](https://twitter.com/sokodtreshnje)
* Turkish: [Burak Yüksek](https://twitter.com/burakyuksek).

Many thanks also to the people who worked on the documentation. Initially, [Manuel Cortez](https://twitter.com/manuelcortez00) did the documentation in Spanish, and translated to English by [Bryner Villalobos](https://twitter.com/Bry_StarkCR), [Robert Spangler](https://twitter.com/glasscity1837), [Sussan Rey](https://twitter.com/sussanrey17), [Anibal Hernandez](https://twitter.com/anibalmetal), and [Holly Scott-Gardner](https://twitter.com/holly1994). It was updated by [Sukil Etxenike](https://twitter.com/sukil2011), with some valuable corrections by [Brian Hartgen](https://twitter.com/brianhartgen) and [Bill Dengler](https://twitter.com/codeofdusk).

------------------------------------------------------------------------

Copyright © 2013-2016. Manuel Cortéz