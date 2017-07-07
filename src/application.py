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
authors = ["Manuel Cortéz", "José Manuel Delicado"]
authorEmail = "manuel@manuelcortez.net"
copyright = "Copyright (C) 2013-2017, Manuel cortéz."
description = "{} is an app designed to use Twitter simply and efficiently while using minimal system resources. This app provides access to most Twitter features.".format(name)
translators = ["Manuel Cortéz, Bill Dengler (English)", "Mohammed Al Shara, Hatoun Felemban (Arabic)", "Francisco Torres (Catalan)", "Manuel cortéz (Spanish)", "Sukil Etxenike Arizaleta (Basque)", "Jani Kinnunen (finnish)", "Rémy Ruiz (French)", "Juan Buño (Galician)", "Steffen Schultz (German)", "Zvonimir Stanečić (Croatian)", "Robert Osztolykan (Hungarian)", "Christian Leo Mameli (Italian)", "Riku (Japanese)", "Paweł Masarczyk (Polish)", "Odenilton Júnior Santos (Portuguese)", "Florian Ionașcu, Nicușor Untilă (Romanian)", "Natalia Hedlund, Valeria Kuznetsova (Russian)", "Aleksandar Đurić (Serbian)", "Burak Yüksek (Turkish)"]
url = "http://twblue.es"
report_bugs_url = "http://twblue.es/bugs/api/soap/mantisconnect.php?wsdl"