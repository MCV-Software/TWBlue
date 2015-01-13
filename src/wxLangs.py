import wx
import languageHandler

def getLanguage():
	lang = languageHandler.curLang
	lang = lang[:2]
	languages = {"ar": wx.LANGUAGE_ARABIC,
	"ca": wx.LANGUAGE_CATALAN,
	"en": wx.LANGUAGE_ENGLISH,
	"es": wx.LANGUAGE_SPANISH,
	"eu": wx.LANGUAGE_BASQUE,
	"fr": wx.LANGUAGE_FRENCH,
	"fi": wx.LANGUAGE_FINNISH,
	"gl": wx.LANGUAGE_GALICIAN,
	"hu": wx.LANGUAGE_HUNGARIAN,
	"it": wx.LANGUAGE_ITALIAN,
	"pl": wx.LANGUAGE_POLISH,
	"pt": wx.LANGUAGE_PORTUGUESE,
	"de": wx.LANGUAGE_GERMAN,
	"ru": wx.LANGUAGE_RUSSIAN,
	"tr": wx.LANGUAGE_TURKISH,
	}
	return languages[lang]