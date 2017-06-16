# -*- coding: cp1252 -*-

class InvalidSessionError(Exception): pass
class NonExistentSessionError(Exception): pass
class NotLoggedSessionError(BaseException): pass
class NotConfiguredSessionError(BaseException): pass
class RequireCredentialsSessionError(BaseException): pass
class AlreadyAuthorisedError(BaseException): pass