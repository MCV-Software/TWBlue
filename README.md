TWBlue
======

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

See the [TWBlue's webpage](http://twblue.com.mx) for more details.

## Using TWBlue from sources

This document describes how to run tw blue from source, and, after that, how to build a binary version, which doesn't need Python and the other dependencies to run.

### Required dependencies.

The following dependencies need to be installed in your system. If you want to build tw blue for 32-bit versions of Windows, you will find the required software in the x86 folder, inside windows-dependencies directory. If you want to build tw blue for 64-bit windows versions, use the x64 folder.

In this document you will also find links to each dependency website.

If you want to build manually some of the following libraries, you need Microsoft Visual studio 2008 professional.

Dependencies list:

* [Python,](http://python.org) version 2.7.8
* [wxPython](http://www.wxpython.org) for Python 2.7, version 3.0.0 (2.9.5 to avoid problems in windows xp)
* [Python windows extensions (pywin32)](http://www.sourceforge.net/projects/pywin32/) for python 2.7, build 218
* [ConfigObj,](http://www.voidspace.org.uk/python/configobj.html) version 4.7.2
* [oauthlib](https://pypi.python.org/pypi/oauthlib/0.6.1) 0.6.1
* [Pycurl](http://pycurl.sourceforge.net) 7.19.3.1 for Python 2.7: [32-bit downloads,](https://pypi.python.org/pypi/pycurl/7.19.3.1) [64-bit downloads](http://www.lfd.uci.edu/~gohlke/pythonlibs/)
* [Requests](http://www.python-requests.org/en/latest/) 2.2.1: [Recommended download site](https://pypi.python.org/pypi/requests/2.2.1)
* [Requests-oauthlib](https://github.com/requests/requests-oauthlib) 0.4.0
* [Suds](https://fedorahosted.org/suds) 0.4: [Recommended download site](https://pypi.python.org/pypi/suds/0.4)
* Bootstrap 1.2.1: included in dependencies directory.  
Copy the bootstrap.exe file corresponding to the desired platform in the windows folder, inside this repository.  
This dependency has been built using pure basic 4.61. Its source can be found at http://hg.q-continuum.net/updater
* [oggenc2.exe,](http://www.rarewares.org/ogg-oggenc.php) version 2.87  
Copy the oggenc2.exe file corresponding to the desired platform in the windows folder, inside this repository.
* Visual C++ 2008 dlls, included in vcredist-x86.7z and vcredist-x64.7z:  
Extract the file corresponding to your platform to the src folder.

If you want to build the binary version:

* [Py2exe](http://www.sourceforge.net/projects/py2exe/) for Python 2.7, version 0.6.9
* [Setuptools](https://pypi.python.org/pypi/setuptools) 2.1
- [7-zip](http://7-zip.org)

### How to run tw blue from source

Run the file main.py located in the src folder. If you have a x64 system, you can install both 32-bit and 64-bit python versions, and test tw blue in these platforms.

### How to build a binary version

You must type the following command. In this example, we will assume that python is the path to the python executable (x86 or x64) and that you have navigated to the src directory:

    python setup.py py2exe

	You will find the binary version in the dist directory. You can compress this folder using 7-zip and you will get the zip version.

### How to generate a translation template

You must run the gen_pot.bat file, located in the tools directory. Your python installation should be in your path environment variable. The pot file will appear in the tools directory too.