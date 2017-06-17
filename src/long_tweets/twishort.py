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

from builtins import range
import requests
import keys
import logging
log = logging.getLogger("long_tweets.twishort")
from twitter import utils
from requests_oauthlib import OAuth1Session

def get_twishort_uri(url):
 try:
  return url.split("twishort.com/")[1]
 except ValueError:
  return False

def is_long(tweet):
 longtw = False
 for url in range(0, len(tweet["entities"]["urls"])):
  try:
   if tweet["entities"]["urls"][url] != None and "twishort.com" in tweet["entities"]["urls"][url]["expanded_url"]:
    longtw = get_twishort_uri(tweet["entities"]["urls"][url]["expanded_url"])
  except IndexError:
   pass
  # sometimes Twitter returns URL's with None objects, so let's take it.
  # see https://github.com/manuelcortez/TWBlue/issues/103
  except TypeError:
   pass
 if not longtw and "retweeted_status" in tweet:
  for url in range(0, len(tweet["retweeted_status"]["entities"]["urls"])):
   try:
    if tweet["retweeted_status"]["entities"]["urls"][url] != None and "twishort.com" in tweet["retweeted_status"]["entities"]["urls"][url]["expanded_url"]:
     long = get_twishort_uri(tweet["retweeted_status"]["entities"]["urls"][url]["expanded_url"])
   except IndexError:
    pass
   except TypeError:
    pass
 return longtw

def get_full_text(uri):
 try:
  r = requests.get("http://api.twishort.com/1.1/get.json", params={"uri": uri, "api_key": keys.keyring.get("twishort_api_key")})
  msg = r.json()["text"]
  # Try to parse possible HTML entities.
  from twitter.compose import StripChars
  msg = StripChars(msg)
  return msg
 except:
  return False

def create_tweet(user_token, user_secret, text, media=0):
 twitter = OAuth1Session(keys.keyring.get("api_key"), client_secret=keys.keyring.get("api_secret"), resource_owner_key=user_token, resource_owner_secret=user_secret)
 twishort_key=keys.keyring.get("twishort_api_key")
 x_auth_service_provider = "https://api.twitter.com/1.1/account/verify_credentials.json"
 twishort_post_url = "http://api.twishort.com/1.1/post.json"
 twishort_update_ids_url = "http://api.twishort.com/1.1/update_ids.json"
 r=requests.Request('GET', x_auth_service_provider)
 prep=twitter.prepare_request(r)
 resp=twitter.send(prep)
 twitter.headers={
  'X-Auth-Service-Provider':x_auth_service_provider,
  'X-Verify-Credentials-Authorization':prep.headers['Authorization'],
 }
 data = {'api_key':twishort_key,
 "text": text.encode("utf-8"),
 "media": media}
 response = twitter.post(twishort_post_url, data=data)
 try:
  return response.json()["text_to_tweet"]
 except:
  log.exception("There was a problem creating a long tweet.")