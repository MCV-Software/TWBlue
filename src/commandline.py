# -*- coding: utf-8 -*-
import argparse
import paths
import logging
log = logging.getLogger("commandlineLauncher")

parser = argparse.ArgumentParser(description="TW Blue command line launcher")
group = parser.add_mutually_exclusive_group()
group.add_argument("-p", "--portable", help="Use TW Blue as a portable application.", action="store_true", default=True)
group.add_argument("-i", "--installed", help="Use TW Blue as an installed application. Config files will be saved in the user data directory", action="store_true")
parser.add_argument("-d", "--data-directory", action="store", dest="directory", help="Specifies the directory where TW Blue saves userdata.")
args = parser.parse_args()
log.debug("Starting TWBlue with the following arguments: installed = %s, portable = %s and directory = %s" % (args.installed, args.portable, args.directory))
if args.installed == True: paths.mode = "installed"
elif args.portable == True:
 paths.mode = "portable"
 if args.directory != None: paths.directory = args.directory
