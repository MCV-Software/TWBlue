import requests

class URLShortener (object):

 def __init__ (self, *args, **kwargs):
  #Stub out arguments, silly object. :(
  return super(URLShortener, self).__init__()

 def shorten (self, url):
  if self.created_url(url):
   return url
  else:
   return self._shorten(url)

 def _shorten (self, url):
  raise NotImplementedError

 def created_url (self, url):
  """Returns a boolean indicating whether or not this shortener created a provided url"""
  raise NotImplementedError

 def unshorten(self, url):
  try:
   r=requests.head(url)
   if 'location' in r.headers.keys():
    if 'dropbox.com' in r.headers['location']:
     return handle_dropbox(r.headers['location'])
    else:
     return r.headers['location']
   else: # if the head method does not work, use get instead. Performance may decrease
    r=requests.get(url, allow_redirects=False)
    return r.headers['location']
  except:
   return url #we cannot expand

def handle_dropbox(url):
 if url.endswith("dl=1"):
  return url
 else:
  return url.replace("dl=0", "dl=1")
