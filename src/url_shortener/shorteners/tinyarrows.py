import urllib.request, urllib.parse, urllib.error
import requests
from .url_shortener import URLShortener

class TinyArrowsShortener (URLShortener):
 def __init__ (self, *args, **kwargs):
  self.name = "TinyArro.ws"
  super(TinyArrowsShortener, self).__init__(*args, **kwargs)

 def _shorten (self, url):
  answer = url
  api = requests.get("http://tinyarro.ws/api-create.php?utfpure=1&url=%s" % urllib.parse.quote(url))
  if api.status_code == 200:
   answer = api.text
  return answer.decode('UTF-8')

 def created_url(self, url):
  return "tinyarro.ws" in url
