from requests import certs, utils, adapters
import paths
import config
import requests.sessions
orig_session_init=requests.sessions.Session.__init__

def patched_where():
 return paths.app_path("cacert.pem")

def fix(frozen):
 if frozen==True:
  certs.where=patched_where
  utils.DEFAULT_CA_BUNDLE_PATH=patched_where()
  adapters.DEFAULT_CA_BUNDLE_PATH=patched_where()
 requests.sessions.Session.__init__=patched_session_init
 requests.Session.__init__=patched_session_init
 requests.session.__init__=patched_session_init

def patched_session_init(self):
 orig_session_init(self)
 if config.app["proxy"]["server"] != "" and config.app["proxy"]["port"] != "" and config.app["proxy"]["type"] in config.proxyTypes:
  self.proxies={"http":"{0}://{1}:{2}/".format(config.app["proxy"]["type"], config.app["proxy"]["server"], config.app["proxy"]["port"]),
   "https": "{0}://{1}:{2}/".format(config.app["proxy"]["type"], config.app["proxy"]["server"], config.app["proxy"]["port"])}
  if config.app["proxy"]["user"] != "" and config.app["proxy"]["password"] != "":
   self.proxies={"http": "{0}://{1}:{2}@{3}:{4}/".format(config.app["proxy"]["type"], config.app["proxy"]["user"], config.app["proxy"]["password"], config.app["proxy"]["server"], config.app["proxy"]["port"]),
    "https": "{0}://{1}:{2}@{3}:{4}/".format(config.app["proxy"]["type"], config.app["proxy"]["user"], config.app["proxy"]["password"], config.app["proxy"]["server"], config.app["proxy"]["port"])}
