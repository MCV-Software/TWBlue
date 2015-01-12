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
import re

api_key = "d757b8e7f9221d8b95880a02bab524b7"

def get_tweet(uri):
 global api_key
 data = requests.get("http://api.twishort.com/1.1/get.json", params={"uri": uri, "api_key": api_key})
 return data.json()["text"]

def get_uri(url):
 url_ = re.search("twishort.com/", url)
 return url[url_.end():]

