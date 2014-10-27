from functools import wraps

def matches_url(url):
 def url_setter(func):
  @wraps(func)
  def internal_url_setter(*args, **kwargs):
   return func(*args, **kwargs)
  internal_url_setter.url = url
  return internal_url_setter
 return url_setter

def find_url_transformer(url):
 from audio_services import services
 funcs = []
 for i in dir(services):
  possible = getattr(services, i)
  if callable(possible) and hasattr(possible, 'url'):
   funcs.append(possible)
 for f in funcs:
  if url.lower().startswith(f.url.lower()):
   return f
 return services.convert_generic_audio
