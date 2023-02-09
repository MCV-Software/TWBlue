# -*- coding: utf-8 -*-
import datetime

# Make date check for feb 9.
now = datetime.datetime.now()
end_of_twitter = datetime.datetime(2023, 2, 13)
twitter_support_enabled = True
#if now >= end_of_twitter:
#    twitter_support_enabled = False
name = 'TWBlue'
short_name='twblue'
update_url = 'https://twblue.es/updates/updates.php'
mirror_update_url = 'https://raw.githubusercontent.com/mcv-software/TWBlue/next-gen/updates/updates.json'
authors = ["Manuel Cortéz", "José Manuel Delicado"]
authorEmail = "manuel@manuelcortez.net"
copyright = "Copyright (C) 2013-2022, MCV Software."
description = name+" is an app designed to use Twitter simply and efficiently while using minimal system resources. This app provides access to most Twitter  features."
translators = ["Manuel Cortéz (English)", "Mohammed Al Shara, Hatoun Felemban (Arabic)", "Francisco Torres (Catalan)", "Manuel cortéz (Spanish)", "Sukil Etxenike Arizaleta (Basque)", "Jani Kinnunen (finnish)", "Corentin Bacqué-Cazenave (Français)", "Juan Buño (Galician)", "Steffen Schultz (German)", "Zvonimir Stanečić (Croatian)", "Robert Osztolykan (Hungarian)", "Christian Leo Mameli (Italian)", "Riku (Japanese)", "Paweł Masarczyk (Polish)", "Odenilton Júnior Santos (Portuguese)", "Florian Ionașcu, Nicușor Untilă (Romanian)", "Natalia Hedlund, Valeria Kuznetsova (Russian)", "Aleksandar Đurić (Serbian)", "Burak Yüksek (Turkish)"]
url = "https://twblue.es"
report_bugs_url = "https://github.com/mcvsoftware/twblue/issues"
supported_languages = []
version = "11"
