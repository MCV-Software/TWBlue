
from future import standard_library
standard_library.install_aliases()
import urllib.request, urllib.parse, urllib.error

from .url_shortener import URLShortener

class XedccShortener (URLShortener):
 def __init__ (self, *args, **kwargs):
  self.name = "Xed.cc"
  super(XedccShortener, self).__init__(*args, **kwargs)

 def _shorten (self, url):
  answer = url
  api = urllib.request.urlopen ("http://xed.cc/yourls-api.php?action=shorturl&format=simple&url=" + urllib.parse.quote(url))
  if api.getcode() == 200:
   answer = api.read()
  api.close()
  return answer

 def created_url (self, url):
  return 'xed.cc' in url.lower()
