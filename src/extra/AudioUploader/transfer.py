# -*- coding: utf-8 -*-
import pycurl
import sys
import threading
import time
import json
import logging
from utils import *
from pubsub import pub

log = logging.getLogger("extra.AudioUploader.transfer")
class Transfer(object):

 def __init__(self, url=None, filename=None, follow_location=True, completed_callback=None, verbose=False, *args, **kwargs):
  self.url = url
  self.filename = filename
  log.debug("Uploading audio to %s, filename %s" % (url, filename))
  self.curl = pycurl.Curl()
  self.start_time = None
  self.completed_callback = completed_callback
  self.background_thread = None
  self.transfer_rate = 0
  self.curl.setopt(self.curl.PROGRESSFUNCTION, self.progress_callback)
  self.curl.setopt(self.curl.URL, url)
  self.curl.setopt(self.curl.NOPROGRESS, 0)
  self.curl.setopt(self.curl.HTTP_VERSION, self.curl.CURL_HTTP_VERSION_1_0)
  self.curl.setopt(self.curl.FOLLOWLOCATION, int(follow_location))
  self.curl.setopt(self.curl.VERBOSE, int(verbose))
  super(Transfer, self).__init__(*args, **kwargs)

 def elapsed_time(self):
  if not self.start_time:
   return 0
  return time.time() - self.start_time

 def progress_callback(self, down_total, down_current, up_total, up_current):
  progress = {}
  progress["total"] = up_total
  progress["current"] = up_current
#  else:
#   print "Killed function"
#   return
  if progress["current"] == 0:
   progress["percent"] = 0
   self.transfer_rate = 0
  else:
   progress["percent"] = int((float(progress["current"]) / progress["total"]) * 100)
   self.transfer_rate = progress["current"] / self.elapsed_time()
  progress["speed"] = '%s/s' % convert_bytes(self.transfer_rate)
  if self.transfer_rate:
   progress["eta"] = (progress["total"] - progress["current"]) / self.transfer_rate
  else:
   progress["eta"] = 0
  pub.sendMessage("uploading", data=progress)

 def perform_transfer(self):
  log.debug("starting upload...")
  self.start_time = time.time()
  self.curl.perform()
  self.curl.close()
  log.debug("Upload finished.")
  self.complete_transfer()

 def perform_threaded(self):
  self.background_thread = threading.Thread(target=self.perform_transfer)
  self.background_thread.daemon = True
  self.background_thread.start()

 def complete_transfer(self):
  if callable(self.completed_callback):
   self.curl.close()
   self.completed_callback()

class Upload(Transfer):

 def __init__(self, field=None, filename=None, *args, **kwargs):
  super(Upload, self).__init__(filename=filename, *args, **kwargs)
  self.response = dict()
  self.curl.setopt(self.curl.POST, 1)
  if isinstance(filename, unicode):
   local_filename = filename.encode(sys.getfilesystemencoding())
  else:
   local_filename = filename
  self.curl.setopt(self.curl.HTTPPOST, [(field, (self.curl.FORM_FILE, local_filename, self.curl.FORM_FILENAME, filename.encode("utf-8")))])
  self.curl.setopt(self.curl.HEADERFUNCTION, self.header_callback)
  self.curl.setopt(self.curl.WRITEFUNCTION, self.body_callback)

 def header_callback(self, content):
  self.response['header'] = content

 def body_callback(self, content):
  self.response['body'] = content

 def get_url(self):
  return json.loads(self.response['body'])['url']

class Download(Transfer):

 def __init__(self, follow_location=True, *args, **kwargs):
  super(Download, self).__init__(*args, **kwargs)
  self.download_file = open(self.filename, 'wb')
  self.curl.setopt(self.curl.WRITEFUNCTION, self.download_file.write)

 def complete_transfer(self):
  self.download_file.close()
  super(DownloadDialog, self).complete_transfer()