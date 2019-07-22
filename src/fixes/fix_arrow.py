# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from arrow import locales
from arrow.locales import Locale

def fix():
	# insert a modified function so if there is no language available in arrow, returns English locale.
	locales.get_locale = get_locale

def get_locale(name):
	locale_cls = locales._locales.get(name.lower())
	if locale_cls is None:
		name = name[:2]
		locale_cls = locales._locales.get(name.lower())
		if locale_cls == None:
			return locales.EnglishLocale()
	return locale_cls()

class CatalaLocale(Locale):
	names = ['ca', 'ca_es', 'ca_ca']
	past = 'Fa {0}'
	future = '{0}' # I don't know what's the right phrase in catala for the future.

	timeframes = {
		'now': 'Ara mateix',
		'seconds': 'segons',
		'minute': '1 minut',
		'minutes': '{0} minuts',
		'hour': 'una hora',
		'hours': '{0} hores',
		'day': 'un dia',
		'days': '{0} dies',
		'month': 'un mes',
		'months': '{0} messos',
		'year': 'un any',
		'years': '{0} anys',
	}

	month_names = ['', 'Jener', 'Febrer', 'Març', 'Abril', 'Maig', 'Juny', 'Juliol', 'Agost', 'Setembre', 'Octubre', 'Novembre', 'Decembre']
	month_abbreviations = ['', 'Jener', 'Febrer', 'Març', 'Abril', 'Maig', 'Juny', 'Juliol', 'Agost', 'Setembre', 'Octubre', 'Novembre', 'Decembre']
	day_names = ['', 'Dilluns', 'Dimars', 'Dimecres', 'Dijous', 'Divendres', 'Disabte', 'Diumenge']
	day_abbreviations = ['', 'Dilluns', 'Dimars', 'Dimecres', 'Dijous', 'Divendres', 'Disabte', 'Diumenge']

class GalicianLocale(Locale):
	names = ['gl', 'gl_es', 'gl_gl']
	past = 'Fai {0}'
	future = 'En {0}'

	timeframes = {
		'now': 'Agora mesmo',
		'seconds': 'segundos',
		'minute': 'un minuto',
		'minutes': '{0} minutos',
		'hour': 'una hora',
		'hours': '{0} horas',
		'day': 'un día',
		'days': '{0} días',
		'month': 'un mes',
		'months': '{0} meses',
		'year': 'un ano',
		'years': '{0} anos',
	}

	month_names = ['', 'Xaneiro', 'Febreiro', 'Marzo', 'Abril', 'Maio', 'Xuño', 'Xullo', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Decembro']
	month_abbreviations = ['', 'Xan', 'Feb', 'Mar', 'Abr', 'Mai', 'Xun', 'Xul', 'Ago', 'Set', 'Out', 'Nov', 'Dec']
	day_names = ['', 'Luns', 'Martes', 'Mércores', 'Xoves', 'Venres', 'Sábado', 'Domingo']
	day_abbreviations = ['', 'Lun', 'Mar', 'Mer', 'xov', 'Ven' 'Sab', 'Dom']

class BasqueLocale(Locale):
	names = ['eu', 'eu_es', 'eu_eu']
	past = 'duela {0}'
	future = '{0} igarota'

	timeframes = {
		'now': 'Orain',
		# 'second': 'segundu bat',
		'seconds': 'segundu batzuk', # without specifying a number.
		#'seconds':  '{0} segundu', # specifying a number
		'minute': 'minutu bat',
		'minutes': '{0} minutu',
		'hour': 'ordu bat',
		'hours': '{0} ordu',
		'day': 'egun bat',
		'days': '{0} egun',
		'month': 'hilabete bat',
		'months': '{0} hilabete',
		'year': 'urte bat',
		'years': '{0} urte',
	}

	month_names = ['', 'Urtarrilak', 'Otsailak', 'Martxoak', 'Apirilak', 'Maiatzak', 'Ekainak', 'Uztailak', 'Abuztuak', 'Irailak', 'Urriak', 'Azaroak', 'Abenduak']
	month_abbreviations = ['', 'urt', 'ots', 'mar', 'api', 'mai', 'eka', 'uzt', 'abu', 'ira', 'urr', 'aza', 'abe']
	day_names = ['', 'Asteleehna', 'Asteartea', 'Asteazkena', 'Osteguna', 'Ostirala', 'Larunbata', 'Igandea']
	day_abbreviations = ['', 'al', 'ar', 'az', 'og', 'ol', 'lr', 'ig']

