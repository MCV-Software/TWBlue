# -*- coding: utf-8 -*-
import gettext
import os
import locale
import paths
import markdown
import shutil
from importlib import reload

# Languages already translated or translating the documentation.
documentation_languages = ["en", "es", "fr", "de", "it", "gl", "ja", "ru", "ro", "eu", "ca", "da", "sr"]


# Changelog translated languages.
changelog_languages = ["en", "ca", "de", "es", "eu", "fr", "gl", "ja", "ro", "ru", "sr"]

# this function will help us to have both strings.py and changelog.py without issues by installing a global dummy translation function.
def install_null_translation(name):
    _ = gettext.NullTranslations()
    _.install()
    return

def get_translations(name):
    """ Create translation instances for every language of the translated document. """
    translations = {}
    if "documentation" in name:
        langs = documentation_languages
    else:
        langs = changelog_languages
    for l in langs:
        if l != "en":
            _ = gettext.translation(name, os.path.join(paths.app_path(), "locales"), languages=[l])
            translations[l] = _
        else:
            _ = gettext.NullTranslations()
            translations[l] = _
    return translations

def generate_document(lang, lang_name, document_type="documentation"):
    """ Generates a document by using the provided lang object, which should be a translation, and lang_name, which should be the two letter code representing the language. """
    if document_type == "documentation":
        translation_file = "twblue-documentation"
        markdown_file = markdown.markdown("\n".join([lang.gettext(s) if s != "" else s for s in strings.documentation[1:]]), extensions=["markdown.extensions.toc"])
        title = lang.gettext(strings.documentation[0])
        filename = "manual.html"
    elif document_type == "changelog":
        translation_file = "twblue-changelog"
        markdown_file = markdown.markdown("\n".join([lang.gettext(s) if s != "" else s for s in changelog.documentation[1:]]), extensions=["markdown.extensions.toc"])
        title = lang.gettext(changelog.documentation[0])
        filename = "changelog.html"
    first_html_block = """<!doctype html>
    <html lang="%s">
    <head>
        <title>%s</title>
        <meta charset="utf-8">
        </head>
        <body>
        <header><h1>%s</h1></header>
        """ %  (lang_name, title, title)
    first_html_block = first_html_block+ markdown_file
    first_html_block = first_html_block + "\n</body>\n</html>"
    if not os.path.exists(os.path.join("documentation", lang_name)):
        os.mkdir(os.path.join("documentation", lang_name))
    mdfile = open(os.path.join("documentation", lang_name, filename), "w", encoding="utf-8")
    mdfile.write(first_html_block)
    mdfile.close()

def create_documentation():
    changelog_translations = get_translations("twblue-changelog")
    documentation_translations = get_translations("twblue-documentation")
    print("Creating documentation in the supported languages...\n")
    if not os.path.exists("documentation"):
        os.mkdir("documentation")
    if os.path.exists(os.path.join("documentation", "license.txt")) == False:
        shutil.copy(os.path.join("..", "license.txt"), os.path.join("documentation", "license.txt"))
    for i in documentation_languages:
        print("Creating documentation for: %s" % (i,))
        generate_document(lang_name=i, lang=documentation_translations.get(i))
    for i in changelog_languages:
        print("Creating changelog  for: %s" % (i,))
        generate_document(lang_name=i, lang=changelog_translations.get(i), document_type="changelog")
    print("Done")

install_null_translation("twblue-documentation")
import strings
import changelog
create_documentation()