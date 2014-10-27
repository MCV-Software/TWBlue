import gettext_windows, os

def get(rootFolder):
 defaultLocale = gettext_windows.get_language()[0][:2]
 if os.path.exists(rootFolder+"/"+defaultLocale):
  return defaultLocale
 else:
  return "en"

