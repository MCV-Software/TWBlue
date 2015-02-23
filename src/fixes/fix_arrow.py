# -*- coding: utf-8 -*-
from arrow import locales
from arrow.locales import Locale

def fix():
	''' This function adds the Catala, Basque and galician locales to the list of locales supported in Arrow'''
	locales.CatalaLocale = CatalaLocale
	locales.GalicianLocale = GalicianLocale
	locales.BasqueLocale = BasqueLocale
	# We need to reassign the locales list for updating the list with our new contents.
	locales._locales = locales._map_locales()

class CatalaLocale(Locale):
	names = ['ca', 'ca_ca']
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
	names = ['gl', 'gl_gl']
	past = 'Fai {0}'
	future = '{0}' # I don't know what's the right phrase in Galician for the future.

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
	names = ['eu', 'eu_eu']
	past = 'duela {0}'
	future = '{0}' # I don't know what's the right phrase in Basque for the future.

	timeframes = {
		'now': 'Orain',
		'seconds': 'segundu',
		'minute': 'minutu bat',
		'minutes': '{0} minutu',
		'hour': 'ordu bat',
		'hours': '{0} ordu',
		'day': 'egun bat',
		'days': '{0} egun',
		'month': 'hilabete bat',
		'months': '{0} hilabet',
		'year': 'urte bat',
		'years': '{0} urte',
	}

	month_names = ['', 'Urtarrilak', 'Otsailak', 'Martxoak', 'Apirilak', 'Maiatzak', 'Ekainak', 'Uztailak', 'Abuztuak', 'Irailak', 'Urriak', 'Azaroak', 'Abenduak']
	month_abbreviations = ['', 'urt', 'ots', 'mar', 'api', 'mai', 'eka', 'uzt', 'abu', 'ira', 'urr', 'aza', 'abe']
	day_names = ['', 'Asteleehna', 'Asteartea', 'Asteazkena', 'Osteguna', 'Ostirala', 'Larunbata', 'Igandea']
	day_abbreviations = ['', 'al', 'ar', 'az', 'og', 'ol', 'lr', 'ig']

