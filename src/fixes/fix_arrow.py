# -*- coding: utf-8 -*-
from arrow import locales
from arrow.locales import Locale

def fix():
    # insert a modified function so if there is no language available in arrow, returns English locale.
    locales.get_locale = get_locale

def get_locale(name):
    locale_cls = locales._locale_map.get(name.lower())
    if locale_cls is None:
        name = name[:2]
        locale_cls = locales._locale_map.get(name.lower())
        if locale_cls == None:
            return locales.EnglishLocale()
    return locale_cls()

class GalicianLocale(object):
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

