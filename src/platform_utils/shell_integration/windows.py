from future import standard_library
standard_library.install_aliases()
import winreg

SHELL_REGKEY = r"Directory\shell"

def context_menu_integrate(item_key_name, item_display_text, item_command):
 app_menu_key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, SHELL_REGKEY, 0, winreg.KEY_WRITE)
 menu_item_key = winreg.CreateKey(app_menu_key, item_key_name)
 winreg.SetValueEx(menu_item_key, None, None, winreg.REG_SZ, item_display_text)
 item_command_key = winreg.CreateKey(menu_item_key, 'command')
 winreg.SetValueEx(item_command_key, None, None, winreg.REG_SZ, item_command)
