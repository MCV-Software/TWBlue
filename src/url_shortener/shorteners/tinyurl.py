from url_shortener import URLShortener
import urllib
class TinyurlShortener (URLShortener):
 def __init__(self, *args, **kwargs):
  self.name = "TinyURL.com"
  super(TinyurlShortener, self).__init__(*args, **kwargs)

 def _shorten (self, url):

  answer = url
  api = urllib.urlopen ("http://tinyurl.com/api-create.php?url=" + urllib.quote(url))
  if api.getcode() == 200:
   answer = api.read()
  api.close()
  return answer

 def created_url (self, url):
  return 'tinyurl.com' in url
