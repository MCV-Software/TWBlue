
from future import standard_library
standard_library.install_aliases()
import urllib.request, urllib.parse, urllib.error

from .url_shortener import URLShortener

class HKCShortener (URLShortener):
 def __init__ (self, *args, **kwargs):
  self.name = "HKC.im"
  super(HKCShortener, self).__init__(*args, **kwargs)

 def _shorten (self, url):
  answer = url
  api = urllib.request.urlopen ("http://hkc.im/yourls-api.php?action=shorturl&format=simple&url=" + urllib.parse.quote(url))
  if api.getcode() == 200:
   answer = api.read()
  api.close()
  return answer

 def created_url (self, url):
  return 'hkc.im' in url.lower()
