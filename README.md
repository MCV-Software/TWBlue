TWBlue -
======

TW Blue is an app designed to use Twitter simply and efficiently while using minimal system resources.
With this app you’ll have access to twitter features such as:

* Create, reply to, like, retweet and delete tweets,
* Send and delete direct messages,
* See your friends and followers,
* Follow, unfollow, block and report users as spam,
* Open a user’s timeline, which will allow you to get that user’s tweets separately,
* Open URLs when attached to a tweet or direct message,
* Play audio tweets
* and more!

See [TWBlue's webpage](http://twblue.es) for more details.

## Running TWBlue from source

This document describes how to run tw blue from source and how to build a binary version which doesn't need Python and the other dependencies to run.

### Required dependencies.

Although most dependencies can be found in the windows-dependencies directory, we provide links to their official websites. If you are cloning with git, don't forget to initialize and update the submodules to get the windows-dependencies folder. You can use these two commands to perform this task from git bash:  
    git submodule init  
    git submodule update

	All the dependencies provided in this folder are prebuilt. If you want to build them from source, you will need Microsoft visual Studio 2008.

#### Dependencies packaged in windows installers

* [Python,](http://python.org) version 2.7.13  
If you want to build both x86 and x64 binaries, you can install python x86 to C:\python27 and python x64 to C:\python27x64, for example.
* [Python windows extensions (pywin32)](http://www.sourceforge.net/projects/pywin32/) for python 2.7, build 220
* [PyEnchant,](http://pythonhosted.org/pyenchant/) version 1.6.6.  
x64 version has been built by TWBlue developers, so you only will find it in windows-dependencies folder

The windows installers are available only in the windows-dependencies folder

To build a binary version:

* [Py2exe](http://www.sourceforge.net/projects/py2exe/) for Python 2.7, version 0.6.9

#### Dependencies that must be installed using easy_install

setuptools installs a script, called easy_install. You can find it in the python scripts directory. To install packages using easy_install, you have to navigate to the scripts directory using a command prompt, for example:

    cd C:\python27x64\scripts

	You can also add the scripts folder to your path environment variable.
	Note: pip and setuptools are included in the Python installer since version 2.7.9.

	After that, run the following command to install a package, replacing packagename with the names listed below:

    easy_install -Z package

	The -z switch unzips the package, instead of installing it compressed. If you add the --upgrade switch, you can upgrade a package to its latest version. The following packages need to be installed:

* pypubsub==3.3.0
* configobj
* requests-oauthlib
* requests-toolbelt
* future
* pygeocoder
* arrow==0.6
* markdown
* winpaths
* PySocks
* win_inet_pton
* yandex.translate

easy_install will automatically get the additional libraries that these packages need to work properly.
Run the following command to quickly install and upgrade all packages and their dependencies:  
easy_install -Z --upgrade six configobj markdown future requests oauthlib requests-oauthlib requests-toolbelt pypubsub==3.3.0 pygeocoder arrow==0.6 python-dateutil futures winpaths PySocks win_inet_pton yandex.translate idna chardet urllib3

#### Dependencies that must be installed using pip
WXPython must be installed using pip. To install it, run the following command:

    pip install -U --pre -f https://wxpython.org/Phoenix/snapshot-builds/ wxPython

#### Other dependencies

These dependencies are located in the windows-dependencies directory. You don't need to install or modify them.

* Bootstrap 1.2.1: included in dependencies directory.  
This dependency has been built using pure basic 4.61. Its source can be found at http://hg.q-continuum.net/updater
* [oggenc2.exe,](http://www.rarewares.org/ogg-oggenc.php) version 2.87  
* Microsoft Visual c++ 2008 redistributable dlls.

#### Dependencies required to build the installer

* [NSIS,](http://nsis.sourceforge.net/) version 3.01

#### Dependencies required to build the portableApps.com format archive

* [NSIS Portable,](http://portableapps.com/apps/development/nsis_portable) version 3.0
* [PortableApps.com Launcher,](http://portableapps.com/apps/development/portableapps.com_launcher) version 2.2.1
* [PortableApps.com Installer,](http://portableapps.com/apps/development/portableapps.com_installer) version 3.4.4

Important! Install these 3 apps into the same folder, otherwise you won't be able to build the pa.c version. For example: D:\portableApps\NSISPortable, D:\PortableApps\PortableApps.com installer, ...

#### Dependencies to make the spell checker multilingual ####

In order to add the support for spell checking in more languages than english you need to add some additional dictionaries to pyenchant. These are located on the dictionaries folder under windows-dependencies. Simply copy them to the share/enchant/myspell folder located in your enchant installation or in the compiled copy of TWBlue.

### Running TW Blue from source

Now that you have installed all these packages, you can run TW Blue from source using a command prompt. Navigate to the repo's src directory, and type the following command:

    python main.py

	If necessary, change the first part of the command to reflect the location of your python executable. You can run TW Blue using python x86 and x64

### Generating the documentation

To generate the documentation in html format, navigate to the doc folder inside this repo. After that, run these commands:  
python document_importer.py  
python generator.py  
The documentation will be generated, placing each language in a separate folder in the doc directory. Move these folders (for example de, en, es, fr, it, ...) to src/documentation, creating the directory if necesary.
Also, copy the license.txt located in the root of the repo to the documentation folder.

### Building a binary version

A binary version doesn't need python and the other dependencies to run, it's the same version that you will find on the TW Blue website if you download the zip files or the snapshot versions.

To build it, run the following command from the src folder:

    python setup.py py2exe

	You will find the binaries in the dist directory.

### Building an installer

If you want to install TWBlue on your computer, you must create the installer first. Follow these steps:

* Navigate to the src directory, and create a binary version for x86: C:\python27\python setup.py py2exe
* Move the dist directory to the scripts folder in this repo, and rename it to twblue
* Repeat these steps with Python for x64: C:\python27x64\python setup.py py2exe
* Move the new dist directory to the scripts folder, and rename it to twblue64
* Go to the scripts folder, right click on the twblue.nsi file, and choose compyle unicode NSIS script
* This may take a while. After the process, you will find the installer in the scripts folder

### How to generate a translation template

Run the gen_pot.bat file, located in the tools directory. Your python installation must be in your path environment variable. The pot file will appear in the tools directory.

### How to build the portableApps.com archive

If you want to have TWBlue on your PortableApps.com platform, follow these steps:

* Navigate to the src directory, and create a binary version for x86: C:\python27\python setup.py py2exe
* Move the dist directory to the misc\pa.c format\app folder in this repo, and rename it to twblue
* Repeat these steps with Python for x64: C:\python27x64\python setup.py py2exe
* Move the new dist directory to the misc\pa.c format\app folder, and rename it to twblue64
* Run the PortableApps.com Launcher Generator, and follow the wizard. Choose the pa.c format folder and continue to generate the launcher. If the wizard is completed, you will see a file named TWBlue portable.exe inside the pa.c format folder.
* Run the PortableApps.com Installer, and follow the wizard. As in the above step, choose the pa.c format folder. When it completes, you will see a file named TWBluePortable_x.y.paf.exe inside the misc folder, where x.y is the version number.

