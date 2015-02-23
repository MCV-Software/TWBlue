# -*- coding: utf-8 -*-
""" This module contains some bugfixes for packages used in TWBlue. We will make pull requests to the source code of these packages."""
import fix_arrow # A few new locales for Three languages in arrow.

def setup():
	fix_arrow.fix()