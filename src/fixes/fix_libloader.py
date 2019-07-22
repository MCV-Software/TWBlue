# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
import win32com
import paths
win32com.__build_path__=paths.com_path()
import sys
import os
sys.path.append(os.path.join(win32com.__gen_path__, "."))
from win32com.client import gencache
from pywintypes import com_error
from libloader import com

log = logging.getLogger("fixes.fix_libloader")

fixed=False

def patched_getmodule(modname):
	mod=__import__(modname)
	return sys.modules[modname]

def load_com(*names):
	global fixed
	if fixed==False:
		gencache._GetModule=patched_getmodule
		com.prepare_gencache()
		fixed=True
	result = None
	for name in names:
		try:
			result = gencache.EnsureDispatch(name)
			break
		except com_error:
			continue
	if result is None:
		raise com_error("Unable to load any of the provided com objects.")
	return result

def fix():
	log.debug("Applying fix for Libloader...")
	com.load_com = load_com
	log.debug("Load_com has been mapped correctly.")