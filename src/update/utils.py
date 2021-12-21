# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from builtins import str
def convert_bytes(n):
    K, M, G, T, P = 1 << 10, 1 << 20, 1 << 30, 1 << 40, 1 << 50
    if   n >= P:
        return '%.2fPb' % (float(n) / T)
    elif   n >= T:
        return '%.2fTb' % (float(n) / T)
    elif n >= G:
        return '%.2fGb' % (float(n) / G)
    elif n >= M:
        return '%.2fMb' % (float(n) / M)
    elif n >= K:
        return '%.2fKb' % (float(n) / K)
    else:
        return '%d' % n

def seconds_to_string(seconds, precision=0):
    day = seconds // 86400
    hour = seconds // 3600
    min = (seconds // 60) % 60
    sec = seconds - (hour * 3600) - (min * 60)
    sec_spec = "." + str(precision) + "f"
    sec_string = sec.__format__(sec_spec)
    string = ""
    if day == 1:
        string += _(u"%d day, ") % day
    elif day >= 2:
        string += _(u"%d days, ") % day
    if (hour == 1):
        string += _(u"%d hour, ") % hour
    elif (hour >= 2):
        string += _("%d hours, ") % hour
    if (min == 1):
        string += _(u"%d minute, ") % min
    elif (min >= 2):
        string += _(u"%d minutes, ") % min
    if sec >= 0 and sec <= 2:
        string += _(u"%s second") % sec_string
    else:
        string += _(u"%s seconds") % sec_string
    return string
