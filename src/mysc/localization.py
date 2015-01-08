import os
import languageHandler

def get(rootFolder):
 defaultLocale = languageHandler.curLang
 if len(defaultLocale) > 2:
  defaultLocale = defaultLocale[:2]
 if os.path.exists(rootFolder+"/"+defaultLocale):
  return defaultLocale
 else:
  return "en"

