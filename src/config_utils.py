# -*- coding: utf-8 -*-
from UserDict import UserDict
from configobj import ConfigObj, ParseError
from validate import Validator, VdtValueError
import os

"""We're using the configobj python package
from http://www.voidspace.org.uk/python/configobj.html """

class ConfigurationResetException(Exception):
 pass


class Configuration (UserDict):

 def __init__ (self, file=None, spec=None, *args, **kwargs):
  self.file = file
  self.spec = spec
  self.validator = Validator()
  self.setup_config(file=file, spec=spec)
  self.validated = self.config.validate(self.validator, copy=True)
  if self.validated:
   self.write()
  UserDict.__init__(self, self.config)

 def setup_config (self, file, spec):
 #The default way -- load from a file
  spec = ConfigObj(spec, list_values=False, encoding="utf-8")
  try:
   self.config = ConfigObj(infile=file, configspec=spec, create_empty=True, stringify=True, encoding="utf-8")
  except ParseError:
   os.remove(file)
   self.config = ConfigObj(infile=file, configspec=spec, create_empty=True, stringify=True)
   raise ConfigurationResetException
 def __getitem__ (self, *args, **kwargs):
  return dict(self.config).__getitem__(*args, **kwargs)

 def __setitem__ (self, *args, **kwargs):
  self.config.__setitem__(*args, **kwargs)
  UserDict.__setitem__(self, *args, **kwargs)

 def write (self):
  if hasattr(self.config, 'write'):
   self.config.write()

class SessionConfiguration (Configuration):
 def setup_config (self, file, spec):
  #No infile required.
  spec = ConfigObj(spec, list_values=False)
  self.config = ConfigObj(configspec=spec, stringify=True)
