# -*- coding: utf-8 -*-
import threading
import wx
from pubsub import pub
from twython import TwythonRateLimitError
import time

def call_threaded(func, *args, **kwargs):
 #Call the given function in a daemonized thread and return the thread.
 def new_func(*a, **k):
  try:
   func(*a, **k)
  except TwythonRateLimitError:
   pass
  except:
   logging.exception("Thread %d with function %r, args of %r, and kwargs of %r failed to run." % (threading.current_thread().ident, func, a, k))
#   pass
 thread = threading.Thread(target=new_func, args=args, kwargs=kwargs)
 thread.daemon = True
 thread.start()
 return thread

def stream_threaded(func, *args, **kwargs):
 def new_func(*a, **k):
  try:
   func(**k)
  except:
   pub.sendMessage("streamError", session=a[0])
 thread = threading.Thread(target=new_func, args=args, kwargs=kwargs)
 thread.daemon = True
 thread.start()
 return thread