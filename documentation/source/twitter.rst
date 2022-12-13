Twitter
-------

Twitter is a social networking or micro-blogging tool which allows you to compose short status updates of your activities in 280 characters or less. Twitter is a way for friends, family and co-workers to communicate and stay connected through the exchange of quick, frequent messages. You can restrict delivery of updates to those in your circle of friends or, by default, allow anyone to access them.

You can monitor the status of updates from your friends, family or co-workers (known as following), and they in turn can read any updates you create, (known as followers). The updates are referred to as Tweets. The Tweets are posted to your Twitter profile or Blog and are searchable using Twitter Search.

In order to use TWBlue, you must first have created an account on the Twitter website. The process for signing up for a Twitter account is very accessible. During the account registration, you will need to choose a Twitter username. This serves two purposes. This is the method through which people will comunicate with you, but most importantly, your username and password will be required to connect TWBlue to your Twitter account. We suggest you choose a username which is memorable both to you and the people you hope will follow you.

We'll start from the premise that you have a Twitter account with its corresponding username and password.

authorizing TWBlue
==================

First of all, it's necessary to authorise the program so it can access your Twitter account and act on your behalf. The authorisation process is quite simple, and the program never retains data such as your password. In order to authorise the application, you just need to run the main executable file, called TWBlue.exe (on some computers it may appear simply as TWBlue if Windows Explorer is not set to display file extensions). We suggest you may like to place a Windows shortcut on your Desktop pointing to this executable file for quick and easy location.

You can log into several Twitter accounts simultaneously. The program refers to each Twitter account you have configured as a "Session". If this is the first time you have launched TWBlue, and if no Twitter session exists, you will see the Session Manager. This dialogue box allows you to authorise as many accounts as you wish. If you press the Tab key to reach the "new account" button and activate it by pressing the Space Bar, you will see a menu with all available services to configure in TWBlue. By choosing Twitter, a dialogue box will advise you that your default internet browser will be opened in order to authorise the application and you will be asked if you would like to continue. Activate the "yes" Button by pressing the letter "Y" so the process may start.

Your default browser will open on the Twitter page to request authorisation. Enter your username and password into the appropriate edit fields if you're not already logged in, select the authorise button, and press it.

Once you've authorised your twitter account, the website will redirect you to a page which will notify you that TWBlue has been authorised successfully. On this page, you will be shown a code composed of several numbers that you must paste in the TWBlue authorization dialogue in order to allow the application to access your account. Once you have pasted the code in the corresponding text field, press enter to finish the account setup and go back to the session manager. On the session list, you will see a new item temporarily called "Authorised account x" -where x is a number. The session name will change once you open that session.

To start running TWBlue, press the Ok button in the Session Manager dialogue. By default, the program starts all the configured sessions automatically, however, you can change this behavior.

If all went well, the application will start playing sounds, indicating your data is being updated.

When the process is finished, by default the program will play another sound, and the screen reader will say "ready" (this behaviour can be configured).

Buffer types
============

The following is a description for every one of TWBlue's buffers available for Twitter sessions, and the kind of items they work with.

* Home: this shows all the tweets on the main timeline. These are the tweets by users you follow.
* Mentions: if a user, whether you follow them or not, mentions you on Twitter, you will find it in this list.
* Direct messages: here you will find the private direct messages you exchange with users who follow you , or with any user, if you allow direct messages from everyone (this setting is configurable from Twitter). This list only shows received messages.
* Sent direct messages: this buffer shows all the direct messages sent from your account.
* Sent tweets: this shows all the tweets sent from your account.
* Likes: here you will see all the tweets you have liked.
* Followers: when users follow you, you'll be able to see them on this buffer, with some of their account details.
* Following: the same as the previous buffer, but these are the users you follow.
* Muted users: when you mute someone in Twitter, you no longer see their tweets in any of your buffers. However, you still can receive direct messages from them. This buffer contains the list of your muted users.
* Blocked users: Contains a list with all people you have blocked in Twitter. When blocking an user, they cannot see your profile, timelines or exchange direct messages with your account.
* User timelines: these are buffers you may create. They contain only the tweets by a specific user. They're used so you can see the tweets by a single person and you don't want to look all over your timeline. You may create as many as you like.
* Lists: A list is similar to a user timeline, except that you can configure it to contain tweets from multiple users.
* Search: A search buffer contains the results of a search operation.
* User likes: You can have the program create a buffer containing tweets liked by a particular user.
* Followers or following timeline: You can have TWBlue create a buffer containing all users who follow, or are followed by a specific user.
* Trending Topics: a trend buffer shows the top 50 most used terms in a geographical region. This region may be a country or a city. Trends are updated every five minutes.

If a tweet contains a URL, you can press enter in the GUI to open it. If it contains video or audio, including live stream content, you can press Control + Enter to play it, respectively. TWBlue will play a sound if the tweet contains video metadata or the \#audio hashtag, but there may be tweets which contain media without this.

Actions
=======

The available actions for each buffer may vary, and are found by pressing the Tab key, once a specific buffer has been focused. Note that these are not all the actions available for the Twitter session in TWBlue. Generally, you can perform the actions you want from 3 different ways: 

* In each buffer, by pressing the Tab key until you find the action panel.
* By using the menu bar, which can be accessed by pressing the Alt key.
* Using the keyboard shortcuts, either from the graphical interface or the invisible interface.

You can find more information on the meaning of these actions later in this topic:

* For all sessions, you can log in or log out of TWBlue, as well as control whether the session should start automatically when you start the application.
* For buffers containing tweets (home, mentions, favorites, timelines and searches), you can write a new tweet, reply to the currently selected tweet, retweet it or send a direct message to the user who wrote it.
* For buffers containing direct messages, you can reply to the selected direct message.
* For buffers containing users (followers, following, blocked users, muted, timelines and searches), the available actions are to mention the selected user, send a direct message or open the actions dialog for that user.
* Buffers showing trends allow you to write a Tweet about the selected trend.

Context menus
==============

By pressing the contextual menu key, or the right mouse button on a focused item, TWBlue will display a list of some actions that can be performed on it. These actions will be different depending on the type of item that is selected (for example, tweets allow you to retweet them, while a trend will allow you to perform a Twitter search on it). Below are the options that you will be able to see in the menus, sorted according to the type of element that is selected when displayed:

Tweets
++++++

* Retweet: this option retweets the message you're reading. After you press it, if you haven't configured the application not to do so, you'll be asked if you want to add a comment or simply send it as written. If you choose to add a comment,  it will post a quoted tweet, that is,  the comment with a  link to the originating tweet.
* Reply: when you're viewing a tweet, you can reply to the user who sent it by pressing this option. A dialogue will open up similar to the one for tweeting. If there are more users referred to in the tweet, you can press tab and activate the mention to all checkbox, or enabling checkbox for the users you want to mention separately. Note, however, that sometimes -especially when replying to a retweet or quoted tweet, the user who made the retweet or quote may also be mentioned. This is done by Twitter automatically.
* Like: Adds the tweet you're viewing to your likes list.
* Unlike: removes the tweet from your likes, but not from Twitter.
* Open URL: if the focused tweet contains URL addresses, shows up a dialogue where you can choose which one to open in the default web browser. Bear in mind that if the tweet contains only one URL, it will open it automatically.
* Open in Twitter: Opens the focused tweet in Twitter's website.
* Play audio: if the focused tweet contains audio or video streams, shows up a dialogue where you can choose which one to play. TWBlue uses a reduced version of VLC media player to play most audio and video streams. Bear in mind that if the tweet contains only one audio or video URL, it will play it automatically.
* Show tweet: opens up a dialogue box where you can read the item which has focus. You can read the text with the arrow keys. It's a similar dialog box as used for composing tweets, without the ability to send the tweet, file attachment and autocompleting capabilities. It does however include a retweets and likes count.
* Copy to clipboard: copies focused item text to clipboard.
* Delete: permanently removes the tweet which has focus from Twitter and from your lists. Bear in mind that Twitter only allows you to delete tweets you have posted yourself.
* User actions: Opens a dialogue where you can interact with a user. This dialogue box will be populated with the user who sent the item in focus. User actions are described later.

Direct messages
++++++++++++++++

* Reply: Opens a direct message dialogue, from where you can reply to the focused direct message. Sending direct messages will be described later.
* Open URL: if the focused item contains URL addresses, shows up a dialogue where you can choose which one to open in the default web browser. Bear in mind that if the item contains only one URL, it will open it automatically.
* Play audio: if the focused item contains audio or video streams, shows up a dialogue where you can choose which one to play. TWBlue uses a reduced version of VLC media player to play most audio and video streams. Bear in mind that if the item contains only one audio or video URL, it will play it automatically.
* Show direct message: opens up a dialogue box where you can read the item which has focus. You can read the text with the arrow keys. It's a dialogue with the text to be read and a close button.
* Copy to clipboard: copies focused item text to clipboard.
* Delete: permanently removes the direct message which has focus from your account. Note that this will not remove the message from its recipient's account.
* User actions: Opens a dialogue where you can interact with a user. This dialogue box will be populated with the user who sent the item in focus. User actions are described later.

Users
++++++

* Direct message: Opens up a dialogue box from where it is possible to send a private message to the focused user.
* Show user profile: Opens up a dialog box from where it is possible to see details for the focused user. You can read the dialog by using the up and down arrow keys. If the user has a website in their profile, you can press tab and find a button to open it in your default browser.
* Show user:
* Open in Twitter: 
* Copy to clipboard:
* User actions:

Trending topics
+++++++++++++++

* Search topic:
* Tweet about this trend: 
* Show item:
* Copy to clipboard:

Posting Tweets
==============

Sending Direct messages
=======================

User actions
============

Timelines
=========

Trends
======

Searches
========

User aliases
==============

Lists management
===================

Account settings
=================

User Autocomplete
==================

Template editor
================

Filters
=======
