# -*- coding: utf-8 -*-
#Translation building Tool
#Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
#Copyright (C) 2020-2021 guredora <contact@guredora.com>

import sys
import os
import subprocess
import glob
import shutil

if not os.path.exists("src/locales"):
	print("Error: no locale folder found. Your working directory must be the root of the project. You shouldn't cd to tools and run this script.")
	sys.exit()
if not os.path.exists("tools/bin/msgfmt.exe"):
	print("Error: msgfmt is missing.")
	sys.exit()

langs=[]
for elem in glob.glob("src/locales/*"):
	if os.path.isdir(elem): langs.append(os.path.basename(elem))

print("Detected languages:")
for l in langs:
	print(l)

print("Building mo files")
for l in langs:
	subprocess.call(("tools\\bin\\msgfmt.exe -o src/locales/%s/LC_MESSAGES/twblue.mo src/locales/%s/LC_MESSAGES/twblue.po" % (l,l)).split())
print("Done")
sys.exit(0)
