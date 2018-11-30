# -*- coding: utf-8 -*-
############################################################
#    Copyright (c) 2015 Manuel Eduardo Cortéz Vallejo <manuel@manuelcortez.net>
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
from sessions.twitter import utils

def is_long(tweet):
 """ Check if the passed tweet contains a quote in its metadata.
  tweet dict: a tweet dictionary.
  returns True if a quote is detected, False otherwise."""
 if "quoted_status_id" in tweet and "quoted_status" in tweet:
  return tweet["quoted_status_id"]
 elif "retweeted_status" in tweet and "quoted_status_id" in tweet["retweeted_status"] and "quoted_status" in tweet["retweeted_status"]:
  return tweet["retweeted_status"]["quoted_status_id"]
 return False

def clear_url(tweet):
 """ Reads data from a quoted tweet and removes the link to the Status from the tweet's text.
  tweet dict: a tweet dictionary.
  returns a tweet dictionary without the URL to the status ID in its text to display."""
 if "retweeted_status" in tweet:
  if "full_text" in tweet["retweeted_status"]:
   value = "full_text"
  else:
   value = "text"
  urls = utils.find_urls_in_text(tweet["retweeted_status"][value])
  try: tweet["message"] = tweet["message"].replace(urls[-1], "")
  except IndexError: pass
 else:
  if "full_text" in tweet:
   value = "full_text"
  else:
   value = "text"
  urls = utils.find_urls_in_text(tweet[value])
  try: tweet["message"] = tweet["message"].replace(urls[-1], "")
  except IndexError: pass
 return tweet