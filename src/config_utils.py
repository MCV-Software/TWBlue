# -*- coding: utf-8 -*-
from configobj import ConfigObj, ParseError
from validate import Validator, ValidateError
import os
import string
from logging import getLogger
log = getLogger("config_utils")

class ConfigLoadError(Exception): pass

def load_config(config_path, configspec_path=None, *args, **kwargs):
 if os.path.exists(config_path):
  clean_config(config_path)
 spec = ConfigObj(configspec_path, encoding='UTF8', list_values=False, _inspec=True)
 try:
  config = ConfigObj(infile=config_path, configspec=spec, create_empty=True, encoding='UTF8', *args, **kwargs)
 except ParseError:
  raise ConfigLoadError("Unable to load %r" % config_path)
 validator = Validator()
 validated = config.validate(validator, preserve_errors=False, copy=True)
 if validated == True:
  config.write()
  return config
 else:
  log.exception("Error in config file: {0}".format(validated,))

def is_blank(arg):
 "Check if a line is blank."
 for c in arg:
  if c not in string.whitespace:
   return False
 return True

def get_keys(path):
 "Gets the keys of a configobj config file."
 res=[]
 fin=open(path)
 for line in fin:
  if not is_blank(line):
   res.append(line[0:line.find('=')].strip())
 fin.close()
 return res

def hist(keys):
 "Generates a histogram of an iterable."
 res={}
 for k in keys:
  res[k]=res.setdefault(k,0)+1
 return res

def find_problems(hist):
 "Takes a histogram and returns a list of items occurring more than once."
 res=[]
 for k,v in hist.items():
  if v>1:
   res.append(k)
 return res

def clean_config(path):
 "Cleans a config file. If duplicate values are found, delete all of them and just use the default."
 orig=[]
 cleaned=[]
 fin=open(path)
 for line in fin:
  orig.append(line)
 fin.close()
 for p in find_problems(hist(get_keys(path))):
  for o in orig:
   o.strip()
   if p not in o:
    cleaned.append(o)
 if len(cleaned) != 0:
  cam=open(path,'w')
  for c in cleaned:
   cam.write(c)
  cam.close()
  return True
 else:
  return False