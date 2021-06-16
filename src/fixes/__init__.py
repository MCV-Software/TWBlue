# -*- coding: utf-8 -*-
""" This module contains some bugfixes for packages used in TWBlue."""
from __future__ import absolute_import
from __future__ import unicode_literals
import sys
from . import fix_arrow # A few new locales for Three languages in arrow.
from . import fix_libloader # Regenerates comcache properly.
from . import fix_urllib3_warnings # Avoiding some SSL warnings related to Twython.
from . import fix_win32com
#from . import fix_requests #fix cacert.pem location for TWBlue binary copies
def setup():
    fix_arrow.fix()
    if hasattr(sys, "frozen"):
        fix_libloader.fix()
        fix_win32com.fix()
#		fix_requests.fix()
#	else:
#		fix_requests.fix(False)
    fix_urllib3_warnings.fix()
