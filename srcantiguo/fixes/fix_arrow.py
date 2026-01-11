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
    past = 'Hai {0}'
    future = 'En {0}'
    and_word = "e"

    timeframes = {
        'now': 'Agora',
        "second": "un segundo",
        'seconds': '{0} segundos',
        'minute': 'un minuto',
        'minutes': '{0} minutos',
        'hour': 'unha hora',
        'hours': '{0} horas',
        'day': 'un día',
        'days': '{0} días',
        "week": "unha semana",
        "weeks": "{0} semanas",
        'month': 'un mes',
        'months': '{0} meses',
        'year': 'un ano',
        'years': '{0} anos',
    }

    meridians = {"am": "am", "pm": "pm", "AM": "AM", "PM": "PM"}

    month_names = ['', 'xaneiro', 'febreiro', 'marzo', 'abril', 'maio', 'xuño', 'xullo', 'agosto', 'setembro', 'outubro', 'novembro', 'decembro']
    month_abbreviations = ['', 'xan', 'feb', 'mar', 'abr', 'mai', 'xun', 'xul', 'ago', 'set', 'out', 'nov', 'dec']
    day_names = ['', 'luns', 'martes', 'mércores', 'xoves', 'venres', 'sábado', 'domingo']
    day_abbreviations = ['', 'lun', 'mar', 'mer', 'xov', 'ven', 'sab', 'dom']
    ordinal_day_re = r"((?P<value>[1-3]?[0-9](?=[ºª]))[ºª])"

