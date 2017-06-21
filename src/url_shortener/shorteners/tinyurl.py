
from future import standard_library
standard_library.install_aliases()
from .url_shortener import URLShortener
import urllib.request, urllib.parse, urllib.error
class TinyurlShortener (URLShortener):
 def __init__(self, *args, **kwargs):
  self.name = "TinyURL.com"
  super(TinyurlShortener, self).__init__(*args, **kwargs)

 def _shorten (self, url):

  answer = url
  api = urllib.request.urlopen ("http://tinyurl.com/api-create.php?url=" + urllib.parse.quote(url))
  if api.getcode() == 200:
   answer = api.read()
  api.close()
  return answer

 def created_url (self, url):
  return 'tinyurl.com' in url
