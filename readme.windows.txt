tw blue build instructions for Windows

Introduction.
This document describes how to run tw blue from source, and, after that, how to build a binary version, which doesn't need Python and the other dependencies to run.

Required dependencies.
The following dependencies need to be installed in your system. If you want to build tw blue for 32-bit versions of Windows, you will find the required software in the x86 folder, inside dependencies directory. If you want to build tw blue for 64-bit windows versions, use the x64 folder.
In this document you will also find links to each dependency website.
If you want to build manually some of the following libraries, you need Microsoft Visual studio 2008 professional.

Dependencies list:
- Python, version 2.7.8: http://www.python.org
- wxPython for Python 2.7, version 3.0.0 (2.9.5 to avoid problems in windows xp): http://www.wxpython.org
-Python windows extensions (pywin32) for python 2.7, build 218: http://www.sourceforge.net/projects/pywin32/
- ConfigObj, version 4.7.2: http://www.voidspace.org.uk/python/configobj.html
- oauthlib 0.6.1: https://pypi.python.org/pypi/oauthlib/0.6.1
- Pycurl 7.19.3.1 for Python 2.7:
Official website: http://pycurl.sourceforge.net/
32-bit downloads: https://pypi.python.org/pypi/pycurl/7.19.3.1
64-bit downloads: http://www.lfd.uci.edu/~gohlke/pythonlibs/
- Requests 2.2.1:
Official website: http://www.python-requests.org/en/latest/
Recommended download site: https://pypi.python.org/pypi/requests/2.2.1
- Requests-oauthlib 0.4.0: https://github.com/requests/requests-oauthlib
- Suds 0.4:
Official website: https://fedorahosted.org/suds
Recommended download site: https://pypi.python.org/pypi/suds/0.4
- Twython 3.1.2: https://pypi.python.org/pypi/twython/3.1.2
- Bootstrap 1.2.1: included in dependencies directory.
Copy the bootstrap.exe file corresponding to the desired platform in the windows folder, inside this repository.
This dependency has been built using pure basic 4.61. Its source can be found at http://hg.q-continuum.net/updater
- oggenc2.exe, version 2.87: http://www.rarewares.org/ogg-oggenc.php
Copy the oggenc2.exe file corresponding to the desired platform in the windows folder, inside this repository.
-Visual C++ 2008 dlls, included in vcredist-x86.7z and vcredist-x64.7z:
Extract the file corresponding to your platform to the windows folder.

To build the binary version:
- Py2exe for Python 2.7, version 0.6.9: http://www.sourceforge.net/projects/py2exe/
- Setuptools 2.1: https://pypi.python.org/pypi/setuptools
- 7-zip: http://7-zip.org

To generate the documentation:
- Pandoc, version 1.12.3:
Official website: http://johnmacfarlane.net/pandoc/
Downloads site: http://code.google.com/p/pandoc/downloads/list

How to run tw blue from source
Run the file main.py located in windows folder. If you have a x64 system, you can install both 32-bit and 64-bit python versions, and test tw blue in these platforms.

How to generate the documentation
To generate quickly the documentation, a bash console is required. You can find bash in git for windows, cygwin, or MSYS, for example.
You must navigate to the tools directory and run the script gen_doc.sh. It will generate and place all html documentation in windows\documentation directory.

How to build a binary version
You must type the following command. In the following example, we will assume that python is the path to the python executable (x86 or x64) and that you have navigated to the windows directory:
python setup.py py2exe
You will find the binary version in the dist directory. You can compress this folder using 7-zip and you will get the zip version.

How to generate a translation template
You must run the gen_pot.bat file, located in the tools directory. Your python installation should be in your path environment variable. The pot file will appear in the tools directory too.
