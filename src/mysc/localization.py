import os
import languageHandler

def get(rootFolder):
# defaultLocale = gettext_windows.get_language()[0][:2]
 defaultLocale = languageHandler.curLang
 if len(defaultLocale) > 2:
  defaultLocale = defaultLocale[:2]
 print defaultLocale
 if os.path.exists(rootFolder+"/"+defaultLocale):
  return defaultLocale
 else:
  return "en"

