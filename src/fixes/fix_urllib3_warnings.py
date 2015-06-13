# -*- coding: utf-8 -*-
from requests.packages import urllib3

def fix():
 urllib3.disable_warnings()