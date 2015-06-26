# -*- coding: utf-8 -*-
import markdown
import os
from codecs import open as _open
import languageHandler
languageHandler.setLanguage("en")
import strings

# the list of supported language codes of TW Blue
languages = ["en", "es"]
#"eu", "ar", "ca", "es", "fi", "fr", "gl", "hu", "it", "pl", "pt", "ru", "tr"]

def generate_document(language):
 reload(languageHandler)
 languageHandler.setLanguage(language)
 reload(strings)
 markdown_file = markdown.markdown("\n".join(strings.documentation[1:]), extensions=["markdown.extensions.toc"])
 first_html_block = """<!doctype html>
 <html lang="%s">
 <head>
  <title>%s</title>
  <meta charset="utf-8">
  </head>
  <body>
  <header><h1>%s</h1></header>
  """ %  (language, strings.documentation[0], strings.documentation[0])
 first_html_block = first_html_block+ markdown_file
 first_html_block = first_html_block + "\n</body>\n</html>"
 if not os.path.exists(language):
  os.mkdir(language)
 mdfile = _open("%s/manual.html" % language, "w", encoding="utf-8")
 mdfile.write(first_html_block)
 mdfile.close()

def create_documentation():
 print("Creating documentation in the supported languages...\n")
 for i in languages:
  print("Creating documentation for: %s" % (i,))
  generate_document(i)
 print("Done")

create_documentation()