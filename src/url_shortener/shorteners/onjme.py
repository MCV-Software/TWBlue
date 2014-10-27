import urllib

from url_shortener import URLShortener

class OnjmeShortener (URLShortener):
 def __init__ (self, *args, **kwargs):
  self.name = "Onj.me"
  super(OnjmeShortener, self).__init__(*args, **kwargs)

 def _shorten (self, url):
  answer = url
  api = urllib.urlopen ("http://onj.me/yourls-api.php?action=shorturl&format=simple&url=" + urllib.quote(url))
  if api.getcode() == 200:
   answer = api.read()
  api.close()
  return answer

 def created_url (self, url):
  return 'onj.me' in url.lower()
