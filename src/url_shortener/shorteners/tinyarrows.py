
from future import standard_library
standard_library.install_aliases()
import urllib.request, urllib.parse, urllib.error

from .url_shortener import URLShortener

class TinyArrowsShortener (URLShortener):
 def __init__ (self, *args, **kwargs):
  self.name = "TinyArro.ws"
  super(TinyArrowsShortener, self).__init__(*args, **kwargs)

 def _shorten (self, url):
  answer = url
  answer = urllib.request.urlopen("http://tinyarro.ws/api-create.php?utfpure=1&url=%s" % urllib.parse.quote(url)).read()
  return answer

 def created_url(self, url):
  return False
