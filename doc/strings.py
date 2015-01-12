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
documentation.append(_(u"""You're reading documentation produced for a program still in development. The object of this manual is explaining some details of the operation of the program. Bear in mind that as the software is in the process of active development, parts of this document may change in the near future, so it is advisable to keep an eye on it from time to time to avoid missing too much out."""))
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
documentation.append(_(u"""First off, it's necessary to authorise the program so it can access your Twitter account and act on your behalf. The authorisation process is quite simple, and the program never gets data such as your username and password. In order to authorise the application, you just need to run the main executable file, called TWBlue.exe (on some computers it may appear simply as TWBlue)."""))
documentation.append(_(u"""
"""))
#$documentation.append(_(u"""When executed, if you have not previously configured the program, it will show a dialogue box where it tells you'll be taken to Twitter in order to authorise the application as soon as you press OK. To begin the authorisation process, press the only available button on the box."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""Your default browser will open on the Twitter page to request authorisation. Enter your user name and password if you're not already logged in, look for the authorise button, and press it."""))
documentation.append(_(u"""
"""))
#$documentation.append(_(u"""Read the instructions you will get if the process is successful. In summary, you will be given a numeric code with several digits you must paste on an edit field open by the application on another window."""))
#$documentation.append(_(u"""
#$"""))
#$documentation.append(_(u"""Paste the verification code, and press the enter key. """))
#$documentation.append(_(u"""
#$"""))
### Add here the instructions on how to deal with the session manager.
documentation.append(_(u"""If all went well, the application will start playing sounds, indicating your data are being updated."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""When the process is finished,the program will play another sound, and the screen reader will say "ready"."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""## The program's interface"""))
documentation.append(_(u"""
"""))
### Add the new GUI description here
#$documentation.append(_(u"""The easiest way to describe the graphical interface of the application is a window with a menu bar with five menus (application, tweet, user, buffer and help), a list with several elements, and, in most cases, three buttons: tweet, retweet and reply. The actions available for each element are described below."""))
#$documentation.append(_(u"""
#$"""))
#$documentation.append(_(u"""Elements on the lists may be tweets, direct messages or users. TW Blue creates different tabs for each list, which can be sent tweets, main timeline tweets, favourites, or direct messages, and each tab contains a single type of tweet. These tabs are called lists or buffers."""))
#$documentation.append(_(u"""
#$"""))
#$documentation.append(_(u"""To switch from list to list press control-tab to go forward, and control-shift-tab to go back. Screen readers will announce the list that gains the focus at all times. These are the basic lists of TW Blue, which are configured by default."""))
#$documentation.append(_(u"""
#$"""))
documentation.append(_(u"""* Home: it shows all the tweets on the main timeline. These are the tweets by users you follow."""))
documentation.append(_(u"""* Mentions: if a user, whether you follow them or not, mentions you on Twitter, you will find it on this list."""))
documentation.append(_(u"""* Direct messages: here go the private direct messages you exchange with users you follow and who follow you back. This list only shows received messages."""))
documentation.append(_(u"""* Sent: it shows all the tweets and direct messages sent from your account."""))
documentation.append(_(u"""* Favourites: here you will see all tweets you have favourited."""))
documentation.append(_(u"""* Followers: when users follow you, you'll be able to see them on this list, with some of their account information."""))
documentation.append(_(u"""* Friends: the same as the previous list, but these are the users you follow."""))
documentation.append(_(u"""* User timelines: these are lists you may create. They contain only the tweets by a specific user. They're used so you can see the tweets by a single person and you don't want to look all over your timeline. You may create as many as you like."""))
documentation.append(_(u"""* Events: An event is anything that happens on Twitter, such as when someone follows you, when someone adds or removes one of your tweets from their favorites list, or when you subscribe to a list.  There are many more but TW Blue shows the most common ones in the events buffer so that you can easily keep track of what is happening on your account."""))
documentation.append(_(u"""* Lists: A list is similar to a temporary timeline, except that you can configure it to contain tweets from multiple users."""))
documentation.append(_(u"""* Search: A search buffer contains the results of a search operation."""))
documentation.append(_(u"""* User favorites: You can have TW Blue create a buffer containing tweets favorited by a particular user."""))
### add here the trending buffers description.
documentation.append(_(u"""
"""))
#$documentation.append(_(u"""Note: In this version of TW Blue, you will be able to see up to (or around) 400 friends and followers in their respective buffers.  In the next version, we will provide a solution for those who have more to be able to see them."""))
#$documentation.append(_(u"""
#$"""))
#$documentation.append(_(u"""Bear in mind the default configuration only allows getting the last 200 tweets for the home,, mentions, direct messages, and user timeline lists. You can change this on the setup dialogue. For the sent list, the last 200 tweets and the last 200 sent direct messages will be retrieved. Future versions will allow changing this parameter."""))
#$documentation.append(_(u"""
#$"""))
documentation.append(_(u"""If there's a URL on a tweet TW Blue will try to open it when you press enter on it. If there are several, it will show you a list with all of them so you choose the one you want. If you're on the followers or friends buffer, the enter key will show you additional information on them."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""If you press control-enter, TW Blue will try to play the audio from the focused tweet, as long as it has a URL. If it has the #audio hashtag, you will hear a sound when it is selected, letting you know you can try to play it. However, a tweet can be missing the hashtag and TW Blue will still be able to play it so long as it contains a URL with audio."""))
documentation.append(_(u"""
"""))
### Add information about the GEO location in tweets.
documentation.append(_(u"""## Controls"""))
documentation.append(_(u"""
"""))
### add more information about using invisible shorcuts in the GUI mode in the next variable.
documentation.append(_(u"""Beginning with the 0.36 version, there's support for an interface which does not require a visible window. It can be activated by pressing control-m, or choosing hide window from the application menu. This interface is entirely driven through shortcut keys. These shortcuts are different from those used to drive the graphical interface.  This section describes both the graphical and the invisible interface."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""### The graphical user interface (GUI)"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""Here you have a list divided into two parts. On the one hand, the buttons you will find while tabbing around on the program's interface, and on the other, the different elements present on the menu bar."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""#### Buttons on the application"""))
documentation.append(_(u"""
"""))
### Add information on spell correction, translate, attach images and audio.
documentation.append(_(u"""* Tweet: this button opens up a dialogue box to write your tweet. The message must not exceed 140 characters. If you write past this limit, a sound will play to warn you. You may use the shorten and expand URL buttons to comply with the character limit. Press enter to send the tweet. If all goes well, you'll hear a sound confirming it. Otherwise, the screen reader will say an error message in English describing the problem."""))
documentation.append(_(u"""* Retweet: this button retweets the message you're reading. After you press it, you'll be asked if you want to add a comment or simply send it as written."""))
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
documentation.append(_(u"""* Update profile: opens a dialogue box where you can update your information on Twitter: name, location, URL and bio. If you have already set this up the fields will be prefilled with the existing information. Also, you can upload a photo to your profile."""))
documentation.append(_(u"""* Hide window: turns off the Graphical User Interface. Read the section on the invisible interface for further details."""))
documentation.append(_(u"""* Search: shows a dialog where you can search for tweets or users on Twitter."""))
documentation.append(_(u"""* Lists Manager: This dialog allows you to manage your Twitter lists.  In order to use them, you must first create them.  Here, you can view, edit, create, delete or, optionally, open them in buffers similar to temporary timelines."""))
documentation.append(_(u"""* Sound tutorial: Opens a dialog where you can familiarize yourself with the different sounds of the program."""))
documentation.append(_(u"""* Preferences: opens up a preference dialogue box from which you can control some of the program settings. The options need no explanation."""))
documentation.append(_(u"""* Quit: asks whether you want to exit the program. If the answer is yes, it shuts the application down."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""##### Tweet menu {#tweet}"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""* You will first find the items to tweet, reply and retweet, which are equivalent to the buttons with the same name."""))
documentation.append(_(u"""* Mark as favourite: marks the tweet you're viewing as a favourite."""))
documentation.append(_(u"""* Remove tweet from favourites: removes the tweet from your favourites, but not from Twitter."""))
documentation.append(_(u"""* Show tweet: opens up a dialogue box where you can read the tweet, direct message, friend or follower under focus. You can read the text with the cursors. It's the same dialogue box used to write tweets on."""))
documentation.append(_(u"""* Delete: permanently removes the tweet or direct message you're on from Twitter and from your lists. Bear in mind that Twitter only allows you to delete tweets you have posted yourself."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""##### User menu {#user}"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""Bear in mind the four topmost items on this menu open up the same dialogue box. This box has an edit field where you can choose the user you want to act on, by using up and down arrows or by writing the text in yourself. Afterwards you will find a group with four radio buttons to follow, unfollow, report as spam and block. If you choose the follow menu item, the radio button on the dialogue box will be set to follow, and the same applies to unfollow, report as spam and block. Press OK to try to carry out the action. If it doesn't succeed, you'll hear the error message in English."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""The remaining items on the menu are described below:"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""* Direct message: same action as the button."""))
documentation.append(_(u"""* Add to List: In order to see someone's tweets in one or more of your lists, you must add them first.  This option will open a dialog where you can select the user you wish to add.  Next, you will be asked to select the list you wish to add them to.  Afterwards, the list will contain a new member and their tweets will show up there."""))
documentation.append(_(u"""* View user profile: opens up a dialogue box to choose the user whose profile you want to browse."""))
documentation.append(_(u"""* Timeline: opens up a dialogue box to choose whose user you want a timeline for. Create it by pressing enter. If you try it with a user that has no tweets, the program will fail. If you try creating an already existing timeline the program will warn you and will not create it again."""))
documentation.append(_(u"""* View favourites: Opens a buffer where you can see what tweets have been favorited by a particular user."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""##### Buffer menu{#buffer}"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""* Mute buffer: Mutes notifications of a particular buffer so you will not hear when new tweets arrive."""))
documentation.append(_(u"""* autoread tweets for this buffer: When enabled, the screen reader or SAPI 5 (if enabled) will read the text of incoming tweets.  Please note that this could get rather chatty if there are a lot of incoming tweets."""))
documentation.append(_(u"""* Clear buffer: Deletes all items from the buffer."""))
documentation.append(_(u"""* Remove buffer: dismiss the list you're on."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""##### Help menu {#help}"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""* Documentation: opens up this file, where you can read some useful program concepts."""))
documentation.append(_(u"""* What's new in this version?: opens up a document with the list of changes from the current version down to the first."""))
documentation.append(_(u"""* Check for updates: every time you open the program it automatically checks for new versions. If there are, it will ask you if you want to download it. If you accept, it will do so, after which it will install it and ask you to let it restart itself, which it does automatically. This item checks for new updates without having to restart the application."""))
documentation.append(_(u"""* TW Blue's website: visit our [home page](http://twblue.com.mx) where you can find all relevant information and downloads for TW Blue and become a part of the community."""))
documentation.append(_(u"""* Report a bug: opens up a dialogue box to report a bug by filling a couple of fields: the title and a short description of what happened. Pressing enter will send the report. If the operation doesn't succeed the program will show a warning."""))
documentation.append(_(u"""* About TW Blue: shows the credits of the program."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""### Invisible interface {#invisible_interface}"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""If you press control-m, or if you choose hide window from the application menu, you will activate an interface that cannot be used in the usual way, because it is invisible."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""Every action on the invisible interface is done through keyboard shortcuts, even browsing lists. Eventually you may open dialogue boxes and these will be visible, but not the application's main window. Read the section on invisible interface shortcuts to know which ones you can use for the time being."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""### Keyboard shortcuts for the graphical interface {#shortcuts}"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""Instead of using the buttons and menus, most actions can be carried out by pressing a key combination. The ones available at present are described below:"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""* Enter: open a URL. If there are more than one you will get a list that will allow you to choose the one you want. On the friends or followers lists it will show details on the selected item."""))
documentation.append(_(u"""* Control-enter: attempt to play audio from URL."""))
documentation.append(_(u"""* F5: decrease sounds volume. It affects the program sounds as well as audio played from the program."""))
documentation.append(_(u"""* F6: increase application sounds volume."""))
documentation.append(_(u"""* Control-n: open new tweet dialogue."""))
documentation.append(_(u"""* Control-m: hide window."""))
documentation.append(_(u"""* Control-q: quit."""))
documentation.append(_(u"""* Control-r: open reply tweet dialogue."""))
documentation.append(_(u"""* Control-shift-r: Retweet."""))
documentation.append(_(u"""* Control-d: send direct message."""))
documentation.append(_(u"""* Control-f: mark as favourite."""))
documentation.append(_(u"""* Control-shift-f: remove from favourites."""))
documentation.append(_(u"""* Control-shift-v: view tweet."""))
documentation.append(_(u"""* Control-s: follow a user."""))
documentation.append(_(u"""* Control-shift-s: unfollow a user."""))
documentation.append(_(u"""* Control-k: block a user."""))
documentation.append(_(u"""* Control-shift-k: report as spam."""))
documentation.append(_(u"""* Control-i: open user's timeline."""))
documentation.append(_(u"""* Control-shift-i: remove timeline."""))
documentation.append(_(u"""* Control-p: edit profile."""))
documentation.append(_(u"""* Delete: remove tweet or direct message."""))
documentation.append(_(u"""* Shift-delete: empty the buffer removing all the elements. This doesn't remove them from Twitter itself."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""### Keyboard shortcuts for the invisible interface {#invisible_shortcuts}"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""These are the shortcuts you may use from the invisible interface. Bear in mind that when the graphical user interface is shown you may not use these. By "win" the left windows key is intended."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""* Control+win+up arrow: go up on the current list."""))
documentation.append(_(u"""* Control+win+down arrow: go down on the current list."""))
documentation.append(_(u"""* Control+win+left arrow: go to the previous tab."""))
documentation.append(_(u"""* Control+win+right arrow: go to the next tab."""))
documentation.append(_(u"""* Control+win+home: go to the first element on the list."""))
documentation.append(_(u"""* Control+win+end: go to the last element on the list."""))
documentation.append(_(u"""* Control+win+page down: move 20 elements down on the current list."""))
documentation.append(_(u"""* Control+win+page up: move 20 elements up on the current list."""))
documentation.append(_(u"""* Control+win+alt+up arrow: increase volume by 5%."""))
documentation.append(_(u"""* control+win+alt+down arrow: decrease volume by 5%."""))
documentation.append(_(u"""* Control+win+enter: open URL on the current tweet, or further information for a friend or follower."""))
documentation.append(_(u"""* control+win+alt+enter: attempt to play audio."""))
documentation.append(_(u"""* control+win+m: show the graphical interface, turning the invisible one off."""))
documentation.append(_(u"""* Control+win+n: new tweet."""))
documentation.append(_(u"""* Control+win+r: reply to tweet."""))
documentation.append(_(u"""* Control+win+shift-r: retweet."""))
documentation.append(_(u"""* Control+win+d: send direct message."""))
documentation.append(_(u"""* Control+win+delete: remove a tweet or direct message."""))
documentation.append(_(u"""* Control+win+shift+delete: empty the buffer removing all the elements. This doesn't remove them from Twitter itself."""))
documentation.append(_(u"""* Win+alt+f: mark as favourite."""))
documentation.append(_(u"""* Win+alt+shift+f: remove from favourites."""))
documentation.append(_(u"""* Control+win+s: follow a user."""))
documentation.append(_(u"""* Control+win+shift+s: unfollow a user."""))
documentation.append(_(u"""* Control+win+alt+n: see user details."""))
documentation.append(_(u"""* Control+win+v: show tweet on an edit box."""))
documentation.append(_(u"""* Control+win+i: open user timeline."""))
documentation.append(_(u"""* Control+win+shift+i: remove user timeline."""))
documentation.append(_(u"""* Alt+win+p: edit profile."""))
documentation.append(_(u"""* Control+win+c: Copy to clipboard."""))
documentation.append(_(u"""* Control+win+space: Listen the current message."""))
documentation.append(_(u"""* Control+win+a: Add to list."""))
documentation.append(_(u"""* Control+win+shift+a: Remove from list."""))
documentation.append(_(u"""* Control+Win+Shift+M: Mutes/unmutes the active buffer."""))
documentation.append(_(u"""* Control+Win+E: toggles the automatic reading of incoming tweets in the active buffer."""))
documentation.append(_(u"""* Control+Win+Shift+Up arrow: move up one tweet in the conversation."""))
documentation.append(_(u"""* Control+Win+Shift+Down arrow: move down one tweet in the conversation."""))
documentation.append(_(u"""* Win+Alt+M: Globally mute/unmute TW Blue."""))
documentation.append(_(u"""* control+win+minus: Search on twitter."""))
documentation.append(_(u"""* Control+win+f4: quit."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""## Lists {#lists}"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""One of the most useful features of Twitter is the ability to create lists.  Lists allow you to group users whose tweets you wish to see together instead of viewing their individual buffers.  A common example of this would be if you follow multiple tech news accounts; it would be more convenient to have, for example, a "Tech News" list in which you can see tweets from these similar accounts together.  A temporary buffer, such as what is created when you are viewing an individual person's timeline, is created and you can add/remove people from the list."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""In TW Blue, we have begun working on this feature little by little.  It is still experimental but is in working condition.  Below, we will explain how to configure lists."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""* First, you will need to open the lists manager which can be found under the application menu."""))
documentation.append(_(u"""* In the lists manager, you will first see the lists you have created followed by those which you are a member.  If you see no lists, it means that you have not created any and that you are not a part of any list."""))
documentation.append(_(u"""* You will then see a group of buttons: Create a New List, Edit, Remove and Open in Buffer.  Perhaps the last one is a bit less self-explanatory: it will open the list in a buffer similar to when opening someone's timeline.  """))
documentation.append(_(u"""
"""))
documentation.append(_(u"""Once you have created a new list, the next step will be to add users to it.  If you were to open it in a buffer right now, it would be empty and no tweets would show up in it.  To add users, follow these steps:"""))
documentation.append(_(u"""* While browsing your tweets, find a tweet from the user which you wish to add to a list.  Next, press ctrl+win+A or select "Add to List" from the User menu."""))
documentation.append(_(u"""* A dialog will then appear asking for the user which you wish to add.  The name of the user whose tweet you just selected should already be in the box.  Simply confirm that it is correct and press the "OK" button."""))
documentation.append(_(u"""* Another dialog will appear showing all of your lists.  Arrow to the one you want and press the "Add" button."""))
documentation.append(_(u"""* To remove a user from a list, repeat the same process but press ctrl+win+shift+A and, from the dialog that appears, choose the list from which you wish to remove the selected user."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""## Reporting bugs from the web {#reporting}"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""Note: if you're running the program you can also report a bug from it, by using the help menu item. This process only allows for two edit fields and takes care of the rest. These steps are described for those who can't run the program, don't have it opened at a given moment, or simply want to report from the web instead of using the integrated bug reporting system."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""All things under the sun (yes, this includes computer programs) are very far from being perfect, so often you may find unforeseen bugs in the application. But as our intent is to always improve you're free (what's more, it would be great if you did) to report the bugs you find on the program so they can be reviewed and eventually fixed"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""In order to open the bug tracker's web, [follow this link](http://twblue.com.mx/errores/bug_report_page.php) It's a website with a form where you must fill several fields. Only three of them are really required (those marked with a star), but the more you can fill the better."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""Here are the different form fields and what you must enter on each. Remember only fields mark witha  star are required:"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""* Category: this field allows to choose what category to assign the bug to. You can choose general, if it's a program error, or documentation, if you have found a mistake in this manual or the changes list. This is a required field."""))
documentation.append(_(u"""* Reproducibility: here you must indicate how easy or hard it is to reproduce the bug. Available options are unknown, not reproducible, not attempted (by default), random, sometimes, or always. Depending on whether you can reproduce the error or not, you should choose the one closest to your situation. If you're making a feature request, this field is irrelevant."""))
documentation.append(_(u"""* Severity: here you choose how much it affects the program. Available options are functionality (choose this for a feature request), trivial, text, setting, minor, major, failure, or crash. Note the options go in increasing order. Choose the one which fits the situation best. If you're not sure which to choose you can leave it as it is."""))
documentation.append(_(u"""* Priority: choose according to the importance of the bug or feature requested. Available options are none, low, normal, high, urgent, and immediate."""))
documentation.append(_(u"""* Choose profile: here you can choose between 32 or 64 bit architecture and OS (Windows 7 for now). If they don't fit, you can fill the edit fields below with your specific information."""))
documentation.append(_(u"""* Product version: choose the version of the program you're running in order to find out when the error was introduced. This field will contain a sorted list of the available versions. Although it's not required, it would help a lot in quickly finding the bug."""))
documentation.append(_(u"""* Summary: a title for the bug, explaining in a few words what the problem is. It's a required text field."""))
documentation.append(_(u"""* Description: this required field asks you to describe in more detail what happened to the program."""))
documentation.append(_(u"""* Steps to reproduce: this field is used if you know how to cause the error. It's not required, but it would help a lot knowing how the program gets to the error in order to track it down."""))
documentation.append(_(u"""* Additional information: if you have a comment or note to add, it can go here. It's not required."""))
documentation.append(_(u"""* File attachment: you can attach the TW Blue.exe.log generated due to the bug. It is not required."""))
documentation.append(_(u"""* Visibility: choose if you want the bug to be publically visible or private. By default it's public, and it's recommended to keep it that way."""))
documentation.append(_(u"""* Send report: press the button to send the report and have it looked into."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""Many thanks for your participation in reporting bugs and trying out new functionality."""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""## Contact {#contact}"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""If what's explained in this document is not enough, if you want to collaborate in some other way, or if you simply want to get in touch with the application developer, follow the Twitter account [@tw_blue2](https://twitter.com/tw_blue2)  or [@manuelcortez00.](https://twitter.com/manuelcortez00) You can also visit [our website](http://twblue.com.mx)"""))
documentation.append(_(u"""
"""))
documentation.append(_(u"""---"""))
documentation.append(_(u"""Copyright © 2013-2014. Manuel Cortéz"""))
