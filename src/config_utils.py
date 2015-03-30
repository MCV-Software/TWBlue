# -*- coding: utf-8 -*-
from configobj import ConfigObj, ParseError
from validate import Validator, ValidateError
import os

class ConfigLoadError(Exception): pass

def load_config(config_path, configspec_path=None, *args, **kwargs):
 spec = ConfigObj(configspec_path, encoding='UTF8', list_values=False, _inspec=True)
 try:
  config = ConfigObj(infile=config_path, configspec=spec, create_empty=True, encoding='UTF8', *args, **kwargs)
 except ParseError:
  raise ConfigLoadError("Unable to load %r" % config_path)
 validator = Validator()
 validated = config.validate(validator, copy=True)
 if validated == True:
  config.write()
  return config
