# -*- coding: utf-8 -*-
""" A base class to be derived in possible new sessions for TWBlue and services."""
from __future__ import absolute_import
from __future__ import unicode_literals
from builtins import str
from builtins import object
import os
import paths
import output
import time
import sound
import logging
import config_utils
import shelve
import application
import os
from . import session_exceptions as Exceptions
log = logging.getLogger("sessionmanager.session")

class baseSession(object):
	""" toDo: Decorators does not seem to be working when using them in an inherited class."""

	# Decorators.

	def _require_login(fn):
		""" Decorator for checking if the user is logged in.
		Some functions may need this to avoid making unneeded calls."""
		def f(self, *args, **kwargs):
			if self.logged == True:
				fn(self, *args, **kwargs)
			else:
				raise Exceptions.NotLoggedSessionError("You are not logged in yet.")
		return f

	def _require_configuration(fn):
		""" Check if the user has a configured session."""
		def f(self, *args, **kwargs):
			if self.settings != None:
				fn(self, *args, **kwargs)
			else:
				raise Exceptions.NotConfiguredSessionError("Not configured.")
		return f

	def __init__(self, session_id):
		""" session_id (str): The name of the folder inside the config directory where the session is located."""
		super(baseSession, self).__init__()
		self.session_id = session_id
		self.logged = False
		self.settings = None
		self.db={}
  
	@property
	def is_logged(self):
		return self.logged

	def get_configuration(self):
		""" Get settings for a session."""
		file_ = "%s/session.conf" % (self.session_id,)
		log.debug("Creating config file %s" % (file_,))
		self.settings = config_utils.load_config(os.path.join(paths.config_path(), file_), os.path.join(paths.app_path(), "Conf.defaults"))
		self.init_sound()
		self.deshelve()

	def init_sound(self):
		try: self.sound = sound.soundSystem(self.settings["sound"])
		except: pass

	@_require_configuration
	def login(self, verify_credentials=True):
		pass

	@_require_configuration
	def authorise(self):
		pass

	def shelve(self):
		"""Shelve the database to allow for persistance."""
		shelfname=os.path.join(paths.config_path(), str(self.session_id)+"/cache")
		if self.settings["general"]["persist_size"] == 0:
			if os.path.exists(shelfname+".dat"):
				os.remove(shelfname+".dat")
			return
		try:
			if not os.path.exists(shelfname+".dat"):
				output.speak("Generating database, this might take a while.",True)
			shelf=shelve.open(os.path.join(paths.config_path(), shelfname),'c')
			for key,value in list(self.db.items()):
				if type(key) != str and type(key) != str:
					output.speak("Uh oh, while shelving the database, a key of type " + str(type(key)) + " has been found. It will be converted to type str, but this will cause all sorts of problems on deshelve. Please bring this to the attention of the " + application.name + " developers immediately. More information about the error will be written to the error log.",True)
					log.error("Uh oh, " + str(key) + " is of type " + str(type(key)) + "!")
				if type(value) == list and self.settings["general"]["persist_size"] != -1 and len(value) > self.settings["general"]["persist_size"]:
					shelf[key]=value[self.settings["general"]["persist_size"]:]
				else:
					shelf[key]=value
			shelf.close()
		except:
			output.speak("An exception occurred while shelving the " + application.name + " database. It will be deleted and rebuilt automatically. If this error persists, send the error log to the " + application.name + " developers.",True)
			log.exception("Exception while shelving" + shelfname)
			os.remove(shelfname)

	def deshelve(self):
		"""Import a shelved database."""
		shelfname=os.path.join(paths.config_path(), str(self.session_id)+"/cache")
		if self.settings["general"]["persist_size"] == 0:
			if os.path.exists(shelfname+".dat"):
				os.remove(shelfname+".dat")
			return
		try:
			shelf=shelve.open(os.path.join(paths.config_path(), shelfname),'c')
			for key,value in list(shelf.items()):
				self.db[key]=value
			shelf.close()
		except:
			output.speak("An exception occurred while deshelving the " + application.name + " database. It will be deleted and rebuilt automatically. If this error persists, send the error log to the " + application.name + " developers.",True)
			log.exception("Exception while deshelving" + shelfname)
			try: 
				os.remove(shelfname)
			except:
				pass

