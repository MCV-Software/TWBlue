TWBlue - Next generation
======

Note
======

Please note that this  branch is a new generation of TWBlue, so the code is been written using the MVC design pattern and it is very unstable. This code does not works properly and it is not recommended its use, only you use this code for testing purposes. You may find some huge bugs, because we're written most of the source code from scratch.

TWBlue, an accessible, open source and multiplatform twitter application. 

TW Blue is an app designed to use Twitter in a simple and fast way and avoiding, as far as possible, the consumtion of excessive resources of the machine where it’s running. With this app you’ll have access to twitter features such as:

* Create, reply to, retweet and delete tweets,
* Add and remove tweets from favourites,
* Send and delete direct messages,
* See your friends and followers,
* Follow, unfollow, block and report users as spam,
* Open a user’s timeline, which will allow you to get that user’s tweets separately,
* Open URL addresses when attached to a tweet or direct message,
* Play various file and URL types which contain audio
* and more!

See the [TWBlue's webpage](http://twblue.es) for more details.

## Using TWBlue from sources

This document describes how to run tw blue from source, and, after that, how to build a binary version, which doesn't need Python and the other dependencies to run.

### Required dependencies.

Although most dependencies can be found in the windows-dependencies directory, we provide links to their official websites. If you are cloning with git, don't forget to initialize and update the submodules to get the windows-dependencies folder. You can use these two commands to perform this task from git bash:  
    git submodule init  
    git submodule update

	All the dependencies provided in this folder are prebuilt. If you want to build them from source, you will need Microsoft visual Studio 2008.

#### Dependencies packaged in windows installers

* [Python,](http://python.org) version 2.7.9  
If you want to build both x86 and x64 binaries, you can install python x86 to C:\python27 and python x64 to C:\python27x64, for example.
* [wxPython](http://www.wxpython.org) for Python 2.7, version 3.0.2
* [Python windows extensions (pywin32)](http://www.sourceforge.net/projects/pywin32/) for python 2.7, build 219
* [Pycurl](http://pycurl.sourceforge.net) 7.19.5 for Python 2.7: [32-bit downloads,](https://pypi.python.org/pypi/pycurl/7.19.3.1) [64-bit downloads](http://www.lfd.uci.edu/~gohlke/pythonlibs/)
* [PyEnchant,](http://pythonhosted.org/pyenchant/) version 1.6.6.  
x64 version has been built by TW Blue developers, so you only will find it in windows-dependencies folder

The windows installers are available only in the windows-dependencies folder

To build a binary version:

* [Py2exe](http://www.sourceforge.net/projects/py2exe/) for Python 2.7, version 0.6.9

#### Dependencies that must be installed using easy_install

setuptools install a script, called easy_install. You can find it in the python scripts directory. To install packages using easy_install, you have to navigate to the scripts directory using a command prompt, for example:

    cd C:\python27x64\scripts

	You can also add the scripts folder to your path environment variable.

	After that, run the following command to install a package, replacing packagename with the names listed below:

    easy_install -Z package

	The -z switch unzips the package, instead of installing it compressed. If you add the --upgrade switch, you can upgrade a package to its latest version. The following packages need to be installed:

* pubsub
* dropbox
* configobj
* requests-oauthlib
* future
* pygeocoder
* suds
* arrow
* markdown

easy_install will automatically get the additional libraries that these packages need to work properly.

#### Other dependencies

These dependencies are located in the windows-dependencies directory. You don't need to install or modify them.

* Bootstrap 1.2.1: included in dependencies directory.  
This dependency has been built using pure basic 4.61. Its source can be found at http://hg.q-continuum.net/updater
* [oggenc2.exe,](http://www.rarewares.org/ogg-oggenc.php) version 2.87  
* Microsoft Visual c++ 2008 redistributable dlls.

#### Dependencies required to build the installer

* [NSIS unicode,](http://www.scratchpaper.com/) version 2.46.5

### Running TW Blue from source

Now that you have installed all these packages, you can run TW Blue from source using a command prompt. Navigate to the src directory into the repo, and type the following command:

    python main.py

	If necesary, change the first part of the command to reflect where is your python executable. You can run TW Blue using python x86 and x64

### Building a binary version

A binary version doesn't need python and the other dependencies to run, it's the same version that you will find in TW Blue website if you download the zip files.

To build it, run the following command from the src folder:

    python setup.py py2exe

	You will find the binaries in the dist directory.

### How to generate a translation template

You must run the gen_pot.bat file, located in the tools directory. Your python installation should be in your path environment variable. The pot file will appear in the tools directory too.