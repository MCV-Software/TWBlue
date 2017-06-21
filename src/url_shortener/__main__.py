
from functools import wraps
from . import shorteners


def service_selecter (func):
 @wraps(func)
 def wrapper (*args, **kwargs):
  tmp = dict(kwargs)
  if 'service' in tmp:
   del(tmp['service'])
   kwargs['service'] = find_service(kwargs['service'], **tmp) or default_service()
  else:
   kwargs['service'] = default_service()
  return func(*args, **kwargs)
 return wrapper

@service_selecter
def shorten (url, service=None, **kwargs):
 return service(**kwargs).shorten(url)


@service_selecter
def unshorten (url, service=None, **kwargs):
 return service(**kwargs).unshorten(url)


def default_service ():
 return shorteners.TinyurlShortener

def find_service (service, **kwargs):
 for i in shorteners.__all__:
  obj = getattr(shorteners, i)(**kwargs)
  if obj.name.lower() == service.lower():
   return getattr(shorteners, i)

def list_services ():
 return [getattr(shorteners, i)().name for i in shorteners.__all__]

def unshorten_any (url):
 """Unshortens an URL using any available unshortener. Check to see if unshortened URL was created by a shortener (nested) and unshorten if so."""
 unshortened_url = shorteners.URLShortener().unshorten(url)
 # None is returned if URL not unshortened
 if unshortened_url:
  return unshorten_any(unshortened_url)
 return url
