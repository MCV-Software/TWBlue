# -*- coding: utf-8 -*-


from builtins import object
from past.utils import old_div
import sys
import threading
import time
import logging
from .utils import convert_bytes
from pubsub import pub
log = logging.getLogger("extra.AudioUploader.transfer")
from requests_toolbelt.multipart.encoder import MultipartEncoder, MultipartEncoderMonitor
import requests
import os
class Upload(object):
 def __init__(self, field=None, obj=None, url=None, filename=None, follow_location=True, completed_callback=None, verbose=False, *args, **kwargs):
  super(Upload, self).__init__(*args, **kwargs)
  self.url=url
  self.filename=filename
  log.debug("Uploading audio to %s, filename %s" % (url, filename))
  self.start_time = None
  self.completed_callback = completed_callback
  self.background_thread = None
  self.transfer_rate = 0
  self.local_filename=os.path.basename(self.filename)
  if isinstance(self.local_filename, str):
    self.local_filename=self.local_filename.encode(sys.getfilesystemencoding())
  self.fin=open(self.filename, 'rb')
  self.m = MultipartEncoder(fields={field:(self.local_filename, self.fin, "application/octet-stream")})
  self.monitor = MultipartEncoderMonitor(self.m, self.progress_callback)
  self.response=None
  self.obj=obj
  self.follow_location=follow_location
  #the verbose parameter is deprecated and will be removed soon

 def elapsed_time(self):
  if not self.start_time:
   return 0
  return time.time() - self.start_time

 def progress_callback(self, monitor):
  progress = {}
  progress["total"] = monitor.len
  progress["current"] = monitor.bytes_read
  if progress["current"] == 0:
   progress["percent"] = 0
   self.transfer_rate = 0
  else:
   progress["percent"] = int((old_div(float(progress["current"]), progress["total"])) * 100)
   self.transfer_rate = old_div(progress["current"], self.elapsed_time())
  progress["speed"] = '%s/s' % convert_bytes(self.transfer_rate)
  if self.transfer_rate:
   progress["eta"] = old_div((progress["total"] - progress["current"]), self.transfer_rate)
  else:
   progress["eta"] = 0
  pub.sendMessage("uploading", data=progress)

 def perform_transfer(self):
  log.debug("starting upload...")
  self.start_time = time.time()
  self.response=requests.post(url=self.url, data=self.monitor, headers={"Content-Type":self.m.content_type}, allow_redirects=self.follow_location, stream=True)
  log.debug("Upload finished.")
  self.complete_transfer()

 def perform_threaded(self, *args, **kwargs):
  self.background_thread = threading.Thread(target=self.perform_transfer)
  self.background_thread.daemon = True
  self.background_thread.start()

 def complete_transfer(self):
  if callable(self.completed_callback):
   self.completed_callback(self.obj)
  if hasattr(self,'fin') and callable(self.fin.close):
   self.fin.close()
 def get_url(self):
  return self.response.json()['url']
