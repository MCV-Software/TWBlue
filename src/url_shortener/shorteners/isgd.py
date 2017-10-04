import urllib
import requests
from url_shortener import URLShortener


class IsgdShortener (URLShortener):
 def __init__ (self, *args, **kwargs):
  self.name = "Is.gd"
  super(IsgdShortener, self).__init__(*args, **kwargs)

 def _shorten (self, url):
  answer = url
  api = requests.get ("http://is.gd/api.php?longurl=" + urllib.quote(url))
  if api.status_code == 200:
   answer = api.text
  return answer

 def created_url (self, url):
  return 'is.gd' in url
