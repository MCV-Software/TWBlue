import _winreg

SHELL_REGKEY = ur"Directory\shell"

def context_menu_integrate(item_key_name, item_display_text, item_command):
 app_menu_key = _winreg.OpenKey(_winreg.HKEY_CLASSES_ROOT, SHELL_REGKEY, 0, _winreg.KEY_WRITE)
 menu_item_key = _winreg.CreateKey(app_menu_key, item_key_name)
 _winreg.SetValueEx(menu_item_key, None, None, _winreg.REG_SZ, item_display_text)
 item_command_key = _winreg.CreateKey(menu_item_key, 'command')
 _winreg.SetValueEx(item_command_key, None, None, _winreg.REG_SZ, item_command)
