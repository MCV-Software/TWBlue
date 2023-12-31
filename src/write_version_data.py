#! /usr/bin/env python# -*- coding: iso-8859-1 -*-
""" Write version info (taken from the last commit) to application.py. This method has been implemented this way for running updates.
This file is not intended to be called by the user. It will be used only by the Gitlab CI runner."""
import os
from codecs import open

print("Writing version data for update...")
new_version = os.environ.get("GITHUB_REF_NAME")
file = open("application.py", "r", encoding="utf-8")
lines = file.readlines()
lines[-1] = 'version = "{}"'.format(new_version)
file.close()
file2 = open("application.py", "w", encoding="utf-8")
file2.writelines(lines)
file2.close()
print("Wrote application.py with the new version info.")

print("Updating next version on installer setup...")
file = open("..\\scripts\\twblue.nsi", "r", encoding="utf-8")
contents = file.read()
contents = contents.replace("0.95", new_version)
file.close()
file2 = open("..\\scripts\\twblue.nsi", "w", encoding="utf-8")
file2.write(contents)
file2.close()
print("done")
