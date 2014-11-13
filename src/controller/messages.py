# -*- coding: utf-8 -*-
import widgetUtils
from wxUI.dialogs import message

class tweet(object):
 def __init__(self, session):
  super(tweet, self).__init__()
  self.message = message.tweet(_(u"Write the tweet here"), _(u"tweet - 0 characters"), "")
  