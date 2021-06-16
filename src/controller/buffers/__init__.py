# -*- coding: utf-8 -*-
""" this package contains logic related to buffers. A buffer is a virtual representation of a group of items retrieved through the Social network API'S.
  Ideally, new social networks added to TWBlue will have its own "buffers", and these buffers should be defined within this package, following the Twitter example.
  Currently, the package contains the following modules:
    * baseBuffers: Define a set of functions and structure to be expected in all buffers. New buffers should inherit its classes from one of the classes present here.
    * twitterBuffers: All other code, specific to Twitter.
"""
from __future__ import unicode_literals
