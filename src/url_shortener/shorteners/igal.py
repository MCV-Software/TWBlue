from url_shortener import URLShortener
import requests
import urllib
class IgalShortener (URLShortener):
 def __init__(self, *args, **kwargs):
  self.name = "i.gal"
  super(IgalShortener, self).__init__(*args, **kwargs)

 def _shorten (self, url):
  answer = url
  api = requests.get ("https://i.gal/api/v2/action/shorten?key=apikey&url=" + urllib.quote(url))
  if api.status_code == 200:
   answer = api.text
  return answer

 def created_url (self, url):
  return 'i.gal' in url
  