# -*- coding: utf-8 -*-
import gettext
import os
import locale
import paths
import markdown
import shutil
from codecs import open as _open
from importlib import reload

def change_language(name, language):
 global _
 os.environ["lang"] = language
 _ = gettext.install(name, os.path.join(paths.app_path(), "locales"))

# the list of supported language codes of TW Blue
languages = ["en", "es", "fr", "de", "it", "gl", "ja", "ru", "ro", "eu", "ca", "da"]

def generate_document(language, document_type="documentation"):
 if document_type == "documentation":
  translation_file = "twblue-documentation"
  change_language(translation_file, language)
  reload(strings)
  markdown_file = markdown.markdown("\n".join(strings.documentation[1:]), extensions=["markdown.extensions.toc"])
  title = strings.documentation[0]
  filename = "manual.html"
 elif document_type == "changelog":
  translation_file = "twblue-changelog"
  change_language(translation_file, language)
  reload(changelog)
  markdown_file = markdown.markdown("\n".join(changelog.documentation[1:]), extensions=["markdown.extensions.toc"])
  title = changelog.documentation[0]
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
  generate_document(i)
  generate_document(i, "changelog")
 print("Done")

change_language("twblue-documentation", "en")
import strings
import changelog
create_documentation()