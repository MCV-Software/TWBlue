from url_shortener import URLShortener
import urllib
class AcortameShortener (URLShortener):
 def __init__(self, *args, **kwargs):
  self.name = "acorta.me"
  super(AcortameShortener, self).__init__(*args, **kwargs)

 def _shorten (self, url):

  answer = url
  api = urllib.urlopen ("https://acorta.me/api.php?action=shorturl&format=simple&url=" + urllib.quote(url))
  if api.getcode() == 200:
   answer = api.read()
  api.close()
  return answer

 def created_url (self, url):
  return 'acorta.me' in url

 def unshorten (self, url):

  answer = url
  api = urllib.urlopen ("https://acorta.me/api.php?action=expand&format=simple&shorturl=" + urllib.quote(url))
  answer = api.read()
  api.close()
  return answer
