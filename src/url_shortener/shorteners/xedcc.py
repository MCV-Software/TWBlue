import urllib

from url_shortener import URLShortener

class XedccShortener (URLShortener):
 def __init__ (self, *args, **kwargs):
  self.name = "Xed.cc"
  super(XedccShortener, self).__init__(*args, **kwargs)

 def _shorten (self, url):
  answer = url
  api = urllib.urlopen ("http://xed.cc/yourls-api.php?action=shorturl&format=simple&url=" + urllib.quote(url))
  if api.getcode() == 200:
   answer = api.read()
  api.close()
  return answer

 def created_url (self, url):
  return 'xed.cc' in url.lower()
