# -*- coding: utf-8 -*-
import logging
from logging.handlers import RotatingFileHandler
import paths
import sys

APP_LOG_FILE = 'debug.log'
ERROR_LOG_FILE = "error.log"
MESSAGE_FORMAT = "%(asctime)s %(name)s %(levelname)s: %(message)s"
DATE_FORMAT = "%d/%m/%Y %H:%M:%S"

formatter = logging.Formatter(MESSAGE_FORMAT, datefmt=DATE_FORMAT)

requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)
oauthlib_log = logging.getLogger("oauthlib")
oauthlib_log.setLevel(logging.WARNING)
requests_oauthlib_log = logging.getLogger("requests_oauthlib")
requests_oauthlib_log.setLevel(logging.WARNING)
suds_log = logging.getLogger("suds")
suds_log.setLevel(logging.WARNING)
server_log = logging.getLogger("BaseHTTPServer")
server_log.setLevel(logging.WARNING)


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

#handlers

app_handler = RotatingFileHandler(paths.logs_path(APP_LOG_FILE), mode="w")
app_handler.setFormatter(formatter)
app_handler.setLevel(logging.DEBUG)
logger.addHandler(app_handler)

error_handler = logging.FileHandler(paths.logs_path(ERROR_LOG_FILE), mode="w")
error_handler.setFormatter(formatter)
error_handler.setLevel(logging.ERROR)
logger.addHandler(error_handler)
