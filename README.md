TWBlue
======

[![Build status](https://ci.appveyor.com/api/projects/status/fml5fu7h1fj8vf6l?svg=true)](https://ci.appveyor.com/project/manuelcortez/twblue)

TWBlue is a free and open source application that allows you to interact with the main features of Twitter and mastodon from the comfort of a windows software, with 2 different interfaces specially designed for screen reader users.

See [TWBlue's webpage](https://twblue.es) for more details.

## Running TWBlue from source

This document describes how to run tw blue from source and how to build a binary version which doesn't need Python and the other dependencies to run.

### Generating application keys

In order to communicate with Twitter, you will need to generate a set of API keys in their [developer portal](https://developer.twitter.com/en/portal/dashboard) (If you haven't signed up, [visit this site to register as a developer](https://developer.twitter.com/en/docs/twitter-api/getting-started/getting-access-to-the-twitter-api)) and create a module called appkeys.py, within the src directory, with the following content, replacing the example values with your set of API keys:

```
twitter_api_key='xxxxxxxxxx'
twitter_api_secret='xxxxxxxxxx'
```

### Required dependencies.

Although most dependencies can be found in the windows-dependencies directory, we provide links to their official websites. If you are cloning with git, don't forget to initialize and update the submodules to get the windows-dependencies folder. You can use these two commands to perform this task from git bash:  
```
    git submodule init  
    git submodule update
```

#### Dependencies packaged in windows installers

* [Python,](https://python.org) version 3.10.8  
If you want to build both x86 and x64 binaries, you can install python x64 to C:\python310 and python x86 to C:\python310-32, for example.

#### Dependencies that must be installed using pip

Python installs a tool called Pip that allows to install packages in a simple way. You can find it in the python scripts directory. To install packages using Pip, you have to navigate to the scripts directory using a command prompt, for example:

    `cd C:\python310\scripts`

	You can also add the scripts folder to your path environment variable or choose the corresponding option when installing Python.  
	Note: pip and setuptools are included in the Python installer since version 2.7.9.

Note: If you are using Python for 32-bit systems, you will need to install WXPython for 32-bits before running the command for installing everything else. You can do so by running the following command:

    `pip install --upgrade https://github.com/josephsl/wxpy32whl/blob/main/wxPython-4.2.0-cp310-cp310-win32.whl?raw=true`

Pip is able to install packages listed in a special text file, called the requirements file. To install all remaining dependencies, perform the following command:

    `pip install -r requirements.txt`

Note that if you perform the command from the path where Pip is located, you need to specify the path to your Tw Blue root folder where the requirements file is located, for example:

    `pip install -r D:\repos\TwBlue\requirements.txt`

Pip will automatically get the additional libraries that the listed packages need to work properly.  
If you need to update your dependencies, perform the following command:

    `pip install --upgrade -r requirements.txt`

#### Other dependencies

These dependencies are located in the windows-dependencies directory. You don't need to install or modify them.

* Bootstrap 1.2.1: included in dependencies directory.  
This dependency has been built using pure basic 4.61. Its source can be found at http://hg.q-continuum.net/updater
* [oggenc2.exe,](http://www.rarewares.org/ogg-oggenc.php) version 2.87  
* Microsoft Visual c++ 2019 redistributable dlls.
* VLC plugins and DLL libraries.

#### Dependencies required to build the installer

* [NSIS,](http://nsis.sourceforge.net/) version 3.04

#### Dependencies to make the spell checker multilingual

In order to add the support for spell checking in more languages than english you need to add some additional dictionaries to pyenchant. These are located on the dictionaries folder under windows-dependencies. Simply copy them to the share/enchant/myspell folder located in your enchant installation. They will be automatically copied when building a binary version.

### Running TW Blue from source

Now that you have installed all these packages, you can run TW Blue from source using a command prompt. Navigate to the repo's `src` directory, and type the following command:

    `python main.py`

	If necessary, change the first part of the command to reflect the location of your python executable. You can run TW Blue using python x86 and x64.

### Generating the documentation

To generate the documentation in html format, navigate to the doc folder inside this repo. After that, run these commands:  

    `python document_importer.py`  
    `python generator.py`  

The documentation will be generated, placing each language in a separate folder in the doc directory. Move these folders (for example `de`, `en`, `es`, `fr`, `it`, ...) to `src/documentation`, creating the directory if necessary.  
Also, copy the `license.txt` file located in the root of the repo to the documentation folder.

### Building a binary version

A binary version doesn't need python and the other dependencies to run, it's the same version that you will find on the TW Blue website if you download the zip files or the snapshot versions.

To build it, run the following command from the src folder:

    `python setup.py build`

	You will find the binaries in the dist directory.

### Building an installer

If you want to install TWBlue on your computer, you must create the installer first. Follow these steps:

* Navigate to the src directory, and create a binary version for x86: C:\python37\python setup.py build
* Move the dist directory to the scripts folder in this repo, and rename it to twblue
* Repeat these steps with Python for x64: C:\python37x64\python setup.py build
* Move the new dist directory to the scripts folder, and rename it to twblue64
* Go to the scripts folder, right click on the twblue.nsi file, and choose compyle unicode NSIS script
* This may take a while. After the process, you will find the installer in the scripts folder

### How to generate a translation template

To manage translations in TWBlue, you can install the [Babel package.](https://pypi.org/project/Babel/) You can extract message catalogs and generate the main template file with the following command:

pybabel extract -o twblue.pot --msgid-bugs-address "manuel@manuelcortez.net" --copyright-holder "MCV software" --input-dirs ..\src

Take into account, though, that we use [weblate](https://weblate.mcvsoftware.com) to track translation work for TWBlue. If you wish to be part of our translation team, please open an issue so we can create an account for you in Weblate.