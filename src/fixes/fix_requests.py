from requests import certs, utils, adapters
import paths

def patched_where():
 return paths.app_path(u"cacert.pem")

def fix():
 certs.where=patched_where
 utils.DEFAULT_CA_BUNDLE_PATH=patched_where()
 adapters.DEFAULT_CA_BUNDLE_PATH=patched_where()
