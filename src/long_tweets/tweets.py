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
from twitter import utils

def get_id(url):
 return url.split("/")[-1]

def is_long(tweet):
 long = False
 for url in range(0, len(tweet["entities"]["urls"])):
  if "twitter.com" in tweet["entities"]["urls"][url]["expanded_url"]:
   long = get_id(tweet["entities"]["urls"][url]["expanded_url"])
 return long

def clear_url(tweet):
 urls = utils.find_urls_in_text(tweet["text"])
 tweet["message"] = tweet["message"].replace(urls[-1]+".", "")
 return tweet