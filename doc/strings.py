# -*- coding: utf-8 -*-
import application
documentation = []
documentation.append(_(u"""Documentation for {0} - {1}""").format(application.name, application.version))
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
documentation.append(_(u"""You're reading documentation produced for a program still in development. The object of this manual is to explain some details of the operation of the program. Bear in mind that as the software is in the process of active development, parts of this document may change in the near future, so it is advisable to keep an eye on it from time to time to avoid missing too much out."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""If you want to see what has changed from the previous version, [read the list of updates here.](changes.html)"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""## Introduction"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""TW Blue is an application to make Twitter simple and fast, while using as few resources as possible. With it, you can do things like the following:"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""* Tweet, reply, retweet and delete tweets,"""))
documentation.append(_(u"""* Mark and unmark a tweet as a favourite,"""))
documentation.append(_(u"""* Send and delete direct messages,"""))
documentation.append(_(u"""* See your friends and followers,"""))
documentation.append(_(u"""* Follow, unfollow, report as spam and block a user,"""))
documentation.append(_(u"""* Open a user's timeline to see only their tweets,"""))
documentation.append(_(u"""* Open URLs from a tweet or direct message,"""))
documentation.append(_(u"""* Play several types of audio files from addresses,"""))
documentation.append(_(u"""* And more."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""## Usage"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""In order to use an application like TW Blue which allows you to manage your Twitter account, you must first be registered on it. It's beyond the scope of this document to explain how to do so. We'll start from the premise that you have an account with its corresponding user name and password."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""### Authorising the application"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""First off, it's necessary to authorise the program so it can access your Twitter account and act on your behalf. The authorisation process is quite simple, and the program never gets data such as your  password. In order to authorise the application, you just need to run the main executable file, called TWBlue.exe (on some computers it may appear simply as TWBlue)."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""If this is the first time you open TWBlue, or if you don't have any session, you will see the session manager. This dialogue box allows you to authorise as many accounts as you wish. If you press the "new account" button a dialogue will tell you that your default browser will be opened in order to authorise the application. Press "yes" so the process may start."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""Your default browser will open on the Twitter page to request authorisation. Enter your user name and password if you're not already logged in, look for the authorise button, and press it."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""Once you've authorised your twitter account, Twitter will redirect you to a web page which will notify you that TWBlue has been authorised successfully. Now you are able to close that window and  go back to the session manager. On the session list, you will see  a new item temporarily called "Authorised account x" -where x is a number. The session name will change once you open that session."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""To start running TWBlue, press the Ok button in the session manager dialogue box. By default, TWBlue starts all the configured sessions automatically, however, you can change this behavior."""))
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
documentation.append(_(u"""Before starting to describe TW Blue's usage, we'll explain some concepts that will be used extensively throughout this manual."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""### Buffer"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""A buffer is a list of items to manage the data which arrives from Twitter, after being processed by the application. When you configure a new session on TWBlue and start it, many buffers are created.  Each  of them may contain some of the items which TWBlue works with: Tweets, direct messages, users, trends or events. According to the buffer you are focusing, you will be able to do different actions with these items."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""The following is a description for every kind of TWBlue's buffers and the kind of items they work with."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""* Home: it shows all the tweets on the main timeline. These are the tweets by users you follow."""))
documentation.append(_(u"""* Mentions: if a user, whether you follow them or not, mentions you on Twitter, you will find it on this list."""))
documentation.append(_(u"""* Direct messages: here go the private direct messages you exchange with users  who follow you back, or with any user, if they allow direct messages from everyone. This list only shows received messages."""))
documentation.append(_(u"""* Sent direct messages: it shows all the direct messages sent from your account."""))
documentation.append(_(u"""* Sent tweets: it shows all the tweets  sent from your account."""))
documentation.append(_(u"""* Favourites: here you will see all the tweets you have favourited."""))
documentation.append(_(u"""* Followers: when users follow you, you'll be able to see them on this list, with some of their account information."""))
documentation.append(_(u"""* Friends: the same as the previous list, but these are the users you follow."""))
documentation.append(_(u"""* User timelines: these are  buffers you may create. They contain only the tweets by a specific user. They're used so you can see the tweets by a single person and you don't want to look all over your timeline. You may create as many as you like."""))
documentation.append(_(u"""* Events: An event is anything that happens on Twitter, such as when someone follows you, when someone adds or removes one of your tweets from their favourites list, or when you subscribe to a list.  There are many more but TW Blue shows the most common ones in the events buffer so that you can easily keep track of what is happening on your account."""))
documentation.append(_(u"""* Lists: A list is similar to a  user timeline, except that you can configure it to contain tweets from multiple users."""))
documentation.append(_(u"""* Search: A search buffer contains the results of a search operation."""))
documentation.append(_(u"""* User favourites: You can have TW Blue create a buffer containing tweets favourited by a particular user."""))
documentation.append(_(u"""* Trending Topics: a trend buffer shows the top ten most used terms in a geographical region. This region may be a country or a city. Trends are updated every five minutes."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""### Username fields"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""These fields accept a Twitter username (without the at sign) as the input. They are present in the send direct message and the user actions   dialogue boxes. Those dialogues will be discussed later. The initial value of these fields depends on where they were opened from. They are prepopulated with the username of the  sender of the focused tweet (if they were  opened from  the home and sent timelines, from users'' timelines or from lists), the sender of the focused direct message (if from the received and sent direct message buffers) or in the focused user (if from the followers and friends buffer). If  one of those dialogue boxes is opened from a tweet, and if there are more users mentioned in it, you can use the arrow keys to  switch between them. In any case, you can also type a username."""))
documentation.append(_(u"""## Tw Blue's interfaces'"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""Beginning with the 0.36 version, there's support for an interface which does not require a visible window. It can be activated by pressing control-m, or choosing hide window from the application menu. This interface is entirely driven through shortcut keys. These shortcuts are different from those used to drive the graphical interface. By default, you can't use the invisible interface shortcuts on the GUI. It has been made this way to keep  compatibility with applications like TheQube and Chicken nugget which may use the same shortcuts. If you wish to have available the invisible interface shortcuts even if you are using the GUI, activate this option on the General tab of the global settings dialogue box. This section describes both the graphical and the invisible interface."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""### The graphical user interface (GUI)"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""The easiest way to describe the graphical user interface of TWBlue is saying that the application has a window which contains a menu bar with five menus (application, tweet, user, buffer and help); one tree view, one list of items and, mostly in every case, three buttons: Tweet, retweet and reply. The actions that are available for every item will be described later."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""Here you have a list divided into two parts. On the one hand, the buttons you will find while tabbing around on the program's interface, and on the other, the different elements present on the menu bar."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""#### Buttons on the application"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""* Tweet: this button opens up a dialogue box to write your tweet. The message must not exceed 140 characters.  If you write past this limit, a sound will play to warn you. Note that the character count is displayed in the title bar. You may use the shorten and expand URL buttons to comply with the character limit. You can  upload a picture, check spelling, attach audio or translate your message by selecting one of the available buttons in the dialogue box. In addition, you can autocomplete users by pressing alt+a or   the button for that purpose if you have the database of users configured. Press enter to send the tweet. If all goes well, you'll hear a sound confirming it. Otherwise, the screen reader will say an error message in English describing the problem."""))
documentation.append(_(u"""* Retweet: this button retweets the message you're reading. After you press it, if you haven't configured the application not to do so, you'll be asked if you want to add a comment or simply send it as written. If you choose to add a comment, and if the original tweet plus the comment exceeds 140 characters, you will be asked if you want to post it as a comment   with a mention to the original user and a link to the original tweet."""))
documentation.append(_(u"""* Reply: when you're viewing a tweet, you can reply to the user who sent it by pressing this button. A dialogue will open up like the one for tweeting, but with the name of the user already filled in (for example @user) so you only need to write your message. If there are more users mentioned on the tweet, you can press shift-tab and press the mention all users button. When you're on the friends or followers lists, the button will be called mention instead."""))
documentation.append(_(u"""* Direct message: exactly like sending a tweet, but it's a private message which can only be read by the user you send it to. Press shift-tab to see the recipient. If there were other users mentioned on the tweet you were reading, you can arrow up or down to choose which one to send it to, or write the username yourself without the at sign."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""Bear in mind that buttons will appear according to which actions are possible on the list you are browsing. For example, on the home timeline, mentions, sent, favourites and user timelines you will see the four buttons, while on the direct messages list you'll only get the direct message and tweet buttons, and on friends and followers lists you will get the direct message, tweet, and mention buttons."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""#### Menus"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""On top of the program window there's a menu bar which has the same functions, and some more. To access the menu bar, press alt. You will find five: application, tweet, user, buffer and help. This section describes the items on each one of them."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""##### Application menu"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""* Manage accounts: Opens a window with all the sessions configured in TWBlue, where you can add new sessions or delete the ones you've already created."""))
documentation.append(_(u"""* Update profile: opens a dialogue  where you can update your information on Twitter: name, location, website and bio. If you have already set this up the fields will be prefilled with the existing information. Also, you can upload a photo to your profile."""))
documentation.append(_(u"""* Hide window: turns off the Graphical User Interface. Read the section on the invisible interface for further details."""))
documentation.append(_(u"""* Search: shows a dialogue box where you can search for tweets or users on Twitter."""))
documentation.append(_(u"""* Lists Manager: This dialogue box allows you to manage your Twitter lists.  In order to use them, you must first create them.  Here, you can view, edit, create, delete or, optionally, open them in buffers similar to  user timelines."""))
documentation.append(_(u"""* Edit keystrokes: It opens a dialogue where you can see and edit the invisible interface's shortcuts. """))
documentation.append(_(u"""* Account settings: Opens a dialogue box which lets you customize settings for the current account."""))
documentation.append(_(u"""* Global settings: Open a dialogue which lets you configure settings for the entire application."""))
documentation.append(_(u"""* Quit: asks whether you want to exit the program. If the answer is yes, it shuts the application down.  If you wish TWBlue not to ask you for confirmation before exiting, uncheck the checkbox from the preferences dialogue box."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""##### Tweet menu"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""* You will first find the items to tweet, reply and retweet, which are equivalent to the buttons with the same name."""))
documentation.append(_(u"""* Add to favourites: marks the tweet you're viewing as a favourite."""))
documentation.append(_(u"""* Remove  from favourites: removes the tweet from your favourites, but not from Twitter."""))
documentation.append(_(u"""* Show tweet: opens up a dialogue box where you can read the tweet, direct message, friend or follower under focus. You can read the text with the arrow keys. It's the same dialogue  used to write tweets on, without the tweeting, attaching and autocompleting capabilities, and with a retweets and favourites count. If you are in the followers or the friends list, it will only contain a read-only edit box with the information in the focused item and a close button."""))
documentation.append(_(u"""* View address: If the selected tweet has geographical information, TWBlue may display a dialogue box where you can read the tweet address. This address is  retrieved by sending the geographical coordinates of the tweet to Google maps."""))
documentation.append(_(u"""* View conversation: If you are focusing a tweet with a mention, it opens a buffer where you can view the whole conversation."""))
documentation.append(_(u"""* Delete: permanently removes the tweet or direct message you're on from Twitter and from your lists. Bear in mind that Twitter only allows you to delete tweets you have posted yourself."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""##### User menu"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""* Actions: Opens a dialogue  where you can do certain things with a user. This dialogue box will be populated with the user who sent the tweet or direct message  in focus or the user in focus in the friends or followers buffer. You can edit it or leave it as is and choose one of the following actions:"""))
documentation.append(_(u"""    * Follow: Follows a user. This means you'll see his/her tweets on your main timeline, and if he/she also follows you, you'll be able to interchange direct messages."""))
documentation.append(_(u"""    * Unfollow: Stops following a user, which causes you not being able to see his/her tweets on your main timeline neither interchanging direct messages."""))
documentation.append(_(u"""    * Mute: While muting someone, TWBlue won't show you nor his/her tweets on your main timeline; neither you'll see that person's mentions. But you both will be able to interchange direct messages. The muted user is not informed of this action."""))
documentation.append(_(u"""    * Unmute: It turns the way TWBlue treats this user to its normal way. You will see his/her tweets and mentions again."""))
documentation.append(_(u"""    * Block: Blocks a user. This forces the user to unfollow you ."""))
documentation.append(_(u"""    * Unblock: Stops blocking a user."""))
documentation.append(_(u"""    * Report as spam: It suggests twitter this user is performing prohibited practices on the social network."""))
documentation.append(_(u"""    * Ignore tweets from this client: Adds the client from which the focused tweet was sent to the ignored clients list."""))
documentation.append(_(u"""* View timeline: Lets you open a user's timeline by choosing the user in a dialog box. It is created when you press enter. If you try it with a user that has no tweets, the program will fail. If you try creating an already existing timeline the program will warn you and will not create it again."""))
documentation.append(_(u"""* Direct message: same action as the button."""))
documentation.append(_(u"""* Add to List: In order to see someone's tweets in one or more of your lists, you must add them first. In the dialogue box that opens up after selecting the user, you will be asked to select the list you wish to add the user to.  Afterwards, the list will contain a new member and their tweets will show up there."""))
documentation.append(_(u"""* Remove from list: lets you remove a user from a list."""))
### Add description for view list
documentation.append(_(u"""* Show user profile: opens up a dialogue  with the profile of the specified user."""))
documentation.append(_(u"""* View favourites: Opens a buffer where you can see what tweets have been favourited by a particular user."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""##### Buffer menu"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""* New trending topics buffer: It opens a buffer to get the worlwide trending topics or those of a country or a city.  You'll be able to select from a dialogue box if you wish to get countries' trends, cities' trends or worldwide trends (this options is in the cities' list) and choose one from the selected list. The trending topics buffer will be created once pressing "ok" on this dialogue box. Remember this kind of buffer will be updated every five minutes."""))
documentation.append(_(u"""* Load previous items: This allows more items to be loaded for the specified buffer."""))
documentation.append(_(u"""* Mute: Mutes notifications of a particular buffer so you will not hear when new tweets arrive."""))
documentation.append(_(u"""* autoread : When enabled, the screen reader or SAPI 5 (if enabled) will read the text of incoming tweets.  Please note that this could get rather chatty if there are a lot of incoming tweets."""))
documentation.append(_(u"""* Clear buffer: Deletes all items from the buffer."""))
documentation.append(_(u"""* Destroy: dismisses the list you're on."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""##### Help menu"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""* Documentation: opens up this file, where you can read some useful program concepts."""))
documentation.append(_(u"""* Sounds tutorial: Opens a dialog box where you can familiarize yourself with the different sounds of the program."""))
documentation.append(_(u"""* What's new in this version?: opens up a document with the list of changes from the current version down to the first."""))
documentation.append(_(u"""* Check for updates: every time you open the program it automatically checks for new versions. If there is any, it will ask you if you want to download the update. If you accept, it will do so, and after that, the update will be installed, and the application will be restarted. This item checks for new updates without having to restart the application."""))
documentation.append(_(u"""* Report an error: opens up a dialogue box to report a bug by filling a couple of fields. Pressing enter will send the report. If the operation doesn't succeed the program will show a warning."""))
documentation.append(_(u"""* TW Blue's website: visit our [home page](http://twblue.es) where you can find all relevant information and downloads for TW Blue and become a part of the community."""))
documentation.append(_(u"""* About TW Blue: shows the credits of the program."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""### The invisible user interface"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""The invisible interface, as its name suggests, has no graphical window and works directly with screen readers such as JAWS, NVDA and System Access. It works similarly to TheQube and Chicken Nugget. Its shortcuts are similar to those found in these two clients. In addition, Tw Blue has builtin support for the keymaps for these applications, configurable through the global settings dialogue."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""In the next section there is a list of keyboard shortcuts for both interfaces. Bear in mind that we will only describe the default keymap."""))
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
### Add view conversation shortcut info, if any.
documentation.append(_(u"""* Control + M: Hide the GUI."""))
documentation.append(_(u"""* Control + N: Compose a new tweet."""))
documentation.append(_(u"""* Control + R: Reply / mention."""))
documentation.append(_(u"""* Control + Shift + R: Retweet."""))
documentation.append(_(u"""* Control + D: Send a direct message."""))
documentation.append(_(u"""* control + F: Add tweet to favourites."""))
documentation.append(_(u"""* Control + Shift + F: Remove a tweet from favourites."""))
documentation.append(_(u"""* Control + S: Open the user actions dialogue."""))
### Add shortcut info for user details, if any.
documentation.append(_(u"""* Control + Shift + V: Show tweet."""))
documentation.append(_(u"""* Alt + F4: Quit from Tw Blue."""))
documentation.append(_(u"""* Control + I: Open user timeline."""))
documentation.append(_(u"""* Control + Shift + i: Destroy buffer."""))
documentation.append(_(u"""* F5: Increase volume by 5%."""))
documentation.append(_(u"""* F6: Decrease volume by 5%."""))
documentation.append(_(u"""* Control + P: Edit your profile."""))
documentation.append(_(u"""* Control + Delete: Delete a tweet or direct message."""))
documentation.append(_(u"""* Control + Shift + Delete: Empty the current buffer."""))
### Add shortcut info for add to list, remove from list, mute buffer, mute session, autoread, search, keystroke editor, show lists for specified user, load previous items, show geolocation information, display geolocation information in a dialog and  create a trending topics buffer, if any
documentation.append(_(u"""
"""))
documentation.append(_(u"""### Shortcuts of the invisible interface (default keymap)"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""* Control + Windows + Up: go up in the current buffer."""))
documentation.append(_(u"""* Control + Windows + Down: Go down in the current buffer."""))
documentation.append(_(u"""* Control + Windows + Left: Go to the previous buffer."""))
documentation.append(_(u"""* Control + Windows + Right: Go to the next buffer."""))
documentation.append(_(u"""* Control + Windows + Shift + Left: Focus the previous session."""))
documentation.append(_(u"""* Control + Windows + Shift + Right: Focus the next session."""))
documentation.append(_(u"""* Control + Windows + Shift + C: View conversation."""))
documentation.append(_(u"""* Control + Enter: Open URL."""))
documentation.append(_(u"""* Control + Windows + Enter: Play audio."""))
documentation.append(_(u"""* Control + Windows + M: Show or hide the GUI."""))
documentation.append(_(u"""* Control + Windows + N: New tweet."""))
documentation.append(_(u"""* Control + Windows + R: Reply / Mention."""))
documentation.append(_(u"""* Control + Windows + Shift + R: Retweet."""))
documentation.append(_(u"""* Control + Windows + D: Send direct message."""))
documentation.append(_(u"""* Windows+ Alt + F: Mark as favourite."""))
documentation.append(_(u"""* Alt + Windows + Shift + F: Remove from favourites."""))
documentation.append(_(u"""* Control + Windows + S: Open the user actions dialogue."""))
documentation.append(_(u"""* Control + Windows + Alt + N: See user details."""))
documentation.append(_(u"""* Control + Windows + V: Show tweet."""))
documentation.append(_(u"""* Control + Windows + F4: Quit from Tw Blue."""))
documentation.append(_(u"""* Open user timeline: Control + Windows + I: Open user timeline."""))
documentation.append(_(u"""* Control + Windows + Shift + I: Destroy buffer."""))
documentation.append(_(u"""* Control + Windows + Alt + Up: Increase volume by 5%."""))
documentation.append(_(u"""* Control + Windows + Alt + Down: Decrease volume by 5%."""))
documentation.append(_(u"""* Control + Windows + Home: Jump to the first element of the current buffer."""))
documentation.append(_(u"""* Control + Windows + End: Jump to the last element of the current buffer."""))
documentation.append(_(u"""* Control + Windows + PageUp: Jump 20 elements up in the current buffer."""))
documentation.append(_(u"""* Control + Windows + PageDown: Jump 20 elements down in the current buffer."""))
documentation.append(_(u"""* Windows + Alt + P: Edit profile."""))
documentation.append(_(u"""* Control + Windows + Delete: Delete a tweet or direct message."""))
documentation.append(_(u"""* Control + Windows + Shift + Delete: Empty the current buffer."""))
documentation.append(_(u"""* Control + Windows + Space: Repeat last item."""))
documentation.append(_(u"""* Control + Windows + C: Copy to clipboard."""))
documentation.append(_(u"""* Control + Windows+ A: Add user to list."""))
documentation.append(_(u"""* Control + Windows + Shift + A: Remove user from list."""))
documentation.append(_(u"""* Control + Windows + M: Mute / unmute the current buffer."""))
documentation.append(_(u"""* Windows + Alt + M: Mute / unmute the current session."""))
documentation.append(_(u"""* Control + Windows + E: Toggle the automatic reading of incoming tweets in the current buffer."""))
documentation.append(_(u"""* Control + Windows + -: Search on Twitter."""))
documentation.append(_(u"""* Control + Windows + K: Show the keystroke editor."""))
documentation.append(_(u"""* Control + Windows + L: Show lists for a specified user."""))
documentation.append(_(u"""* Windows + Alt + PageUp: Load previous items for the current buffer."""))
documentation.append(_(u"""* Control + Windows + G: Get geolocation."""))
documentation.append(_(u"""* Control + Windows + Shift + G: Display the tweet's geolocation in a dialogue."""))
documentation.append(_(u"""* Control + Windows + T: Create a trending topics' buffer."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""## Configuring Tw Blue"""))
documentation.append(_(u"""As described above, Tw Blue has two configuration dialogues, the global settings dialogue and the account settings dialogue."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""### The account settings dialogue"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""#### General tab"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""* Autocompletion settings: Allows you to configure the autocompletion database. You can add users manually or let Tw Blue add your followers, friends or both."""))
documentation.append(_(u"""* Relative timestamps: Allows you to configure whether Tw Blue will calculate the time the tweet or direct message was sent or received based on the current time, or simply say the time it was received or sent."""))
documentation.append(_(u"""* API calls: Allows you to adjust the number of API calls to send to Twitter by Tw Blue."""))
documentation.append(_(u"""* Items on each API calls: Allows you to specify how many items should retrieved from Twitter for each API call (default and maximum is 200)."""))
documentation.append(_(u"""* Inverted buffers: Allows you to specify whether the buffers should be inverted, which means that the oldest items will show at the end of them and the newest at the beginning."""))
documentation.append(_(u"""* Retweet mode: Allows you to specify  the behaviour when doing a retweet: you can choose  between retweeting with a comment, retweeting without comment or being asked."""))
documentation.append(_(u"""* Number of items per buffer to cache in database: This allows you to specify how many items should Tw Blue cache in a database. YOu can type any number, 0 to cache all items, or leave blank to disable caching entirely."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""#### buffers tab"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""In this tab, you get a list for each buffer you have in Tw Blue, except for searches, timelines, favourites'' timelines and lists. You can show, hide and move them."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""#### The ignored clients tab"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""In this tab, you can add and remove clients to be ignored by Tw Blue."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""#### Sound tab"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""In this tab, you can adjust the sound volume, select the input and output device and set the soundpack used by Tw Blue."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""#### Audio service tab"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""In this tab, you can enter your SndUp API key (if you have one) to upload audio to SndUp with your account. Otherwhise you will upload announimously."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""### Global settings"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""This dialogue allows to configure some settings which will affect the entire application."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""#### General tab"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""* Language: This allows you to change the language of Tw Blue. Currently supported languages are arabic, Catalan, German, English, Spanish, Basque, Finnish, French, Galician, Croatian, Hungarian, Italian, Polish, Portuguese, Russian and Turkish."""))
documentation.append(_(u"""* Ask before exiting Tw Blue: This checkbox allows you to control whether Tw Blue will ask for confirmation before exiting."""))
documentation.append(_(u"""* Play a sound when Tw Blue launches: This checkbox allows to configure whether Tw Blue will play a sound when it has finished loading the buffers."""))
documentation.append(_(u"""* Speak a message when Tw Blue launches: The same as the previous option, but this checkbox configures whether the screen reader will say \"ready\"."""))
documentation.append(_(u"""* Use the invisible interface's shortcuts in the GUI: As the invisible interface and the Graphical User Interface have  their own shortcuts, you may want to use the invisible interface's ones all the time. If this option is checked, the invisible  interface's shortcuts ''will be usable in the GUI."""))
documentation.append(_(u"""* Activate SAPI5 when any other screen reader is not being run: This checkbox allows to activate SAPI 5 TTS when no other screen reader is being run."""))
documentation.append(_(u"""* Hide GUI on launch: This allows you to configure whether Tw Blue whould start with the GUI or the invisible interface."""))
documentation.append(_(u"""* Keymap: This options allows you to change the keymap used by Tw Blue in the invisible interface. The shipped keymaps are Default, Qwitter, TheQube and Chicken Nugget. The keymaps are in the \"keymaps\" folder, and you can create new ones. Just create a new \".keymap\" file and change the keystrokes associated with the actions, as it is done in the shipped keymaps."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""#### Proxi tab"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""In this tab you can configure Tw Blue to use a Proxi server by filling the fields in it (server, port, user and password)."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""## License, source code and donations"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""Tw Blue is under the GNU GPL icense, version 2. You can view the license in the file named license.txt, or online at <http://www.gnu.org/licenses/old-licenses/gpl-2.0.html>."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""The source code of the program is available on GitHub at <https://www.github.com/manuelcortez/twblue>."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""If you want to donate to the project, you can do so at <http://twblue.es/?q=node/3&language=en>. Thank you for your support!"""))
documentation.append(_(u"""...
"""))
documentation.append(_(u"""## Contact"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""If what's explained in this document is not enough, if you want to collaborate in some other way, or if you simply want to get in touch with the application developer, follow the Twitter account [@tw_blue2](https://twitter.com/tw_blue2)  or [@manuelcortez00.](https://twitter.com/manuelcortez00) You can also visit [our website](http://twblue.es)"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""---"""))
documentation.append(_(u"""Copyright © 2013-2015. Manuel Cortéz"""))
