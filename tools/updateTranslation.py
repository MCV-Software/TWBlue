# -*- coding: utf-8 -*-
#Translation update Tool
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
if not os.path.exists("tools/bin/xgettext.exe") or not os.path.exists("tools/bin/msgmerge.exe"):
	print("Error: xgettext or msgmerge is missing.")
	sys.exit()

BASE_LOCALE_DIR = "src/locales"
langs=[]
for elem in glob.glob("src/locales/*"):
	if os.path.isdir(elem): langs.append(os.path.basename(elem))

print("Detected languages:")
for l in langs:
	print(l)
files = glob.glob("src/*.py")
files.extend(glob.glob("src/**/*.py", recursive=True))
print("Detected files:")
print("Detected files: %d" % len(files))
print("Updating the base dictionary(pot)")
subprocess.call(("tools/bin/xgettext.exe -p %s -d twblue --from-code utf-8 --package-name=twblue %s" % (BASE_LOCALE_DIR, " ".join(files))).split())
for l in langs:
	lang_file = "%s/%s/LC_MESSAGES/twblue.po" % (BASE_LOCALE_DIR, l)
	if os.path.exists(lang_file):
		print("Merging %s" % l)
		subprocess.call(("tools/bin/msgmerge.exe -U %s %s/twblue.po" % (lang_file, BASE_LOCALE_DIR)).split())
	else:
		print("Creating %s" % l)
		if not os.path.exists("%s/%s/LC_MESSAGES" % (BASE_LOCALE_DIR, l)):
			print("Creating LC_MESSAGES")
			os.mkdir("%s/%s/LC_MESSAGES" % (BASE_LOCALE_DIR, l))
		shutil.copyfile("%s/twblue.po"% BASE_LOCALE_DIR, lang_file)
print("Done")
sys.exit(0)
