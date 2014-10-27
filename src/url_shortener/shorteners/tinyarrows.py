import urllib

from url_shortener import URLShortener

class TinyArrowsShortener (URLShortener):
 def __init__ (self, *args, **kwargs):
  self.name = "TinyArro.ws"
  super(TinyArrowsShortener, self).__init__(*args, **kwargs)

 def _shorten (self, url):
  answer = url
  answer = urllib.urlopen("http://tinyarro.ws/api-create.php?utfpure=1&url=%s" % urllib.quote(url)).read()
  return answer.decode('UTF-8')

 def created_url(self, url):
  return False
