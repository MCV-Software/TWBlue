import urllib

from url_shortener import URLShortener


class IsgdShortener (URLShortener):
 def __init__ (self, *args, **kwargs):
  self.name = "Is.gd"
  return super(IsgdShortener, self).__init__(*args, **kwargs)

 def _shorten (self, url):
  answer = url
  api = urllib.urlopen ("http://is.gd/api.php?longurl=" + urllib.quote(url))
  if api.getcode() == 200:
   answer = api.read()
  api.close()
  return answer

 def created_url (self, url):
  return 'is.gd' in url
