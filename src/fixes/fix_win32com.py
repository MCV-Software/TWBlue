import win32com.client


def fix():
	if win32com.client.gencache.is_readonly == True:
		win32com.client.gencache.is_readonly = False
		win32com.client.gencache.Rebuild()