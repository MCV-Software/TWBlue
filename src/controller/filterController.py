# -*- coding: utf-8 -*-
import application
from wxUI.dialogs import filterDialogs

class filter(object):
 def __init__(self):
  self.dialog = filterDialogs.filterDialog(languages=[i["name"] for i in application.supported_languages])
  self.dialog.get_response()