from audio_services import matches_url
import json
import re
import urllib.request, urllib.parse, urllib.error

@matches_url('https://audioboom.com')
def convert_audioboom(url):
 if "audioboom.com" not in url.lower():
  raise TypeError('%r is not a valid URL' % url)
 audio_id = url.split('.com/')[-1]
 return 'https://audioboom.com/%s.mp3' % audio_id

@matches_url ('https://soundcloud.com/')
def convert_soundcloud (url):
 client_id = "df8113ca95c157b6c9731f54b105b473"
 permalink = urllib.request.urlopen ('http://api.soundcloud.com/resolve.json?client_id=%s&url=%s' %(client_id, url))
 if permalink.getcode () == 404:
  permalink.close ()
  raise TypeError('%r is not a valid URL' % url)
 else:
  resolved_url = permalink.geturl ()
  permalink.close ()
 track_url = urllib.request.urlopen (resolved_url)
 track_data = json.loads (track_url.read ())
 track_url.close ()
 if track_data ['streamable']:
  return track_data ['stream_url'] + "?client_id=%s" %client_id
 else:
  raise TypeError('%r is not streamable' % url)

def convert_generic_audio(url):
 return url
