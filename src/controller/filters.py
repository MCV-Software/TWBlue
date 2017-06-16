# -*- coding: utf-8 -*-
from builtins import object
from wxUI.dialogs import filters

class filterController(object):
 def __init__(self):
  self.dialog = filters.filterDialog()
  self.dialog.get_response()