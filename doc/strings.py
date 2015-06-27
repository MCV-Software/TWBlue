# -*- coding: utf-8 -*-
import application
documentation = []
documentation.append(_(u"""Documentation for " + application.name + " - {0}""").format(application.version))
# Translators: This is the new line character, don't change it in the translations.
documentation.append(_(u"""
"""))
documentation.append(_(u"""## Table of contents"""))
# Table of contents for the python markdown extension
documentation.append("""[TOC]""")
documentation.append(_(u"""
"""))
documentation.append(_(u"""## Warning!"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""You are reading documentation produced for a program still in development. The object of this manual is to explain some details of the operation of the program. Bear in mind that as the software is in the process of active development, parts of this user guide may change in the near future, so it is advisable to keep checking from time to time to avoid missing important information."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""If you want to see what has changed from the previous version, [read the list of updates here.](changes.html)"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""## Introduction"""))
documentation.append(_(u"""
"""))
documentation.append(unicode(application.name)+_(u""" is an application to make Twitter simple and fast, while using as few resources as possible. With this application, you can:"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""* Tweet, reply to, retweet and delete tweets,"""))
documentation.append(_(u"""* Mark and unmark a tweet as favorite,"""))
documentation.append(_(u"""* Send, receive, and manage direct messages,"""))
documentation.append(_(u"""* See your friends and followers,"""))
documentation.append(_(u"""* Follow, unfollow, report and block users,"""))
documentation.append(_(u"""* Open a user's timeline to see their tweets separately,"""))
documentation.append(_(u"""* Open URLs from a tweet or direct message,"""))
documentation.append(_(u"""* Play several types of embeded audio from within the client,"""))
documentation.append(_(u"""* And more."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""## Usage"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""Twitter is a social networking or micro-blogging tool which allows you to compose short status updates of your activities in 140 characters or less. Twitter is a way for friends, family and co-workers to communicate and stay connected through the exchange of quick, frequent messages. You can restrict delivery of updates to those in your circle of friends or, by default, allow anyone to access them."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""You can monitor the status of updates from your friends, family or co-workers (known as following), and they in turn can read any updates you create, (known as followers). The updates are referred to as Tweets. The Tweets are posted to your Twitter profile or Blog and are searchable using Twitter Search."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""In order to use this application, you must first have created an account on the Twitter website. The process of signing up for a Twitter account is very accessible. When registering, you will need to choose a Twitter username. This serves two purposes: this is the name by which people will refer to you, and it, along with your password, will be required to connect this application to your Twitter account. We suggest you choose a username which is both memorable to you and the people you hope will follow you."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""We'll start from the premise that you have a Twitter account with its corresponding username and password."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""### Authorizing the application"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""First of all, it is necessary to authorize the program so it can access your Twitter account and act on your behalf. The authorization process is quite simple, and the program does not retain your log-in credentials. In order to authorize the application, simply  run the main executable file."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""You can log into several Twitter accounts simultaneously. The program refers to each Twitter account you have configured as a "Session". If this is the first time you've launched the program or if no sessions exist, you will see the Session Manager. This dialogue box allows you to authorize as many accounts as you wish. If you click on the "new account" button, a dialogue box will inform you that your default internet browser will be opened in order to authorize the application and you will be asked if you would like to continue. Activate the "yes" Button so the process may start."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""Your default browser will open on the Twitter page to request authorization. Enter your username and password into the appropriate edit fields if you're not already logged in, select the authorize button, and press it."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""Once you've authorized your twitter account, the website will redirect you to a page which will notify you that the program has been authorized successfully. Now you are able to close the page by pressing ALT+F4 which will return you to the Session Manager. On the session list, you will see a new item temporarily called "authorized account x" -where x is a number. The session name will change once you open that session."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""To start the program, press the Ok button in the Session Manager dialogue. By default, all sessions are started automatically, however, you can change this behavior."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""If all went well, the application will start playing sounds, indicating your data is being updated."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""When the process is finished, by default the program will play another sound, and the screen reader will say "ready" (this behaviour  can be configured)."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""## General concepts"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""Before starting to describe this program's usage, we'll explain some concepts that will be used extensively throughout this manual."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""### Buffer"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""A buffer is a list of items to manage the data which arrives from Twitter, after being processed by the application. When you configure a new session and start it, many buffers are created.  Each  of them may contain  items such as tweets, direct messages, users, trends or events. According to the buffer you are focusing, you will be able to perform different actions on these items."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""The following is a list of all possible buffers. After the name of each buffer is a description of the types of items it contains."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""* Home: this shows all the tweets on the main timeline. These are the tweets by users you follow."""))
documentation.append(_(u"""* Mentions: if a user, whether you follow them or not, mentions you on Twitter, you will find it in this list."""))
documentation.append(_(u"""* Direct messages: here you will find the private direct messages you exchange with users who follow you , or with any user, if you allow direct messages from everyone (this setting is configurable from Twitter). This list only shows received messages."""))
documentation.append(_(u"""* Sent direct messages: this buffer shows all direct messages sent from your account."""))
documentation.append(_(u"""* Sent tweets: this shows all tweets  sent from your account."""))
documentation.append(_(u"""* Favorites: here you will see all the tweets you have favorited."""))
documentation.append(_(u"""* Followers: when users follow you, they will be displayed  in this buffer."""))
documentation.append(_(u"""* Friends: the same as the previous buffer, but these are the users you follow."""))
documentation.append(_(u"""* User timelines: these are  buffers you may create. They contain only the tweets by a specific user. They're used so you can see the tweets by a single person and you don't want to look all over your timeline. You may create as many as you like."""))
documentation.append(_(u"""* Events: An event is anything that happens on Twitter, such as when someone follows you, when someone adds or removes one of your tweets from their favorites list, or when you subscribe to a list.  There are many more, but this program shows the most common ones in the events buffer so that you can easily keep track of what is happening on your account."""))
documentation.append(_(u"""* Lists: A list is similar to a  user timeline, except that you can configure it to contain tweets from multiple users."""))
documentation.append(_(u"""* Search: A search buffer contains the results of a search operation."""))
documentation.append(_(u"""* User favorites: You can have this program create a buffer containing tweets favorited by a particular user."""))
documentation.append(_(u"""* Trending Topics: a trend buffer shows the top ten most used terms in a geographical region. This region may be a country or a city. Trends are updated every five minutes."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""If a tweet contains a URL, you can press enter in the GUI or Control + Windows + Enter in the invisible interface to open it. If it contains audio, you can press Control + Enter or Control + Windows + Alt + Enter to play it, respectively. this program will play a sound if the tweet contains the #audio hashtag, but there may be tweets which contain audio without this. Finally, if a tweet contains geographical information, you can press   Control + Windows + G in the invisible interface to retrieve it."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""### Username fields"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""These fields accept a Twitter username (without the at sign) as the input. They are present in the send direct message and the user actions   dialogue boxes. Those dialogues will be discussed later. The initial value of these fields depends on where they were opened from. They are prepopulated with the username of the  sender of the focused tweet (if they were  opened from  the home and sent timelines, from users' timelines or from lists), the sender of the focused direct message (if from the received or sent direct message buffers) or in the focused user (if from the followers' or friends' buffer). If  one of those dialogue boxes is opened from a tweet, and if there are more users mentioned in it, you can use the arrow keys to  switch between them. Alternatively, you can also type a username."""))
documentation.append(_(u"""## the user interface"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""### The graphical user interface (GUI)"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""The graphical user interface consists of a window containing:"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""* a menu bar with five menus (application, tweet, user, buffer and help);"""))
documentation.append(_(u"""* One tree view, containing a list of sessions and the buffers within each"""))
documentation.append(_(u"""* One list view containing the items in the currently active buffer"""))
documentation.append(_(u"""* Four buttons in most dialogs: Tweet, retweet , reply and direct message."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""The actions that are available for every item will be described later."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""In summary, the GUI contains two core components. These are the controls you will find while pressing the Tab key within the program's interface, and the different elements present on the menu bar."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""#### Buttons in the application"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""* Tweet: this button opens up a dialogue box to write your tweet. The message must not exceed 140 characters.  If you write past this limit, a sound will play to warn you. Note that the character count is displayed in the title bar. You may use the shorten and expand URL buttons to comply with the character limit. You can  upload a picture, check spelling, attach audio or translate your message by selecting one of the available buttons in the dialogue box. In addition, you can autocomplete the entering of users by pressing Alt + A or the button for that purpose if you have the database of users configured. Press enter to send the tweet. If all goes well, you'll hear a sound confirming it. Otherwise, the screen reader will speak an error message in English describing the problem."""))
documentation.append(_(u"""* Retweet: this button retweets the message you're reading. After you press it, if you haven't configured the application not to do so, you'll be asked if you want to add a comment or simply send it as written. If you choose to add a comment, and if the original tweet plus the comment exceeds 140 characters, you will be asked if you want to post it as a comment   with a mention to the original user and a link to the original tweet."""))
documentation.append(_(u"""* Reply: when you're viewing a tweet, you can reply to the user who sent it by pressing this button. A dialogue will open up similar to the one for tweeting, but with the name of the user already filled in (for example @user) so you only need to write your message. If there are more users referred to in the tweet, you can press shift-tab and activate the mention all users button. When you're on the friends or followers lists, the button will be called mention instead."""))
documentation.append(_(u"""* Direct message: exactly like sending a tweet, but it's a private message which can only be read by the user you send it to. Press shift-tab to see the recipient. If there were other users mentioned in the tweet you were reading, you can arrow up or down to choose which one to send it to, or write the username yourself without the at sign."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""Bear in mind that buttons will appear according to which actions are possible on the list you are browsing. For example, on the home timeline, mentions, sent, favorites and user timelines you will see the four buttons, while on the direct messages list you'll only get the direct message and tweet buttons, and on friends and followers lists the direct message, tweet, and mention buttons will be available."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""#### Menus"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""Visually, Towards the top of the main application window, can be found a menu bar which contains many of the same functions as listed in the previous section, together with some additional items. To access the menu bar, press the alt key. You will find five menus listed: application, tweet, user, buffer and help. This section describes the items on each one of them."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""##### Application menu"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""* Manage accounts: Opens a window with all configured sessions, where you can add new sessions or delete the ones you've already created."""))
documentation.append(_(u"""* Update profile: opens a dialogue  where you can update your Twitter profile: name, location, website and bio. If you have already set this up the fields will be prefilled with the existing information. Also, you can upload a photo to your profile."""))
documentation.append(_(u"""* Hide window: turns off the Graphical User Interface. Read the section on the invisible interface for further details."""))
documentation.append(_(u"""* Search: shows a dialogue box where you can search for tweets or users on Twitter."""))
documentation.append(_(u"""* Lists Manager: This dialogue box allows you to manage your Twitter lists.  In order to use them, you must first create them.  Here, you can view, edit, create, delete or, optionally, open them in buffers similar to  user timelines."""))
documentation.append(_(u"""* Edit keystrokes: this opens a dialogue where you can see and edit the shortcuts used by the invisible interface."""))
documentation.append(_(u"""* Account settings: Opens a dialogue box which lets you customize settings for the current account."""))
documentation.append(_(u"""* Global settings: Opens a dialogue which lets you configure settings for the entire application."""))
documentation.append(_(u"""* Quit: asks whether you want to exit the program. If the answer is yes, it closes the application. If you do not want to be asked for confirmation before exiting, uncheck the checkbox from the global settings dialogue box."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""##### Tweet menu"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""*Tweet, reply and retweet - equivalent to the buttons with the same name."""))
documentation.append(_(u"""* Add to favorites: marks the tweet you're viewing as a favorite."""))
documentation.append(_(u"""* Remove  from favorites: removes the tweet from your favorites."""))
documentation.append(_(u"""* Show tweet: opens up a dialogue box where you can read the tweet, direct message, friend or follower which has focus. You can read the text with the arrow keys. It's a similar dialog box as used for composing tweets, without the ability to send the tweet, file attachment and autocompleting capabilities. It does however include a retweets and favorites count. If you are in the followers or the friends list, it will only contain a read-only edit box with the information in the focused item and a close button."""))
documentation.append(_(u"""* View address: If the selected tweet has geographical information, this program may display a dialogue box where you can read the tweet address. This address is  retrieved by sending the geographical coordinates of the tweet to Google maps."""))
documentation.append(_(u"""* View conversation: If you are focusing a tweet with a mention, it opens a buffer where you can view the whole conversation."""))
documentation.append(_(u"""* Delete: permanently removes the tweet or direct message which has focus from Twitter and from your lists. Bear in mind that Twitter only allows you to delete tweets you have posted."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""##### User menu"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""* Actions: Opens a dialogue where you can interact with a user. This dialogue box will be populated with the user who sent the tweet or direct message in focus or the selected user in the friends or followers buffer. You can edit it or leave it as is and choose one of the following actions:"""))
documentation.append(_(u"""    * Follow: Follows a user. This means you'll see their tweets on your  home timeline, and if they also follow you, you'll be able to exchange direct messages. You may also exchange direct messages without following if you have configured the option to allow direct messages from anyone."""))
documentation.append(_(u"""    * Unfollow: Stops following a user, which causes you to be unable to see their tweets on your main timeline or exchange direct messages with them,  unless they have enabled receiving direct messages from anyone."""))
documentation.append(_(u"""    * Mute: When someone is muted, their tweets will not be shown. But you will be able to exchange direct messages. The muted user is not informed of this action."""))
documentation.append(_(u"""    * Unmute: this option allows  the display of a muted user's tweets and mentions again."""))
documentation.append(_(u"""    * Block: Blocks a user. This forces the user to unfollow you."""))
documentation.append(_(u"""    * Unblock: Stops blocking a user."""))
documentation.append(_(u"""    * Report as spam: this option sends a message to Twitter suggesting the user is performing prohibited practices on the social network."""))
documentation.append(_(u"""    * Ignore tweets from this client: Adds the client from which the focused tweet was sent to the ignored clients list."""))
documentation.append(_(u"""* View timeline: Lets you open a user's timeline by choosing the user in a dialog box. It is created when you press enter. If you invoke this option relative to a user that has no tweets, the operation will fail. If you try creating an existing timeline the program will warn you and will not create it again."""))
documentation.append(_(u"""* Direct message: same action as the button."""))
documentation.append(_(u"""* Add to List: In order to see someone's tweets in one or more of your lists, you must add them first. In the dialogue box that opens after selecting the user, you will be asked to select the list you wish to add the user to. Thereafter, the list will contain a new member and their tweets will be displayed there."""))
documentation.append(_(u"""* Remove from list: lets you remove a user from a list."""))
documentation.append(_(u"""* View lists: Shows the lists created by a specified user."""))
documentation.append(_(u"""* Show user profile: opens a dialogue  with the profile of the specified user."""))
documentation.append(_(u"""* View favorites: Opens a buffer where you can see the tweets which have been favorited by a particular user."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""##### Buffer menu"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""* New trending topics buffer: This opens a buffer to get the worldwide trending topics or those of a country or a city.  You'll be able to select from a dialogue box if you wish to retrieve countries' trends, cities' trends or worldwide trends (this option is in the cities' list) and choose one from the selected list. The trending topics buffer will be created once the "OK" button has been activated within the dialogue box. Remember this kind of buffer will be updated every five minutes."""))
documentation.append(_(u"""* Load previous items: This allows more items to be loaded for the specified buffer."""))
documentation.append(_(u"""* Mute: Mutes notifications of a particular buffer so you will not hear when new tweets arrive."""))
documentation.append(_(u"""* autoread: When enabled, the screen reader or SAPI 5 Text to Speech voice (if enabled) will read the text of incoming tweets. Please note that this could get rather chatty if there are a lot of incoming tweets."""))
documentation.append(_(u"""* Clear buffer: Deletes all items from the buffer."""))
documentation.append(_(u"""* Destroy: dismisses the list you're on."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""##### Help menu"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""* Documentation: generates and displays the latest documentation."""))
documentation.append(_(u"""* Sounds tutorial: Opens a dialog box where you can familiarize yourself with the different sounds of the program."""))
documentation.append(_(u"""* What's new in this version?: opens up a document with the list of changes from the current version to the earliest."""))
documentation.append(_(u"""* Check for updates: every time you open the program it automatically checks for new versions. If an update is available, it will ask you if you want to download the update. If you accept, the updating process will commence. When complete, this program will be restarted. This item checks for new updates without having to restart the application."""))
documentation.append(_(u"""* Report an error: opens up a dialogue box to report a bug by completing a small number of fields. Pressing enter will send the report. If the operation doesn't succeed the program will display a warning."""))
documentation.append(_(u"""* this program's website: visit our [home page](" + application.url + ") where you can find all relevant information and downloads for this program and become a part of the community."""))
documentation.append(_(u"""* About: shows the credits of the program."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""### The invisible user interface"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""The invisible interface, as its name suggests, has no graphical window and works directly with screen readers such as JAWS for Windows, NVDA and System Access. This interface is disabled by default, but you can enable it by pressing Control + M. It works similarly to Qwitter, TheQube and Chicken Nugget. Its shortcuts are similar to those found in these clients. In addition, this program can fully emulate the keymaps of Qwitter and Chicken Nugget. The application keymap is configurable through the global settings dialogue."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""The next section contains a list of keyboard shortcuts for the graphical user interface. For a list of shortcuts for the invisible interface, open the keymap editor."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""## Keyboard shortcuts"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""### Shortcuts of the graphical user interface (GUI)"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""* Enter: Open URL."""))
documentation.append(_(u"""* Control + Enter: Play audio."""))
documentation.append(_(u"""* Control + M: Hide the GUI."""))
documentation.append(_(u"""* Control + N: Compose a new tweet."""))
documentation.append(_(u"""* Control + R: Reply / mention."""))
documentation.append(_(u"""* Control + Shift + R: Retweet."""))
documentation.append(_(u"""* Control + D: Send a direct message."""))
documentation.append(_(u"""* control + F: Add tweet to favorites."""))
documentation.append(_(u"""* Control + Shift + F: Remove a tweet from favorites."""))
documentation.append(_(u"""* Control + S: Open the user actions dialogue."""))
documentation.append(_(u"""* Control + Shift + V: Show tweet."""))
documentation.append(_(u"""* Control + Q: Quit this program."""))
documentation.append(_(u"""* Control + I: Open user timeline."""))
documentation.append(_(u"""* Control + Shift + i: Destroy buffer."""))
documentation.append(_(u"""* F5: Increase volume by 5%."""))
documentation.append(_(u"""* F6: Decrease volume by 5%."""))
documentation.append(_(u"""* Control + P: Edit your profile."""))
documentation.append(_(u"""* Control + Delete: Delete a tweet or direct message."""))
documentation.append(_(u"""* Control + Shift + Delete: Empty the current buffer."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""## Configuring this program"""))
documentation.append(_(u"""As described above, this program has two configuration dialogues, the global settings dialogue and the account settings dialogue."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""### The account settings dialogue"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""#### General tab"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""* Autocompletion settings: Allows you to configure the autocompletion database. You can add users manually or let the program add your followers, friends or both automatically."""))
documentation.append(_(u"""* Relative timestamps: Allows you to configure whether this program will calculate the time the tweet or direct message was sent or received based on the current time, or simply say the time it was received or sent."""))
documentation.append(_(u"""* API calls: Allows you to adjust the number of API calls to make to Twitter."""))
documentation.append(_(u"""* Items on each API call: Allows you to specify how many items should be retrieved from Twitter for each API call (default and maximum is 200)."""))
documentation.append(_(u"""* Inverted buffers: Allows you to specify whether the buffers should be inverted, which means that the oldest items will show at the end of them and the newest at the beginning."""))
documentation.append(_(u"""* Retweet mode: Allows you to specify  the behaviour when posting a retweet: you can choose  between retweeting with a comment, retweeting without comment or being asked."""))
documentation.append(_(u"""* Number of items per buffer to cache in database: This allows you to specify how many items  this program should cache in it's database. You can type any number, leave blank to cache all items, or enter 0 to disable caching entirely."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""#### buffers tab"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""This tab displays a list of all available buffers, except for searches, timelines, favorites' timelines and lists. You can show, hide and move them."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""#### The ignored clients tab"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""In this tab, you can add and remove clients to be ignored by this program."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""#### Sound tab"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""In this tab, you can adjust the sound volume, select the input and output device and set the soundpack used by this program."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""#### Audio service tab"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""In this tab, you can enter your SndUp API key (if you have one) to upload audio to SndUp with your account. Note that if account credentials are not specified you will upload anonymously."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""### Global settings"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""This dialogue allows you to configure some settings which will affect the entire application."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""#### General tab"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""* Language: This allows you to change the language of this program. Currently supported languages are arabic, Catalan, German, English, Spanish, Basque, Finnish, French, Galician, Croatian, Hungarian, Italian, Polish, Portuguese, Russian and Turkish."""))
documentation.append(_(u"""* Ask before exiting : This checkbox allows you to control whether you will be asked for confirmation before exiting."""))
documentation.append(_(u"""* Play a sound on launch : This checkbox allows you to configure whether a sound will be played  when all buffers have loaded."""))
documentation.append(_(u"""* Speak a message on launch: This is the same as the previous option, but this checkbox configures whether the screen reader will say \"ready\"."""))
documentation.append(_(u"""* Use the invisible interface's shortcuts in the GUI: As the invisible interface and the Graphical User Interface have  their own shortcuts, you may want to use the invisible interface's keystrokes all the time. If this option is checked, the invisible interface's shortcuts will be usable in the GUI."""))
documentation.append(_(u"""* Activate SAPI5 when any other screen reader is not being run: This checkbox allows to activate SAPI 5 TTS when no other screen reader is being run."""))
documentation.append(_(u"""* Hide GUI on launch: This allows you to configure whether this program will start with the GUI or the invisible interface."""))
documentation.append(_(u"""* Keymap: This option allows you to change the keymap used by this program in the invisible interface. The shipped keymaps are Default, Qwitter, Windows 10 and Chicken Nugget. The keymaps are in the \"keymaps\" folder, and you can create new ones. Just create a new \".keymap\" file and change the keystrokes associated with the actions, as it is done in the shipped keymaps."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""#### Proxi tab"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""In this tab you can configure this program to use a Proxy server by completing the fields displayed (server, port, user and password)."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""## License, source code and donations"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""This program is free software, licensed under the GNU GPL, either version 2 of the license, or (at your option) any later version. You can view the license in the file named license.txt, or online at <http://www.gnu.org/licenses/old-licenses/gpl-2.0.html>."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""The source code of the program is available on GitHub at <https://www.github.com/manuelcortez/TWBlue>."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""If you want to donate to the project, visit the project website. Thank you for your support!"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""## Contact"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""If you still have questions after reading this document, if you wish to collaborate to the project in some other way, or if you simply want to get in touch with the application developer, follow the Twitter account [@tw_blue2](https://twitter.com/tw_blue2)  or [@manuelcortez00.](https://twitter.com/manuelcortez00) You can also visit [our website](" + application.url + ")"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""## Credits"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""this program is developed and maintained by [Manuel Cortéz](https://twitter.com/manuelcortez00), [José Manuel Delicado](https://twitter.com/jmdaweb), and [Bill Dengler](https://twitter.com/codeofdusk). It is supported and sponsored by [Technow S. L.](https://twitter.com/technow)"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""We would also like to thank the translators of this program, who have allowed the spreading of the application."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""* English: [Bryner Villalobos](https://twitter.com/Bry_StarkCR) and [Bill Dengler](https://twitter.com/codeofdusk)."""))
documentation.append(_(u"""* Arabic: Mohammed Al Shara."""))
documentation.append(_(u"""* Catalan: [Joan Rabat](https://twitter.com/joanrabat) and Juan Carlos Rivilla."""))
documentation.append(_(u"""* Spanish: [Manuel Cortéz](https://twitter.com/manuelcortez00)."""))
documentation.append(_(u"""* Basque: [Sukil Etxenike](https://twitter.com/sukil2011)."""))
documentation.append(_(u"""* Finnish: Jani Kinnunen."""))
documentation.append(_(u"""* French: Rémi Ruiz."""))
documentation.append(_(u"""* Galician: [Alba Kinteiro](https://twitter.com/albasmileforeve)."""))
documentation.append(_(u"""* German: Steffen Schultz."""))
documentation.append(_(u"""* Hungarian: Robert Osztolykan."""))
documentation.append(_(u"""* Polish: Pawel Masarczyk."""))
documentation.append(_(u"""* Portuguese: Odenilton Júnior Santos."""))
documentation.append(_(u"""* Russian: Alexander Jaszyn."""))
documentation.append(_(u"""* Turkish: Burak."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""Many thanks also to the people who worked on the documentation. Initially, [Manuel Cortéz](https://twitter.com/manuelcortez00) did the documentation in Spanish, and translated to English by [Bryner Villalobos](https://twitter.com/Bry_StarkCR), [Robert Spangler](https://twitter.com/glasscity1837), [Sussan Rey](https://twitter.com/sussanrey17), [Anibal Hernandez](https://twitter.com/anibalmetal), and [Holly Scott-Gardner](https://twitter.com/holly1994). It was updated by [Bill Dengler](http://twitter.com/codeofdusk) and [Sukil Etxenike](https://twitter.com/sukil2011), with some valuable corrections by [Brian Hartgen](https://twitter.com/brianhartgen)."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""---"""))
documentation.append(_(u"""Copyright © 2013-2015. Manuel Cortéz"""))
