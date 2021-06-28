import  shutil
import os
import sys

def create_archive():
	os.chdir("..\\src")
	print("Creating zip archive...")
	folder = "dist"
	shutil.make_archive("twblue", "zip", folder)
	os.chdir("..\\scripts")

create_archive()