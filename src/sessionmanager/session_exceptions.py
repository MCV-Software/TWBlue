# -*- coding: cp1252 -*-
import exceptions

class InvalidSessionError(exceptions.Exception): pass
class NonExistentSessionError(exceptions.Exception): pass
class NotLoggedSessionError(exceptions.BaseException): pass
class NotConfiguredSessionError(exceptions.BaseException): pass
class RequireCredentialsSessionError(exceptions.BaseException): pass
class AlreadyAuthorisedError(exceptions.BaseException): pass