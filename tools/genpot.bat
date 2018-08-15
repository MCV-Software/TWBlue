@echo off
echo Generating application translation strings...
C:\python27\python.exe pygettext.py  -v -d twblue ../src/*.pyw ../src/*.py ../src/*/*.py ../src/*/*.pyw ../src/*/*/*.py ../src/*/*/*.pyw ../src/*/*/*/*.py ../src/*/*/*/*.pyw ../src/*/*/*/*/*.py ../src/*/*/*/*/*.pyw
C:\python27\python.exe pygettext.py -v -d twblue-documentation ../doc/strings.py
C:\python27\python.exe pygettext.py -v -d twblue-changelog ../doc/changelog.py