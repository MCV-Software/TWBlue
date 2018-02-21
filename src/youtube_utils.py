# -*- coding: utf-8 -*-
import youtube_dl

def get_video_url(url):
 ydl = youtube_dl.YoutubeDL({'quiet': True, 'format': 'bestaudio/best', 'outtmpl': u'%(id)s%(ext)s'})
 with ydl:
  result = ydl.extract_info(url, download=False)
 if 'entries' in result:
  video = result['entries'][0]
 else:
  video = result
 return video["url"]
