import urllib

from url_shortener import URLShortener


class ClckruShortener (URLShortener):
 def __init__ (self, *args, **kwargs):
  self.name = "clck.ru"
  return super(ClckruShortener, self).__init__(*args, **kwargs)

 def _shorten (self, url):
  answer = url
  api = urllib.urlopen ("http://clck.ru/--?url=" + urllib.quote(url))
  if api.getcode() == 200:
   answer = api.read()
  api.close()
  return answer

 def created_url (self, url):
  return 'clck.ru' in url
