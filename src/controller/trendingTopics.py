# -*- coding: utf-8 -*-
from builtins import object
from wxUI.dialogs import trends
import widgetUtils

class trendingTopicsController(object):
 def __init__(self, session):
  super(trendingTopicsController, self).__init__()
  self.countries = {}
  self.cities = {}
  self.dialog = trends.trendingTopicsDialog()
  self.information = session.twitter.twitter.get_available_trends()
  self.split_information()
  widgetUtils.connect_event(self.dialog.country, widgetUtils.RADIOBUTTON, self.get_places)
  widgetUtils.connect_event(self.dialog.city, widgetUtils.RADIOBUTTON, self.get_places)
  self.get_places()

 def split_information(self):
  for i in self.information:
   if i["placeType"]["name"] == "Country":
    self.countries[i["name"]] = i["woeid"]
   else:
    self.cities[i["name"]] = i["woeid"]

 def get_places(self, event=None):
  values = []
  if self.dialog.get_active() == "country":
   for i in self.information:
    if i["placeType"]["name"] == "Country":
     values.append(i["name"])
  elif self.dialog.get_active() == "city":
   for i in self.information:
    if i["placeType"]["name"] != "Country":
     values.append(i["name"])
  self.dialog.set(values)

 def get_woeid(self):
  selected = self.dialog.get_item()
  if self.dialog.get_active() == "country":
   woeid = self.countries[selected]
  else:
   woeid = self.cities[selected]
  return woeid

 def get_string(self):
  return self.dialog.get_item()