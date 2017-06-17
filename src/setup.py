# -*- coding: utf-8 -*-
""" Setup file to create executables and distribute the source code of this application. Don't forget this file! """
############################################################
#    Copyright (c) 2014 José Manuel Delicado Alcolea <jmdaweb@gmail.com>
#    Copyright (c) 2013, 2014 Manuel Eduardo Cortéz Vallejo <manuel@manuelcortez.net>
#       
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
############################################################
from setuptools import setup, find_packages
import py2exe
import os
import gettext
import application
import platform
from glob import glob
import wx
from requests import certs

def get_architecture_files():
	if platform.architecture()[0][:2] == "32":
		return [
  ("", ["../windows-dependencies/x86/oggenc2.exe", "../windows-dependencies/x86/bootstrap.exe"]),
  ("Microsoft.VC90.CRT", glob("../windows-dependencies/x86/Microsoft.VC90.CRT/*")),
  ("Microsoft.VC90.MFC", glob("../windows-dependencies/x86/Microsoft.VC90.MFC/*")),]
	elif platform.architecture()[0][:2] == "64":
		return [
  ("", ["../windows-dependencies/x64/oggenc2.exe", "../windows-dependencies/x64/bootstrap.exe"]),
  ("Microsoft.VC90.CRT", glob("../windows-dependencies/x64/Microsoft.VC90.CRT/*")),
  ("Microsoft.VC90.MFC", glob("../windows-dependencies/x64/Microsoft.VC90.MFC/*")),]

def get_data():
	import sound_lib
	import enchant
	return [
  ("", ["conf.defaults", "app-configuration.defaults", "icon.ico"]),
    ("", [certs.where()]),
  ("accessible_output2/lib", glob("accessible_output2/lib/*.dll")),
  ("keys/lib", glob("keys/lib/*.dll")),
("keymaps", glob("keymaps/*.keymap")),
("share/enchant/myspell", glob("../windows-dependencies/dictionaries/*")),
]+get_sounds()+get_locales()+get_documentation()+sound_lib.find_datafiles()+enchant.utils.win32_data_files()+get_architecture_files()+wx_files()

def get_documentation ():
	answer = [("documentation", ["documentation/license.txt"])]
	depth = 10
	for root, dirs, files in os.walk('documentation'):
		if depth == 0:
			break
		new = (root, glob(os.path.join(root, "*.html")))
		answer.append(new)
		depth -= 1
	return answer

def get_sounds():
	answer = []
	depth = 6
	for root, dirs, files in os.walk('sounds'):
		if depth == 0:
			break
		new = (root, glob(os.path.join(root, "*.ogg")))
		answer.append(new)
		depth -= 1
	return answer

def get_locales():
	answer = []
	for root, dirs, files in os.walk('locales'):
		new = (root, glob(os.path.join(root, '*.mo')))
		answer.append(new)
	return answer

def wx_files():
	wxDir=wx.__path__[0]
	localeMoFiles=set()
	for f in glob("locales/*/LC_MESSAGES"):
		g=f.replace("locales", "locale")
		wxMoFile=os.path.join(wxDir,g,"wxstd.mo")
		if os.path.isfile(wxMoFile):
			localeMoFiles.add((f,(wxMoFile,))) 
		lang=os.path.split(os.path.split(f)[0])[1]
		if '_' in lang:
				lang=lang.split('_')[0]
				f=os.path.join('locale',lang,'lc_messages')
				g=f.replace("locale", "locales")
				wxMoFile=os.path.join(wxDir,f,"wxstd.mo")
				if os.path.isfile(wxMoFile):
					localeMoFiles.add((g,(wxMoFile,))) 
	return list(localeMoFiles)

if __name__ == '__main__':
	setup(
  name = application.name,
  author = ", ".join(application.authors),
  author_email = application.authorEmail,
  version = application.version,
  url = application.url,
packages= find_packages(),
data_files = get_data(),
options = {
   'py2exe': {   
    'optimize':2,
   'packages': ["pubsub", "pubsub.core", "pubsub.core.kwargs", "dbhash"],
    'dll_excludes': ["MPR.dll", "api-ms-win-core-apiquery-l1-1-0.dll", "api-ms-win-core-console-l1-1-0.dll", "api-ms-win-core-delayload-l1-1-1.dll", "api-ms-win-core-errorhandling-l1-1-1.dll", "api-ms-win-core-file-l1-2-0.dll", "api-ms-win-core-handle-l1-1-0.dll", "api-ms-win-core-heap-obsolete-l1-1-0.dll", "api-ms-win-core-libraryloader-l1-1-1.dll", "api-ms-win-core-localization-l1-2-0.dll", "api-ms-win-core-processenvironment-l1-2-0.dll", "api-ms-win-core-processthreads-l1-1-1.dll", "api-ms-win-core-profile-l1-1-0.dll", "api-ms-win-core-registry-l1-1-0.dll", "api-ms-win-core-synch-l1-2-0.dll", "api-ms-win-core-sysinfo-l1-2-0.dll", "api-ms-win-security-base-l1-2-0.dll", "api-ms-win-core-heap-l1-2-0.dll", "api-ms-win-core-interlocked-l1-2-0.dll", "api-ms-win-core-localization-obsolete-l1-1-0.dll", "api-ms-win-core-string-l1-1-0.dll", "api-ms-win-core-string-obsolete-l1-1-0.dll", "WLDAP32.dll", "MSVCP90.dll", "CRYPT32.dll", "mfc90.dll"],
    'compressed': True
   },
  },
  windows = [
   {
    'script': 'main.py',
    'dest_base': 'TWBlue',
}
  ],
  install_requires = [
  ]
 )
