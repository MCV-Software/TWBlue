# -*- coding: utf-8 -*-
from builtins import str
name = 'TWBlue'
snapshot = False
if snapshot == False:
 version = "0.90"
 update_url = 'http://twblue.es/updates/twblue_ngen.json'
 mirror_update_url = 'https://raw.githubusercontent.com/manuelcortez/TWBlue/next-gen/updates/stable.json'
else:
 version = "10.99"
 update_url = 'http://twblue.es/updates/snapshots_ngen.json'
 mirror_update_url = 'https://raw.githubusercontent.com/manuelcortez/TWBlue/next-gen/updates/snapshots.json'
authors = [u"Manuel Cortéz", u"José Manuel Delicado"]
authorEmail = "manuel@manuelcortez.net"
copyright = u"Copyright (C) 2013-2017, Manuel cortéz."
description = str(name+" is an app designed to use Twitter simply and efficiently while using minimal system resources. This app provides access to most Twitter features.")
translators = [u"Manuel Cortéz (English)", u"Mohammed Al Shara, Hatoun Felemban (Arabic)", u"Francisco Torres (Catalan)", u"Manuel cortéz (Spanish)", u"Sukil Etxenike Arizaleta (Basque)", u"Jani Kinnunen (finnish)", u"Rémy Ruiz (French)", u"Juan Buño (Galician)", u"Steffen Schultz (German)", u"Zvonimir Stanečić (Croatian)", u"Robert Osztolykan (Hungarian)", u"Christian Leo Mameli (Italian)", u"Riku (Japanese)", u"Paweł Masarczyk (Polish)", u"Odenilton Júnior Santos (Portuguese)", u"Florian Ionașcu, Nicușor Untilă (Romanian)", u"Natalia Hedlund, Valeria Kuznetsova (Russian)", u"Aleksandar Đurić (Serbian)", u"Burak Yüksek (Turkish)"]
url = u"http://twblue.es"
report_bugs_url = "http://twblue.es/bugs/api/soap/mantisconnect.php?wsdl"