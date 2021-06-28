#! /usr/bin/env python
import sys
import os
import glob
import ftplib

transferred=0

def callback(progress):
	global transferred
	transferred = transferred+len(progress)
	print("Uploaded {}".format(convert_bytes(transferred),))

ftp_server = os.environ.get("FTP_SERVER") or sys.argv[1]
ftp_username = os.environ.get("FTP_USERNAME") or sys.argv[2]
ftp_password = os.environ.get("FTP_PASSWORD") or sys.argv[3]

print("Uploading files to the TWBlue server...")
print("Connecting to %s" % (ftp_server,))
connection = ftplib.FTP(ftp_server)
print("Connected to FTP server {}".format(ftp_server,))
connection.login(user=ftp_username, passwd=ftp_password)
print("Logged in successfully")
connection.cwd("web/pubs")
files = glob.glob("*.zip")+glob.glob("*.exe")
print("These files will be uploaded into the version folder: {}".format(files,))
for file in files:
	transferred = 0
	print("Uploading {}".format(file,))
	with open(file, "rb") as f:
		connection.storbinary('STOR %s' % file, f, callback=callback, blocksize=1024*1024) 
print("Upload completed. exiting...")
connection.quit()