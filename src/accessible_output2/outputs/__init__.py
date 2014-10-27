import platform
if platform.system() == 'Windows':
 import nvda
 import jaws
 import sapi5
 import window_eyes
 import system_access
 import dolphin
 import pc_talker
 #import sapi4
elif platform.system() == "Darwin":
 import voiceover
elif platform.system() == "Linux":
 import speechDispatcher

import auto
