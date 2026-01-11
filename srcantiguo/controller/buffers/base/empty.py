# -*- coding: utf-8 -*-
import logging
from wxUI import buffers
from . import base

log = logging.getLogger("controller.buffers.base.empty")

class EmptyBuffer(base.Buffer):
    def __init__(self, parent, name, account):
        super(EmptyBuffer, self).__init__(parent=parent)
        log.debug("Initializing buffer %s, account %s" % (name, account,))
        self.buffer = buffers.emptyPanel(parent, name)
        self.type = self.buffer.type
        self.compose_function = None
        self.account = account
        self.buffer.account = account
        self.name = name
        self.session = None
        self.needs_init = True
