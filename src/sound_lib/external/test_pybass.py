from __future__ import print_function
from future.builtins import hex
from .pybass import *

def play_handle(handle, show_tags = True):
	if handle == 0:
		print(('BASS_StreamCreateFile error', get_error_description(BASS_ErrorGetCode())))
	else:
		if show_tags:
			print('============== Tags Information ==============')
			try:
				import pytags
				print((pytags.TAGS_Read(handle, '%IFV1(%ITRM(%TRCK),%ITRM(%TRCK). )%IFV2(%ITRM(%ARTI),%ICAP(%ITRM(%ARTI)),no artist) - %IFV2(%ITRM(%TITL),%ICAP(%ITRM(%TITL)),no title)%IFV1(%ITRM(%ALBM), - %IUPC(%ITRM(%ALBM)))%IFV1(%YEAR, %(%YEAR%))%IFV1(%ITRM(%GNRE), {%ITRM(%GNRE)})%IFV1(%ITRM(%CMNT), [%ITRM(%CMNT)])')))
			except:
				print('============== tags module not accessible ==============')
				print('============== BASS_ChannelGetTags return ==============')
				for tag in get_tags(handle):
					print(tag)
				for key, value in get_tags_as_dict(handle).items():
					print((key, ':', value))
		print('============== Channel Information ==============')
		channel_info = BASS_CHANNELINFO()
		if not BASS_ChannelGetInfo(handle, channel_info):
			print(('BASS_ChannelGetInfo error', get_error_description(BASS_ErrorGetCode())))
		else:
			print(('default playback rate =', channel_info.freq))
			print(('channels =', channel_info.chans))
			print(('BASS_SAMPLE/STREAM/MUSIC/SPEAKER flags =', channel_info.flags))
			print(('type of channel =', hex(channel_info.ctype)))
			print(('original resolution =', channel_info.origres))
			print(('plugin =', channel_info.plugin))
			print(('sample =', channel_info.sample))
			print(('filename =', channel_info.filename))
		print('============== Ext Channel Information ==============')
		channel_length = BASS_ChannelGetLength(handle, BASS_POS_BYTE)
		channel_position = BASS_ChannelGetPosition(handle, BASS_POS_BYTE)
		print(('Channel Length =', channel_length))
		print(('Channel Length =', int(BASS_ChannelBytes2Seconds(handle, channel_length)), 'seconds'))
		import time
		if not BASS_ChannelPlay(handle, False):
			print(('BASS_ChannelPlay error', get_error_description(BASS_ErrorGetCode())))
		else:
			print('============== Play Information ==============')
			while channel_position < channel_length:
				channel_position = BASS_ChannelGetPosition(handle, BASS_POS_BYTE)
				print(('Channel Position =', channel_position))
				print(('Channel Position =', int(BASS_ChannelBytes2Seconds(handle, channel_position)), 'seconds'))
				print(('CPU =', BASS_GetCPU()))
				time.sleep(1)
		if not BASS_StreamFree(handle):
			print(('BASS_StreamFree error', get_error_description(BASS_ErrorGetCode())))

if __name__ == "__main__":
	print(('BASS implemented Version', BASSVERSIONTEXT))
	print(('BASS real Version', hex(BASS_GetVersion())))
	if not BASS_Init(-1, 44100, 0, 0, 0):
		print(('BASS_Init error', get_error_description(BASS_ErrorGetCode())))
	else:
		print('============== BASS Information ==============')
		bi = BASS_INFO()
		if not BASS_GetInfo(bi):
			print(('BASS_GetInfo error', get_error_description(BASS_ErrorGetCode())))
		else:
			print(('device capabilities (DSCAPS_xxx flags) =', bi.flags))
			print(('size of total device hardware memory =', bi.hwsize))
			print(('size of free device hardware memory =', bi.hwfree))
			print(('number of free sample slots in the hardware =', bi.freesam))
			print(('number of free 3D sample slots in the hardware =', bi.free3d))
			print(('min sample rate supported by the hardware =', bi.minrate))
			print(('max sample rate supported by the hardware =', bi.maxrate))
			print(('device supports EAX? (always FALSE if BASS_DEVICE_3D was not used) =', bool(bi.eax)))
			print(('recommended minimum buffer length in ms (requires BASS_DEVICE_LATENCY) =', bi.minbuf))
			print(('DirectSound version =', bi.dsver))
			print(('delay (in ms) before start of playback (requires BASS_DEVICE_LATENCY) =', bi.latency))
			print(('BASS_Init "flags" parameter =', bi.initflags))
			print(('number of speakers available', bi.speakers))
			print(('current output rate (Vista/OSX only) =', bi.freq))
		print('============== volume ==============')
		print(('volume =', BASS_GetVolume()))
		print('============== Device Information ==============')
		bd = BASS_DEVICEINFO()
		if not BASS_GetDeviceInfo(BASS_GetDevice(), bd):
			print(('BASS_GetDeviceInfo error', get_error_description(BASS_ErrorGetCode())))
		else:
			print(('description =', bd.name))
			print(('driver =', bd.driver))
			print(('flags =', bd.flags))
		handle = BASS_StreamCreateFile(False, 'test.ogg', 0, 0, 0)
		play_handle(handle)
		if not BASS_Free():
			print(('BASS_Free error', get_error_description(BASS_ErrorGetCode())))
