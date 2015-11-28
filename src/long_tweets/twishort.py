# -*- coding: utf-8 -*-
############################################################
#    Copyright (c) 2013, 2014 Manuel Eduardo Cortéz Vallejo <manuel@manuelcortez.net>
#       
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
############################################################
import requests
import keys
import application
from twitter import utils

def get_twishort_uri(url):
 try:
  return url.split("twishort.com/")[1]
 except IndexError:
  return False

def is_long(tweet):
 long = False
 for url in range(0, len(tweet["entities"]["urls"])):
  if "twishort.com" in tweet["entities"]["urls"][url]["expanded_url"]:
   long = get_twishort_uri(tweet["entities"]["urls"][url]["expanded_url"])
 return long

def get_full_text(uri):
# try:
 r = requests.get("http://api.twishort.com/1.1/get.json", params={"uri": uri, "api_key": keys.keyring.get("twishort_api_key")})
 return r.json()["text"]
# except:
#  return False

def create_tweet(user_token, user_secret, text, media=0):
 if application.snapshot == True:
  url = "http://twblue.es/snapshot_twishort.php"
 else:
  url = "http://twblue.es/stable_twishort.php"
 data = {"user_token": user_token,
 "user_secret": user_secret,
 "text": text.encode("utf-8"),
 "media": media}
 response = requests.post(url, data=data)
# print response.json()
 return response.json()["text_to_tweet"]