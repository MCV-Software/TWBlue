from __future__ import unicode_literals
from future import standard_library
standard_library.install_aliases()
from . url_shortener import URLShortener
import requests
import urllib.request, urllib.parse, urllib.error
class AcortameShortener (URLShortener):
 def __init__(self, *args, **kwargs):
  self.name = "acorta.me"
  super(AcortameShortener, self).__init__(*args, **kwargs)

 def _shorten (self, url):
  answer = url
  api = requests.get ("https://acorta.me/api.php?action=shorturl&format=simple&url=" + urllib.parse.quote(url))
  if api.status_code == 200:
   answer = api.text
  return answer

 def created_url (self, url):
  return 'acorta.me' in url

 def unshorten (self, url):
  if not 'acorta.me' in url:
   #use generic expand method
   return super(AcortameShortener, self).unshorten(url)
  answer = url
  api = requests.get ("https://acorta.me/api.php?action=expand&format=simple&shorturl=" + urllib.parse.quote(url))
  if api.status_code == 200:
   answer = api.text
  return answer
