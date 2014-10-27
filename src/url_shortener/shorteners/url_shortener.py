from httplib import HTTPConnection
from urlparse import urlparse


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
  working = urlparse(url)
  if not working.netloc:
   raise TypeError, "Unable to parse URL."
  con = HTTPConnection(working.netloc)
  con.connect()
  con.request('GET', working.path)
  resp = con.getresponse()
  con.close()
  return resp.getheader('location')
