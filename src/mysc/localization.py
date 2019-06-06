from __future__ import unicode_literals
import os
import languageHandler
import logging
log = logging.getLogger("mysc.localization")

def get(rootFolder):
 log.debug("Getting documentation folder. RootFolder: %s" % (rootFolder,))
 defaultLocale = languageHandler.curLang
 if len(defaultLocale) > 2:
  defaultLocale = defaultLocale[:2]
 log.debug("Locale: %s" % (defaultLocale,))
 if os.path.exists(rootFolder+"/"+defaultLocale):
  return defaultLocale
 else:
  log.debug("The folder does not exist, using the English folder...")
  return "en"

