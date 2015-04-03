# -*- coding: utf-8 -*-
from gi.repository import Gtk
import widgetUtils

class soundsTutorialDialog(Gtk.Dialog):
 def __init__(self, actions):
  super(soundsTutorialDialog, self).__init__("Sounds tutorial", None, 0, (Gtk.STOCK_CANCEL, widgetUtils.CANCEL))
  box = self.get_content_area()
  label = Gtk.Label("Press enter for listen the sound")
  self.list = widgetUtils.list("Action")
  self.populate_actions(actions)
  lBox = Gtk.Box(spacing=6)
  lBox.add(label)
  lBox.add(self.list.list)
  box.add(lBox)
  self.play = Gtk.Button("Play")
  box.add(self.play)
  self.show_all()

 def populate_actions(self, actions):
  for i in actions:
   self.list.insert_item(i)

 def get_selected(self):
  return self.list.get_selected()