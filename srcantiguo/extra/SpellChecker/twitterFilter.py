# -*- coding: utf-8 -*-
import re
from enchant.tokenize import Filter

class TwitterFilter(Filter):
    """Filter skipping over twitter usernames and hashtags.
    This filter skips any words matching the following regular expression:
    ^[#@](\S){1, }$
    That is, any words that resemble users and hashtags.
    """
    _pattern = re.compile(r"^[#@](\S){1,}$")
    def _skip(self,word):
        if self._pattern.match(word):
            return True
        return False
