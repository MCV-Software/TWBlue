# -*- coding: utf-8 -*-
import subprocess
import youtube_dl

player = None # Let's control player from here

def get_video_url(url):
 ydl = youtube_dl.YoutubeDL({'quiet': True, 'format': '251', 'outtmpl': u'%(id)s%(ext)s'})
 with ydl:
  result = ydl.extract_info(url, download=False)
 if 'entries' in result:
  video = result['entries'][0]
 else:
  video = result
 return video["url"]

def play_video(url):
 global player
 if player != None:
  player.kill()
  player = None
 player = subprocess.Popen(["ffplay.exe", "-i", url, "-nodisp", "-vn", "-hide_banner"], stderr=subprocess.PIPE, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
 return player

def stop():
 global player
 if player != None:
  player.kill()
 player = None
