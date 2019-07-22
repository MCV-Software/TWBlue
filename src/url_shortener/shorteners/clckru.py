from __future__ import unicode_literals
from future import standard_library
standard_library.install_aliases()
import urllib.request, urllib.parse, urllib.error
import requests
from . url_shortener import URLShortener


class ClckruShortener (URLShortener):
 def __init__ (self, *args, **kwargs):
  self.name = "clck.ru"
  super(ClckruShortener, self).__init__(*args, **kwargs)

 def _shorten (self, url):
  answer = url
  api = requests.get ("http://clck.ru/--?url=" + urllib.parse.quote(url))
  if api.status_code == 200:
   answer = api.text
  return answer

 def created_url (self, url):
  return 'clck.ru' in url
