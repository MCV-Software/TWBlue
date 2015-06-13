# -*- coding: utf-8 -*-
import paths

def where():
 return paths.app_path(r"requests\cacert.pem")

def fix():
 from requests import certs
 certs.where = where