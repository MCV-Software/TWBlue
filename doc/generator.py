# -*- coding: utf-8 -*-
import markdown
import os
from codecs import open as _open
import languageHandler
languageHandler.setLanguage("en")
import strings
import changelog

# the list of supported language codes of TW Blue
languages = ["en", "es", "fr", "de", "it", "gl", "ja", "ru", "ro", "eu", "ca"]
#"eu", "ar", "ca", "es", "fi", "fr", "gl", "hu", "it", "pl", "pt", "ru", "tr"]

def generate_document(language, document_type="documentation"):
 reload(languageHandler)
 if document_type == "documentation":
  translation_file = "twblue-documentation"
  languageHandler.setLanguage(language, translation_file)
  reload(strings)
  markdown_file = markdown.markdown("\n".join(strings.documentation[1:]), extensions=["markdown.extensions.toc"])
  title = strings.documentation[0]
  filename = "manual.html"
 elif document_type == "changelog":
  translation_file = "twblue-changelog"
  languageHandler.setLanguage(language, translation_file)
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
 if not os.path.exists(language):
  os.mkdir(language)
 mdfile = _open("%s/%s" % (language, filename), "w", encoding="utf-8")
 mdfile.write(first_html_block)
 mdfile.close()

def create_documentation():
 print("Creating documentation in the supported languages...\n")
 for i in languages:
  print("Creating documentation for: %s" % (i,))
  generate_document(i)
  generate_document(i, "changelog")
 print("Done")

create_documentation()