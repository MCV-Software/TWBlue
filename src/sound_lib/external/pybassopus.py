# Copyright(c) Max Kolosov 2009 maxkolosov@inbox.ru
# http://vosolok2008.narod.ru
# BSD license

__version__ = '0.1'
__versionTime__ = '2009-11-15'
__author__ = 'Max Kolosov <maxkolosov@inbox.ru>'
__doc__ = '''
pybassflac.py - is ctypes python module for
BASSFLAC - extension to the BASS audio library,
enabling the playing of FLAC (Free Lossless Audio Codec) encoded files.
'''

import os, sys, ctypes, pybass
from paths import x86_path, x64_path
import libloader

bassopus_module = libloader.load_library('bassopus', x86_path=x86_path, x64_path=x64_path)
func_type = libloader.get_functype()
#Register the plugin with the Bass plugin system.
pybass.BASS_PluginLoad(libloader.find_library_path('bassopus', x86_path=x86_path, x64_path=x64_path), 0)

QWORD = pybass.QWORD
HSTREAM = pybass.HSTREAM
DOWNLOADPROC = pybass.DOWNLOADPROC
BASS_FILEPROCS = pybass.BASS_FILEPROCS

# BASS_CHANNELINFO type
BASS_CTYPE_STREAM_OPUS = 0x11200


#HSTREAM BASSOPUSDEF(BASS_OPUS_StreamCreateFile)(BOOL mem, const void *file, QWORD offset, QWORD length, DWORD flags);
BASS_OPUS_StreamCreateFile = func_type(HSTREAM, ctypes.c_byte, ctypes.c_void_p, QWORD, QWORD, ctypes.c_ulong)(('BASS_OPUS_StreamCreateFile', bassopus_module))
#HSTREAM BASSFLACDEF(BASS_FLAC_StreamCreateURL)(const char *url, DWORD offset, DWORD flags, DOWNLOADPROC *proc, void *user);
BASS_OPUS_StreamCreateURL = func_type(HSTREAM, ctypes.c_char_p, ctypes.c_ulong, ctypes.c_ulong, DOWNLOADPROC, ctypes.c_void_p)(('BASS_OPUS_StreamCreateURL', bassopus_module))
#HSTREAM BASSFLACDEF(BASS_FLAC_StreamCreateFileUser)(DWORD system, DWORD flags, const BASS_FILEPROCS *procs, void *user);
BASS_OPUS_StreamCreateFileUser = func_type(HSTREAM, ctypes.c_ulong, ctypes.c_ulong, ctypes.POINTER(BASS_FILEPROCS), ctypes.c_void_p)(('BASS_OPUS_StreamCreateFileUser', bassopus_module))


if __name__ == "__main__":
	if not pybass.BASS_Init(-1, 44100, 0, 0, 0):
		print 'BASS_Init error', pybass.get_error_description(pybass.BASS_ErrorGetCode())
	else:
		handle = BASS_OPUS_StreamCreateFile(False, 'test.opus', 0, 0, 0)
		pybass.play_handle(handle)
		if not pybass.BASS_Free():
			print 'BASS_Free error', pybass.get_error_description(pybass.BASS_ErrorGetCode())
