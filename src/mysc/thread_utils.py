# -*- coding: utf-8 -*-
import threading
import wx
from twython import TwythonRateLimitError
import time

def call_threaded(func, *args, **kwargs):
 #Call the given function in a daemonized thread and return the thread.
 def new_func(*a, **k):
  try:
   func(*a, **k)
  except TwythonRateLimitError:
   wx.MessageDialog(None, u"Has superado el límite de llamadas a la API que Twitter permite. Eso puede deberse a  muchas líneas temporales abiertas, a abrir y cerrar el programa en un periodo corto de tiempo, o a tener muchas llamadas a la API en tu configuración. TW Blue esperará 5 minutos y volverá a intentarlo.", u"Límite de llamadas a la API Superado", wx.ICON_ERROR|wx.OK).ShowModal()
   time.sleep(300)
   call_threaded(func, *args, **kwargs)
#  except:
#   pass
 thread = threading.Thread(target=new_func, args=args, kwargs=kwargs)
 thread.daemon = True
 thread.start()
 return thread
