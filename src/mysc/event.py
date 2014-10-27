# -- coding: utf-8 -*-
from wx.lib.newevent import NewEvent
import wx
EVT_DELETED = wx.NewEventType()
MyEVT_DELETED = wx.PyEventBinder(EVT_DELETED, 1)
EVT_STARTED = wx.NewEventType()
MyEVT_STARTED = wx.PyEventBinder(EVT_STARTED, 1)
EVT_OBJECT = wx.NewEventType()
MyEVT_OBJECT = wx.PyEventBinder(EVT_OBJECT, 1)

ResultEvent, EVT_RESULT = NewEvent()
#DeletedEvent, EVT_DELETED = NewEvent()

class event(wx.PyCommandEvent):
 def __init__(self, evtType, id):
  self.text = ""
  wx.PyCommandEvent.__init__(self, evtType, id)

 def SetItem(self, item):
  self.item = item

 def GetItem(self):
  return self.item

 def SetAnnounce(self, text ):
  self.text = text

 def GetAnnounce(self):
  try: return self.text
  except: pass

class infoEvent(event):
 def __init__(self, evtType, id):
  event.__init__(self, evtType, id)

 def SetItem(self, page, items):
  self.page = page
  self.items = items

 def GetItem(self):
  return [self.page, self.items]