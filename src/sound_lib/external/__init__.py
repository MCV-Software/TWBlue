import platform
#if platform.system() == 'Windows':
# import sound_lib.external.pybasswma
if platform.system() != 'Darwin':
 import sound_lib.external.pybass_aac
 import sound_lib.external.pybass_alac
 import sound_lib.external.pybassopus
 import sound_lib.external.pybassflac
 import sound_lib.external.pybassmidi
