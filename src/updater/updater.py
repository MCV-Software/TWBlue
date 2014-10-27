#AutoUpdater
#Released under an MIT license

import logging
logger = logging.getLogger('updater')

import application
from urllib import FancyURLopener, URLopener
import urllib2
from functools import total_ordering
import hashlib
import os
try:
 from czipfile import ZipFile
except ImportError:
 from zipfile import ZipFile
import subprocess
import stat
import platform
import shutil
import json
if platform.system() == 'Windows':
 import win32api


class AutoUpdater(object):

 def __init__(self, URL, save_location, bootstrapper, app_path, postexecute=None, password=None, MD5=None, percentage_callback=None, finish_callback=None):
  """Supply a URL/location/bootstrapper filename to download a zip file from
     The finish_callback argument should be a Python function it'll call when done"""
  #Let's download the file using urllib
  self.complete = 0
  self.finish_callback = finish_callback #What to do on exit
  self.percentage_callback = percentage_callback or self.print_percentage_callback
  self.URL = URL
  self.bootstrapper = bootstrapper
  #The application path on the Mac should be 1 directory up from where the .app file is.
  tempstr = ""
  if (platform.system() == "Darwin"):
    for x in (app_path.split("/")):
      if (".app" in x):
        break
      else:
        tempstr = os.path.join(tempstr, x)
    app_path = "/" + tempstr + "/"
    #The post-execution path should include the .app file
    tempstr = ""
    for x in (postexecute.split("/")):
      if (".app" in x):
        tempstr = os.path.join(tempstr, x)
        break
      else:
        tempstr = os.path.join(tempstr, x)
    postexecute = "/" + tempstr
  self.app_path = app_path
  self.postexecute = postexecute
  logging.info("apppath: " + str(app_path))
  logging.info("postexecute: " + str(postexecute))
  self.password = password  
  self.MD5 = MD5
  self.save_location = save_location
  #self.save_location contains the full path, including the blabla.zip
  self.save_directory = os.path.join(*os.path.split(save_location)[:-1])
  #self.save_directory doesn't contain the blabla.zip

 def prepare_staging_directory(self):
  if not os.path.exists(self.save_directory):
   #We need to make all folders but the last one
   os.makedirs(self.save_directory)
   logger.info("Created staging directory  %s" % self.save_directory)

 def transfer_callback(self, count, bSize, tSize):
  """Callback to update percentage of download"""
  percent = int(count*bSize*100/tSize)
  self.percentage_callback(percent)

 @staticmethod
 def print_percentage_callback(percent):
  print percent

 def start_update(self):
  """Called to start the whole process"""
  logger.debug("URL: %s   SL: %s" % (self.URL, self.save_location))
  self.prepare_staging_directory()
  Listy = CustomURLOpener().retrieve(self.URL, self.save_location, reporthook=self.transfer_callback)
  if self.MD5:
   #Check the MD5
   if self.MD5File(location) != self.MD5:
    #ReDownload
    self.start_update()
  self.download_complete(Listy[0])

 def MD5File(self, fileName):
  "Custom function that will get the Md5 sum of our file"
  file_reference=open(fileName, 'rb').read() 
  return hashlib.md5(file_reference).hexdigest()

 def download_complete(self, location):
  """Called when the file is done downloading, and MD5 has been successfull"""
  logger.debug("Download complete.")
  zippy = ZipFile(location, mode='r')
  extracted_path = os.path.join(self.save_directory, os.path.basename(location).strip(".zip"))
  zippy.extractall(extracted_path, pwd=self.password)
  bootstrapper_path = os.path.join(self.save_directory, self.bootstrapper) #where we will find our bootstrapper
  old_bootstrapper_path = os.path.join(extracted_path, self.bootstrapper)
  if os.path.exists(bootstrapper_path):
   os.chmod(bootstrapper_path, 666)
   os.remove(bootstrapper_path)
  shutil.move(old_bootstrapper_path, self.save_directory) #move bootstrapper
  os.chmod(bootstrapper_path, stat.S_IRUSR|stat.S_IXUSR)
  if platform.system() == "Windows": 
   bootstrapper_command = r'%s' % bootstrapper_path
   bootstrapper_args = r'"%s" "%s" "%s" "%s"' % (os.getpid(), extracted_path, self.app_path, self.postexecute)
   win32api.ShellExecute(0, 'open', bootstrapper_command, bootstrapper_args, "", 5)
  else:
   #bootstrapper_command = [r'sh "%s" -l "%s" -d "%s" "%s"' % (bootstrapper_path, self.app_path, extracted_path, str(os.getpid()))]
   bootstrapper_command = r'"%s" "%s" "%s" "%s" "%s"' % (bootstrapper_path, os.getpid(), extracted_path, self.app_path, self.postexecute)
   shell = True
   #logging.debug("Final bootstrapper command: %r" % bootstrapper_command)
   subprocess.Popen([bootstrapper_command], shell=shell)
  self.complete = 1
  if callable(self.finish_callback):
   self.finish_callback()

 def cleanup(self):
  """Delete stuff"""
  try:
   shutil.rmtree(self.save_directory)
  except any:
   return

def find_update_url(URL, version):
 """Return a URL to an update of the application for the current platform at the given URL if one exists, or None""
  Assumes Windows, Linux, or Mac"""
 response = urllib2.urlopen(URL)
 json_str = response.read().strip("\n")
 json_p = json.loads(json_str)
 if is_newer(version, json_p['current_version']):
  if application.snapshot == False: return json_p['downloads'][platform.system()+platform.architecture()[0][:2]]
  else: return json_p['downloads'][platform.system()]

  
def is_newer(local_version, remote_version):
  """Returns True if the remote version is newer than the local version."""
  return Version(remote_version) > local_version



@total_ordering
class Version(object):
 VERSION_QUALIFIERS = {
  'alpha': 1,
  'beta': 2,
  'rc': 3
 }

 def __init__(self, version):
  self.version = version
  self.version_qualifier = None
  self.version_qualifier_num = None
  self.sub_version = None
  if isinstance(version, basestring):
   version = version.lower()
   if '-' not in version:
    for q in self.VERSION_QUALIFIERS:
     if q in version:
      self.version_qualifier = q
      self.version_qualifier_num = self.VERSION_QUALIFIERS[q]
      split_version = version.split(q)
      self.version_number = float(split_version[0])
      if len(split_version) > 1:
       self.sub_version = split_version[1]
      return
    self.version_number= float(version)
    return
   split_version = version.split('-')
   self.version_number= float(split_version[0])
   self.version_qualifier = split_version [1]
   self.version_qualifier_num = self.VERSION_QUALIFIERS[self.version_qualifier]
   if len(split_version) == 3:
    self.sub_version = int(split_version[2])
  else:
   self.version_number= float(version)

 def __lt__(self, other):
  if not isinstance(other, self.__class__):
   other = Version(other)
  if other.version_qualifier == self.version_qualifier == None:
   return self.version_number< other.version_number
  if self.version_number < other.version_number:
   return True
  elif self.version_number > other.version_number:
   return False
  if other.version_number == self.version_number and not other.version_qualifier_num and self.version_qualifier_num:
   return True
  if other.version_number == self.version_number and self.version_qualifier_num == self.version_qualifier_num and self.sub_version < other.sub_version:
   return True
  return self.version_qualifier_num < other.version_qualifier_num

 def __gt__(self, other):
  if not isinstance(other, self.__class__):
   other = Version(other)
  if other.version_qualifier == self.version_qualifier == None:
   return self.version_number > other.version_number
  if self.version_number < other.version_number:
   return False
  elif self.version_number > other.version_number:
   return True
  if other.version_number == self.version_number and not other.version_qualifier_num and self.version_qualifier_num:
   return False
  if other.version_number == self.version_number and self.version_qualifier_num == self.version_qualifier_num and self.sub_version > other.sub_version:
   return True
  return self.version_qualifier_num > other.version_qualifier_num



  
class CustomURLOpener(FancyURLopener):
 def http_error_default(*a, **k):
  return URLopener.http_error_default(*a, **k)
