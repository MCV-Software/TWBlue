# -*- coding: utf-8 -*-
import argparse
import paths

parser = argparse.ArgumentParser(description="TW Blue command line launcher")
group = parser.add_mutually_exclusive_group()
group.add_argument("-p", "--portable", help="Use TW Blue as a portable aplication", action="store_true", default=True)
group.add_argument("-i", "--installed", help="Use TW Blue as an installed application. Config files will be saved on the user data directory", action="store_true")
parser.add_argument("-d", "--data-directory", action="store", dest="directory", help="Specifies the directory where TW Blue saves the data files")
args = parser.parse_args()
if args.installed == True: paths.mode = "installed"
elif args.portable == True:
 paths.mode = "portable"
 if args.directory != None: paths.directory = args.directory
