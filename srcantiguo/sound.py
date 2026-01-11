# -*- coding: utf-8 -*-
import os
import logging as original_logger 
import sys
import subprocess
import platform
import tempfile
import glob
import audio_services
import paths
import sound_lib
import output
from audio_services import youtube_utils
import application
system = platform.system()
if system=="Windows" and not hasattr(sys, 'frozen'): # We are running from source on Windows
    current_dir=os.getcwd()
    os.chdir(os.environ['PYTHON_VLC_MODULE_PATH'])
import vlc
if system=="Windows" and not hasattr(sys, 'frozen'): # Restore the original folder
    os.chdir(current_dir)
import sound_lib.output, sound_lib.input, sound_lib.stream, sound_lib.recording
from mysc.repeating_timer import RepeatingTimer
from mysc.thread_utils import call_threaded

URLPlayer = None

log = original_logger.getLogger("sound")

def setup():
    global URLPlayer
    if not URLPlayer:
        log.debug("creating stream URL player...")
        URLPlayer = URLStream()

def recode_audio(filename, quality=4.5):
    global system
    if system == "Windows": subprocess.call(r'"%s" -q %r "%s"' % (os.path.join(paths.app_path(), 'oggenc2.exe'), quality, filename))

def recording(filename):
    # try:
    val = sound_lib.recording.WaveRecording(filename=filename)
# except sound_lib.main.BassError:
#  sound_lib.input.Input()
#  val = sound_lib.recording.WaveRecording(filename=filename)
    return val

class soundSystem(object):

    def check_soundpack(self):
        """ Checks if the folder where live the current soundpack exists."""
        self.soundpack_OK = False
        if os.path.exists(os.path.join(paths.sound_path(), self.config["current_soundpack"])):
            self.path = os.path.join(paths.sound_path(), self.config["current_soundpack"])
            self.soundpack_OK = True
        elif os.path.exists(os.path.join(paths.sound_path(), "default")):
            log.error("The soundpack does not exist, using default...")
            self.path = os.path.join(paths.sound_path(), "default")
            self.soundpack_OK = True
        else:
            log.error("The current soundpack could not be found and the default soundpack has been deleted, " + application.name + " will not play sounds.")
            self.soundpack_OK = False

    def __init__(self, soundConfig):
        """ Sound Player."""
        self.config = soundConfig
        # Set the output and input default devices.
        try:
            self.output = sound_lib.output.Output()
            self.input = sound_lib.input.Input()
        except:
            pass
            # Try to use the selected device from the configuration. It can fail if the machine does not has a mic.
        try:
            log.debug("Setting input and output devices...")
            self.output.set_device(self.output.find_device_by_name(self.config["output_device"]))
            self.input.set_device(self.input.find_device_by_name(self.config["input_device"]))
        except:
            log.error("Error in input or output devices, using defaults...")
            self.config["output_device"] = "Default"
            self.config["input_device"] = "Default"

        self.files = []
        self.cleaner = RepeatingTimer(60, self.clear_list)
        self.cleaner.start()
        self.check_soundpack()

    def clear_list(self):
        if len(self.files) == 0: return
        try:
            for i in range(0, len(self.files)):
                if self.files[i].is_playing == False:
                    self.files[i].free()
                    self.files.pop(i)
        except IndexError:
            pass

    def play(self, sound, argument=False):
        if self.soundpack_OK == False: return
        if self.config["session_mute"] == True: return
        sound_object = sound_lib.stream.FileStream(file="%s/%s" % (self.path, sound))
        sound_object.volume = float(self.config["volume"])
        self.files.append(sound_object)
        sound_object.play()

class URLStream(object):
    """ URL Stream Player implementation."""

    def __init__(self):
        # URL status. Should be True after URL expansion and transformation.
        self.prepared = False
        log.debug("URL Player initialized")
        # LibVLC controls.
        self.instance = vlc.Instance("--quiet")
        self.instance.log_unset()
        self.player = self.instance.media_player_new()
        self.event_manager = self.player.event_manager()
        self.event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self.end_callback)

    def prepare(self, url):
        """ Takes an URL and prepares it to be streamed. This function will try to unshorten the passed URL and, if needed, to transform it into a valid URL."""
        log.debug("Preparing URL: %s" % (url,))
        self.prepared = False
        self.url = url
        if self.url == None:
            self.url = url
            log.debug("Expanded URL: %s" % (self.url,))
        if self.url != None:
            transformer = audio_services.find_url_transformer(self.url)
            transformed_url = transformer(self.url)
            self.url = transformed_url
        log.debug("Transformed URL: %s. Prepared" % (self.url,))
        self.prepared = True

    def seek(self, step):
        pos=self.player.get_time()
        pos+=step
        pos=self.player.set_time(pos)

    def playpause(self):
        if self.player.is_playing() == True:
            self.player.pause()
        else:
            self.player.play()

    def play(self, url=None, volume=1.0, announce=True):
        if announce:
            output.speak(_(u"Playing..."))
        log.debug("Attempting to play an URL...")
        if url != None:
            self.prepare(url)
        if self.prepared == True:
            media = self.instance.media_new(self.url)
            self.player.set_media(media)
            self.player.audio_set_volume(int(volume*100))
            self.player.play()
            log.debug("played")
            self.prepared=False

    def stop_audio(self):
        output.speak(_(u"Stopped."), True)
        self.player.stop()

    def end_callback(self, event, *args, **kwargs):
        call_threaded(self.player.stop)

    def __del__(self):
        self.event_manager.event_detach(vlc.EventType.MediaPlayerEndReached)