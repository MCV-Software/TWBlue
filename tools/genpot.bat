@echo off
echo Generating application translation strings...
C:\python27\python.exe pygettext.py -v -d twblue ../src/*.pyw ../src/*.py ../src/*/*.py ../src/*/*.pyw ../src/*/*/*.py ../src/*/*/*.pyw ../src/*/*/*/*.py ../src/*/*/*/*.pyw ../src/*/*/*/*/*.py ../src/*/*/*/*/*.pyw
C:\python27\python.exe pygettext.py -v -d twblue-documentation ../src/*.pyw ../src/*.py ../gendoc/*/*.py ../src/*/*.pyw ../src/*/*/*.py ../src/*/*/*.pyw ../src/*/*/*/*.py ../src/*/*/*/*.pyw ../src/*/*/*/*/*.py ../src/*/*/*/*/*.pyw
