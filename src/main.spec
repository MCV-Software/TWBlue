# -*- mode: python -*-
""" specification file for creating distributable versions using Pyinstaller. """
import os
import glob
import wx
import platform
from requests import certs

block_cipher = None

def get_architecture_files():
	""" Returns architecture files for 32 or 64 bits. """
	if platform.architecture()[0][:2] == "32":
		return [
			("..\\windows-dependencies\\x86\\oggenc2.exe", "."),
			("..\\windows-dependencies\\x86\\bootstrap.exe", "."),
			("..\\windows-dependencies\\x86\\*.dll", "."),
			("..\\windows-dependencies\\x86\\plugins", "plugins"),
		]
	elif platform.architecture()[0][:2] == "64":
		return [
			("..\\windows-dependencies\\x64\\oggenc2.exe", "."),
			("..\\windows-dependencies\\x64\\bootstrap.exe", "."),
			("..\\windows-dependencies\\x64\\*.dll", "."),
			("..\\windows-dependencies\\x64\\plugins", "plugins"),
		]

def wx_files():
	wxDir=wx.__path__[0]
	localeMoFiles=set()
	for f in glob.glob("locales/*/LC_MESSAGES"):
		g=f.replace("locales", "locale")
		wxMoFile=os.path.join(wxDir,g,"wxstd.mo")
		if os.path.isfile(wxMoFile):
			localeMoFiles.add((wxMoFile, f))
		lang=os.path.split(os.path.split(f)[0])[1]
		if '_' in lang:
				lang=lang.split('_')[0]
				f=os.path.join('locale',lang,'lc_messages')
				g=f.replace("locale", "locales")
				wxMoFile=os.path.join(wxDir,f,"wxstd.mo")
				if os.path.isfile(wxMoFile):
					localeMoFiles.add((wxMoFile, g)) 
	return list(localeMoFiles)

a = Analysis(['main.py'],
             pathex=['.'],
             binaries=[("sounds", "sounds"),
("documentation", "documentation"),
("locales", "locales"),
("keymaps", "keymaps"),
("keys/lib", "keys/lib"),
("..\\windows-dependencies\\dictionaries", "enchant\\share\\enchant\\myspell"),
(certs.where(), "."),
("app-configuration.defaults", "."),
("conf.defaults", "."),
("icon.ico", "."),
]+get_architecture_files()+wx_files(),

             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='TWBlue',
          debug=False,
          strip=False,
          upx=True,
          console=False)
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='TWBlue')
