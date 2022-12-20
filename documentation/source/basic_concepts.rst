Basic concepts
----------------------

Before starting to describe TWBlue's usage, we'll explain some concepts that will be used extensively throughout this manual.

Session
++++++

A session is an account set up on a service. When you authorize TWBlue to use any of your social network accounts, a session will be created in the application. In this session, TWBlue creates buffers that allow you to display different types of items present in the social network. TWBlue allows you to have any number of sessions authorized and started. You can have TWBlue automatically start all your sessions, which is the default setting, although it is also possible to make certain sessions not start when you open the application.

Buffer
++++++

A buffer is a list of items that come from your configured account, after being processed by TWBlue. TWBlue will create buffers with different types of items. For example, your posts sent on a social network, or your private messages with other users. You can perform certain actions on each of these elements depending on the type of buffer you are focusing.

Graphical user Interface (GUI)
+++++++++++++++++++++++++++++++++

TWBlue has two different interfaces: The graphical user interface (GUI) and the invisible interface. The GUI allows you to interact with the application through a window containing two important elements: A menu bar, which can be accessed by pressing the Alt key, and the list of sessions, buffers and available actions for them, which you can access by pressing the Tab key.

The list of sessions and buffers is grouped in a tree view, where sessions are located at the root level and each session contains the buffers that belong to it. When you select one of these buffers, you can access the list of items it contains by using the Tab key. Depending on the selected buffer, you can find, also with the Tab key, a list of buttons representing actions you can perform on the session (such as posting a message on the social network) or on the focused item.

Invisible interface
++++++++++++++++++

The invisible interface, as its name suggests, has no graphical window and works directly with screen readers such as JAWS for Windows, NVDA and System Access through keyboard shortcuts that you can use in any window. This interface is disabled by default, but you can enable it by pressing Control + M, which will hide the TWBlue window. If you use other applications to manage Twitter, such as The Qube and chicken Nugget, TWBlue includes support for keymaps for these clients, which you can configure from the global options dialog. It is also possible to use the invisible interface from TWBlue's graphical window, although this option can be disabled to avoid conflicting with other applications that require the keyboard shortcuts globally.

Global settings and session settings
++++++++++++++++++++++++++++++++++++++++++++++

TWBlue has two different configuration dialogs: the global configuration dialog, which affects how TWBlue works for all sessions, and the session configuration dialog, which only affects how the current session works. You will find specific information about the session settings dialog for Twitter and Mastodon in its corresponding chapter in this guide.