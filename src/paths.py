# -*- coding: utf-8 -*-
import sys
import platform
import os
import glob
from platform_utils import paths as paths_

mode = "portable"
directory = None
fsencoding = sys.getfilesystemencoding()

if len(glob.glob("Uninstall.exe")) > 0: # installed copy
    mode= "installed"

def app_path():
    return paths_.app_path()

def config_path():
    global mode, directory
    if mode == "portable":
        if directory != None: path = os.path.join(directory, "config")
        elif directory == None: path = os.path.join(app_path(), "config")
    elif mode == "installed":
        path = os.path.join(data_path(), "config")
    if not os.path.exists(path):
        #		log.debug("%s path does not exist, creating..." % (path,))
        os.mkdir(path)
    return path

def logs_path():
    global mode, directory
    if mode == "portable":
        if directory != None: path = os.path.join(directory, "logs")
        elif directory == None: path = os.path.join(app_path(), "logs")
    elif mode == "installed":
        path = os.path.join(data_path(), "logs")
    if not os.path.exists(path):
        #		log.debug("%s path does not exist, creating..." % (path,))
        os.mkdir(path)
    return path

def data_path(app_name='socializer'):
    if platform.system() == "Windows":
        data_path = os.path.join(os.getenv("AppData"), app_name)
    else:
        data_path = os.path.join(os.environ['HOME'], ".%s" % app_name)
    if not os.path.exists(data_path):
        os.mkdir(data_path)
    return data_path

def locale_path():
    return os.path.join(app_path(), "locales")

def sound_path():
    return os.path.join(app_path(), "sounds")

def com_path():
    global mode, directory
    if mode == "portable":
        if directory != None: path = os.path.join(directory, "com_cache")
        elif directory == None: path = os.path.join(app_path(), "com_cache")
    elif mode == "installed":
        path = os.path.join(data_path(), "com_cache")
    if not os.path.exists(path):
        #		log.debug("%s path does not exist, creating..." % (path,))
        os.mkdir(path)
    return path
