# -*- coding: utf-8 -*-
name = 'TWBlue'
snapshot = False
if snapshot == False:
 version = "0.91"
 update_url = 'http://twblue.es/updates/twblue_ngen.json'
 mirror_update_url = 'https://raw.githubusercontent.com/manuelcortez/TWBlue/next-gen/updates/stable.json'
else:
 version = "10.99"
 update_url = 'http://twblue.es/updates/snapshots_ngen.json'
 mirror_update_url = 'https://raw.githubusercontent.com/manuelcortez/TWBlue/next-gen/updates/snapshots.json'
author = u"Manuel Cortéz"
authorEmail = "manuel@manuelcortez.net"
copyright = u"Copyright (C) 2013-2016, Manuel cortéz."
description = unicode(name+" is an app designed to use Twitter simply and efficiently while using minimal system resources. This app provides access to most Twitter features.")
translators = [u"Bryner Villalobos, Bill Dengler (English)", u"Mohammed Al Shara (Arabic)", u"Joan Rabat, Juan Carlos Rivilla (Catalan)", u"Manuel cortéz (Spanish)", u"Sukil Etxenike Arizaleta (Basque)", u"Jani Kinnunen (finnish)", u"Rémy Ruiz (French)", u"Juan Buño (Galician)", u"Steffen Schultz (German)", u"Robert Osztolykan (Hungarian)", u"Paweł Masarczyk (Polish)", u"Odenilton Júnior Santos (Portuguese)", u"Alexander Jaszyn (Russian)", u"Burak (Turkish)"]
url = u"http://twblue.es"
report_bugs_url = "http://twblue.es/bugs/api/soap/mantisconnect.php?wsdl"