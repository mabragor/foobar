#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (c) 2009 Ruslan Popov <ruslan.popov@gmail.com>

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class DlgWaitingRFID(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        self.parent = parent

        self.layout = QVBoxLayout()

        self.label = QLabel(self.tr('Put the RFID label on to the RFID reader, please.'))
        self.layout.addWidget(self.label)

        self.setLayout(self.layout)
        #self.setWindowTitle(self.tr('Place the course'))
