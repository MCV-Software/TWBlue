# -*- coding: utf-8 -*-


from builtins import str
from past.utils import old_div
def convert_bytes(n):
 K, M, G, T, P = 1 << 10, 1 << 20, 1 << 30, 1 << 40, 1 << 50
 if   n >= P:
  return '%.2fPb' % (old_div(float(n), T))
 elif   n >= T:
  return '%.2fTb' % (old_div(float(n), T))
 elif n >= G:
  return '%.2fGb' % (old_div(float(n), G))
 elif n >= M:
  return '%.2fMb' % (old_div(float(n), M))
 elif n >= K:
  return '%.2fKb' % (old_div(float(n), K))
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
  string += _("%d day, ") % day
 elif day >= 2:
  string += _("%d days, ") % day
 if (hour == 1):
  string += _("%d hour, ") % hour
 elif (hour >= 2):
  string += _("%d hours, ") % hour
 if (min == 1):
  string += _("%d minute, ") % min
 elif (min >= 2):
  string += _("%d minutes, ") % min
 if sec >= 0 and sec <= 2:
  string += _("%s second") % sec_string
 else:
  string += _("%s seconds") % sec_string
 return string