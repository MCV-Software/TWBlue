# -*- coding: cp1252 -*-
from __future__ import unicode_literals

class InvalidSessionError(Exception): pass
class NonExistentSessionError(Exception): pass
class NotLoggedSessionError(BaseException): pass
class NotConfiguredSessionError(BaseException): pass
class RequireCredentialsSessionError(BaseException): pass
class AlreadyAuthorisedError(BaseException): pass