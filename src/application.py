# -*- coding: utf-8 -*-
import datetime

name = 'TWBlue'
snapshot = True
if snapshot == False:
 version = "0.93"
 update_url = 'https://twblue.es/updates/stable.php'
 mirror_update_url = 'https://raw.githubusercontent.com/manuelcortez/TWBlue/next-gen/updates/stable.json'
else:
 version = "6"
 update_url = 'https://twblue.es/updates/snapshot.php'
 mirror_update_url = 'https://raw.githubusercontent.com/manuelcortez/TWBlue/next-gen/updates/snapshots.json'
authors = [u"Manuel Cortéz", u"José Manuel Delicado"]
authorEmail = "manuel@manuelcortez.net"
copyright = u"Copyright (C) 2013-2018, Manuel cortéz."
description = unicode(name+" is an app designed to use Twitter simply and efficiently while using minimal system resources. This app provides access to most Twitter features.")
translators = [u"Manuel Cortéz (English)", u"Mohammed Al Shara, Hatoun Felemban (Arabic)", u"Francisco Torres (Catalan)", u"Manuel cortéz (Spanish)", u"Sukil Etxenike Arizaleta (Basque)", u"Jani Kinnunen (finnish)", u"Rémy Ruiz (French)", u"Juan Buño (Galician)", u"Steffen Schultz (German)", u"Zvonimir Stanečić (Croatian)", u"Robert Osztolykan (Hungarian)", u"Christian Leo Mameli (Italian)", u"Riku (Japanese)", u"Paweł Masarczyk (Polish)", u"Odenilton Júnior Santos (Portuguese)", u"Florian Ionașcu, Nicușor Untilă (Romanian)", u"Natalia Hedlund, Valeria Kuznetsova (Russian)", u"Aleksandar Đurić (Serbian)", u"Burak Yüksek (Turkish)"]
url = u"https://twblue.es"
report_bugs_url = "https://github.com/manuelcortez/twblue/issues"
supported_languages = []

def streaming_lives():
 """ Check if we are in August 16.
 ToDo: This method should be removed after deadline==True"""
 # Let's import config here so we will avoid breaking things when setup.py is going to be used.
 # Check if user has disabled the streaming API things from settings.
 import config
 if config.app != None:
  no_streaming = config.app["app-settings"]["no_streaming"]
  if no_streaming == True:
   return False
 deadline = datetime.date(2018, 8, 16)
 now = datetime.datetime.now().date()
 return deadline>now