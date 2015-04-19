# -*- coding: utf-8 -*-
import argparse
import paths
import logging
import application
log = logging.getLogger("commandlineLauncher")

parser = argparse.ArgumentParser(description=application.name+" command line launcher")
group = parser.add_mutually_exclusive_group()
group.add_argument("-p", "--portable", help="Use " + application.name + " as a portable application.", action="store_true", default=True)
group.add_argument("-i", "--installed", help="Use " + application.name + " as an installed application. Config files will be saved in the user data directory", action="store_true")
parser.add_argument("-d", "--data-directory", action="store", dest="directory", help="Specifies the directory where " + application.name + " saves userdata.")
args = parser.parse_args()
log.debug("Starting " + application.name + " with the following arguments: installed = %s, portable = %s and directory = %s" % (args.installed, args.portable, args.directory))
if args.installed == True: paths.mode = "installed"
elif args.portable == True:
 paths.mode = "portable"
 if args.directory != None: paths.directory = args.directory
