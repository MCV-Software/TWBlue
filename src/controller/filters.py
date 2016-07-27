# -*- coding: utf-8 -*-
from wxUI.dialogs import filters

class filterController(object):
 def __init__(self):
  self.dialog = filters.filterDialog()
  self.dialog.get_response()