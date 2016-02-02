# -*- coding: utf-8 -*-
import argparse
import paths
import logging
import application
log = logging.getLogger("commandlineLauncher")

parser = argparse.ArgumentParser(description=application.name+" command line launcher")
parser.add_argument("-d", "--data-directory", action="store", dest="directory", help="Specifies the directory where " + application.name + " saves userdata.")
args = parser.parse_args()
log.debug("Starting " + application.name + " with the following arguments: directory = %s" % (args.directory))
if args.directory != None: paths.directory = args.directory
