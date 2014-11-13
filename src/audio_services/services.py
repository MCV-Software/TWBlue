from audio_services import matches_url
import json
import re
import urllib

@matches_url('https://audioboom.com')
def convert_audioboom(url):
 if "audioboom.com" not in url.lower():
  raise TypeError('%r is not a valid URL' % url)
 audio_id = url.split('.com/')[-1]
 return 'https://audioboom.com/%s.mp3' % audio_id

@matches_url ('http://soundcloud.com/')
def convert_soundcloud (url):
 client_id = "df8113ca95c157b6c9731f54b105b473"
 permalink = urllib.urlopen ('http://api.soundcloud.com/resolve.json?client_id=%s&url=%s' %(client_id, url))
 if permalink.getcode () == 404:
  permalink.close ()
  raise TypeError('%r is not a valid URL' % url)
 else:
  resolved_url = permalink.geturl ()
  permalink.close ()
 track_url = urllib.urlopen (resolved_url)
 track_data = json.loads (track_url.read ())
 track_url.close ()
 if track_data ['streamable']:
  return track_data ['stream_url'] + "?client_id=%s" %client_id
 else:
  raise TypeError('%r is not streamable' % url)

@matches_url('http://twup.me')
def convert_twup(url):
 result = re.match("^http://twup.me/(?P<audio_id>[A-Za-z0-9]+/?)$", url, re.I)
 if not result or result.group("audio_id") is None:
  raise TypeError('%r is not a valid URL' % url)
 audio_id = result.group("audio_id")
 return 'http://twup.me/%s' % audio_id

#@matches_url('http://sndup.net')
#def convert_sndup(url):
# result = re.match("^http://sndup.net/(?P<audio_id>[a-z0-9]+/?)(|d|l|a)/?$", url, re.I)
# if not result or result.group("audio_id") is None:
#  raise TypeError('%r is not a valid URL' % url)
# audio_id = result.group("audio_id")
# return 'http://sndup.net/%s/a' % audio_id

def convert_generic_audio(url):
 return url
