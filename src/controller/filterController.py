# -*- coding: utf-8 -*-
from wxUI.dialogs import filterDialogs

class filter(object):
 def __init__(self):
  self.dialog = filterDialogs.filterDialog()
  self.dialog.get_response()