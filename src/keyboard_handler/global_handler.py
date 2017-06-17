
import platform
if platform.system() == 'Linux':
 from .linux import LinuxKeyboardHandler as GlobalKeyboardHandler
elif platform.system() == 'Windows':
 from .wx_handler import WXKeyboardHandler as GlobalKeyboardHandler
elif platform.system() == 'Darwin':
 from .osx import OSXKeyboardHandler as GlobalKeyboardHandler
