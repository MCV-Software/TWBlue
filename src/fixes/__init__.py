# -*- coding: utf-8 -*-
""" This module contains some bugfixes for packages used in TWBlue."""
import sys
import fix_arrow # A few new locales for Three languages in arrow.
# import fix_requests_cert_location # For a better compilation in Windows.
import fix_urllib3_warnings # Avoiding some SSL warnings related to Twython.

def setup():
	fix_arrow.fix()
#	if hasattr(sys, "frozen"):
#		fix_requests_cert_location.fix()
	fix_urllib3_warnings.fix()