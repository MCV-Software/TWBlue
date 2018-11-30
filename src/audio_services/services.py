from audio_services import matches_url
import json
import re
import urllib
import youtube_utils

@matches_url('https://audioboom.com')
def convert_audioboom(url):
 if "audioboom.com" not in url.lower():
  raise TypeError('%r is not a valid URL' % url)
 audio_id = url.split('.com/')[-1]
 return 'https://audioboom.com/%s.mp3' % audio_id

@matches_url ('https://soundcloud.com/')
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

@matches_url ('https://www.youtube.com/watch')
def convert_youtube_long (url):
 return youtube_utils.get_video_url(url)

@matches_url ('http://anyaudio.net/listen')
def convert_anyaudio(url):
 values = url.split("audio=")
 if len(values) != 2:
  raise TypeError('%r is not streamable' % url)
 return "http://anyaudio.net/audiodownload?audio=%s" % (values[1],)

def convert_generic_audio(url):
 return url
