import requests

class URLShortener (object):

 def __init__ (self, *args, **kwargs):
  #Stub out arguments, silly object. :(
  return super(URLShortener, self).__init__()

 def shorten (self, url):
  if self.created_url(url):
   return url
  else:
   return self._shorten(url)

 def _shorten (self, url):
  raise NotImplementedError

 def created_url (self, url):
  """Returns a boolean indicating whether or not this shortener created a provided url"""
  raise NotImplementedError

 def unshorten(self, url):
  try:
   r=requests.head(url)
   return r.headers['location']
  except:
   return url #we cannot expand
