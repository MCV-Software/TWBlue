# -*- coding: utf-8 -*-
import gettext
import os
import locale
import paths
import markdown
import shutil
from codecs import open as _open
from importlib import reload

def get_translation_function(name, language):
 if language == "en":
  return gettext.NullTranslations()
 translation_function = gettext.translation(name, os.path.join(paths.app_path(), "locales"), languages=[language])
 return translation_function

# the list of supported language codes of TW Blue
languages = ["en", "es", "fr", "de", "it", "gl", "ja", "ru", "ro", "eu", "ca", "da", "sr"]

def generate_document(language, document_type="documentation"):
 if document_type == "documentation":
  translation_file = "twblue-documentation"
  translation_function = get_translation_function(translation_file, language)
  markdown_file = markdown.markdown("\n".join([translation_function.gettext(s[:-1]) if s != "\n" else s for s in strings.documentation[1:]]), extensions=["markdown.extensions.toc"])
  title = translation_function.gettext(strings.documentation[0][:-1])
  filename = "manual.html"
 elif document_type == "changelog":
  translation_file = "twblue-changelog"
  translation_function = get_translation_function(translation_file, language)
  markdown_file = markdown.markdown("\n".join([translation_function.gettext(s[:-1]) if s != "\n" else s for s in changelog.documentation[1:]]), extensions=["markdown.extensions.toc"])
  title = translation_function.gettext(changelog.documentation[0][:-1])
  filename = "changelog.html"
 first_html_block = """<!doctype html>
 <html lang="%s">
 <head>
  <title>%s</title>
  <meta charset="utf-8">
  </head>
  <body>
  <header><h1>%s</h1></header>
  """ %  (language, title, title)
 first_html_block = first_html_block+ markdown_file
 first_html_block = first_html_block + "\n</body>\n</html>"
 if not os.path.exists(os.path.join("documentation", language)):
  os.mkdir(os.path.join("documentation", language))
 mdfile = _open(os.path.join("documentation", language, filename), "w", encoding="utf-8")
 mdfile.write(first_html_block)
 mdfile.close()

def create_documentation():
 print("Creating documentation in the supported languages...\n")
 if not os.path.exists("documentation"):
  os.mkdir("documentation")
 if os.path.exists(os.path.join("documentation", "license.txt")) == False:
  shutil.copy(os.path.join("..", "license.txt"), os.path.join("documentation", "license.txt"))
 for i in languages:
  print("Creating documentation for: %s" % (i,))
  try:
   generate_document(i)
   generate_document(i, "changelog")
  except:
   continue
 print("Done")

import strings
import changelog
create_documentation()